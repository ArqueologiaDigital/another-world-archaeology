#!/usr/bin/env python3
"""Canonicalize synonym labels across N branches' .asm files.

When two branches' EQU tables map different label NAMES to the same
OFFSET, those names are synonyms. Pick the more descriptive one as
canonical and rewrite the less-descriptive name throughout the
sources, eliminating cosmetic differences before running
`tools/unify_asm.py`.

Heuristic for "more descriptive":
- Count underscore-separated *alphabetic* components (skip pure-digit
  and pure-hex components).
- More alpha components = more descriptive.
- Tie-break: longer total length.

Example:
  CINEMATIC_054                    → 1 alpha (CINEMATIC) + 1 digit
  CINEMATIC_WALKING_FEET_ARRIVING_0 → 4 alpha + 1 digit
  → canonical: the second one.

Per-branch usage:
    python3 tools/canonicalize_labels.py \\
        --in heineman_cartridge=path/to/cartridge.asm \\
        --in foxy_gba_2004=path/to/gba.asm \\
        --out heineman_cartridge=path/to/cartridge.canonical.asm \\
        --out foxy_gba_2004=path/to/gba.canonical.asm
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RE_EQU = re.compile(r'^([A-Z][A-Z_0-9]*)\s+EQU\s+(0x[0-9A-Fa-f]+)\s*$')
RE_TOKEN = re.compile(r'\b([A-Z][A-Z_0-9]*)\b')


def parse_equs(path: Path) -> dict[str, int]:
    """Parse EQU table from an .asm file. Returns {name: offset}."""
    out = {}
    for line in path.read_text().splitlines():
        m = RE_EQU.match(line)
        if m:
            out[m.group(1)] = int(m.group(2), 16)
    return out


def descriptiveness(name: str) -> tuple[int, int]:
    """Score a label name. Higher = more descriptive.

    Returns (alpha_components, total_length). Compare lexicographically.
    """
    parts = name.split('_')
    alpha_components = 0
    for p in parts:
        # Skip pure digit
        if p.isdigit():
            continue
        # Skip pure hex (looks like an address)
        if all(c in '0123456789ABCDEFabcdef' for c in p):
            continue
        # Anything else with alphabetic content
        if any(c.isalpha() for c in p):
            alpha_components += 1
    return (alpha_components, len(name))


def pick_canonical(names: list[str]) -> str:
    """Pick the most descriptive name from a list."""
    return max(names, key=descriptiveness)


def build_rename_map(equs_per_branch: dict[str, dict[str, int]]) -> dict[str, dict[str, str]]:
    """For each branch, return {old_name: canonical_name} based on
    cross-branch synonym discovery.

    Algorithm:
    1. Build a global offset → set-of-names map (union across branches).
    2. For each offset, pick the most-descriptive name.
    3. For each branch's EQU table: if this branch uses a non-canonical
       name for that offset, rename to canonical.
    """
    # All names per offset, across all branches.
    offset_to_names: dict[int, set[str]] = {}
    for branch, equs in equs_per_branch.items():
        for name, off in equs.items():
            offset_to_names.setdefault(off, set()).add(name)

    # Canonical name per offset.
    offset_to_canonical: dict[int, str] = {
        off: pick_canonical(list(names))
        for off, names in offset_to_names.items()
    }

    # Per-branch rename map.
    rename: dict[str, dict[str, str]] = {}
    for branch, equs in equs_per_branch.items():
        m = {}
        for name, off in equs.items():
            canonical = offset_to_canonical[off]
            if name != canonical:
                m[name] = canonical
        rename[branch] = m
    return rename


def apply_rename(text: str, rename_map: dict[str, str]) -> str:
    """Rewrite text, replacing every label name in `rename_map` with
    its canonical version. Whole-token replacement only."""
    if not rename_map:
        return text
    # Build one regex with alternation for efficiency.
    pattern = re.compile(
        r'\b(' + '|'.join(re.escape(k) for k in rename_map) + r')\b'
    )
    return pattern.sub(lambda m: rename_map[m.group(1)], text)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--in", dest="inputs", action="append", default=[],
                   metavar="BRANCH=PATH",
                   help="input source spec (BRANCH=path); repeat for each input")
    p.add_argument("--out", dest="outputs", action="append", default=[],
                   metavar="BRANCH=PATH",
                   help="output path per branch (must match --in branches)")
    args = p.parse_args()

    if len(args.inputs) < 2:
        sys.exit("specify at least 2 inputs via --in BRANCH=path")
    if len(args.outputs) != len(args.inputs):
        sys.exit("--out count must match --in count")

    # Parse inputs
    inputs: dict[str, Path] = {}
    for spec in args.inputs:
        br, _, path_str = spec.partition("=")
        inputs[br] = Path(path_str)
    outputs: dict[str, Path] = {}
    for spec in args.outputs:
        br, _, path_str = spec.partition("=")
        outputs[br] = Path(path_str)
    if set(inputs) != set(outputs):
        sys.exit(f"--in branches {set(inputs)} != --out branches {set(outputs)}")

    # Parse EQU tables
    equs_per_branch: dict[str, dict[str, int]] = {}
    for br, path in inputs.items():
        equs_per_branch[br] = parse_equs(path)
        print(f"  {br}: {len(equs_per_branch[br])} EQU entries")

    # Build rename maps
    rename = build_rename_map(equs_per_branch)
    print(f"\nrename counts:")
    for br, m in rename.items():
        print(f"  {br}: {len(m)} synonym renames")

    # Build the union of EQU tables (post-rename). After renames, each
    # branch uses canonical names; collect every (canonical_name, offset)
    # pair seen in any branch.
    union_equs: dict[str, int] = {}
    for br, equs in equs_per_branch.items():
        rmap = rename[br]
        for name, off in equs.items():
            canon = rmap.get(name, name)
            # Sanity: if the same canonical name maps to different
            # offsets in different branches, something's wrong.
            if canon in union_equs and union_equs[canon] != off:
                sys.exit(
                    f"EQU union conflict: {canon} = "
                    f"0x{union_equs[canon]:04X} vs 0x{off:04X}"
                )
            union_equs[canon] = off

    # Apply renames + augment EQU tables with the union (per-branch
    # additions). Augmentation matters because some `CINEMATIC_xxx`
    # labels exist in only one branch's disasm — usually because the
    # OTHER branch's disasm couldn't reach the bytecode region that
    # references them, even though the bytes ARE there. Adding the
    # missing EQUs lets `tools/redisasm_db.py` emit symbolic
    # `video offset=CINEMATIC_xxx` lines that match across branches.
    for br, in_path in inputs.items():
        text = in_path.read_text()
        out_text = apply_rename(text, rename[br])
        # Find this branch's existing EQU names (post-rename).
        existing_names = set()
        for line in out_text.splitlines():
            m = RE_EQU.match(line)
            if m:
                existing_names.add(m.group(1))
        # Compute which union EQUs this branch is missing.
        missing = sorted(
            (name, off) for name, off in union_equs.items()
            if name not in existing_names
        )
        # Sort the EQU section deterministically across branches so
        # that augmented and original EQUs interleave in the SAME
        # order in every branch. Without this, augmenting at the end
        # of gba's EQU section puts CINEMATIC_660-669 in a different
        # logical position than cart (where they appear MID-section
        # because they were registered earlier in cart's disassembly
        # walk). The position mismatch causes difflib to emit TWO
        # `;@if` blocks for the same set of EQUs.
        #
        # Strategy: collect every EQU line (whether original or
        # augmented), sort by NAME, and re-emit them as a contiguous
        # block at the position of the FIRST EQU in the original
        # file. The non-EQU lines between EQUs (e.g., blank-line
        # separators inserted by the disasm) are preserved by being
        # left in place; only the EQU lines themselves get
        # repositioned + sorted.
        lines = out_text.splitlines()
        all_equs: list[tuple[str, int]] = []
        equ_indices: list[int] = []
        for i, line in enumerate(lines):
            m = RE_EQU.match(line)
            if m:
                all_equs.append((m.group(1), int(m.group(2), 16)))
                equ_indices.append(i)
        for name, off in missing:
            all_equs.append((name, off))
        if equ_indices:
            # Drop existing EQU lines + augmentation insertion point
            # (we'll re-emit a sorted block).
            non_equ_lines = [
                l for i, l in enumerate(lines) if i not in set(equ_indices)
            ]
            # Sort by name (alpha), tie-break by offset.
            all_equs.sort(key=lambda kv: (kv[0], kv[1]))
            sorted_equ_lines = [
                f"{name}\t\tEQU 0x{off:04X}"
                for name, off in all_equs
            ]
            # Splice back in: insert sorted block at original
            # first-EQU position (relative to non_equ_lines).
            first_equ_pos = equ_indices[0]
            # Position in non_equ_lines: equal to the number of non-EQU
            # lines that came before the first EQU (in the original).
            insert_at = sum(1 for i in range(first_equ_pos) if i not in set(equ_indices))
            lines = (
                non_equ_lines[:insert_at]
                + sorted_equ_lines
                + non_equ_lines[insert_at:]
            )
            out_text = "\n".join(lines)
            if not out_text.endswith("\n"):
                out_text += "\n"
        out_path = outputs[br]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_text)
        print(f"  wrote {out_path}  ({len(missing)} EQUs added from union)")


if __name__ == "__main__":
    main()
