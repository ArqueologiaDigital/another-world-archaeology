#!/usr/bin/env python3
"""Strip unused EQU declarations from .asm files.

For each input file:
  1. Collect EQU declarations: NAME EQU 0xVALUE (or similar).
  2. Walk the rest of the file, find all identifier references in
     instruction operands.
  3. Drop EQU declarations whose name is never referenced.
  4. Verify byte-equivalence after.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from awvm_preprocess import expand_fill_macros

from _paths import AWVM_ASM


# An EQU line: <NAME>\t\tEQU 0xVALUE  or  <NAME> EQU <expr>
RE_EQU = re.compile(r'^\s*([A-Z_][A-Z_0-9]*)\s+EQU\s+', re.M)


def assemble(text):
    text = expand_fill_macros(text)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        local = td / "test.asm"
        local.write_text(text)
        try:
            subprocess.run([str(AWVM_ASM), local.name], cwd=td,
                           check=True, capture_output=True, text=True)
            return local.with_suffix(".bin").read_bytes()
        except subprocess.CalledProcessError:
            return None


def find_references(text):
    """Find all UPPERCASE_IDENTIFIER references in the file (excluding EQU declarations)."""
    refs = set()
    for line in text.splitlines():
        # Skip EQU declaration lines (their LHS doesn't count as a reference)
        m = re.match(r'^\s*([A-Z_][A-Z_0-9]*)\s+EQU\s+', line)
        if m:
            # Look at the RHS of the EQU for references
            after_equ = line[m.end():]
            for ref in re.finditer(r'\b([A-Z_][A-Z_0-9]+)\b', after_equ):
                refs.add(ref.group(1))
            continue
        # Skip comment lines
        if line.lstrip().startswith(';'):
            continue
        # Find all UPPER_CASE identifiers
        for ref in re.finditer(r'\b([A-Z_][A-Z_0-9]+)\b', line):
            refs.add(ref.group(1))
    return refs


def strip_unused(text):
    refs = find_references(text)
    
    # For each EQU line, check if its name is referenced
    new_lines = []
    stripped = 0
    kept = 0
    for line in text.splitlines():
        m = re.match(r'^\s*([A-Z_][A-Z_0-9]*)\s+EQU\s+', line)
        if m:
            name = m.group(1)
            if name in refs:
                new_lines.append(line)
                kept += 1
            else:
                stripped += 1
                continue
        else:
            new_lines.append(line)
    
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
        p = Path(arg)
        text = p.read_text()
        orig_bytes = assemble(text)
        if orig_bytes is None:
            print(f"  {arg}: FAIL-ASM original", file=sys.stderr)
            continue
        new_text, s, k = strip_unused(text)
        new_bytes = assemble(new_text)
        if new_bytes != orig_bytes:
            print(f"  {arg}: bytes differ — skipping", file=sys.stderr)
            continue
        p.write_text(new_text)
        total_stripped += s
        total_kept += k
        print(f"  {p.name}: stripped {s} EQUs, kept {k}", file=sys.stderr)
    
    print(f"\nTOTAL: stripped {total_stripped}, kept {total_kept}", file=sys.stderr)


if __name__ == '__main__':
    main()
