#!/usr/bin/env python3
"""Consolidate arm-prefixed chunk files that have byte-identical content.

When the unified-source pipeline forks a chunk per arm
(`amiga__post_X.inc` / `cart__post_X.inc` / `dos__post_X.inc`)
but a later rename / fold pass equalises their content, the three
files end up byte-identical. The parent's `;@if BRANCH == "..."`
include block then has 3 arms all selecting an identical file —
pure noise.

This tool finds those identical-arm cases and consolidates them:

  1. Renames the first arm's file to drop the arm prefix
     (`amiga__post_X.inc` → `post_X.inc`).
  2. Deletes the other arm files (cart__, dos__, etc.).
  3. Updates the parent chunk's `;@if BRANCH ==` include block
     to a single bare `;@include "post_X.inc"`.

Safe by construction:
  - Only touches files where the per-arm content is byte-identical.
  - Only touches parents whose `;@if BRANCH ==` block matches the
    expected pattern (3 arms selecting the matching files in
    order). Anything more elaborate is skipped and reported.

Usage:
    python3 tools/consolidate_identical_arm_chunks.py <src-tree-root>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


ARM_PREFIXES = ("amiga", "cart", "dos", "gba", "snes")


def find_identical_arm_groups(unified: Path) -> list[tuple[Path, dict[str, Path]]]:
    """Yield (stage_dir, {arm: path}) groups where every arm's
    file content is byte-identical."""
    groups = []
    for stage_dir in unified.iterdir():
        if not stage_dir.is_dir() or stage_dir.name.startswith("_"):
            continue
        per_suffix: dict[str, dict[str, Path]] = {}
        for f in stage_dir.glob("*__*.inc"):
            arm, sep, rest = f.name.partition("__")
            if arm not in ARM_PREFIXES:
                continue
            suffix = rest.rsplit(".", 1)[0]
            per_suffix.setdefault(suffix, {})[arm] = f
        for suffix, arms_map in per_suffix.items():
            if len(arms_map) < 2:
                continue
            try:
                contents = {arm: f.read_bytes() for arm, f in arms_map.items()}
            except OSError:
                continue
            if len(set(contents.values())) == 1:
                groups.append((stage_dir, suffix, arms_map))
    return groups


def find_parent_with_if_block(unified: Path, suffix: str, arms: list[str]) -> tuple[Path, int, int] | None:
    """Find a parent chunk whose @if block selects exactly the
    arm-prefixed files we want to consolidate. Returns
    (path, start_line, end_line_exclusive) if found, else None."""
    for stage_dir in unified.iterdir():
        if not stage_dir.is_dir() or stage_dir.name.startswith("_"):
            continue
        for f in stage_dir.glob("*.inc"):
            if "__" in f.name:
                continue  # only check non-arm-prefixed files
            text = f.read_text()
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if not re.match(r'^\s*;@if\s+BRANCH', line):
                    continue
                # Walk this @if and see if it selects {amiga,cart,dos}__post_<suffix>.inc
                arm_includes_seen = []
                j = i + 1
                depth = 1
                while j < len(lines) and depth > 0:
                    sub = lines[j]
                    if re.match(r'^\s*;@if\b', sub):
                        depth += 1
                    elif re.match(r'^\s*;@endif\b', sub):
                        depth -= 1
                        if depth == 0:
                            break
                    elif depth == 1:
                        m = re.match(r'^\s*;@include\s+"([^"]+)"', sub)
                        if m:
                            arm_includes_seen.append(m.group(1))
                    j += 1
                # The @if block we want has exactly N arm-prefixed
                # includes pointing to the suffix.
                expected = {f"{arm}__{suffix}.inc" for arm in arms}
                if set(arm_includes_seen) == expected:
                    return (f, i, j + 1)  # j is the @endif line
    return None


BRANCH_FOR_ARM = {
    "amiga": "chahi_amiga_1991",
    "cart": "cartridge_1992",
    "dos": "dos_1992",
    "gba": "gba_2004",
    "snes": "snes_eu",
}


def consolidate(unified: Path, stage_dir: Path, suffix: str, arms_map: dict[str, Path]) -> bool:
    arms = sorted(arms_map.keys())
    parent_info = find_parent_with_if_block(unified, suffix, arms)
    if parent_info is None:
        return False
    parent_path, start, end = parent_info
    # New shared filename: drop the arm prefix.
    new_path = stage_dir / f"{suffix}.inc"
    if new_path.exists():
        return False  # collision; skip
    # Pick first arm's file, rename to shared.
    first_arm = arms[0]
    arms_map[first_arm].rename(new_path)
    # Delete remaining arm files.
    for arm in arms[1:]:
        arms_map[arm].unlink()
    # Update parent: replace @if/@endif block with a guarded include
    # if the original block didn't cover ALL branches, else with a
    # bare include if it did.
    text = parent_path.read_text()
    lines = text.splitlines()
    indent = re.match(r'^(\s*)', lines[start]).group(1)
    branches = [BRANCH_FOR_ARM[a] for a in arms]
    if len(branches) >= 3:
        # All-arm case: the bare include is fine (the chunk should
        # ship for every branch).
        new_block = [f'{indent};@include "{suffix}.inc"']
    else:
        # 2-arm case: keep a `;@if BRANCH in (...)` guard so branches
        # outside `arms` do NOT pick up the chunk.
        branch_list = ", ".join(f'"{b}"' for b in branches)
        new_block = [
            f"{indent};@if BRANCH in ({branch_list})",
            f'{indent};@include "{suffix}.inc"',
            f"{indent};@endif",
        ]
    new_lines = lines[:start] + new_block + lines[end:]
    new_text = "\n".join(new_lines)
    if text.endswith("\n"):
        new_text += "\n"
    parent_path.write_text(new_text)
    return True


def main(roots: list[str]) -> int:
    if not roots:
        print("usage: consolidate_identical_arm_chunks.py <src-tree-root>", file=sys.stderr)
        return 2
    src_root = Path(roots[0])
    unified = src_root / "src" / "levels" / "_unified"
    if not unified.is_dir():
        print(f"not a source-recon root: {src_root}", file=sys.stderr)
        return 2

    groups = find_identical_arm_groups(unified)
    print(f"Identical-arm chunk groups found: {len(groups)}")

    consolidated = 0
    skipped = []
    for stage_dir, suffix, arms_map in groups:
        ok = consolidate(unified, stage_dir, suffix, arms_map)
        if ok:
            consolidated += 1
        else:
            skipped.append(f"{stage_dir.name}/{suffix} ({len(arms_map)} arms)")
    print(f"Consolidated: {consolidated}")
    if skipped:
        print(f"Skipped (no matching parent @if block, or shared name collision): {len(skipped)}")
        for s in skipped[:10]:
            print(f"  {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
