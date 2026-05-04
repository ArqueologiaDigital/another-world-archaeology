#!/usr/bin/env python3
"""Compress trailing runs of 'db 0xFF, ...' into FILL(n, 0xFF) macros.

The disassembler emits 8 bytes per line for unreached/padding bytes.
Trailing runs at the end of bytecode chunks can be hundreds or
thousands of lines. The FILL macro packs them into a single line.

Usage:
    python3 tools/compress_fill_padding.py FILE...

verify_stage's expand_fill_macros() expands FILL(n, 0xFF) to exactly
n bytes worth of db directives, so the byte output is identical.
"""
import re
import sys
from pathlib import Path

DB_LINE = re.compile(r'^(\s+)db\s+((?:0x[0-9A-Fa-f]+(?:,\s*)?)+)\s*$')


def compress_runs(text):
    """Replace runs of repeated `db <byte>, <byte>...` lines with FILL.

    Looks for consecutive lines that are JUST db directives with the same
    byte value, all of them. Collapses them into FILL(n, 0xXX).
    """
    lines = text.splitlines()
    out = []
    i = 0
    while i < len(lines):
        # Try to detect a run of db lines with the same byte value
        m = DB_LINE.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        
        # Parse bytes from this line
        bytes_in_line = [b.strip() for b in m.group(2).split(',')]
        if not bytes_in_line:
            out.append(lines[i])
            i += 1
            continue
        
        # All bytes in line must be the same value
        first_byte = bytes_in_line[0]
        if not all(b == first_byte for b in bytes_in_line):
            out.append(lines[i])
            i += 1
            continue
        
        indent = m.group(1)
        # Count consecutive lines with same byte value
        run_start = i
        run_bytes = 0
        while i < len(lines):
            mm = DB_LINE.match(lines[i])
            if not mm:
                break
            ll_bytes = [b.strip() for b in mm.group(2).split(',')]
            if not all(b == first_byte for b in ll_bytes):
                break
            run_bytes += len(ll_bytes)
            i += 1
        
        # If run is short, don't compress (4+ lines = 32+ bytes minimum)
        if i - run_start < 4:
            for j in range(run_start, i):
                out.append(lines[j])
            continue
        
        out.append(f"{indent}FILL({run_bytes}, {first_byte})")
    
    new_text = '\n'.join(out)
    if text.endswith('\n'):
        new_text += '\n'
    return new_text


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: FILE...")
    
    total_lines_removed = 0
    for arg in sys.argv[1:]:
        p = Path(arg)
        text = p.read_text()
        new_text = compress_runs(text)
        old_lines = text.count('\n')
        new_lines = new_text.count('\n')
        removed = old_lines - new_lines
        if removed > 0:
            p.write_text(new_text)
            print(f"  {p.name}: removed {removed} lines", file=sys.stderr)
            total_lines_removed += removed
    
    print(f"\nTOTAL: {total_lines_removed} lines removed", file=sys.stderr)


if __name__ == '__main__':
    main()
