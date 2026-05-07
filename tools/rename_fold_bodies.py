#!/usr/bin/env python3
"""Aggressive FOLD_BODY renamer."""
import re
import sys
from pathlib import Path

from _paths import AW_SRC



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


def gen_semantic_name(label, body_lines):
    code_lines = []
    for ln in body_lines:
        s = re.sub(r';@raw=[^;]*$', '', ln).rstrip()
        if not s.strip() or s.strip().startswith(';'):
            continue
        code_lines.append(s.strip())
    
    if not code_lines:
        return None
    
    # Pattern: all breaks
    if all(l == 'break' for l in code_lines):
        return f"DELAY_{len(code_lines)}_QUANTUMS"
    
    # Single-instruction
    if len(code_lines) == 1:
        first = code_lines[0]
        m = re.match(r'mov \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m:
            v = m.group(2).lstrip('0') or '0'
            return f"INLINE_SET_VAR{m.group(1)}_TO_{v}"
        m = re.match(r'sub \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m:
            v = m.group(2).lstrip('0') or '0'
            return f"INLINE_SUB_VAR{m.group(1)}_BY_{v}"
        m = re.match(r'add \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m:
            v = m.group(2).lstrip('0') or '0'
            return f"INLINE_ADD_VAR{m.group(1)}_BY_{v}"
        m = re.match(r'and \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m:
            return f"INLINE_AND_VAR{m.group(1)}_WITH_{m.group(2)}"
        m = re.match(r'mov \[0x([0-9A-F]+)\], \[0x([0-9A-F]+)\]', first)
        if m:
            return f"INLINE_COPY_VAR{m.group(2)}_TO_VAR{m.group(1)}"
        m = re.match(r'shr \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m:
            v = m.group(2).lstrip('0') or '0'
            return f"INLINE_SHR_VAR{m.group(1)}_BY_{v}"
        m = re.match(r'shl \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m:
            v = m.group(2).lstrip('0') or '0'
            return f"INLINE_SHL_VAR{m.group(1)}_BY_{v}"
        m = re.match(r'video type=[01], offset=(CINEMATIC_(\d+)|COMMON_VIDEO_(\d+)),\s+x=(\d+),\s+y=(\d+)', first)
        if m:
            n = m.group(2) or m.group(3)
            kind = "CIN" if m.group(2) else "CV"
            return f"INLINE_DRAW_{kind}_{n}_AT_{m.group(4)}_{m.group(5)}"
        # Bank switch
        m = re.match(r'bankSwitch (\d+)', first)
        if m:
            return f"INLINE_BANKSWITCH_{m.group(1)}"
        m = re.match(r'killChannel', first)
        if m:
            return None  # leave alone
        m = re.match(r'fill page=0x([0-9A-F]+), color=0x([0-9A-F]+)', first)
        if m:
            return f"INLINE_FILL_PAGE_{m.group(1)}_COLOR_{m.group(2)}"
    
    # Multi-instruction pattern: alternating sub+break
    if len(code_lines) >= 4 and len(code_lines) % 2 == 0:
        sub_break = True
        sub_var = None
        for i, l in enumerate(code_lines):
            if i % 2 == 0:
                m = re.match(r'sub \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', l)
                if m:
                    if sub_var is None: sub_var = m.group(1)
                    elif sub_var != m.group(1): sub_break = False; break
                else:
                    sub_break = False; break
            else:
                if l != 'break': sub_break = False; break
        if sub_break and sub_var:
            n = len(code_lines) // 2
            return f"DRIFT_DOWN_VAR{sub_var}_{n}X_AT_{label[-8:]}"
    
    # Multi-instruction: starts with mov + multiple subsequent ops, ends with killChannel
    if any('killChannel' in l for l in code_lines):
        for line in code_lines:
            bm = re.match(r'bankSwitch (\d+)', line)
            if bm:
                # Find first CIN drawn
                for line2 in code_lines:
                    cm = re.match(r'video type=[01], offset=CINEMATIC_(\d+)', line2)
                    if cm:
                        return f"DRAW_CIN_{cm.group(1)}_BANK{bm.group(1)}_KILL_AT_{label[-8:]}"
                return f"BANKSWITCH_{bm.group(1)}_AND_KILL_AT_{label[-8:]}"
    
    # Multi-instruction: video draws sequence
    cins = [m.group(1) for line in code_lines for m in [re.search(r'CINEMATIC_(\d+)', line)] if m]
    if cins and len(cins) >= 2:
        unique_cins = list(dict.fromkeys(cins))
        if len(unique_cins) <= 3:
            return f"DRAW_CIN_{'_'.join(unique_cins)}_SEQ_AT_{label[-8:]}"
        return f"DRAW_CIN_{unique_cins[0]}_TO_{unique_cins[-1]}_{len(cins)}F_AT_{label[-8:]}"
    
    # Multi-mov init block
    if all(re.match(r'mov \[0x[0-9A-F]+\], 0x[0-9A-F]+', l) for l in code_lines):
        vars = []
        for l in code_lines:
            mm = re.match(r'mov \[0x([0-9A-F]+)\]', l)
            if mm:
                vars.append(mm.group(1))
        return f"INIT_VARS_{'_'.join(vars[:3])}_X{len(vars)}"
    
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
        m = re.match(r'^(FOLD_BODY_\S+):$', lines[i])
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
    
    print(f"{stage}: {len(bodies)} FOLD_BODY routines", file=sys.stderr)
    
    used_names = set()
    for inc in (AW_SRC / "src/levels/_unified" / stage.lower()).glob("*.inc"):
        for m in re.finditer(r'^([A-Z_][A-Z_0-9]+):$', inc.read_text(), re.M):
            used_names.add(m.group(1))
    for m in re.finditer(r'^([A-Z_][A-Z_0-9]+):$', text, re.M):
        used_names.add(m.group(1))
    
    renames = []
    for label, body in bodies.items():
        new = gen_semantic_name(label, body)
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
