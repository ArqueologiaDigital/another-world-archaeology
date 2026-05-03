#!/usr/bin/env python3
"""Match cart routines to arm routines by ABSTRACTED symbolic body.

For each line, replace operands that look like labels (e.g. LABEL_<HEX>,
named routines) with a placeholder _LABEL_. This way two routines with
the same instruction sequence but different label targets count as a match.

Usage: python3 /tmp/match_cart_to_arm_v2.py STAGE OTHER_ARM
"""
import os, re, sys
from pathlib import Path

if len(sys.argv) != 3:
    sys.exit(__doc__)

STAGE = sys.argv[1].lower()
OTHER = sys.argv[2]
AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")
CART = AW_SRC / f"src/levels/_unified/{STAGE}/cart.inc"
ARM = AW_SRC / f"src/levels/_unified/{STAGE}/{OTHER}.inc"


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


def abstracted_body(body):
    """Strip ;@raw= and abstract label-like identifiers in operands."""
    out = []
    for ln in body:
        s = re.sub(r';@raw=[^;]*$', '', ln).rstrip()
        if not s.strip():
            continue
        # Abstract label-name operands (anything matching [A-Z_][A-Z_0-9]+ that's NOT a register or var)
        # Replace LABEL_<HEX> and ALL_CAPS_NAMES with _LABEL_ when they appear as operand
        s = re.sub(r'\b(LABEL_[0-9A-F]+|JUNK__[0-9A-F]+|[A-Z_][A-Z_0-9]+)\b',
                   lambda m: '_LABEL_' if not m.group(0) in {'PAUSE_SLICES','LAST_KEYCHAR','HERO_ACTION','HERO_POS_LEFT_RIGHT','HERO_POS_UP_DOWN','HERO_POS_JUMP_DOWN','HERO_POS_MASK','HERO_ACTION_POS_MASK','RANDOM_SEED','MUS_MARK','HACK_VAR_67','HACK_VAR_DC','HACK_VAR_F7','HACK_VAR_54','SCROLL_Y'} else m.group(0),
                   s)
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
