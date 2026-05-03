#!/usr/bin/env python3
"""Auto-fold cross-arm fold candidates via multi_fold.py."""
import re
import subprocess
import sys
from pathlib import Path

AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")
ARCH = Path("/home/fsanches/compartilhado/another-world-archaeology")

if len(sys.argv) < 2:
    sys.exit("usage: auto_fold.py STAGE [--limit N]")

STAGE = sys.argv[1].upper()
LIMIT = None
for a in sys.argv[2:]:
    if a.startswith('--limit='):
        LIMIT = int(a.split('=')[1])


def find_candidates():
    result = subprocess.run(
        ['python3', str(ARCH / 'tools/find_foldable_routines.py'), STAGE],
        capture_output=True, text=True
    )
    cands = []
    for line in result.stdout.splitlines():
        m = re.match(r'\s*(\d+)b\s+(\d)arms\s+(.*)', line)
        if not m:
            continue
        size = int(m.group(1))
        rest = m.group(3).strip()
        parts = [p.strip() for p in rest.split('/')]
        arm_label = {}
        ambiguous = False
        for part in parts:
            pm = re.match(r'(\w+)=(\S+)$', part)
            if not pm:
                continue
            arm = pm.group(1)
            label = pm.group(2)
            if ',' in label:
                ambiguous = True
                break
            arm_label[arm] = label
        if ambiguous or not arm_label:
            continue
        names = set(arm_label.values())
        if len(names) != 1:
            continue
        name = next(iter(names))
        if name.startswith('LABEL_') or name.startswith('JUNK_'):
            continue
        cands.append((size, name, set(arm_label.keys())))
    return cands


def get_byte_positions(arm):
    """Return dict label_name -> (chunk_filename, line_number)."""
    stage_dir = AW_SRC / "src/levels/_unified" / STAGE.lower()
    positions = {}
    for inc in sorted(stage_dir.glob(f"{arm}*.inc")):
        text = inc.read_text()
        for i, line in enumerate(text.splitlines(), 1):
            m = re.match(r'^([A-Z_][A-Z_0-9]+):$', line)
            if m:
                positions[m.group(1)] = (inc.name, i)
    return positions


def main():
    cands = find_candidates()
    print(f"{STAGE}: {len(cands)} foldable candidates", file=sys.stderr)
    
    # Get byte positions in each arm
    arm_positions = {}
    for arm in ('cart', 'dos', 'amiga'):
        stage_dir = AW_SRC / "src/levels/_unified" / STAGE.lower()
        if any(stage_dir.glob(f"{arm}*.inc")):
            arm_positions[arm] = get_byte_positions(arm)
    
    # Order candidates by primary arm's byte position. If cart exists, use cart;
    # else dos.
    if 'cart' in arm_positions:
        order_arm = 'cart'
    elif 'dos' in arm_positions:
        order_arm = 'dos'
    else:
        order_arm = list(arm_positions.keys())[0]
    
    ordered = []
    for size, name, arms in cands:
        if name not in arm_positions[order_arm]:
            continue
        bo = arm_positions[order_arm][name]
        ordered.append((bo, size, name, arms))
    ordered.sort()
    
    # Filter: for each arm involved in a candidate, the order in that arm must match the global order.
    # Greedy: walk through ordered list; for each candidate, check that ALL its arms have this candidate
    # AFTER all previously-accepted candidates that share an arm with it.
    accepted = []
    last_pos_per_arm = {arm: ("", 0) for arm in arm_positions}
    skipped_oo = 0
    for bo, size, name, arms in ordered:
        ok = True
        for arm in arms:
            pos = arm_positions[arm].get(name)
            if pos is None:
                ok = False
                break
            if pos < last_pos_per_arm[arm]:
                ok = False
                break
        if not ok:
            skipped_oo += 1
            continue
        accepted.append((bo, size, name, arms))
        for arm in arms:
            last_pos_per_arm[arm] = arm_positions[arm][name]
    
    print(f"Order-skipped: {skipped_oo}, Accepted: {len(accepted)}", file=sys.stderr)
    
    if LIMIT:
        accepted = accepted[:LIMIT]
    
    fold_args = []
    for _, size, name, arms in accepted:
        arms_str = ','.join(sorted(arms))
        fold_args.append(f"{name}:{arms_str}")
    
    print(f"Folding {len(fold_args)} routines", file=sys.stderr)
    
    cmd = ['python3', str(ARCH / 'tools/multi_fold.py'), STAGE] + fold_args
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    unified_path = AW_SRC / "src/levels/_unified" / f"{STAGE}.asm.in"
    body_start = result.stdout.find(f'; Unified source for {STAGE}')
    if body_start < 0:
        print("ERROR: no body in multi_fold output", file=sys.stderr)
        print("STDERR:", result.stderr[-1500:], file=sys.stderr)
        sys.exit(1)
    unified_path.write_text(result.stdout[body_start:])
    print(f"Wrote {unified_path}", file=sys.stderr)


if __name__ == '__main__':
    main()
