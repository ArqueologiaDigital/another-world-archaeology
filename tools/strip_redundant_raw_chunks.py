#!/usr/bin/env python3
"""Strip chunks with broader keeper set."""
import re
import sys
from pathlib import Path

# Keep all instructions that may have unresolvable cross-chunk operands
KEEP = re.compile(r'^\s*(bankSwitch|video|setPalette|call|je|jne|jl|jg|jle|jge|jmp|djnz|setup|song|load)\b')

if len(sys.argv) < 2:
    sys.exit("usage: FILE...")

total_s = 0
total_k = 0
for arg in sys.argv[1:]:
    p = Path(arg)
    text = p.read_text()
    lines = text.splitlines()
    new = []
    s = 0
    k = 0
    for ln in lines:
        if ';@raw=' not in ln:
            new.append(ln)
            continue
        if KEEP.search(ln):
            new.append(ln)
            k += 1
        else:
            new.append(re.sub(r'\s*;@raw=[^;\n]*$', '', ln))
            s += 1
    nt = '\n'.join(new)
    if text.endswith('\n'):
        nt += '\n'
    p.write_text(nt)
    total_s += s
    total_k += k

print(f"stripped {total_s}, kept {total_k}", file=sys.stderr)
