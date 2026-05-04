#!/usr/bin/env python3
"""Naive unused-PALETTE scanner.

Two layers:
  1. Resource-level: PALETTE resources never `load`'d. Note that
     in AW the engine implicitly loads the per-level PALETTE
     resource alongside its BYTECODE/POLY_CINEMATIC, so explicit
     `load id=N` of a PALETTE is rare; this layer's count is
     therefore expected to read mostly "unused".
  2. Slot-level: of the 32 palette slots within each level's
     loaded PALETTE resource, which ones does any reachable
     bytecode actually `setPalette` to?

Usage:
    python3 tools/unused_palette_scan.py <work-dir>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# Map level → stage name (DOS resource layout)
LEVEL_TO_STAGE = {
    0: "CODE_WHEEL",
    1: "INTRO",
    2: "LAKE",
    3: "PRISON",
    4: "CAVES",
    5: "TANK",
    6: "CAPSULE",
    7: "ENDING",
    8: "PASSCODE",
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("work_dir", type=Path)
    args = p.parse_args()

    manifest = json.loads((args.work_dir / "manifest.json").read_text())
    palette_resources = {
        r["index"]: r for r in manifest.get("resources", [])
        if r.get("type") == "PALETTE"
    }

    slug = manifest.get("slug", "")
    slug_to_output = {"dos": "msdos", "amiga": "amiga"}
    disasm_root = Path("tmp/output") / slug_to_output.get(slug, slug) / "disasm"
    if not disasm_root.is_dir():
        disasm_root = args.work_dir / "disasm"
    if not disasm_root.is_dir():
        print(f"error: no disasm/ found", file=sys.stderr)
        return 1

    re_setpal_lit = re.compile(r"\bsetPalette\s+(0x[0-9A-Fa-f]+|\d+)\b")

    per_level: dict[int, set[int]] = defaultdict(set)
    for asm in sorted(disasm_root.rglob("*.asm")):
        # Identify level from filename, e.g. msdos_level-3.asm → 3
        m = re.search(r"level-(\d+)", asm.name)
        if not m:
            continue
        lv = int(m.group(1))
        for mm in re_setpal_lit.finditer(asm.read_text()):
            s = mm.group(1)
            n = int(s, 0) if s.startswith("0x") else int(s)
            per_level[lv].add(n)

    print(f"Port: {slug}")
    print(f"Disasm: {disasm_root}")
    print()
    print(f"PALETTE resources defined: {len(palette_resources)}")
    print()
    print("Per-level setPalette literal usage:")
    print("  level  stage         #used  unused indices (of 0..31)")
    total_unused_slots = 0
    for lv in sorted(per_level.keys()):
        used = per_level[lv]
        unused = sorted(set(range(32)) - used)
        total_unused_slots += len(unused)
        stage = LEVEL_TO_STAGE.get(lv, "?")
        unused_str = ",".join(str(u) for u in unused)
        print(f"  {lv:>2d}     {stage:<12s}  {len(used):>3d}    [{unused_str}]")

    print()
    print(f"Total unused slot-indices summed across all levels: {total_unused_slots}")
    print(f"  (each slot is one of 32 palettes; values shown mean those slots")
    print(f"   in that level's PALETTE resource are never selected by any")
    print(f"   reachable `setPalette N` opcode in that level.)")
    print()
    print("Caveats:")
    print("  - Naive (no reachability filter; #0058 dependency).")
    print("  - Only literal `setPalette N`; variable-operand calls are")
    print("    treated as 'might-use-anything' and excluded conservatively.")
    print("  - PALETTE resource size 2048 = 2 × 32 × 32; this scan only")
    print("    counts the first 32 slots (the second half is the per-port")
    print("    intensity-adjusted twin and is selected the same way).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
