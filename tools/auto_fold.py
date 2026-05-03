#!/usr/bin/env python3
"""Auto-fold v3: handles 2-arm folds where primary arm doesn't have the routine."""
import re
import subprocess
import sys
from pathlib import Path

AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")
ARCH = Path("/home/fsanches/compartilhado/another-world-archaeology")

if len(sys.argv) < 2:
    sys.exit("usage: auto_fold3.py STAGE")

STAGE = sys.argv[1].upper()


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
    
    arm_positions = {}
    for arm in ('cart', 'dos', 'amiga'):
        stage_dir = AW_SRC / "src/levels/_unified" / STAGE.lower()
        if any(stage_dir.glob(f"{arm}*.inc")):
            arm_positions[arm] = get_byte_positions(arm)
    
    # Topological order: for each candidate, its global position is the 'highest' position
    # across all arms it appears in (where 'highest' means latest in byte order).
    # We sort by primary-arm position if present, else fall back.
    
    # Strategy: compute order using ALL arms by walking a DAG.
    # Simpler: use cart order as primary, but for candidates not in cart,
    # interpolate using their position relative to cart-anchored neighbors in dos.
    
    if 'cart' in arm_positions:
        primary = 'cart'
    elif 'dos' in arm_positions:
        primary = 'dos'
    else:
        primary = next(iter(arm_positions))
    
    # Order each candidate by primary-arm position. For candidates not in primary,
    # use dos position interpolated.
    def candidate_order(cand):
        size, name, arms = cand
        if primary in arms and name in arm_positions[primary]:
            return arm_positions[primary][name]
        # Find this candidate's position in another arm and interpolate
        for arm in ('dos', 'amiga', 'cart'):
            if arm in arms and name in arm_positions.get(arm, {}):
                # Use this position but with a different filename prefix
                fname, line = arm_positions[arm][name]
                # Substitute the arm prefix with primary's prefix to get a comparable position
                return (fname.replace(f"{arm}", primary), line)
        return ('zzz', 0)
    
    # Apply order
    ordered = sorted(cands, key=candidate_order)
    
    # Filter cross-arm order consistency
    accepted = []
    last_pos_per_arm = {arm: ("", 0) for arm in arm_positions}
    skipped_oo = 0
    for size, name, arms in ordered:
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
        accepted.append((size, name, arms))
        for arm in arms:
            last_pos_per_arm[arm] = arm_positions[arm][name]
    
    print(f"Order-skipped: {skipped_oo}, Accepted: {len(accepted)}", file=sys.stderr)
    
    fold_args = []
    for size, name, arms in accepted:
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
