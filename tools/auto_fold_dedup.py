#!/usr/bin/env python3
"""Resolve ambiguous fold candidates: when multiple labels in one
arm share a body with multiple labels in another arm, pair them
by byte-order (first<->first, second<->second, etc.) and rename
each pair to a shared name."""
import re
import subprocess
import sys
from pathlib import Path

AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")
ARCH = Path("/home/fsanches/compartilhado/another-world-archaeology")

if len(sys.argv) < 2:
    sys.exit("usage: auto_fold_dedup.py STAGE")

STAGE = sys.argv[1].upper()
stage_dir = AW_SRC / "src/levels/_unified" / STAGE.lower()


def get_byte_positions(arm):
    positions = {}
    for inc in sorted(stage_dir.glob(f"{arm}*.inc")):
        text = inc.read_text()
        for i, line in enumerate(text.splitlines(), 1):
            m = re.match(r'^([A-Z_][A-Za-z_0-9]+):$', line)
            if m:
                positions[m.group(1)] = (inc.name, i)
    return positions


def apply_renames(arm, mapping):
    for inc in sorted(stage_dir.glob(f"{arm}*.inc")):
        text = inc.read_text()
        new_text = text
        for old, new in mapping.items():
            new_text = re.sub(rf'\b{old}\b', new, new_text)
        if new_text != text:
            inc.write_text(new_text)


def main():
    result = subprocess.run(
        ['python3', str(ARCH / 'tools/find_foldable_routines.py'), STAGE],
        capture_output=True, text=True
    )
    
    # Collect ambiguous tuples
    ambiguous_tuples = []
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
        # Only multi-label tuples
        if any(len(ls) > 1 for ls in arm_labels.values()):
            # Need same count across arms
            counts = {len(ls) for ls in arm_labels.values()}
            if len(counts) == 1 and counts != {1}:
                ambiguous_tuples.append((size, arm_labels))
    
    print(f"{STAGE}: {len(ambiguous_tuples)} ambiguous-tuple candidates", file=sys.stderr)
    
    if not ambiguous_tuples:
        return
    
    # Get byte positions for all arms
    arm_positions = {}
    for arm in ('cart', 'dos', 'amiga'):
        if any(stage_dir.glob(f"{arm}*.inc")):
            arm_positions[arm] = get_byte_positions(arm)
    
    # Used names (existing)
    used_names = set()
    for arm in arm_positions:
        used_names.update(arm_positions[arm].keys())
    
    rename_per_arm = {arm: {} for arm in arm_positions}
    counter = 0
    
    for size, arm_labels in ambiguous_tuples:
        # Sort each arm's labels by byte position
        sorted_per_arm = {}
        for arm, labels in arm_labels.items():
            if arm not in arm_positions:
                continue
            sorted_per_arm[arm] = sorted(labels, key=lambda l: arm_positions[arm].get(l, ('zz', 0)))
        
        # Pair up by index
        if not sorted_per_arm:
            continue
        n = len(next(iter(sorted_per_arm.values())))
        for i in range(n):
            counter += 1
            base_name = f"DEDUP_{STAGE}_{size}B_{counter:03d}"
            new_name = base_name
            suffix = 0
            while new_name in used_names:
                suffix += 1
                new_name = f"{base_name}_{suffix}"
            used_names.add(new_name)
            for arm, labels in sorted_per_arm.items():
                if i < len(labels):
                    rename_per_arm[arm][labels[i]] = new_name
    
    total = 0
    for arm, mapping in rename_per_arm.items():
        if not mapping:
            continue
        apply_renames(arm, mapping)
        total += len(mapping)
        print(f"  {arm}: {len(mapping)} renames", file=sys.stderr)
    print(f"\nTOTAL: {total}", file=sys.stderr)


if __name__ == '__main__':
    main()
