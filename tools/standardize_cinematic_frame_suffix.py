#!/usr/bin/env python3
"""Standardize CINEMATIC frame-index suffixes to bare `_N`.

Two legacy conventions exist in src/levels/:

  - `CINEMATIC_FOO_FN`         (e.g. CINEMATIC_BEAST_WANDER_F0)
  - `CINEMATIC_FOO_FRAME_N`    (e.g. CINEMATIC_BEETLE_LIFT_FRAME_0)

Owner preference (2026-05-04): collapse both to the bare-numeric
form (e.g. `CINEMATIC_BEAST_WANDER_0`) — same numeric suffix that
the largest set of names already uses.

Collision detection: if the bare-numeric target already exists
elsewhere in the source tree, the rename is skipped and reported.
The current known collision set is the
`CINEMATIC_SNEAKY_TENTACLE_F0..F9` group in cartridge / gba LAKE,
where `CINEMATIC_SNEAKY_TENTACLE_0..5` already exists at a
different offset.

Usage:
  python3 tools/standardize_cinematic_frame_suffix.py \
    [--src-tree /path/to/src/levels] [--dry-run] [--verify]

Default src-tree:
  ../another-world-source-reconstruction/src/levels
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from _paths import AW_SRC, REPO_ROOT

DEFAULT_SRC = AW_SRC / "src/levels"

RE_FN = re.compile(r"\bCINEMATIC_([A-Z_]+)_F(\d+)\b")
RE_FRAME = re.compile(r"\bCINEMATIC_([A-Z_]+)_FRAME_(\d+)\b")
RE_ANY_CINEMATIC = re.compile(r"\bCINEMATIC_[A-Z_0-9]+\b")


def collect_all_names(src: Path) -> set[str]:
    """Walk every file and collect every unique CINEMATIC_* identifier."""
    names: set[str] = set()
    for path in src.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in (".asm", ".inc", ".in"):
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        names.update(RE_ANY_CINEMATIC.findall(text))
    return names


def build_rename_map(names: set[str]) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """Return (renames, skipped) where:
      renames[old] = new   for each non-colliding _Fn / _FRAME_n
      skipped = [(old, target)] for each colliding case

    Three collision categories detected:
      1. target already exists as a separate name in `names` (e.g.
         `_F0` → `_0` but `_0` already exists at a different offset).
      2. two source names map to the SAME target (e.g. `_F0` and
         `_FRAME_0` both rename to `_0`); both are skipped.
      3. (transitively) any name participating in a cluster where
         either of the above applies.
    """
    # Phase 1: enumerate all candidate renames, keeping a reverse map
    # target → list of sources.
    candidates: list[tuple[str, str]] = []  # (source, target)
    for name in names:
        m = re.fullmatch(r"CINEMATIC_([A-Z_]+)_F(\d+)", name)
        if m:
            target = f"CINEMATIC_{m.group(1)}_{m.group(2)}"
            candidates.append((name, target))
            continue
        m = re.fullmatch(r"CINEMATIC_([A-Z_]+)_FRAME_(\d+)", name)
        if m:
            target = f"CINEMATIC_{m.group(1)}_{m.group(2)}"
            candidates.append((name, target))

    # Reverse map: target -> sources
    reverse: dict[str, list[str]] = defaultdict(list)
    for src, tgt in candidates:
        reverse[tgt].append(src)

    renames: dict[str, str] = {}
    skipped: list[tuple[str, str]] = []
    for tgt, srcs in reverse.items():
        # Collision class 1: target already exists as a distinct name.
        if tgt in names:
            for s in srcs:
                skipped.append((s, tgt))
            continue
        # Collision class 2: multiple sources map to same target.
        if len(srcs) > 1:
            for s in srcs:
                skipped.append((s, tgt))
            continue
        # Safe rename.
        renames[srcs[0]] = tgt
    return renames, skipped


def apply_renames(src: Path, renames: dict[str, str], dry_run: bool) -> dict[str, int]:
    """Apply the rename map to every text file under src.
    Returns a per-file count of substitutions made."""
    file_changes: dict[str, int] = {}
    if not renames:
        return file_changes
    # Build a single regex that matches any old name as a whole word.
    # Sort by length desc so longer names match before their prefixes.
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(k) for k in sorted(renames, key=len, reverse=True)) + r")\b"
    )
    for path in src.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in (".asm", ".inc", ".in"):
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        new_text, n = pattern.subn(lambda m: renames[m.group(0)], text)
        if n:
            file_changes[str(path)] = n
            if not dry_run:
                path.write_text(new_text)
    return file_changes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--src-tree", type=Path, default=DEFAULT_SRC)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--verify",
        action="store_true",
        help="run verify_stage.py + verify_unified.py after rename",
    )
    args = ap.parse_args()

    if not args.src_tree.is_dir():
        sys.exit(f"src-tree not found: {args.src_tree}")

    names = collect_all_names(args.src_tree)
    print(f"collected {len(names)} unique CINEMATIC_* identifiers")
    renames, skipped = build_rename_map(names)
    print(f"renames planned: {len(renames)}")
    print(f"skipped (collision): {len(skipped)}")
    for old, target in skipped:
        print(f"  skip: {old} → {target} (target already exists)")
    if args.dry_run:
        print("\n--dry-run; not applying changes")
        sample = list(renames.items())[:10]
        for old, new in sample:
            print(f"  {old} → {new}")
        return 0

    file_changes = apply_renames(args.src_tree, renames, dry_run=False)
    total = sum(file_changes.values())
    print(f"\napplied {total} substitutions across {len(file_changes)} files")
    for fp, n in sorted(file_changes.items(), key=lambda kv: -kv[1])[:10]:
        print(f"  {n:5d}  {fp}")

    if args.verify:
        print("\nrunning verify_stage.py + verify_unified.py")
        for tool in ("verify_stage.py", "verify_unified.py"):
            r = subprocess.run(
                [
                    "python3",
                    str(REPO_ROOT / "tools" / tool),
                    "--src-tree",
                    str(args.src_tree),
                ],
                capture_output=True,
                text=True,
            )
            tail = "\n".join(r.stdout.strip().splitlines()[-1:])
            print(f"  {tool}: {tail}")
            if r.returncode != 0:
                return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
