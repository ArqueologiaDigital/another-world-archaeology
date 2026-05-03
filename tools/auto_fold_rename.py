#!/usr/bin/env python3
"""Auto-rename fold candidates: take cross-arm byte-identical
LABEL_<HEX> tuples and rename them to a common semantic-or-hash name
in all arms.

Usage: python3 auto_fold_rename.py STAGE [--dry-run]
"""
import hashlib
import re
import sys
import subprocess
from pathlib import Path

AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")
ARCH = Path("/home/fsanches/compartilhado/another-world-archaeology")

if len(sys.argv) < 2:
    sys.exit("usage: auto_fold_rename.py STAGE [--dry-run]")

STAGE = sys.argv[1].upper()
DRY = '--dry-run' in sys.argv


def extract_fold_specs(stage):
    """Run find_foldable_routines.py and extract all-LABEL_<HEX> fold candidates."""
    result = subprocess.run(
        ['python3', str(ARCH / 'tools/find_foldable_routines.py'), stage],
        capture_output=True, text=True
    )
    specs = []  # list of (size, list_of_(arm, label))
    for line in result.stdout.splitlines():
        m = re.match(r'\s*(\d+)b\s+(\d)arms\s+(.*)', line)
        if not m:
            continue
        size = int(m.group(1))
        rest = m.group(3)
        # Parse "amiga=LABEL_X / cart=LABEL_Y / dos=LABEL_Z"
        pairs = []
        for pair in rest.split('/'):
            pair = pair.strip()
            pm = re.match(r'(\w+)=(\S+)', pair)
            if pm:
                pairs.append((pm.group(1), pm.group(2)))
        # Only keep all-LABEL_<HEX> entries
        if all(name.startswith('LABEL_') for _, name in pairs):
            specs.append((size, pairs))
    return specs


def get_body(stage_dir, arm, label):
    """Find label body across this arm's chunks."""
    for inc in sorted(stage_dir.glob(f"{arm}*.inc")):
        text = inc.read_text()
        m = re.search(rf'^{label}:$', text, re.M)
        if m:
            # Extract body until next label
            start = m.end()
            rest = text[start:]
            next_lbl = re.search(r'\n([A-Za-z_][A-Za-z_0-9]*):', rest)
            if next_lbl:
                body = rest[:next_lbl.start()].strip('\n')
            else:
                body = rest.strip('\n')
            return body
    return None


def gen_name(body_lines):
    """Generate a name from body. Uses simple rules + body-hash fallback."""
    lines = [l.strip() for l in body_lines.splitlines() if l.strip()]
    if not lines:
        return None
    
    first = lines[0]
    
    # Single-instruction patterns
    if len(lines) == 2 and lines[1].startswith('ret'):
        m = re.match(r'sub \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m:
            return f"DECREMENT_VAR{m.group(1)}_BY_{m.group(2).lstrip('0') or '0'}"
        m = re.match(r'add \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m:
            return f"INCREMENT_VAR{m.group(1)}_BY_{m.group(2).lstrip('0') or '0'}"
        m = re.match(r'and \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', first)
        if m:
            return f"AND_VAR{m.group(1)}_WITH_{m.group(2)}"
        m = re.match(r'mov \[0x([0-9A-F]+)\], \[0x([0-9A-F]+)\]', first)
        if m:
            return f"COPY_VAR{m.group(2)}_TO_VAR{m.group(1)}"
    
    # Multiple sub+break drift pattern
    sub_break_pattern = True
    sub_var = None
    for i, line in enumerate(lines):
        if i % 2 == 0:
            sm = re.match(r'sub \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', line)
            if sm:
                if sub_var is None:
                    sub_var = sm.group(1)
                elif sub_var != sm.group(1):
                    sub_break_pattern = False
                    break
            else:
                sub_break_pattern = False
                break
        else:
            if line != 'break':
                # Allow last line to be break or empty
                if i != len(lines) - 1:
                    sub_break_pattern = False
                    break
    if sub_break_pattern and sub_var and len(lines) >= 4:
        n_subs = (len(lines) + 1) // 2
        return f"DRIFT_DOWN_VAR{sub_var}_{n_subs}_BREAKS"
    
    # Multiple add+break drift pattern
    add_break_pattern = True
    add_var = None
    for i, line in enumerate(lines):
        if i % 2 == 0:
            am = re.match(r'add \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', line)
            if am:
                if add_var is None:
                    add_var = am.group(1)
                elif add_var != am.group(1):
                    add_break_pattern = False
                    break
            else:
                add_break_pattern = False
                break
        else:
            if line != 'break':
                if i != len(lines) - 1:
                    add_break_pattern = False
                    break
    if add_break_pattern and add_var and len(lines) >= 4:
        n_adds = (len(lines) + 1) // 2
        return f"DRIFT_UP_VAR{add_var}_{n_adds}_BREAKS"
    
    # Pattern: multiple `mov [varX], const` (init block)
    init_vars = []
    init_pattern = True
    for line in lines:
        im = re.match(r'mov \[0x([0-9A-F]+)\], 0x([0-9A-F]+)', line)
        if im:
            init_vars.append((im.group(1), im.group(2)))
        elif line.startswith('ret'):
            break
        else:
            init_pattern = False
            break
    if init_pattern and len(init_vars) >= 2:
        # Use up to 4 vars in name
        var_list = '_'.join(v for v, _ in init_vars[:4])
        if len(init_vars) > 4:
            return f"INIT_VARS_{var_list}_PLUS{len(init_vars)-4}"
        else:
            return f"INIT_VARS_{var_list}"
    
    # Pattern: video draw at constant position (no var07/08)
    if len(lines) >= 1:
        vm = re.match(r'video type=([01]), offset=(CINEMATIC_(\d+)|COMMON_VIDEO_(\d+)),\s+x=(\d+),\s+y=(\d+)', first)
        if vm:
            n = vm.group(3) or vm.group(4)
            kind = "CIN" if vm.group(3) else "CV"
            if len(lines) == 2 and lines[1].startswith('ret'):
                return f"DRAW_{kind}_{n}_AT_{vm.group(5)}_{vm.group(6)}"
    
    # Body-hash fallback
    body_concat = '\n'.join(lines)
    h = hashlib.sha1(body_concat.encode()).hexdigest()[:8].upper()
    size_hint = len(body_concat)
    return f"FOLD_BODY_{size_hint}B_{h}"


def main():
    stage_dir = AW_SRC / "src/levels/_unified" / STAGE.lower()
    specs = extract_fold_specs(STAGE)
    print(f"{STAGE}: {len(specs)} all-LABEL fold candidates", file=sys.stderr)
    
    # For each spec, get body and generate name
    rename_plan = {}  # arm -> { LABEL_X: new_name }
    for arm in ('amiga', 'cart', 'dos'):
        rename_plan[arm] = {}
    
    used_names = set()
    skipped = 0
    
    # Also check existing named routines to avoid collisions
    for arm in ('amiga', 'cart', 'dos'):
        for inc in sorted(stage_dir.glob(f"{arm}*.inc")):
            text = inc.read_text()
            for m in re.finditer(r'^([A-Z_][A-Z_0-9]+):$', text, re.M):
                used_names.add(m.group(1))
    
    for size, pairs in specs:
        # Get body from any arm
        first_arm, first_label = pairs[0]
        body = get_body(stage_dir, first_arm, first_label)
        if not body:
            skipped += 1
            continue
        name = gen_name(body)
        if not name:
            skipped += 1
            continue
        # Ensure unique
        base = name
        suffix = 0
        while name in used_names:
            suffix += 1
            name = f"{base}_{suffix}"
        used_names.add(name)
        for arm, label in pairs:
            rename_plan[arm][label] = name
    
    # Apply renames
    print(f"\nRename plan: skipped={skipped}", file=sys.stderr)
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
                if not DRY:
                    inc.write_text(new_text)
                # Count actual renames
                
        print(f"  {arm}: {len(mapping)} renames", file=sys.stderr)
        total_renames += len(mapping)
    
    print(f"\nTOTAL: {total_renames} renames", file=sys.stderr)
    return rename_plan


if __name__ == '__main__':
    main()
