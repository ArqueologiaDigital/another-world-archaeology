#!/usr/bin/env python3
"""Sync semantic renames from _unified/<stage>/<arm>__*.inc chunks
into per-branch <branch>/<STAGE>.asm sources.

For each per-branch source file, find LABEL_<HEX> labels whose body
matches a named routine in the corresponding unified arm chunks
(by abstracted-body comparison)."""
import re
import sys
from pathlib import Path

from _paths import AW_SRC


ARM_TO_BRANCH = {
    'cart': 'cartridge_1992',
    'dos': 'dos_1992',
    'amiga': 'chahi_amiga_1991',
}


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
    if len(sys.argv) < 2:
        sys.exit("usage: STAGE")
    
    stage = sys.argv[1].upper()
    stage_dir = AW_SRC / "src/levels/_unified" / stage.lower()
    
    if not stage_dir.is_dir():
        sys.exit(f"FATAL: no per-arm dir at {stage_dir}")
    
    # For each arm, collect named routines from chunks
    for arm in ('cart', 'dos', 'amiga'):
        branch = ARM_TO_BRANCH[arm]
        chunks = sorted(stage_dir.glob(f"{arm}*.inc"))
        if not chunks:
            continue
        
        # Concatenate chunks (in order)
        unified_text = '\n'.join(c.read_text() for c in chunks)
        
        # Collect named bodies
        unified_bodies = {}  # body_hash -> name
        for label, body in parse_routines(unified_text):
            if label.startswith('LABEL_') or label.startswith('JUNK_') or label.startswith('FOLD_BODY_') or label.startswith('DEDUP_'):
                continue
            sym = abstracted_body(body)
            if sym:
                unified_bodies[sym] = label
        
        # Per-branch source
        target = AW_SRC / f"src/levels/{branch}/{stage}.asm"
        if not target.exists():
            continue
        text = target.read_text()
        
        target_bodies = {}
        for label, body in parse_routines(text):
            if not label.startswith('LABEL_'):
                continue
            sym = abstracted_body(body)
            if sym:
                target_bodies.setdefault(sym, []).append(label)
        
        renames = {}
        for sym, labels in target_bodies.items():
            if sym in unified_bodies and len(labels) == 1:
                renames[labels[0]] = unified_bodies[sym]
        
        used = set()
        for m in re.finditer(r'^([A-Z_][A-Z_0-9]+):', text, re.M):
            used.add(m.group(1))
        
        new_text = text
        applied = 0
        skipped = 0
        for old, new in renames.items():
            if new in used:
                skipped += 1
                continue
            used.add(new)
            new_text = re.sub(rf'\b{old}\b', new, new_text)
            applied += 1
        
        target.write_text(new_text)
        print(f"  {arm} → {branch}: {applied} applied, {skipped} skipped", file=sys.stderr)


if __name__ == '__main__':
    main()
