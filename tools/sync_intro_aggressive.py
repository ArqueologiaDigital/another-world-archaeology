#!/usr/bin/env python3
"""Aggressive INTRO sync — abstract CIN/CV operands."""
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


def aggressive_abstract(body):
    out = []
    for ln in body:
        s = re.sub(r';@raw=[^;]*$', '', ln).rstrip()
        if not s.strip():
            continue
        s = re.sub(r'\b(LABEL_[0-9A-F]+|JUNK__[0-9A-F]+)\b', '_LABEL_', s)
        s = re.sub(r'\bCINEMATIC_\d+\b', '_CIN_', s)
        s = re.sub(r'\bCOMMON_VIDEO_\d+\b', '_CV_', s)
        s = re.sub(r'\bPOLY_\d+\b', '_POLY_', s)
        out.append(s)
    return "\n".join(out)


def main():
    cart_path = AW_SRC / "src/levels/cartridge_1992/INTRO.asm"
    cart_text = cart_path.read_text()
    
    cart_named = {}
    for label, body in parse_routines(cart_text):
        if label.startswith('LABEL_') or label.startswith('JUNK_'):
            continue
        sym = aggressive_abstract(body)
        if sym:
            cart_named.setdefault(sym, []).append(label)
    
    print(f"cart named: {len(cart_named)}", file=sys.stderr)
    
    for branch in ('dos_1992', 'gba_2004', 'chahi_amiga_1991'):
        target = AW_SRC / f"src/levels/{branch}/INTRO.asm"
        if not target.exists():
            continue
        text = target.read_text()
        
        target_bodies = {}
        for label, body in parse_routines(text):
            if not label.startswith('LABEL_'):
                continue
            sym = aggressive_abstract(body)
            if sym:
                target_bodies.setdefault(sym, []).append(label)
        
        renames = {}
        for sym, labels in target_bodies.items():
            if sym in cart_named:
                names = cart_named[sym]
                if len(names) == 1 and len(labels) == 1:
                    renames[labels[0]] = names[0]
        
        used = set()
        for m in re.finditer(r'^([A-Z_][A-Z_0-9]+):', text, re.M):
            used.add(m.group(1))
        
        new_text = text
        applied = 0
        for old, new in renames.items():
            if new in used:
                continue
            used.add(new)
            new_text = re.sub(rf'\b{old}\b', new, new_text)
            applied += 1
        
        target.write_text(new_text)
        print(f"  {branch}: {applied} applied", file=sys.stderr)


if __name__ == '__main__':
    main()
