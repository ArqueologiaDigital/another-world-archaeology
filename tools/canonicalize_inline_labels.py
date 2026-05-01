#!/usr/bin/env python3
"""Canonicalize inline `LABEL_NNNN:` labels across branches via structural
alignment.

Companion to `tools/canonicalize_labels.py` (which handles EQU-table
synonym pairs by offset). This tool handles the harder case:
disassembler-generated inline labels that name the same logical
routine across branches but use different addresses (because the
bytecode is at slightly different offsets per port).

Algorithm:
1. Pre-condition: inputs should already have EQU synonyms canonicalized
   (run `tools/canonicalize_labels.py` first), so the only remaining
   per-branch label-name differences are inline labels.
2. Run `difflib.SequenceMatcher` on the two source files line-by-line.
3. For each `replace` diff block, look for `LABEL_<HEX>:` definitions
   on both sides. If the block has exactly one label-definition line
   on each side, they're a synonym pair (same logical position in the
   block, same purpose).
4. Build a rename map per branch:
   - Pick the alphabetically smaller name as canonical (deterministic).
   - In each branch: rename non-canonical name → canonical name
     (touches both the definition line and all reference lines).
5. Filter out conflicts: if the canonical name is already used in the
   target branch (for a DIFFERENT bytecode offset), skip the rename.

Outputs new .asm files alongside the inputs; preserves byte-match.

Usage:
    python3 tools/canonicalize_inline_labels.py \\
        --in heineman_cartridge=cart.asm --in foxy_gba_2004=gba.asm \\
        --out heineman_cartridge=cart.canon.asm --out foxy_gba_2004=gba.canon.asm
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

RE_LABEL_DEF = re.compile(r'^([A-Z][A-Z_0-9]*):\s*$')
RE_INLINE_LABEL = re.compile(r'\bLABEL_[A-Fa-f0-9]+\b')


def normalize_labels_for_diff(line: str) -> str:
    """Replace `LABEL_<HEX>` tokens with `<L>` placeholder for diff
    alignment. Without this, difflib eagerly matches lines like
    `LABEL_1219:` to lines with the SAME NAME in the other branch,
    even when they're at different LOGICAL positions — defeating
    synonym detection."""
    return RE_INLINE_LABEL.sub("<L>", line)


def find_label_synonyms(a_lines: list[str], b_lines: list[str]) -> list[tuple[str, str]]:
    """Return list of (label_a, label_b) synonym pairs found via diff alignment.

    Aligns label-normalized versions of both files: any line containing
    `LABEL_<HEX>` gets the labels replaced with `<L>` before difflib
    matches it. This makes lines like `LABEL_1219:` and `LABEL_1225:`
    look identical to the matcher (`<L>:` vs `<L>:`), so the structural
    alignment is preserved — and we can then extract label names at
    corresponding positions to find synonym pairs."""
    a_norm = [normalize_labels_for_diff(l) for l in a_lines]
    b_norm = [normalize_labels_for_diff(l) for l in b_lines]
    sm = difflib.SequenceMatcher(None, a_norm, b_norm, autojunk=False)
    synonyms: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            # Lines that are "equal" under normalization but DIFFER in
            # their original label names. Pair labels at corresponding
            # positions in each line.
            for ai in range(i1, i2):
                bi = j1 + (ai - i1)
                if bi >= j2:
                    break
                a_orig = a_lines[ai]
                b_orig = b_lines[bi]
                if a_orig == b_orig:
                    continue
                a_labels = RE_INLINE_LABEL.findall(a_orig)
                b_labels = RE_INLINE_LABEL.findall(b_orig)
                if len(a_labels) != len(b_labels):
                    continue
                for la, lb in zip(a_labels, b_labels):
                    if la != lb and (la, lb) not in seen:
                        synonyms.append((la, lb))
                        seen.add((la, lb))
        elif tag == 'replace':
            # Replace blocks: pair labels at same positions if counts match.
            a_block = a_lines[i1:i2]
            b_block = b_lines[j1:j2]
            a_labels = [
                (idx, m.group(1))
                for idx, line in enumerate(a_block)
                if (m := RE_LABEL_DEF.match(line))
            ]
            b_labels = [
                (idx, m.group(1))
                for idx, line in enumerate(b_block)
                if (m := RE_LABEL_DEF.match(line))
            ]
            if len(a_labels) == len(b_labels) and len(a_labels) >= 1:
                for (_, a_name), (_, b_name) in zip(a_labels, b_labels):
                    if a_name != b_name and (a_name, b_name) not in seen:
                        synonyms.append((a_name, b_name))
                        seen.add((a_name, b_name))
    return synonyms


def collect_all_labels(text: str) -> set[str]:
    """All label NAMES defined in text (LABEL_NNNN: lines)."""
    return {
        m.group(1)
        for line in text.splitlines()
        if (m := RE_LABEL_DEF.match(line))
    }


def apply_rename(text: str, rename_map: dict[str, str]) -> str:
    """Whole-token rename, every occurrence."""
    if not rename_map:
        return text
    pattern = re.compile(
        r'\b(' + '|'.join(re.escape(k) for k in rename_map) + r')\b'
    )
    return pattern.sub(lambda m: rename_map[m.group(1)], text)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--in", dest="inputs", action="append", default=[],
                   metavar="BRANCH=PATH",
                   help="input source spec; need exactly two")
    p.add_argument("--out", dest="outputs", action="append", default=[],
                   metavar="BRANCH=PATH",
                   help="output path per branch (must match --in branches)")
    args = p.parse_args()

    if len(args.inputs) != 2:
        sys.exit("specify exactly 2 inputs (this tool is pairwise)")

    inputs: dict[str, Path] = {}
    for spec in args.inputs:
        br, _, path_str = spec.partition("=")
        inputs[br] = Path(path_str)
    outputs: dict[str, Path] = {}
    for spec in args.outputs:
        br, _, path_str = spec.partition("=")
        outputs[br] = Path(path_str)
    if set(inputs) != set(outputs):
        sys.exit("--in and --out branches must match")

    branches = list(inputs.keys())
    a_branch, b_branch = branches[0], branches[1]
    a_text = inputs[a_branch].read_text()
    b_text = inputs[b_branch].read_text()
    a_lines = a_text.splitlines()
    b_lines = b_text.splitlines()

    print(f"diffing {a_branch} ({len(a_lines)} lines) vs {b_branch} ({len(b_lines)} lines)")

    # Find synonym pairs.
    synonyms = find_label_synonyms(a_lines, b_lines)
    print(f"found {len(synonyms)} candidate synonym pairs")

    # Collect all labels per branch (for conflict detection at the
    # POST-RENAME state — see below).
    a_all = collect_all_labels(a_text)
    b_all = collect_all_labels(b_text)

    # Build rename maps. Strategy: pick alphabetically smaller as canonical.
    #
    # Cascading-synonym handling: when the canonical conflicts with an
    # existing label that ITSELF is being renamed away by another pair,
    # the rename is fine (regex alternation in apply_rename() substitutes
    # all tokens in one pass; each occurrence is matched against the
    # ORIGINAL token, not a freshly-renamed one). Example:
    #   pair 1: (A.LABEL_04C9, B.LABEL_04CF) → rename B.LABEL_04CF → LABEL_04C9
    #   pair 2: (A.LABEL_04CF, B.LABEL_04D5) → rename B.LABEL_04D5 → LABEL_04CF
    # Both renames apply in one regex pass, no duplicates after.
    #
    # So the proper conflict check is:
    # 1. Does this rename's TARGET match another rename's SOURCE in the
    #    same branch? (multiple labels collapsing to one — REAL conflict)
    # 2. Does this rename's TARGET match an existing label in the same
    #    branch that's NOT being renamed away by another pair? (REAL conflict)

    a_rename: dict[str, str] = {}
    b_rename: dict[str, str] = {}
    skipped_self = 0
    skipped_dup_target = 0  # multiple renames pointing to same target name
    fresh_names = 0  # used a fresh name to resolve real conflicts

    # First pass: propose renames (canonical = lexicographic min).
    # Skip self-pairs (la == lb).
    proposed: list[tuple[str, str, str, str]] = []  # (branch, old, new, original_pair_other)
    for la, lb in synonyms:
        if la == lb:
            skipped_self += 1
            continue
        canonical = min(la, lb)
        if canonical == la:
            proposed.append((b_branch, lb, la, la))
        else:
            proposed.append((a_branch, la, lb, lb))

    # Second pass: build rename maps with conflict detection.
    # Track what each branch is renaming AWAY (set of source names) and
    # renaming TO (set of target names).
    a_renaming_away: set[str] = set()
    b_renaming_away: set[str] = set()
    for branch, old, _new, _ in proposed:
        if branch == a_branch:
            a_renaming_away.add(old)
        else:
            b_renaming_away.add(old)

    a_rename_targets_used: set[str] = set()
    b_rename_targets_used: set[str] = set()
    for branch, old, new, _ in proposed:
        rename_map = a_rename if branch == a_branch else b_rename
        all_labels = a_all if branch == a_branch else b_all
        renaming_away = a_renaming_away if branch == a_branch else b_renaming_away
        targets_used = a_rename_targets_used if branch == a_branch else b_rename_targets_used

        # Conflict 1: another rename in this branch targets the same name.
        if new in targets_used:
            skipped_dup_target += 1
            continue

        # Conflict 2: target name exists in this branch AND that label is
        # NOT being renamed away.
        # (If it IS being renamed away by another pair, no conflict — the
        # cumulative regex pass resolves it.)
        if new in all_labels and new not in renaming_away:
            # The canonical name `new` is taken in this branch by an
            # unrelated label. We can rescue this case ONLY if there's
            # a *counterpart* synonym pair that renames that conflicting
            # label away in the OTHER branch (i.e., another pair has
            # canonical=`new` from the other side, telling us where the
            # third party should land).
            other_branch = a_branch if branch == b_branch else b_branch
            other = next((s for b2, _, n, s in proposed
                          if b2 == other_branch and n == new), None)
            if other is None:
                # No counterpart pair exists — this is likely a *false*
                # synonym surfaced by difflib's structural alignment
                # (e.g., a jmp instruction was paired across branches
                # whose target labels are at DIFFERENT byte offsets,
                # but happen to look identical after `<L>` normalization).
                # Skipping is strictly better than fabricating a fresh
                # hybrid name: a fresh name introduces a NEW divergence
                # in the unified output (one branch has the hybrid, the
                # other doesn't), whereas skipping leaves the original
                # divergence which the unifier can already handle.
                skipped_dup_target += 1
                continue
            # Otherwise: rename BOTH branches to a fresh combined name.
            fresh = f"LBL_{min(other, old)[6:]}_{max(other, old)[6:]}"
            if fresh in (a_all | b_all):
                fresh = f"UNIFIED_{fresh}"
            # Add both renames
            other_rename = a_rename if other_branch == a_branch else b_rename
            other_targets = a_rename_targets_used if other_branch == a_branch else b_rename_targets_used
            other_rename[other] = fresh
            other_targets.add(fresh)
            rename_map[old] = fresh
            targets_used.add(fresh)
            fresh_names += 1
            continue

        rename_map[old] = new
        targets_used.add(new)

    print(f"  skipped {skipped_self} pairs where labels are already identical")
    print(f"  skipped {skipped_dup_target} pairs due to duplicate-target conflict")
    print(f"  used {fresh_names} fresh names for cascading conflicts")
    print(f"  effective renames:  {a_branch}: {len(a_rename)},  "
          f"{b_branch}: {len(b_rename)}")

    # Apply
    a_out = apply_rename(a_text, a_rename)
    b_out = apply_rename(b_text, b_rename)
    outputs[a_branch].parent.mkdir(parents=True, exist_ok=True)
    outputs[a_branch].write_text(a_out)
    outputs[b_branch].write_text(b_out)
    print(f"\nwrote {outputs[a_branch]}")
    print(f"wrote {outputs[b_branch]}")


if __name__ == "__main__":
    main()
