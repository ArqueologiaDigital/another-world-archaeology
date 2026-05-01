#!/usr/bin/env python3
"""Canonicalize cross-port CINEMATIC_xxxx synonym names by walking
a unified output file produced by `unify_asm.py`.

Each port's disasm assigns `CINEMATIC_NNN` indices in encounter order,
so the SAME logical polygon gets a different index per port. When the
unified source has a `;@if/elif` block whose arms differ only in the
CINEMATIC name (all other operands equal), the names are functioning
as cross-port synonyms — picking one as canonical and renaming the
other(s) collapses the block.

The actual polygon offsets stay per-branch (each port has its own
cinematic.rom layout, so the EQU values differ). After rename, the
EQU section gains a multi-arm `;@if/elif` block for the canonical
name (the conflict-tail mechanism in canonicalize_labels.py handles
this), but the video instructions in the body become identical and
no longer need their own `;@if` blocks. Net win when many video
divergences collapse.

This is safe because:
- The bytecode uses the EQU value (offset), not the name.
- Each branch keeps its own EQU value for the canonical name.
- The canonical name is a NAMING choice, not a semantic claim that
  the polygons are byte-identical (they may not be — research
  question: do per-port cinematic.rom layouts have byte-identical
  polygons in different orderings?).

Algorithm:
1. Parse the unified `.asm.in` file's top-level `;@if/.../;@endif`
   blocks.
2. For each block whose arms differ ONLY in a CINEMATIC name (every
   other token equal, exactly one CINEMATIC per arm), collect the
   per-branch synonym pairs.
3. Build a rename map: pick canonical (more-descriptive name wins;
   numeric tie-break by smaller index), rewrite non-canonical names
   in their respective per-branch source files.
4. Caller re-runs the canonicalize → unify pipeline; the previously
   divergent blocks now collapse into shared lines.

Usage:
    python3 tools/canonicalize_cinematic_refs.py \\
        --unified-in path/to/3way.asm.in \\
        --src cartridge_1992=path/to/cart.asm \\
        --src gba_2004=path/to/gba.asm \\
        --src chahi_amiga_1991=path/to/amiga.asm \\
        --src-out cartridge_1992=path/to/cart.out.asm \\
        --src-out gba_2004=path/to/gba.out.asm \\
        --src-out chahi_amiga_1991=path/to/amiga.out.asm
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

RE_CINEMATIC = re.compile(r'\bCINEMATIC_[A-Z_0-9]+\b')
RE_LABEL = re.compile(r'\bLABEL_[A-Fa-f0-9]+\b')
RE_RAW = re.compile(r';@raw=[0-9A-Fa-fx,]+\s*$')

# The pattern of names this tool canonicalizes is configurable. Default
# is CINEMATIC_*, but the same mechanism works for LABEL_* (inline
# code labels at logically-equivalent positions whose port-disasm
# addresses differ).
_PATTERNS = {
    "cinematic": RE_CINEMATIC,
    "label": RE_LABEL,
}
_ACTIVE_PATTERN: re.Pattern = RE_CINEMATIC


def normalize_for_diff(line: str) -> str:
    """Blank every match of the active token pattern AND the
    `;@raw=` annotation so difflib aligns lines that differ only in
    the named reference."""
    line = _ACTIVE_PATTERN.sub("<X>", line)
    line = RE_RAW.sub("", line).rstrip()
    return line


RE_BRANCH_IF = re.compile(
    r';@if\s+BRANCH\s+(?:==|in)\s+\(?\s*"?([\w,\s")"]+)'
)


def _parse_branch_cond(line: str) -> set[str]:
    """Extract the set of branch names from `;@if BRANCH == "x"` or
    `;@if BRANCH in ("x", "y")`."""
    s = line.strip()
    return set(re.findall(r'"([^"]+)"', s))


def find_synonyms_in_unified(
    unified_lines: list[str],
) -> list[dict[str, str]]:
    """Walk the unified file's top-level `;@if/.../;@endif` blocks.
    Return a list of dicts where each dict maps `branch_name` →
    `cinematic_name`. Each entry corresponds to one cross-port
    synonym set (every branch in the dict refers to the same logical
    cinematic via a different name).
    """
    syn_sets: list[dict[str, str]] = []
    i = 0
    n = len(unified_lines)
    while i < n:
        s = unified_lines[i].lstrip()
        if not s.startswith(";@if "):
            i += 1
            continue
        # Find matching ;@endif
        depth = 1
        sec_starts = [i]
        j = i + 1
        while j < n:
            ss = unified_lines[j].lstrip()
            if ss.startswith(";@if "):
                depth += 1
            elif ss.startswith(";@endif"):
                depth -= 1
                if depth == 0:
                    break
            elif depth == 1 and (
                ss.startswith(";@elif ") or ss.startswith(";@else")
            ):
                sec_starts.append(j)
            j += 1
        if j >= n:
            break
        # Build per-section content (stripping blanks).
        sections = []
        for k in range(len(sec_starts)):
            body_start = sec_starts[k] + 1
            body_end = sec_starts[k + 1] if k + 1 < len(sec_starts) else j
            body = [
                unified_lines[t]
                for t in range(body_start, body_end)
                if unified_lines[t].strip()
            ]
            sections.append((unified_lines[sec_starts[k]], body))
        # Block must have at least 2 sections. All arms must have the
        # same number of content lines, AND each line position must
        # be identical across arms when the active token is blanked.
        # The blanked tokens at corresponding positions form ONE
        # synonym set per (block, line_position).
        if (len(sections) >= 2
                and len(set(len(s[1]) for s in sections)) == 1
                and len(sections[0][1]) >= 1):
            n_lines = len(sections[0][1])
            # All-arm normalized lines: list of tuples.
            normalized_arms = [
                tuple(normalize_for_diff(l) for l in body)
                for _, body in sections
            ]
            # Every arm's normalized form must be identical.
            if all(n == normalized_arms[0] for n in normalized_arms):
                # For each line position, build a synonym set if the
                # line has exactly ONE active-pattern token in every
                # arm AND the tokens differ across arms.
                for line_idx in range(n_lines):
                    tokens_per_arm = [
                        _ACTIVE_PATTERN.findall(body[line_idx])
                        for _, body in sections
                    ]
                    if not all(len(toks) == 1 for toks in tokens_per_arm):
                        continue
                    arm_tokens = [toks[0] for toks in tokens_per_arm]
                    # Build dict: branch → token
                    entry: dict[str, str] = {}
                    ok = True
                    for (header, _), tok in zip(sections, arm_tokens):
                        branches = _parse_branch_cond(header)
                        if not branches:
                            ok = False
                            break
                        for br in branches:
                            if br in entry and entry[br] != tok:
                                ok = False
                                break
                            entry[br] = tok
                        if not ok:
                            break
                    if (ok and len(entry) >= 2
                            and len(set(entry.values())) > 1):
                        syn_sets.append(entry)
        i = j + 1
    return syn_sets


def pick_canonical(name_a: str, name_b: str) -> str:
    """Pick canonical from two CINEMATIC names. Prefer the
    semantically richer name (more alpha components), then
    alphabetically smaller as tie-break."""
    def score(n: str) -> tuple[int, int]:
        parts = n.split('_')
        alpha = sum(1 for p in parts if any(c.isalpha() for c in p)
                    and not all(c in '0123456789ABCDEFabcdef' for c in p))
        return (alpha, -len(n))  # more alpha is better; shorter as tie-break
    return max([name_a, name_b], key=score) if score(name_a) != score(name_b) else min(name_a, name_b)


def apply_renames(text: str, rename_map: dict[str, str]) -> str:
    if not rename_map:
        return text
    pattern = re.compile(
        r'\b(' + '|'.join(re.escape(k) for k in rename_map) + r')\b'
    )
    return pattern.sub(lambda m: rename_map[m.group(1)], text)


def main() -> None:
    global _ACTIVE_PATTERN
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--unified-in", required=True, type=Path,
                   help="path to unified .asm.in file (output of unify_asm.py)")
    p.add_argument("--src", action="append", default=[],
                   metavar="BRANCH=PATH",
                   help="per-branch input source path")
    p.add_argument("--src-out", action="append", default=[],
                   metavar="BRANCH=PATH",
                   help="per-branch output path")
    p.add_argument("--token", default="cinematic",
                   choices=sorted(_PATTERNS.keys()),
                   help="which kind of name to canonicalize: "
                        "'cinematic' (CINEMATIC_*) or 'label' (LABEL_*).")
    p.add_argument("--fresh-name-prefix", default=None,
                   help="when canonical-name conflicts prevent renaming, "
                        "generate fresh names like <PREFIX>_001, _002, ... "
                        "(e.g. --fresh-name-prefix=CINEMATIC_LAKE). Without "
                        "this, conflicted sets are left as ;@if blocks.")
    args = p.parse_args()
    _ACTIVE_PATTERN = _PATTERNS[args.token]

    sources: dict[str, Path] = {}
    for spec in args.src:
        br, _, path_str = spec.partition("=")
        sources[br] = Path(path_str)
    outputs: dict[str, Path] = {}
    for spec in args.src_out:
        br, _, path_str = spec.partition("=")
        outputs[br] = Path(path_str)
    if set(sources) != set(outputs):
        sys.exit("--src and --src-out branches must match")
    if not sources:
        sys.exit("specify at least one --src and matching --src-out")

    unified_lines = args.unified_in.read_text().splitlines()
    syn_sets = find_synonyms_in_unified(unified_lines)
    print(f"  found {len(syn_sets)} {args.token.upper()} synonym set(s)")

    # Each synonym set declares: (branch_X, name_X) and (branch_Y, name_Y)
    # refer to the same logical polygon. Build equivalence classes via
    # union-find over `(branch, name)` keys, then assign one canonical
    # name per class. This handles the case where amiga's `CINEMATIC_015`
    # appears in MULTIPLE synonym sets (each pointing to a different
    # cart/gba name) — all those names land in one equivalence class,
    # not three competing rename targets that fight each other.
    parent: dict[tuple[str, str], tuple[str, str]] = {}

    def find(k: tuple[str, str]) -> tuple[str, str]:
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    def union(a: tuple[str, str], b: tuple[str, str]) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for entry in syn_sets:
        keys = [(br, name) for br, name in entry.items()]
        for k in keys:
            parent.setdefault(k, k)
        for k in keys[1:]:
            union(keys[0], k)

    # Group `(branch, name)` keys by their root.
    classes: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for k in parent:
        classes.setdefault(find(k), []).append(k)

    # Drop trivial classes (only one (branch, name) key — no
    # rename needed).
    classes = {root: members for root, members in classes.items()
               if len({k[1] for k in members}) > 1}
    print(f"  equivalence classes: {len(classes)}")

    # Collect each branch's existing CINEMATIC names (so we can
    # detect canonical-name conflicts).
    branch_existing: dict[str, set[str]] = {}
    for br, path in sources.items():
        branch_existing[br] = set(_ACTIVE_PATTERN.findall(path.read_text()))

    # For each class, pick a canonical name. If the canonical
    # collides with an existing OUT-OF-CLASS name in any branch
    # involved, fall back to a fresh name (when --fresh-name-prefix
    # is given) or skip.
    rename_per_branch: dict[str, dict[str, str]] = {br: {} for br in sources}
    skipped_classes = 0
    canonical_assigned = 0
    fresh_assigned = 0
    fresh_idx = 1
    # Track which (branch, name) have been "used" by previous classes.
    # A class can collide with a previous one if it tries to use a name
    # that another class already claimed in the same branch.
    branch_in_use: dict[str, set[str]] = {br: set() for br in sources}

    for root, members in classes.items():
        names_in_class = list({k[1] for k in members})
        # Pick the most descriptive name in the class.
        canonical = names_in_class[0]
        for n in names_in_class[1:]:
            canonical = pick_canonical(canonical, n)

        # Conflict check: for each branch in this class, would
        # renaming its names to `canonical` collide with a name
        # OUTSIDE this class (i.e., a name that exists in this branch
        # but isn't part of the equivalence)?
        branches_in_class = {k[0] for k in members}
        names_in_class_set = set(names_in_class)

        def conflicts_with(target: str) -> bool:
            for br in branches_in_class:
                if br not in branch_existing:
                    continue
                # Names in this branch that are part of this class.
                in_class_for_br = {
                    k[1] for k in members if k[0] == br
                }
                # If `target` exists in branch but isn't part of this
                # class, it's a conflict.
                if (target in branch_existing[br]
                        and target not in in_class_for_br):
                    return True
                # Also check: has another class already claimed `target`
                # in this branch (potentially mapping it to another
                # canonical)?
                if target in branch_in_use[br] and target != canonical:
                    return True
            return False

        chosen = canonical
        if conflicts_with(canonical):
            if args.fresh_name_prefix:
                while True:
                    candidate = f"{args.fresh_name_prefix}_{fresh_idx:03d}"
                    fresh_idx += 1
                    # Fresh name must not collide with anything in any
                    # involved branch's existing names OR previously
                    # assigned canonicals.
                    bad = False
                    for br in branches_in_class:
                        if (candidate in branch_existing[br]
                                or candidate in branch_in_use[br]):
                            bad = True
                            break
                    if not bad:
                        break
                chosen = candidate
                fresh_assigned += 1
            else:
                skipped_classes += 1
                continue
        else:
            canonical_assigned += 1

        # Apply class rename: every (branch, name) in the class →
        # `chosen`. Skip identity renames.
        for br, name in members:
            if br not in rename_per_branch:
                continue
            if name != chosen:
                rename_per_branch[br][name] = chosen
            branch_in_use[br].add(chosen)

    print(f"  canonical-name renames: {canonical_assigned}")
    print(f"  fresh-name renames: {fresh_assigned}")
    if skipped_classes:
        print(f"  skipped {skipped_classes} class(es) due to conflicts "
              f"(--fresh-name-prefix would unstick these)")

    # Apply renames per branch.
    for br, src_path in sources.items():
        text = src_path.read_text()
        rmap = rename_per_branch[br]
        out_text = apply_renames(text, rmap)
        if not out_text.endswith("\n"):
            out_text += "\n"
        outputs[br].parent.mkdir(parents=True, exist_ok=True)
        outputs[br].write_text(out_text)
        print(f"  {br}: {len(rmap)} renames → {outputs[br]}")


if __name__ == "__main__":
    main()
