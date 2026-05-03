#!/usr/bin/env python3
"""Improved auto-fold renamer — catches more patterns and 2-arm folds."""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")
ARCH = Path("/home/fsanches/compartilhado/another-world-archaeology")

if len(sys.argv) < 2:
    sys.exit("usage: auto_fold_rename2.py STAGE")

STAGE = sys.argv[1].upper()


def extract_fold_specs(stage):
    result = subprocess.run(
        ['python3', str(ARCH / 'tools/find_foldable_routines.py'), stage],
        capture_output=True, text=True
    )
    specs = []
    for line in result.stdout.splitlines():
        m = re.match(r'\s*(\d+)b\s+(\d)arms\s+(.*)', line)
        if not m:
            continue
        size = int(m.group(1))
        rest = m.group(3)
        pairs = []
        ambiguous = False
        for pair in rest.split('/'):
            pair = pair.strip()
            pm = re.match(r'(\w+)=(\S+)$', pair)
            if pm:
                lbl = pm.group(2)
                if ',' in lbl:
                    ambiguous = True
                    break
                pairs.append((pm.group(1), lbl))
        if ambiguous:
            continue
        # Need at least one LABEL_ (otherwise already folded or named)
        if any(name.startswith('LABEL_') for _, name in pairs):
            specs.append((size, pairs))
    return specs


def get_body(stage_dir, arm, label):
    for inc in sorted(stage_dir.glob(f"{arm}*.inc")):
        text = inc.read_text()
        m = re.search(rf'^{label}:$', text, re.M)
        if m:
            start = m.end()
            rest = text[start:]
            next_lbl = re.search(r'\n([A-Za-z_][A-Za-z_0-9]*):', rest)
            body = rest[:next_lbl.start()].strip('\n') if next_lbl else rest.strip('\n')
            return body
    return None


def gen_name(body_lines):
    lines = [l.strip() for l in body_lines.splitlines() if l.strip()]
    if not lines:
        return None
    
    # Strip trailing ret if present
    has_ret = lines and lines[-1].startswith('ret')
    code = lines[:-1] if has_ret else lines
    
    if not code:
        # Just a ret
        return None  # leave as LABEL_, would conflict with TRIVIAL_RET
    
    # Single-instruction patterns
    if len(code) == 1:
        first = code[0]
        m = re.match(r'sub \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m and has_ret:
            v = m.group(2).lstrip('0') or '0'
            return f"DECREMENT_VAR{m.group(1)}_BY_{v}"
        m = re.match(r'add \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m and has_ret:
            v = m.group(2).lstrip('0') or '0'
            return f"INCREMENT_VAR{m.group(1)}_BY_{v}"
        m = re.match(r'and \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m and has_ret:
            return f"AND_VAR{m.group(1)}_WITH_{m.group(2)}"
        m = re.match(r'or \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m and has_ret:
            return f"OR_VAR{m.group(1)}_WITH_{m.group(2)}"
        m = re.match(r'shl \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m and has_ret:
            return f"SHL_VAR{m.group(1)}_BY_{m.group(2).lstrip('0') or '0'}"
        m = re.match(r'shr \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m and has_ret:
            return f"SHR_VAR{m.group(1)}_BY_{m.group(2).lstrip('0') or '0'}"
        m = re.match(r'mov \[0x([0-9A-F]+)\], \[0x([0-9A-F]+)\]', first)
        if m and has_ret:
            return f"COPY_VAR{m.group(2)}_TO_VAR{m.group(1)}"
    
    # sub+break / add+break drift
    drift_var = None
    drift_dir = None
    drift_pattern = True
    for i, line in enumerate(code):
        if i % 2 == 0:
            sm = re.match(r'(sub|add) \[0x([0-9A-F]+)\], 0x[0-9A-F]+', line)
            if sm:
                if drift_var is None:
                    drift_var = sm.group(2)
                    drift_dir = sm.group(1)
                elif drift_var != sm.group(2) or drift_dir != sm.group(1):
                    drift_pattern = False
                    break
            else:
                drift_pattern = False
                break
        else:
            if line != 'break':
                drift_pattern = False
                break
    if drift_pattern and drift_var and len(code) >= 4:
        n_subs = (len(code) + 1) // 2
        op = "DRIFT_DOWN" if drift_dir == "sub" else "DRIFT_UP"
        return f"{op}_VAR{drift_var}_{n_subs}X"
    
    # Multi-mov init block
    init_vars = []
    init_pattern = True
    for line in code:
        im = re.match(r'mov \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', line)
        if im:
            init_vars.append((im.group(1), im.group(2)))
        else:
            init_pattern = False
            break
    if init_pattern and len(init_vars) >= 2 and has_ret:
        var_list = '_'.join(v for v, _ in init_vars[:4])
        if len(init_vars) > 4:
            return f"INIT_VARS_{var_list}_X{len(init_vars)}"
        else:
            return f"INIT_VARS_{var_list}"
    
    # video at constant position (only one video)
    if len(code) == 1 and has_ret:
        first = code[0]
        vm = re.match(r'video type=([01]), offset=(CINEMATIC_(\d+)|COMMON_VIDEO_(\d+)),\s+x=(\d+),\s+y=(\d+)', first)
        if vm:
            n = vm.group(3) or vm.group(4)
            kind = "CIN" if vm.group(3) else "CV"
            return f"DRAW_{kind}_{n}_AT_{vm.group(5)}_{vm.group(6)}"
    
    # Pattern: jne X, Y, Z; ret; (shape: short conditional)
    if len(code) == 1 and has_ret:
        first = code[0]
        jm = re.match(r'(jne|je|jl|jg|jge|jle) \[0x([0-9A-F]+)\], 0x([0-9A-F]+),\s+(\S+)', first)
        if jm:
            return f"{jm.group(1).upper()}_VAR{jm.group(2)}_{jm.group(3)}_{jm.group(4)[:20]}"
    
    # Body-hash fallback
    body_concat = '\n'.join(lines)
    h = hashlib.sha1(body_concat.encode()).hexdigest()[:8].upper()
    size_hint = len(body_concat)
    return f"FOLD_BODY_{size_hint}B_{h}"


def main():
    stage_dir = AW_SRC / "src/levels/_unified" / STAGE.lower()
    specs = extract_fold_specs(STAGE)
    print(f"{STAGE}: {len(specs)} fold candidates with at least one LABEL_", file=sys.stderr)
    
    used_names = set()
    for arm in ('amiga', 'cart', 'dos'):
        for inc in sorted(stage_dir.glob(f"{arm}*.inc")):
            text = inc.read_text()
            for m in re.finditer(r'^([A-Z_][A-Z_0-9]+):$', text, re.M):
                used_names.add(m.group(1))
    
    rename_plan = {arm: {} for arm in ('amiga', 'cart', 'dos')}
    skipped = 0
    
    for size, pairs in specs:
        first_arm, first_label = pairs[0]
        body = get_body(stage_dir, first_arm, first_label)
        if not body:
            skipped += 1
            continue
        
        # If any arm is already named, use that name
        existing_name = None
        for arm, label in pairs:
            if not label.startswith('LABEL_') and not label.startswith('JUNK_'):
                existing_name = label
                break
        
        if existing_name:
            name = existing_name
        else:
            name = gen_name(body)
            if not name:
                skipped += 1
                continue
            base = name
            suffix = 0
            while name in used_names:
                suffix += 1
                name = f"{base}_{suffix}"
            used_names.add(name)
        
        for arm, label in pairs:
            if label != name:  # only rename if needed
                rename_plan[arm][label] = name
    
    print(f"Skipped: {skipped}", file=sys.stderr)
    total_renames = 0
    for arm, mapping in rename_plan.items():
        if not mapping:
            continue
        for inc in sorted(stage_dir.glob(f"{arm}*.inc")):
            text = inc.read_text()
            new_text = text
            for old, new in mapping.items():
                new_text = re.sub(rf'\b{old}\b', new, new_text)
            if new_text != text:
                inc.write_text(new_text)
        print(f"  {arm}: {len(mapping)} renames", file=sys.stderr)
        total_renames += len(mapping)
    print(f"\nTOTAL: {total_renames}", file=sys.stderr)


if __name__ == '__main__':
    main()
