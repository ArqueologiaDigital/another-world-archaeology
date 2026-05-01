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
        --src heineman_cartridge=path/to/cart.asm \\
        --src foxy_gba_2004=path/to/gba.asm \\
        --src chahi_1991=path/to/amiga.asm \\
        --src-out heineman_cartridge=path/to/cart.out.asm \\
        --src-out foxy_gba_2004=path/to/gba.out.asm \\
        --src-out chahi_1991=path/to/amiga.out.asm
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

RE_CINEMATIC = re.compile(r'\bCINEMATIC_[A-Z_0-9]+\b')
RE_RAW = re.compile(r';@raw=[0-9A-Fa-fx,]+\s*$')


def normalize_for_diff(line: str) -> str:
    """Blank every CINEMATIC_xxx token AND the `;@raw=` annotation so
    difflib aligns lines that differ only in the cinematic reference
    (the `;@raw=` bytes encode the cinematic offset, so they
    inherently differ when the offset differs — but they're encoder-
    derived, not semantic, and we want the alignment to depend on
    the named operand only)."""
    line = RE_CINEMATIC.sub("<C>", line)
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
        # Block must have at least 2 sections, all with EXACTLY 1
        # content line, all referencing exactly ONE CINEMATIC, and
        # all lines must be identical when CINEMATIC is blanked.
        if len(sections) >= 2 and all(len(s[1]) == 1 for s in sections):
            normalized_set = {normalize_for_diff(s[1][0]) for s in sections}
            cin_counts = [len(RE_CINEMATIC.findall(s[1][0])) for s in sections]
            if len(normalized_set) == 1 and all(c == 1 for c in cin_counts):
                # All sections share normalized form — synonym set!
                entry: dict[str, str] = {}
                ok = True
                for header, body in sections:
                    branches = _parse_branch_cond(header)
                    cin = RE_CINEMATIC.findall(body[0])[0]
                    if not branches:
                        ok = False
                        break
                    for br in branches:
                        if br in entry and entry[br] != cin:
                            ok = False
                            break
                        entry[br] = cin
                    if not ok:
                        break
                if ok and len(entry) >= 2 and len(set(entry.values())) > 1:
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
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--unified-in", required=True, type=Path,
                   help="path to unified .asm.in file (output of unify_asm.py)")
    p.add_argument("--src", action="append", default=[],
                   metavar="BRANCH=PATH",
                   help="per-branch input source path")
    p.add_argument("--src-out", action="append", default=[],
                   metavar="BRANCH=PATH",
                   help="per-branch output path")
    args = p.parse_args()

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
    print(f"  found {len(syn_sets)} CINEMATIC synonym set(s)")

    # For each synonym set, pick canonical name, build per-branch
    # rename map.
    rename_per_branch: dict[str, dict[str, str]] = {br: {} for br in sources}
    skipped_conflicts = 0
    for entry in syn_sets:
        names = list(set(entry.values()))
        if len(names) <= 1:
            continue
        canonical = names[0]
        for n in names[1:]:
            canonical = pick_canonical(canonical, n)
        for br, name in entry.items():
            if name == canonical:
                continue
            if br not in rename_per_branch:
                continue
            existing = rename_per_branch[br].get(name)
            if existing is not None and existing != canonical:
                skipped_conflicts += 1
                continue
            rename_per_branch[br][name] = canonical
    if skipped_conflicts:
        print(f"  skipped {skipped_conflicts} rename(s) due to conflicting "
              f"canonical targets within a branch")

    # Apply renames per branch. Conflict guard: skip a rename if the
    # canonical name is ALREADY USED in this branch's source for a
    # different existing entity (we'd create a name collision).
    for br, src_path in sources.items():
        text = src_path.read_text()
        rmap = rename_per_branch[br]
        existing = set(RE_CINEMATIC.findall(text))
        # Drop renames whose target already exists in this branch
        # (and isn't the source name itself).
        rmap = {
            k: v for k, v in rmap.items()
            if v == k or v not in existing
        }
        out_text = apply_renames(text, rmap)
        if not out_text.endswith("\n"):
            out_text += "\n"
        outputs[br].parent.mkdir(parents=True, exist_ok=True)
        outputs[br].write_text(out_text)
        print(f"  {br}: {len(rmap)} renames → {outputs[br]}")


if __name__ == "__main__":
    main()
