#!/usr/bin/env python3
"""Rename DEDUP_<STAGE>_<size>B_<seq> routines to body-shape names."""
import re
import sys
from pathlib import Path

AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")


def rename_in_arm_chunks(stage, old, new):
    stage_dir = AW_SRC / "src/levels/_unified" / stage.lower()
    for inc in stage_dir.glob("*.inc"):
        text = inc.read_text()
        if old in text:
            new_text = re.sub(rf'\b{old}\b', new, text)
            if new_text != text:
                inc.write_text(new_text)


def rename_in_unified(stage, old, new):
    p = AW_SRC / f"src/levels/_unified/{stage}.asm.in"
    text = p.read_text()
    if old in text:
        new_text = re.sub(rf'\b{old}\b', new, text)
        if new_text != text:
            p.write_text(new_text)


def gen_dedup_name(label, body_lines):
    """Generate name for a duplicate body."""
    code_lines = []
    for ln in body_lines:
        s = re.sub(r';@raw=[^;]*$', '', ln).rstrip()
        if not s.strip():
            continue
        code_lines.append(s.strip())
    
    if not code_lines:
        return None
    
    # 1-byte dedups
    if len(code_lines) == 1:
        if code_lines[0] == 'killChannel':
            return f"INLINE_KILL_{label[-3:]}"  # use seq number from label
        if code_lines[0] == 'ret':
            return f"INLINE_RET_{label[-3:]}"
        if code_lines[0] == 'break':
            return f"INLINE_BREAK_{label[-3:]}"
    
    # Single-mov constant
    if len(code_lines) == 1:
        first = code_lines[0]
        m = re.match(r'mov \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m:
            return f"INLINE_SET_VAR{m.group(1)}_TO_{m.group(2)}_{label[-3:]}"
        m = re.match(r'sub \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m:
            return f"INLINE_SUB_VAR{m.group(1)}_BY_{m.group(2)}_{label[-3:]}"
        m = re.match(r'video type=[01], offset=(CINEMATIC_(\d+)|COMMON_VIDEO_(\d+))', first)
        if m:
            n = m.group(2) or m.group(3)
            kind = "CIN" if m.group(2) else "CV"
            return f"INLINE_DRAW_{kind}_{n}_{label[-3:]}"
        # bankSwitch
        m = re.match(r'bankSwitch (\d+)', first)
        if m:
            return f"INLINE_BANK_{m.group(1)}_{label[-3:]}"
        m = re.match(r'fill page=0x([0-9A-F]+), color=0x([0-9A-F]+)', first)
        if m:
            return f"INLINE_FILL_P{m.group(1)}_C{m.group(2)}_{label[-3:]}"
    
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: STAGE")
    
    stage = sys.argv[1].upper()
    p = AW_SRC / f"src/levels/_unified/{stage}.asm.in"
    text = p.read_text()
    lines = text.splitlines()
    
    bodies = {}
    i = 0
    while i < len(lines):
        m = re.match(r'^(DEDUP_\S+):$', lines[i])
        if m:
            label = m.group(1)
            body = []
            j = i + 1
            while j < len(lines):
                if lines[j].strip().startswith(';@'):
                    break
                if re.match(r'^[A-Za-z_][A-Za-z_0-9]*:$', lines[j]):
                    break
                body.append(lines[j])
                j += 1
            bodies[label] = body
        i += 1
    
    print(f"{stage}: {len(bodies)} DEDUP routines", file=sys.stderr)
    
    used_names = set()
    for inc in (AW_SRC / "src/levels/_unified" / stage.lower()).glob("*.inc"):
        for m in re.finditer(r'^([A-Z_][A-Z_0-9]+):$', inc.read_text(), re.M):
            used_names.add(m.group(1))
    for m in re.finditer(r'^([A-Z_][A-Z_0-9]+):$', text, re.M):
        used_names.add(m.group(1))
    
    renames = []
    for label, body in bodies.items():
        new = gen_dedup_name(label, body)
        if new is None:
            continue
        base = new
        suffix = 0
        while new in used_names:
            suffix += 1
            new = f"{base}_{suffix}"
        used_names.add(new)
        renames.append((label, new))
    
    print(f"Generated {len(renames)} renames", file=sys.stderr)
    
    for old, new in renames:
        rename_in_arm_chunks(stage, old, new)
        rename_in_unified(stage, old, new)


if __name__ == '__main__':
    main()
