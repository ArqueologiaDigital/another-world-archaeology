#!/usr/bin/env python3
"""Sync semantic renames from cartridge_1992/INTRO.asm into other branches.

The other branches (dos, gba, amiga) have the same routines but at
different byte addresses. Match by abstracted body content."""
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
        s = re.sub(r'\b(LABEL_[0-9A-F]+|JUNK__[0-9A-F]+)\b', '_LABEL_', s)
        out.append(s)
    return "\n".join(out)


def main():
    cart_path = AW_SRC / "src/levels/cartridge_1992/INTRO.asm"
    cart_text = cart_path.read_text()
    
    # Collect cart-named routines (semantic only)
    cart_named_bodies = {}  # body_hash -> name
    for label, body in parse_routines(cart_text):
        if label.startswith('LABEL_') or label.startswith('JUNK_'):
            continue
        sym = abstracted_body(body)
        if sym:
            cart_named_bodies[sym] = label
    
    print(f"cart named bodies: {len(cart_named_bodies)}", file=sys.stderr)
    
    # For each other branch, match
    for branch in ('dos_1992', 'gba_2004', 'chahi_amiga_1991'):
        target_path = AW_SRC / f"src/levels/{branch}/INTRO.asm"
        if not target_path.exists():
            continue
        target_text = target_path.read_text()
        
        target_bodies = {}
        for label, body in parse_routines(target_text):
            if not label.startswith('LABEL_'):
                continue
            sym = abstracted_body(body)
            if sym:
                target_bodies.setdefault(sym, []).append(label)
        
        renames = {}
        for sym, target_labels in target_bodies.items():
            if sym in cart_named_bodies and len(target_labels) == 1:
                renames[target_labels[0]] = cart_named_bodies[sym]
        
        # Filter out collisions
        used_in_target = set()
        for m in re.finditer(r'^([A-Z_][A-Z_0-9]+):', target_text, re.M):
            used_in_target.add(m.group(1))
        
        applied = 0
        skipped = 0
        new_text = target_text
        for old, new in renames.items():
            if new in used_in_target:
                skipped += 1
                continue
            used_in_target.add(new)
            new_text = re.sub(rf'\b{old}\b', new, new_text)
            applied += 1
        
        target_path.write_text(new_text)
        print(f"  {branch}: {applied} applied, {skipped} skipped", file=sys.stderr)


if __name__ == '__main__':
    main()
