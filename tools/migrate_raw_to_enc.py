#!/usr/bin/env python3
"""Rewrite `;@raw=…` annotations as `;@enc=…` (or as explicit
`_trailing=…` operands on `setPalette`).

Three patterns currently catalogued:

1. video … zoom=[var] with first byte in {0x55, 0x56, 0x5A, 0x66,
   0x6A, 0x7A} and (first_byte & 0x03) == 0x02
        → `;@raw=…` replaced by `;@enc=alt`

2. bankSwitch with bytes [0x19, 0x07, 0xDx]
        → `;@raw=…` replaced by `;@enc=legacy_d`

3. bankSwitch with bytes [0x19, 0x07, 0xEx]
        → `;@raw=…` replaced by `;@enc=legacy_e`

4. setPalette … with bytes [0x0B, IDX, 0x00] (canonical trails 0xFF)
        → `;@raw=…` replaced by inserting `, _trailing=0x00` operand,
          before the optional comment.

Annotations that don't match any of the above are LEFT IN PLACE.
Run `audit_raw_annotations.py` afterwards to surface the residue.

Usage:
  python3 tools/migrate_raw_to_enc.py [--dry-run] [path...]

If no paths given, processes every `.asm` and `.inc` file under
the source-reconstruction tree.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SRC_ROOT = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
RE_RAW = re.compile(r"(?P<lead>\s*);@raw=(?P<bytes>[0-9a-fA-FxX,\s]+)\s*$")

# Video opcodes we recognize as the bit-1 zoom-as-var alt encoding.
ALT_VIDEO_OPCODES = {0x55, 0x56, 0x5A, 0x66, 0x6A, 0x7A}


def parse_bytes(s: str) -> list[int] | None:
    out: list[int] = []
    for tok in s.split(","):
        tok = tok.strip()
        if not tok:
            continue
        try:
            if tok.startswith(("0x", "0X")):
                out.append(int(tok, 16))
            else:
                out.append(int(tok))
        except ValueError:
            return None
    return out


def migrate_line(line: str) -> tuple[str, str | None]:
    """Return (new_line, pattern_applied_or_None)."""
    m = RE_RAW.search(line)
    if not m:
        return line, None
    raw = parse_bytes(m.group("bytes"))
    if not raw:
        return line, None

    instr_text = line[: m.start()].rstrip()
    lead = m.group("lead") or ""
    trailing_nl = "\n" if line.endswith("\n") else ""

    # Pattern 1: video alt zoom-as-var
    if (
        raw
        and raw[0] in ALT_VIDEO_OPCODES
        and (raw[0] & 0x03) == 0x02
        and "video" in instr_text
        and "zoom=[" in instr_text
    ):
        return (
            f"{instr_text}\t;@enc=alt{trailing_nl}",
            "alt",
        )

    # Pattern 2 & 3: bankSwitch legacy operand word
    if (
        len(raw) >= 3
        and raw[0] == 0x19
        and "bankSwitch" in instr_text
    ):
        word = (raw[1] << 8) | raw[2]
        if (word & 0xFFF0) == 0x07D0:
            return (
                f"{instr_text}\t;@enc=legacy_d{trailing_nl}",
                "legacy_d",
            )
        if (word & 0xFFF0) == 0x07E0:
            return (
                f"{instr_text}\t;@enc=legacy_e{trailing_nl}",
                "legacy_e",
            )

    # Pattern 4: setPalette with trailing-zero waste byte. The
    # source line is `setPalette 0xNN[\t; comment]\t;@raw=...`. We
    # need to insert `, _trailing=0x00` after the palette index and
    # before any inline comment. Easiest: split instruction text at
    # the first `;` (any preceding inline comment is preserved as a
    # post-fix). But the existing source rarely has inline comments
    # between mnemonic and `;@raw=`, so we just append the operand.
    if (
        len(raw) >= 3
        and raw[0] == 0x0B
        and raw[2] == 0x00
        and "setPalette" in instr_text
    ):
        # Append the keyword operand. parse_common splits on ',' so
        # `setPalette 0x00, _trailing=0x00` parses cleanly.
        return (
            f"{instr_text}, _trailing=0x00{trailing_nl}",
            "setpal_trailing",
        )

    return line, None


def process_file(path: Path, dry_run: bool) -> dict[str, int]:
    counts: dict[str, int] = {}
    out_lines: list[str] = []
    changed = False
    for line in path.read_text().splitlines(keepends=True):
        new_line, applied = migrate_line(line)
        if applied is not None:
            counts[applied] = counts.get(applied, 0) + 1
            changed = True
        out_lines.append(new_line)
    if changed and not dry_run:
        path.write_text("".join(out_lines))
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()

    if args.paths:
        targets: list[Path] = []
        for p in args.paths:
            if p.is_file():
                targets.append(p)
            elif p.is_dir():
                targets.extend(sorted(p.rglob("*.asm")))
                targets.extend(sorted(p.rglob("*.inc")))
    else:
        levels = SRC_ROOT / "src" / "levels"
        targets = sorted(levels.rglob("*.asm")) + sorted(
            levels.rglob("*.inc")
        )

    aggregate: dict[str, int] = {}
    files_changed = 0
    for path in targets:
        counts = process_file(path, args.dry_run)
        if counts:
            files_changed += 1
            for k, v in counts.items():
                aggregate[k] = aggregate.get(k, 0) + v

    print(f"files changed: {files_changed}")
    for k, v in sorted(aggregate.items()):
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
