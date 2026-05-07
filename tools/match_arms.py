#!/usr/bin/env python3
"""Match named routines from one arm to numeric labels in another arm
by ABSTRACTED symbolic body.

For each line, replace operands that look like labels (LABEL_<HEX>
or named routines) with a placeholder. Two routines with the same
abstracted instruction sequence — but different label targets — match.

Usage:
    python3 tools/match_arms.py STAGE TO_ARM           (FROM defaults to cart)
    python3 tools/match_arms.py STAGE FROM_ARM TO_ARM  (explicit FROM)

Output: 'old_label=new_name' lines (sed-friendly).
"""
import os, re, sys
from pathlib import Path

from _paths import AW_SRC

if len(sys.argv) not in (3, 4):
    sys.exit(__doc__)

STAGE = sys.argv[1].lower()
if len(sys.argv) == 3:
    FROM_ARM, TO_ARM = "cart", sys.argv[2]
else:
    FROM_ARM, TO_ARM = sys.argv[2], sys.argv[3]

CART = AW_SRC / f"src/levels/_unified/{STAGE}/{FROM_ARM}.inc"
ARM = AW_SRC / f"src/levels/_unified/{STAGE}/{TO_ARM}.inc"
if not CART.is_file():
    sys.exit(f"FROM-arm not found: {CART}")
if not ARM.is_file():
    sys.exit(f"TO-arm not found: {ARM}")


def parse_routines(path):
    text = Path(path).read_text()
    lines = text.splitlines()
    cur_label, cur_body = None, []
    for ln in lines:
        m = re.match(r'^([A-Za-z_][A-Za-z_0-9]*):$', ln)
        if m:
            if cur_label is not None:
                yield cur_label, cur_body
            cur_label = m.group(1)
            cur_body = []
        elif cur_label is not None:
            cur_body.append(ln)
    if cur_label is not None:
        yield cur_label, cur_body


_PRESERVE_PREFIXES = (
    "CINEMATIC_", "COMMON_VIDEO_", "POLY_", "PAL_", "MUS_", "SFX_",
    "BANK_", "TEXT_", "PAUSE_", "LAST_", "HERO_", "RANDOM_",
    "SCROLL_", "HACK_VAR_",
)
_PRESERVE_EXACT = {
    "PAUSE_SLICES", "LAST_KEYCHAR", "HERO_ACTION",
    "HERO_POS_LEFT_RIGHT", "HERO_POS_UP_DOWN", "HERO_POS_JUMP_DOWN",
    "HERO_POS_MASK", "HERO_ACTION_POS_MASK",
    "RANDOM_SEED", "MUS_MARK", "SCROLL_Y",
}


def abstracted_body(body):
    """Strip ;@raw= and abstract label-like identifiers in operands.

    Only LABEL_<HEX> / JUNK__<HEX> identifiers are abstracted (the
    per-arm numeric labels that legitimately differ across arms).
    Named operands such as CINEMATIC_086 / COMMON_VIDEO_128 are
    preserved verbatim — they encode different bytes in `;@raw=` and
    must not be conflated.

    Already-named cross-arm routines (SHARED_RET, DRAW_CIN_xxx, etc.)
    are also preserved: when the FROM routine and TO routine both call
    SHARED_RET, the body matches; when one still has LABEL_<HEX> in
    that slot, the abstraction will not match yet — that's correct.
    """
    out = []
    for ln in body:
        s = re.sub(r';@raw=[^;]*$', '', ln).rstrip()
        if not s.strip():
            continue
        s = re.sub(r'\b(LABEL_[0-9A-F]+|JUNK__[0-9A-F]+)\b', '_LABEL_', s)
        out.append(s)
    return "\n".join(out)


arm_bodies = {}
for label, body in parse_routines(ARM):
    if not label.startswith("LABEL_"):
        continue
    sym = abstracted_body(body)
    if not sym:
        continue
    arm_bodies.setdefault(sym, []).append(label)

for label, body in parse_routines(CART):
    if label.startswith("LABEL_") or label.startswith("JUNK__"):
        continue
    sym = abstracted_body(body)
    if not sym:
        continue
    if sym in arm_bodies:
        targets = arm_bodies[sym]
        if len(targets) == 1:
            print(f"{targets[0]}={label}")
