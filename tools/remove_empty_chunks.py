#!/usr/bin/env python3
"""Remove empty per-arm chunk files and their corresponding ;@include
directives in the unified .asm.in.

A chunk file is considered empty if it contains only whitespace.
"""
import re
import sys
from pathlib import Path

AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: STAGE")
    
    stage = sys.argv[1].upper()
    stage_dir = AW_SRC / "src/levels/_unified" / stage.lower()
    asm_in = AW_SRC / f"src/levels/_unified/{stage}.asm.in"
    
    if not stage_dir.is_dir() or not asm_in.exists():
        sys.exit(f"FATAL: stage paths missing for {stage}")
    
    # Find empty chunks
    empty_chunks = []
    for inc in stage_dir.glob("*.inc"):
        text = inc.read_text()
        if text.strip() == '':
            empty_chunks.append(inc.name)
    
    print(f"{stage}: {len(empty_chunks)} empty chunks", file=sys.stderr)
    
    if not empty_chunks:
        return
    
    # Update .asm.in: remove ;@include directives + the surrounding ;@if/elif/endif
    text = asm_in.read_text()
    lines = text.splitlines()
    
    # Walk through, removing include directives that point to empty chunks
    # Simplified: remove the include line. If the surrounding ;@if block has no other includes, also remove the ;@if/;@endif.
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Detect ;@if BRANCH == ... block start
        if re.match(r'^;@if\b', line.strip()):
            # Collect the entire block
            block = [line]
            depth = 1
            j = i + 1
            while j < len(lines) and depth > 0:
                block.append(lines[j])
                ll = lines[j].strip()
                if re.match(r'^;@if\b', ll):
                    depth += 1
                elif ll == ';@endif':
                    depth -= 1
                j += 1
            
            # Filter out includes pointing to empty chunks
            filtered_block = []
            for bl in block:
                bm = re.match(r'\s*;@include\s+"' + stage.lower() + r'/([^"]+)"', bl)
                if bm and bm.group(1) in empty_chunks:
                    continue
                filtered_block.append(bl)
            
            # If filtered_block has only ;@if/elif/endif lines (no @include), drop the entire block
            has_content = any(re.search(r';@include|^[^;]', l.strip()) for l in filtered_block)
            if not has_content:
                # Drop block
                pass
            else:
                # Clean up dangling ;@elif blocks (those whose only content was the dropped include)
                cleaned = []
                k = 0
                while k < len(filtered_block):
                    bl = filtered_block[k]
                    # If this is ;@elif and next non-empty line is ;@endif or another ;@if/elif, drop this
                    if re.match(r'^;@elif\b', bl.strip()):
                        # peek next
                        next_significant = None
                        for lk in range(k + 1, len(filtered_block)):
                            if filtered_block[lk].strip():
                                next_significant = filtered_block[lk].strip()
                                break
                        if next_significant in (None,) or re.match(r'^;@(elif|endif)', next_significant):
                            # this elif has no body, drop
                            k += 1
                            continue
                    cleaned.append(bl)
                    k += 1
                # Similar for ;@if at start
                if cleaned and re.match(r'^;@if\b', cleaned[0].strip()):
                    next_significant = None
                    for lk in range(1, len(cleaned)):
                        if cleaned[lk].strip():
                            next_significant = cleaned[lk].strip()
                            break
                    if next_significant in (None,) or re.match(r'^;@(elif|endif)', next_significant):
                        # First if has no body — change first elif to if, or drop entire block
                        # Simpler: just emit no block
                        cleaned = []
                
                new_lines.extend(cleaned)
            
            i = j
        else:
            new_lines.append(line)
            i += 1
    
    new_text = '\n'.join(new_lines)
    if text.endswith('\n'):
        new_text += '\n'
    asm_in.write_text(new_text)
    
    # Delete the empty chunk files
    for fname in empty_chunks:
        (stage_dir / fname).unlink()
    
    print(f"  removed {len(empty_chunks)} chunks + cleaned .asm.in", file=sys.stderr)


if __name__ == '__main__':
    main()
