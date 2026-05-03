#!/usr/bin/env python3
"""Sync LAKE renames from unified/lake/*.inc into per-branch LAKE.asm sources."""
import re
import sys
from pathlib import Path

AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")


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
    out = []
    for ln in body:
        s = re.sub(r';@raw=[^;]*$', '', ln).rstrip()
        if not s.strip():
            continue
        s = re.sub(r'\b(LABEL_[0-9A-F]+|JUNK__[0-9A-F]+|LBL_[0-9A-F]+_[0-9A-F]+)\b', '_LABEL_', s)
        out.append(s)
    return "\n".join(out)


def collect_named_bodies_from_dir(dir_path):
    bodies = {}
    for inc in dir_path.glob('*.inc'):
        text = inc.read_text()
        for label, body in parse_routines(text):
            if label.startswith('LABEL_') or label.startswith('JUNK_') or label.startswith('LBL_'):
                continue
            sym = abstracted_body(body)
            if sym:
                bodies[sym] = label
    return bodies


def main():
    unified_lake = AW_SRC / "src/levels/_unified/lake"
    unified_named = collect_named_bodies_from_dir(unified_lake)
    print(f"Unified lake: {len(unified_named)} named bodies", file=sys.stderr)
    
    cart_path = AW_SRC / "src/levels/cartridge_1992/LAKE.asm"
    cart_text = cart_path.read_text()
    cart_named_bodies = {}
    for label, body in parse_routines(cart_text):
        if label.startswith('LABEL_') or label.startswith('JUNK_') or label.startswith('LBL_'):
            continue
        sym = abstracted_body(body)
        if sym:
            cart_named_bodies[sym] = label
    
    # First sync cart from unified
    cart_target_bodies = {}
    for label, body in parse_routines(cart_text):
        if not (label.startswith('LABEL_') or label.startswith('LBL_')):
            continue
        sym = abstracted_body(body)
        if sym:
            cart_target_bodies.setdefault(sym, []).append(label)
    
    cart_renames = {}
    for sym, labels in cart_target_bodies.items():
        if sym in unified_named and len(labels) == 1:
            cart_renames[labels[0]] = unified_named[sym]
    
    used_in_cart = set()
    for m in re.finditer(r'^([A-Z_][A-Z_0-9]+):', cart_text, re.M):
        used_in_cart.add(m.group(1))
    
    new_cart = cart_text
    applied_cart = 0
    for old, new in cart_renames.items():
        if new in used_in_cart:
            continue
        used_in_cart.add(new)
        new_cart = re.sub(rf'\b{old}\b', new, new_cart)
        applied_cart += 1
    cart_path.write_text(new_cart)
    print(f"cart: {applied_cart} renames", file=sys.stderr)
    
    # Now collect cart's combined named bodies (from unified + just-renamed)
    cart_text = cart_path.read_text()
    cart_named_bodies = {}
    for label, body in parse_routines(cart_text):
        if label.startswith('LABEL_') or label.startswith('JUNK_') or label.startswith('LBL_'):
            continue
        sym = abstracted_body(body)
        if sym:
            cart_named_bodies[sym] = label
    
    # Combine cart + unified for matching
    all_named = {**unified_named, **cart_named_bodies}
    
    # Sync to other branches
    for branch in ('dos_1992', 'gba_2004', 'chahi_amiga_1991'):
        target = AW_SRC / f"src/levels/{branch}/LAKE.asm"
        if not target.exists():
            continue
        text = target.read_text()
        
        target_bodies = {}
        for label, body in parse_routines(text):
            if not (label.startswith('LABEL_') or label.startswith('LBL_')):
                continue
            sym = abstracted_body(body)
            if sym:
                target_bodies.setdefault(sym, []).append(label)
        
        renames = {}
        for sym, labels in target_bodies.items():
            if sym in all_named and len(labels) == 1:
                renames[labels[0]] = all_named[sym]
        
        used = set()
        for m in re.finditer(r'^([A-Z_][A-Z_0-9]+):', text, re.M):
            used.add(m.group(1))
        
        applied = 0
        new_text = text
        for old, new in renames.items():
            if new in used:
                continue
            used.add(new)
            new_text = re.sub(rf'\b{old}\b', new, new_text)
            applied += 1
        
        target.write_text(new_text)
        print(f"  {branch}: {applied} renames", file=sys.stderr)


if __name__ == '__main__':
    main()
