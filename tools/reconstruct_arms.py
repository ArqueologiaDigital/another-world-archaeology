#!/usr/bin/env python3
"""Reconstruct un-split per-arm `.inc` files from a folded `<STAGE>.asm.in`
plus its current chunk files.

This is the inverse of `multi_fold.py`. Useful when you want to re-fold a
stage with a different routine list (or with a new chunk-naming
convention): run this first to regenerate `<arm>.inc`, delete the
chunk files, then re-run `multi_fold.py`.

The reconstruction walks the unified file's `;@include` directives and
the routine bodies in order, emitting them into per-arm reconstructions
based on each `;@if BRANCH ==` block they're under.

Usage:
    python3 tools/reconstruct_arms.py <STAGE>
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from _paths import AW_SRC

if len(sys.argv) != 2:
    sys.exit(__doc__)

STAGE = sys.argv[1].upper()

AW_SRC = Path(os.environ.get(
    "AW_SRC",
    str(AW_SRC)
))
STAGE_DIR = AW_SRC / "src/levels/_unified" / STAGE.lower()
UNIFIED = AW_SRC / "src/levels/_unified" / f"{STAGE}.asm.in"

if not UNIFIED.is_file():
    sys.exit(f"FATAL: no {UNIFIED}")

BR_TO_ARM = {
    "chahi_amiga_1991": "amiga",
    "cartridge_1992": "cart",
    "dos_1992": "dos",
}
ARMS = list(BR_TO_ARM.values())

# Walk the unified file. Track current `;@if BRANCH ==`/`;@if BRANCH in (...)`
# state. For each ;@include directive, emit the included file's content
# into the active arms' reconstruction. For each routine body (lines
# between the directives), emit it into the active arms' reconstruction.

text = UNIFIED.read_text()
lines = text.splitlines()

# State machine for processing the unified file
# Stack: list of "active arm sets" — only emit content if it's for the
# current branch. We track per-arm whether the current line should be
# included in that arm's reconstruction.

# Simpler model: walk linearly. When we hit `;@if BRANCH == "X"`, the
# active arm becomes [X]. `;@elif BRANCH == "Y"` → active becomes [Y].
# `;@if BRANCH in ("X", "Y")` → active becomes [X, Y]. `;@endif` resets.
# Outside any if-block, active = all arms.

reconstructions = {arm: [] for arm in ARMS}


def parse_branch_expr(rest):
    """Parse `BRANCH == "X"` or `BRANCH in ("X", "Y", ...)` → list of arms."""
    m = re.match(r'^\s*BRANCH\s*==\s*"([^"]+)"', rest)
    if m:
        br = m.group(1)
        return [BR_TO_ARM[br]] if br in BR_TO_ARM else []
    m = re.match(r'^\s*BRANCH\s+in\s+\(([^)]+)\)', rest)
    if m:
        result = []
        for part in m.group(1).split(','):
            part = part.strip().strip('"').strip("'")
            if part in BR_TO_ARM:
                result.append(BR_TO_ARM[part])
        return result
    sys.exit(f"FATAL: unparsable branch expr: {rest!r}")


# Active arm context. Outside any if, all arms are active.
active_arms = list(ARMS)
in_if = False  # tracks whether we're inside an ;@if block

for ln in lines:
    s = ln.strip()
    m = re.match(r'^;@if\s+(.*)$', s)
    if m:
        active_arms = parse_branch_expr(m.group(1))
        in_if = True
        continue
    m = re.match(r'^;@elif\s+(.*)$', s)
    if m:
        active_arms = parse_branch_expr(m.group(1))
        continue
    if s == ";@else":
        active_arms = [a for a in ARMS if a not in active_arms]
        continue
    if s == ";@endif":
        active_arms = list(ARMS)
        in_if = False
        continue
    m = re.match(r'^;@include\s+"([^"]+)"', s)
    if m:
        rel = m.group(1)
        target = (UNIFIED.parent / rel).resolve()
        if not target.is_file():
            sys.exit(f"FATAL: include not found: {target}")
        included = target.read_text()
        for arm in active_arms:
            reconstructions[arm].append(included.rstrip())
        continue
    # Plain content line — emit to active arms
    for arm in active_arms:
        reconstructions[arm].append(ln)

# Write each arm's reconstruction
for arm in ARMS:
    body_lines = reconstructions[arm]
    if not body_lines:
        continue
    out = STAGE_DIR / f"{arm}.inc"
    content = "\n".join(body_lines).rstrip() + "\n"
    out.write_text(content)
    print(f"wrote {out.relative_to(AW_SRC)} ({content.count(chr(10))} lines)")
