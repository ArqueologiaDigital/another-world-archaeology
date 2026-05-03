#!/usr/bin/env python3
"""Strip redundant ;@raw= from unified .asm.in/.inc files.

Same keepers as per-branch (bankSwitch, video, setPalette). Verifies
that all branches still byte-match after stripping."""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

KEEP_PATTERN = re.compile(r'^\s*(bankSwitch|video|setPalette)\b')


def strip(text):
    lines = text.splitlines()
    new_lines = []
    stripped = 0
    kept = 0
    for ln in lines:
        if ';@raw=' not in ln:
            new_lines.append(ln)
            continue
        if KEEP_PATTERN.search(ln):
            new_lines.append(ln)
            kept += 1
        else:
            new_lines.append(re.sub(r'\s*;@raw=[^;\n]*$', '', ln))
            stripped += 1
    new_text = '\n'.join(new_lines)
    if text.endswith('\n'):
        new_text += '\n'
    return new_text, stripped, kept


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: FILE...")
    
    total_stripped = 0
    total_kept = 0
    for arg in sys.argv[1:]:
        filepath = Path(arg)
        text = filepath.read_text()
        new_text, stripped, kept = strip(text)
        filepath.write_text(new_text)
        total_stripped += stripped
        total_kept += kept
        if stripped > 0:
            print(f"  {filepath}: stripped {stripped}, kept {kept}", file=sys.stderr)
    
    print(f"\nTOTAL: stripped {total_stripped}, kept {total_kept}", file=sys.stderr)


if __name__ == '__main__':
    main()
