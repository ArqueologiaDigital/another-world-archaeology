#!/usr/bin/env python3
"""Strip redundant ;@raw= comments from .asm files.

Keeps ;@raw= on opcodes where awvm-asm cannot recompute bytes from
the symbolic form alone:
  - bankSwitch — needs the file-offset bytes (e.g., 0x07,0xD1 for
    bank 1 = Prison)
  - video — encoding ambiguity (multiple valid byte sequences for
    the same logical instruction depending on x/y operand size)
  - setPalette — palette ID encoding requires the @raw bytes

For all other opcodes, the assembler produces identical bytes when
@raw is absent, so the comment is redundant.

Usage:
    python3 tools/strip_redundant_raw.py <file.asm>...
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from awvm_preprocess import expand_fill_macros

AWVM_ASM = Path("/home/fsanches/compartilhado/AnotherWorld_VMTools/target/release/awvm-asm")

KEEP_PATTERN = re.compile(r'^\s*(bankSwitch|video|setPalette)\b')


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
        orig_bytes = assemble(text)
        if orig_bytes is None:
            print(f"  {arg}: FAIL-ASM original", file=sys.stderr)
            continue
        new_text, stripped, kept = strip(text)
        new_bytes = assemble(new_text)
        if new_bytes != orig_bytes:
            print(f"  {arg}: bytes differ — keepers insufficient, skipping", file=sys.stderr)
            continue
        filepath.write_text(new_text)
        total_stripped += stripped
        total_kept += kept
        print(f"  {filepath.name}: stripped {stripped}, kept {kept}", file=sys.stderr)
    
    print(f"\nTOTAL: stripped {total_stripped}, kept {total_kept}", file=sys.stderr)


if __name__ == '__main__':
    main()
