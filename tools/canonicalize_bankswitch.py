#!/usr/bin/env python3
"""Convert `bankSwitch N` mnemonic forms to `load id=0x<HHLL>`.

Both encode to the same 3 bytes (`0x19, hi, lo`), but `bankSwitch` has
an awvm-asm encoding bug (#0066) that requires a `;@raw=` override
to assemble correctly. `load id=...` encodes correctly without any
override. So canonicalizing to `load id=...` everywhere:
  1. Eliminates the need for `;@raw=` overrides on these lines.
  2. Unifies the two syntax styles between port-specific disasms
     that happen to use different mnemonics.

Each port's disasm chooses one mnemonic per opcode; cartridge ports
typically emit `load id=...` while Genesis-EU emits `bankSwitch N`.
After canonicalization, both branches use `load id=...`.

Usage:
    python3 tools/canonicalize_bankswitch.py <input.asm> -o <output.asm>
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# Match: leading whitespace, "bankSwitch", a number, optional inline
# comment up to a tab or EOL, then optional ;@raw= annotation.
# Capture the leading whitespace + raw-bytes for substitution.
RE_BANKSWITCH = re.compile(
    r'^(?P<indent>\s*)bankSwitch\s+\d+(?:\s*;[^\t\n]*)?(?:\s*;@raw=(?P<raw>0x[0-9A-Fa-f]{1,2},0x[0-9A-Fa-f]{1,2},0x[0-9A-Fa-f]{1,2}))?\s*$'
)


def canonicalize_line(line: str) -> str:
    """If line is a bankSwitch mnemonic, convert to `load id=0xXXXX`. Otherwise return unchanged."""
    m = RE_BANKSWITCH.match(line)
    if not m:
        return line
    raw = m.group('raw')
    if raw is None:
        # No ;@raw= to source the bytes from. We can't safely compute
        # the id without it (because we don't know what the assembler
        # would have done — the bug means the mnemonic alone gives
        # wrong bytes). Leave as-is.
        return line
    parts = [int(b, 0) for b in raw.split(',')]
    if len(parts) != 3 or parts[0] != 0x19:
        return line
    id_value = (parts[1] << 8) | parts[2]
    return f"{m.group('indent')}load id=0x{id_value:04X}"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("input", type=Path)
    p.add_argument("-o", "--output", type=Path, required=True)
    args = p.parse_args()

    src = args.input.read_text()
    out_lines = []
    n_canon = 0
    for line in src.splitlines():
        new = canonicalize_line(line)
        if new != line:
            n_canon += 1
        out_lines.append(new)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(out_lines) + "\n")
    print(f"  bankSwitch → load conversions: {n_canon}")


if __name__ == "__main__":
    main()
