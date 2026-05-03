#!/usr/bin/env python3
"""Auto-fold v5: handles dedup-named multi-label tuples by splitting
them into separate single-label folds when names match across arms."""
import re
import subprocess
import sys
from pathlib import Path

AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")
ARCH = Path("/home/fsanches/compartilhado/another-world-archaeology")

if len(sys.argv) < 2:
    sys.exit("usage: auto_fold.py STAGE")

STAGE = sys.argv[1].upper()


def find_candidates():
    result = subprocess.run(
        ['python3', str(ARCH / 'tools/find_foldable_routines.py'), STAGE],
        capture_output=True, text=True
    )
    cands = []  # (size, name, set_of_arms)
    for line in result.stdout.splitlines():
        m = re.match(r'\s*(\d+)b\s+(\d)arms\s+(.*)', line)
        if not m:
            continue
        size = int(m.group(1))
        rest = m.group(3).strip()
        parts = [p.strip() for p in rest.split('/')]
        arm_labels = {}
        for part in parts:
            pm = re.match(r'(\w+)=(.+)$', part)
            if pm:
                arm = pm.group(1)
                labels = pm.group(2).split(',')
                arm_labels[arm] = labels
        if not arm_labels:
            continue
        
        # If all arms have the same single label name, it's a simple fold
        single_name_set = set()
        is_simple = all(len(ls) == 1 for ls in arm_labels.values())
        if is_simple:
            names = {ls[0] for ls in arm_labels.values()}
            if len(names) == 1:
                name = next(iter(names))
                if not (name.startswith('LABEL_') or name.startswith('JUNK_')):
                    cands.append((size, name, set(arm_labels.keys())))
            continue
        
        # Multi-label tuple: try to split into per-name folds
        # Find names that appear in ALL arms involved
        all_names = set()
        for ls in arm_labels.values():
            all_names.update(ls)
        # For each name, check if it's in every arm in this tuple
        for name in all_names:
            if name.startswith('LABEL_') or name.startswith('JUNK_'):
                continue
            arms_with_this = {arm for arm, ls in arm_labels.items() if name in ls}
            if arms_with_this == set(arm_labels.keys()):
                # This name appears in all involved arms — fold candidate
                cands.append((size, name, arms_with_this))
    
    return cands


def get_byte_positions(arm):
    stage_dir = AW_SRC / "src/levels/_unified" / STAGE.lower()
    positions = {}
    for inc in sorted(stage_dir.glob(f"{arm}*.inc")):
        text = inc.read_text()
        for i, line in enumerate(text.splitlines(), 1):
            m = re.match(r'^([A-Z_][A-Za-z_0-9]+):$', line)
            if m:
                positions[m.group(1)] = (inc.name, i)
    return positions


def evaluate(cands, arm_positions, primary):
    def candidate_order(cand):
        size, name, arms = cand
        if primary in arms and name in arm_positions.get(primary, {}):
            return arm_positions[primary][name]
        for arm in ('dos', 'amiga', 'cart'):
            if arm in arms and name in arm_positions.get(arm, {}):
                fname, line = arm_positions[arm][name]
                return (fname.replace(f"{arm}", primary), line)
        return ('zzz', 0)
    
    ordered = sorted(cands, key=candidate_order)
    last_pos_per_arm = {arm: ("", 0) for arm in arm_positions}
    accepted = []
    skipped = 0
    for size, name, arms in ordered:
        ok = True
        for arm in arms:
            pos = arm_positions[arm].get(name)
            if pos is None or pos < last_pos_per_arm[arm]:
                ok = False
                break
        if not ok:
            skipped += 1
            continue
        accepted.append((size, name, arms))
        for arm in arms:
            last_pos_per_arm[arm] = arm_positions[arm][name]
    return accepted, skipped


def main():
    cands = find_candidates()
    print(f"{STAGE}: {len(cands)} foldable candidates", file=sys.stderr)
    
    arm_positions = {}
    for arm in ('cart', 'dos', 'amiga'):
        stage_dir = AW_SRC / "src/levels/_unified" / STAGE.lower()
        if any(stage_dir.glob(f"{arm}*.inc")):
            arm_positions[arm] = get_byte_positions(arm)
    
    best_primary = None
    best_accepted = []
    best_skipped = float('inf')
    for primary in arm_positions:
        accepted, skipped = evaluate(cands, arm_positions, primary)
        print(f"  primary={primary}: accepted={len(accepted)}, skipped={skipped}", file=sys.stderr)
        if skipped < best_skipped or (skipped == best_skipped and len(accepted) > len(best_accepted)):
            best_primary = primary
            best_accepted = accepted
            best_skipped = skipped
    
    print(f"Best primary: {best_primary}, Accepted: {len(best_accepted)}, Skipped: {best_skipped}", file=sys.stderr)
    
    fold_args = []
    for size, name, arms in best_accepted:
        arms_str = ','.join(sorted(arms))
        fold_args.append(f"{name}:{arms_str}")
    
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
