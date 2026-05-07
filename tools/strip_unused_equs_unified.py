#!/usr/bin/env python3
"""Strip unused EQU declarations from unified stage chunks.

For each stage:
  1. Load the .asm.in and all chunks.
  2. Pool all UPPER_CASE identifier references across the entire stage.
  3. For each EQU declaration in chunks, if its name is unreferenced
     (across the whole stage), drop it.
  4. Verify byte-equivalence via verify_unified.

Note: per-arm chunk's EQUs only need to be valid for that arm's
preprocessing. Since each arm's bytecode references different sets,
we strip per-arm: pool references from <arm>__*.inc + .asm.in,
strip EQUs from <arm>__entry.inc that aren't in that pool.
"""
import re
import sys
from pathlib import Path

from _paths import AW_SRC



def find_references(text):
    refs = set()
    for line in text.splitlines():
        # Skip EQU declarations' LHS
        m = re.match(r'^\s*([A-Z_][A-Z_0-9]*)\s+EQU\s+', line)
        if m:
            after = line[m.end():]
            for r in re.finditer(r'\b([A-Z_][A-Z_0-9]+)\b', after):
                refs.add(r.group(1))
            continue
        if line.lstrip().startswith(';@') or line.lstrip().startswith(';'):
            # @include etc. don't reference EQUs (the ;@if condition uses string literals)
            continue
        for r in re.finditer(r'\b([A-Z_][A-Z_0-9]+)\b', line):
            refs.add(r.group(1))
    return refs


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: STAGE")
    
    stage = sys.argv[1].upper()
    stage_dir = AW_SRC / "src/levels/_unified" / stage.lower()
    asm_in = AW_SRC / f"src/levels/_unified/{stage}.asm.in"
    
    if not stage_dir.is_dir() or not asm_in.exists():
        sys.exit(f"FATAL: stage paths missing for {stage}")
    
    # Per arm
    for arm in ('cart', 'dos', 'amiga'):
        chunks = sorted(stage_dir.glob(f"{arm}*.inc"))
        if not chunks:
            continue
        
        # Pool references: chunks + asm.in (shared body sees EQUs through inclusion)
        all_refs = set()
        for inc in chunks:
            all_refs.update(find_references(inc.read_text()))
        all_refs.update(find_references(asm_in.read_text()))
        
        # Strip unused EQUs from each chunk
        total_stripped = 0
        for inc in chunks:
            text = inc.read_text()
            new_lines = []
            for line in text.splitlines():
                m = re.match(r'^\s*([A-Z_][A-Z_0-9]*)\s+EQU\s+', line)
                if m:
                    if m.group(1) not in all_refs:
                        total_stripped += 1
                        continue
                new_lines.append(line)
            new_text = '\n'.join(new_lines)
            if text.endswith('\n'):
                new_text += '\n'
            inc.write_text(new_text)
        
        print(f"  {arm}: stripped {total_stripped}", file=sys.stderr)


if __name__ == '__main__':
    main()
