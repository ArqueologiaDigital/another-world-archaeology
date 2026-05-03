#!/usr/bin/env python3
"""Aggressive sync — abstract LABEL_<HEX>, CINEMATIC_<NNN>, COMMON_VIDEO_<NNN>
across branches. This catches routines that are structurally identical but
reference different CIN/CV indices per branch (because the EQU values
differ across branches)."""
import re
import sys
from pathlib import Path

AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")

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


def aggressive_abstract(body):
    """Abstract LABEL_<HEX>, CINEMATIC_<NNN>, COMMON_VIDEO_<NNN>."""
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
    if len(sys.argv) < 2:
        sys.exit("usage: STAGE")
    
    stage = sys.argv[1].upper()
    stage_dir = AW_SRC / "src/levels/_unified" / stage.lower()
    
    if not stage_dir.is_dir():
        sys.exit(f"FATAL: no per-arm dir at {stage_dir}")
    
    for arm in ('cart', 'dos', 'amiga'):
        branch = ARM_TO_BRANCH[arm]
        chunks = sorted(stage_dir.glob(f"{arm}*.inc"))
        if not chunks:
            continue
        
        unified_text = '\n'.join(c.read_text() for c in chunks)
        
        unified_bodies = {}
        for label, body in parse_routines(unified_text):
            if label.startswith('LABEL_') or label.startswith('JUNK_') or label.startswith('FOLD_BODY_') or label.startswith('DEDUP_'):
                continue
            sym = aggressive_abstract(body)
            if sym:
                unified_bodies.setdefault(sym, []).append(label)
        
        target = AW_SRC / f"src/levels/{branch}/{stage}.asm"
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
            if sym in unified_bodies:
                names = unified_bodies[sym]
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
        print(f"  {arm} → {branch}: {applied} applied", file=sys.stderr)


if __name__ == '__main__':
    main()
