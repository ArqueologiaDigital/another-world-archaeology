#!/usr/bin/env python3
"""One-shot migration: introduce HERO_X / HERO_Y aliases for vars
0x01 / 0x02 in the four playable-walking stages (LAKE, PRISON, CAVES,
CAPSULE).

Background: AWVM_Tools commit (2026-05-05) makes the disassembler
emit `HERO_X` / `HERO_Y` for vars 0x01 / 0x02 when looking at a
walking-gameplay stage (per the new `stage_specific_vars` table on
`ReleaseData`). Existing source files in
`another-world-source-reconstruction` were generated before this
change and still carry `[0x01]` / `[0x02]` literals.

This script does the equivalent edit without re-disassembling
(which would clobber hand-curated semantic labels). For each
LAKE / PRISON / CAVES / CAPSULE source file:

  1. Insert `HERO_X EQU 0x01` and `HERO_Y EQU 0x02` immediately after
     the SPECIAL_PURPOSE_VARS EQU block (right after PAUSE_SLICES if
     present, otherwise after the first EQU). Per-port `.asm` files
     and the unified `.asm.in` get this; chunk `.inc` files inherit
     the EQUs from the parent and don't need their own declaration.
  2. Replace every `[0x01]` → `[HERO_X]` and `[0x02]` → `[HERO_Y]`.

Idempotent: running twice is a no-op.

Affected files:
  - src/levels/{chahi_amiga_1991,dos_1992,cartridge_1992,gba_2004}/
    {LAKE,PRISON,CAVES,CAPSULE}.asm                          16 files
  - src/levels/_unified/{LAKE,PRISON,CAVES,CAPSULE}.asm.in    4 files
  - src/levels/_unified/{lake,prison,caves,capsule}/*.inc    many

Other stages (INTRO, ENDING, TANK, CODE_WHEEL, PASSCODE) are NOT
touched: vars 0x01 / 0x02 are used for unrelated purposes there
(loop counters, codewheel-rotation indices, scratch coordinates).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

WALKING_STAGES = ("LAKE", "PRISON", "CAVES", "CAPSULE")
WALKING_STAGES_LOWER = tuple(s.lower() for s in WALKING_STAGES)

# Captures `[0x01]` and `[0x02]`. Word boundaries ensure we don't
# accidentally match `[0x010]` or similar.
VAR01 = re.compile(r"\[0x01\]")
VAR02 = re.compile(r"\[0x02\]")

EQU_BLOCK = "HERO_X\t\tEQU 0x01\nHERO_Y\t\tEQU 0x02\n"
EQU_LINE_HERO_X = re.compile(r"^HERO_X\s+EQU\s+0x01\s*$", re.MULTILINE)


def insert_equ_block(text: str) -> str:
    """Insert the HERO_X / HERO_Y EQU declarations at a location
    that's visible to all branches.

    Per-port `.asm` files declare SPECIAL_PURPOSE_VARS inline at
    the top, so the canonical anchor is the line after PAUSE_SLICES.
    Unified `.asm.in` files instead pull SPECIAL_PURPOSE_VARS via
    `;@include "../_common_vars.inc"`, so we anchor to that include.
    A naive "first EQU" fallback is dangerous: in LAKE.asm.in the
    first EQU line lives inside a `;@if BRANCH in (...)` block that
    excludes amiga, which would silently mis-place the alias and
    break round-trip (regression caught 2026-05-05; verify_unified
    drops one stage)."""
    if EQU_LINE_HERO_X.search(text):
        return text  # already migrated
    # Anchor 1 (per-port .asm): after PAUSE_SLICES.
    pause = re.search(r"^PAUSE_SLICES\s+EQU\s+0x[0-9A-Fa-f]+\s*$", text, re.MULTILINE)
    if pause:
        end = pause.end()
        if text[end : end + 1] != "\n":
            return text[:end] + "\n" + EQU_BLOCK + text[end:]
        return text[: end + 1] + EQU_BLOCK + text[end + 1 :]
    # Anchor 2 (unified .asm.in): before `;@include "../_common_vars.inc"`.
    common_inc = re.search(
        r'^;@include\s+"\.\./_common_vars\.inc"\s*$',
        text,
        re.MULTILINE,
    )
    if common_inc:
        start = common_inc.start()
        return text[:start] + EQU_BLOCK + "\n" + text[start:]
    # No anchor found — prepend at top (safe but rare).
    return EQU_BLOCK + text


def replace_vars(text: str) -> tuple[str, int, int]:
    new_text, n01 = VAR01.subn("[HERO_X]", text)
    new_text, n02 = VAR02.subn("[HERO_Y]", new_text)
    return new_text, n01, n02


def is_walking_stage_per_port(path: Path) -> bool:
    """e.g. src/levels/dos_1992/LAKE.asm"""
    return path.suffix == ".asm" and path.stem in WALKING_STAGES


def is_walking_stage_unified_asm_in(path: Path) -> bool:
    """e.g. src/levels/_unified/LAKE.asm.in"""
    return (
        path.name.endswith(".asm.in")
        and path.stem.removesuffix(".asm") in WALKING_STAGES
    )


def is_walking_stage_chunk(path: Path) -> bool:
    """e.g. src/levels/_unified/lake/<anything>.inc"""
    if path.suffix != ".inc":
        return False
    parts = path.parts
    if "_unified" not in parts:
        return False
    idx = parts.index("_unified")
    if idx + 1 >= len(parts):
        return False
    return parts[idx + 1] in WALKING_STAGES_LOWER


def migrate(src_tree: Path) -> dict:
    stats = {"files_with_equ_added": 0, "files_renamed": 0, "var01": 0, "var02": 0}
    for path in src_tree.rglob("*"):
        if not path.is_file():
            continue
        kind = None
        if is_walking_stage_per_port(path):
            kind = "per_port_asm"
        elif is_walking_stage_unified_asm_in(path):
            kind = "unified_asm_in"
        elif is_walking_stage_chunk(path):
            kind = "chunk_inc"
        if kind is None:
            continue
        text = path.read_text(encoding="utf-8")
        new_text = text
        if kind in ("per_port_asm", "unified_asm_in"):
            new_text = insert_equ_block(new_text)
        new_text, n01, n02 = replace_vars(new_text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            if "HERO_X\t\tEQU 0x01" in new_text and "HERO_X\t\tEQU 0x01" not in text:
                stats["files_with_equ_added"] += 1
            if n01 or n02:
                stats["files_renamed"] += 1
            stats["var01"] += n01
            stats["var02"] += n02
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-tree", required=True, type=Path)
    args = ap.parse_args()
    stats = migrate(args.src_tree)
    print(
        f"HERO_X/Y EQU added in {stats['files_with_equ_added']} files; "
        f"{stats['var01']} [0x01] → [HERO_X] and "
        f"{stats['var02']} [0x02] → [HERO_Y] across "
        f"{stats['files_renamed']} files"
    )


if __name__ == "__main__":
    main()
