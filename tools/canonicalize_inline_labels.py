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


def find_label_synonyms(a_lines: list[str], b_lines: list[str]) -> list[tuple[str, str]]:
    """Return list of (label_a, label_b) synonym pairs found via diff alignment."""
    sm = difflib.SequenceMatcher(None, a_lines, b_lines, autojunk=False)
    synonyms: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'replace':
            continue
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
        # Simple case: 1:1 pairing
        if len(a_labels) == 1 and len(b_labels) == 1:
            synonyms.append((a_labels[0][1], b_labels[0][1]))
            continue
        # N:N pairing where both blocks have the same number of labels:
        # pair them in order. This works when the diff block has
        # parallel structure.
        if len(a_labels) == len(b_labels) and len(a_labels) > 1:
            # Pair label_i with label_i
            for (_, a_name), (_, b_name) in zip(a_labels, b_labels):
                synonyms.append((a_name, b_name))
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

    # Find synonym pairs
    synonyms = find_label_synonyms(a_lines, b_lines)
    print(f"found {len(synonyms)} candidate synonym pairs")

    # Collect all labels per branch (for conflict detection)
    a_all = collect_all_labels(a_text)
    b_all = collect_all_labels(b_text)

    # Build rename maps. Strategy: pick alphabetically smaller as canonical.
    # Detect conflicts: if canonical name already exists in target branch
    # (for a different label), skip this synonym pair.
    a_rename: dict[str, str] = {}
    b_rename: dict[str, str] = {}
    skipped_self = 0
    skipped_conflict = 0
    skipped_dup = 0
    for la, lb in synonyms:
        if la == lb:
            skipped_self += 1
            continue
        canonical = min(la, lb)
        non_canonical = max(la, lb)
        # Decide which branch needs the rename (the one with the non-canonical name).
        if canonical == la:
            # b has the non-canonical; we need b: lb → la
            # Conflict: la already exists in b (at a different label)
            if la in b_all:
                skipped_conflict += 1
                continue
            if lb in b_rename:
                skipped_dup += 1
                continue
            b_rename[lb] = la
        else:
            # a has the non-canonical; we need a: la → lb
            if lb in a_all:
                skipped_conflict += 1
                continue
            if la in a_rename:
                skipped_dup += 1
                continue
            a_rename[la] = lb

    print(f"  skipped {skipped_self} pairs where labels are already identical")
    print(f"  skipped {skipped_conflict} pairs due to conflict (canonical name "
          f"already used in target branch for a different offset)")
    print(f"  skipped {skipped_dup} duplicate-source-label rename attempts")
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
