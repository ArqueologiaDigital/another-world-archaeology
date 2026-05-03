#!/usr/bin/env python3
"""Unify names across stages for routines with identical bodies."""
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
            j = i + 1
            while j < len(lines):
                if lines[j].strip().startswith(';@'):
                    break
                if re.match(r'^[A-Za-z_][A-Za-z_0-9]*:$', lines[j]):
                    break
                body.append(lines[j])
                j += 1
            sym_body = []
            for ln in body:
                s = re.sub(r';@raw=[^;]*$', '', ln).rstrip()
                if s.strip():
                    sym_body.append(s)
            body_str = '\n'.join(sym_body)
            if body_str:
                h = hashlib.sha1(body_str.encode()).hexdigest()
                groups[h].append((stage, label))
        i += 1

# For each group with 2+ stages, pick canonical name
def quality_score(name):
    """Higher = better name. Generic names get low scores."""
    if name.startswith('FOLD_BODY_'): return 0
    if name.startswith('DEDUP_'): return 1
    if name.startswith('JUNK_'): return 2
    if name.startswith('LABEL_'): return 3
    if name.startswith('INLINE_'): return 5  # auto-named, slightly better
    return 10  # other semantic names

renames_per_stage = defaultdict(dict)  # stage -> {old: new}
unified_count = 0

for h, labels in groups.items():
    stages_in_group = {s for s, _ in labels}
    if len(stages_in_group) < 2:
        continue
    # Pick canonical
    sorted_labels = sorted(labels, key=lambda x: (-quality_score(x[1]), x[1]))
    canonical = sorted_labels[0][1]
    # Rename all others to canonical
    for stage, label in labels:
        if label != canonical:
            renames_per_stage[stage][label] = canonical
            unified_count += 1

# Apply
def rename(stage, old, new):
    stage_dir = AW_SRC / "src/levels/_unified" / stage.lower()
    for inc in stage_dir.glob("*.inc"):
        text = inc.read_text()
        if old in text:
            new_text = re.sub(rf'\b{old}\b', new, text)
            if new_text != text:
                inc.write_text(new_text)
    p = AW_SRC / f"src/levels/_unified/{stage}.asm.in"
    text = p.read_text()
    if old in text:
        new_text = re.sub(rf'\b{old}\b', new, text)
        if new_text != text:
            p.write_text(new_text)

print(f"Unifying {unified_count} cross-stage names")
for stage, mapping in renames_per_stage.items():
    if mapping:
        for old, new in mapping.items():
            rename(stage, old, new)
        print(f"  {stage}: {len(mapping)} renames")
