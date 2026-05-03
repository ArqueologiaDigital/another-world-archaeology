#!/usr/bin/env python3
"""Find routines whose bodies match across multiple stages."""
import re
import hashlib
from pathlib import Path
from collections import defaultdict

AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")

stages = ['CAPSULE', 'CAVES', 'CODE_WHEEL', 'ENDING', 'PASSCODE', 'PRISON', 'TANK']

# body_hash -> list of (stage, label, byte_size)
groups = defaultdict(list)

for stage in stages:
    p = AW_SRC / f"src/levels/_unified/{stage}.asm.in"
    text = p.read_text()
    lines = text.splitlines()
    
    i = 0
    while i < len(lines):
        m = re.match(r'^([A-Z_][A-Z_0-9]+):$', lines[i])
        if m:
            label = m.group(1)
            body = []
            byte_count = 0
            j = i + 1
            while j < len(lines):
                if lines[j].strip().startswith(';@'):
                    break
                if re.match(r'^[A-Za-z_][A-Za-z_0-9]*:$', lines[j]):
                    break
                body.append(lines[j])
                # Count bytes from ;@raw=
                rm = re.search(r';@raw=([0-9A-Fa-fxX, ]+)', lines[j])
                if rm:
                    byte_count += len([b for b in rm.group(1).split(',') if b.strip()])
                j += 1
            # Hash the symbolic body (stripped of raw)
            sym_body = []
            for ln in body:
                s = re.sub(r';@raw=[^;]*$', '', ln).rstrip()
                if s.strip():
                    sym_body.append(s)
            body_str = '\n'.join(sym_body)
            if body_str:
                h = hashlib.sha1(body_str.encode()).hexdigest()
                groups[h].append((stage, label, byte_count))
        i += 1

# Find groups present in 2+ stages
cross_stage = []
for h, labels in groups.items():
    stages_in_group = {s for s, _, _ in labels}
    if len(stages_in_group) >= 2:
        cross_stage.append((labels[0][2], stages_in_group, labels))

cross_stage.sort(key=lambda x: -x[0])
print(f"Cross-stage helper candidates: {len(cross_stage)}")
print()
for size, stages_in, labels in cross_stage[:20]:
    stages_str = ','.join(sorted(stages_in))
    # All labels in this group
    label_set = sorted({l for _, l, _ in labels})
    print(f"  {size:3d}b  {stages_str}: {' | '.join(label_set[:3])}{'...' if len(label_set) > 3 else ''}")
