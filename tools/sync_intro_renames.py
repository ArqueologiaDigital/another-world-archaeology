#!/usr/bin/env python3
"""Sync semantic renames from unified/intro/*.inc into cartridge_1992/INTRO.asm.

Match routines by abstracted body — each pair of (unified named, per-branch LABEL_HEX) with identical body content yields a rename.
"""
import re
import sys
from pathlib import Path

from _paths import AW_SRC



def parse_routines(text):
    lines = text.splitlines()
    cur_label = None
    cur_body = []
    for ln in lines:
        m = re.match(r'^([A-Za-z_][A-Za-z_0-9]*):$', ln)
        if m:
            if cur_label is not None:
                yield cur_label, cur_body
            cur_label = m.group(1)
            cur_body = []
        elif cur_label is not None:
            if ln.strip().startswith(';@'):
                continue
            cur_body.append(ln)
    if cur_label is not None:
        yield cur_label, cur_body


def abstracted_body(body):
    """Strip ;@raw= and abstract LABEL_<HEX> tokens."""
    out = []
    for ln in body:
        s = re.sub(r';@raw=[^;]*$', '', ln).rstrip()
        if not s.strip():
            continue
        s = re.sub(r'\b(LABEL_[0-9A-F]+|JUNK__[0-9A-F]+)\b', '_LABEL_', s)
        out.append(s)
    return "\n".join(out)


def main():
    cart_path = AW_SRC / "src/levels/cartridge_1992/INTRO.asm"
    unified_dir = AW_SRC / "src/levels/_unified/intro"
    
    cart_text = cart_path.read_text()
    
    # Collect cart routines: only LABEL_<HEX>
    cart_bodies = {}  # body_hash -> [labels]
    for label, body in parse_routines(cart_text):
        if not label.startswith('LABEL_'):
            continue
        sym = abstracted_body(body)
        if sym:
            cart_bodies.setdefault(sym, []).append(label)
    
    # Collect unified routines: only named (not LABEL_<HEX>)
    unified_bodies = {}  # body_hash -> name
    for inc_path in unified_dir.glob('*.inc'):
        text = inc_path.read_text()
        for label, body in parse_routines(text):
            if label.startswith('LABEL_') or label.startswith('JUNK_'):
                continue
            sym = abstracted_body(body)
            if sym:
                unified_bodies[sym] = label
    
    # Match
    renames = {}
    for sym, cart_labels in cart_bodies.items():
        if sym in unified_bodies and len(cart_labels) == 1:
            renames[cart_labels[0]] = unified_bodies[sym]
    
    print(f"Found {len(renames)} renames", file=sys.stderr)
    
    # Apply
    new_text = cart_text
    used_in_cart = set()
    for m in re.finditer(r'^([A-Z_][A-Z_0-9]+):', cart_text, re.M):
        used_in_cart.add(m.group(1))
    
    applied = 0
    skipped = 0
    for old, new in renames.items():
        if new in used_in_cart:
            skipped += 1
            continue
        used_in_cart.add(new)
        new_text = re.sub(rf'\b{old}\b', new, new_text)
        applied += 1
    
    cart_path.write_text(new_text)
    print(f"Applied {applied}, skipped {skipped}", file=sys.stderr)


if __name__ == '__main__':
    main()
