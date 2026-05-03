#!/usr/bin/env python3
"""Find labels with body = single 'ret' or 'killChannel'.
For each, report the most-referenced one in each arm.

Usage: python3 /tmp/find_singletons.py STAGE
"""
import os, re, sys
from pathlib import Path

if len(sys.argv) != 2:
    sys.exit(__doc__)

STAGE = sys.argv[1].lower()
AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")
STAGE_DIR = AW_SRC / "src/levels/_unified" / STAGE

for arm_inc in sorted(STAGE_DIR.glob("*.inc")):
    arm = arm_inc.stem
    text = arm_inc.read_text()
    lines = text.split('\n')

    ret_only = []
    kill_only = []
    cur_label = None
    cur_body = []
    for ln in lines:
        m = re.match(r'^([A-Z_][A-Z_0-9]*):$', ln)
        if m:
            if cur_label and len(cur_body) == 1 and cur_label.startswith("LABEL_"):
                first = cur_body[0].strip()
                if first.startswith('ret'):
                    ret_only.append(cur_label)
                elif first.startswith('killChannel'):
                    kill_only.append(cur_label)
            cur_label = m.group(1)
            cur_body = []
        elif cur_label is not None and ln.strip():
            cur_body.append(ln)

    for kind, lst in [('ret', ret_only), ('kill', kill_only)]:
        if not lst:
            continue
        counts = sorted([(len(re.findall(r'\b' + L + r'\b', text)), L) for L in lst], reverse=True)
        top_count, top_label = counts[0]
        if top_count >= 5:  # only useful if highly referenced
            target = "SHARED_RET" if kind == "ret" else "KILL_CHANNEL_LANDING"
            print(f"{arm}\t{top_label}\t{target}\t{top_count}refs")
