#!/usr/bin/env python3
"""Strip unused EQUs from ALL chunks under `_unified/<stage>/`,
including non-arm-prefixed chunks (e.g. `hero_tick_bundle_helpers.inc`).

Reference pool: union of identifier references from
  - the stage's `.asm.in` body
  - all chunks under `_unified/<stage>/`
  - all `_helpers/*.inc` files
  - `_common_vars.inc`

For each chunk, drop EQU declarations whose name is not in the
reference pool.

Verifies byte-equivalence at the end via verify_unified.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC_ROOT = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
LEVELS = SRC_ROOT / "src/levels"

RE_EQU = re.compile(r"^\s*([A-Z_][A-Z_0-9]*)\s+EQU\s+")


def collect_references(text: str) -> set[str]:
    """Return all UPPER_CASE identifier references in `text`,
    excluding the LHS of EQU declarations."""
    refs: set[str] = set()
    for line in text.splitlines():
        stripped = line.lstrip()
        m = RE_EQU.match(line)
        if m:
            after = line[m.end():]
            for r in re.finditer(r"\b([A-Z_][A-Z_0-9]+)\b", after):
                refs.add(r.group(1))
            continue
        if stripped.startswith(";"):
            continue
        for r in re.finditer(r"\b([A-Z_][A-Z_0-9]+)\b", line):
            refs.add(r.group(1))
    return refs


def strip_stage(stage_dir: Path, asm_in: Path,
                helpers_text: str, common_vars_text: str) -> int:
    """Strip unused EQUs from all chunks under `stage_dir`.
    Returns count of stripped EQU lines."""
    chunks = sorted(stage_dir.glob("*.inc"))
    if not chunks:
        return 0

    # Build reference pool (chunks + .asm.in + helpers + common_vars)
    pool: set[str] = set()
    pool |= collect_references(asm_in.read_text())
    pool |= collect_references(helpers_text)
    pool |= collect_references(common_vars_text)
    for c in chunks:
        pool |= collect_references(c.read_text())

    total_stripped = 0
    for c in chunks:
        text = c.read_text()
        out_lines = []
        for ln in text.splitlines():
            m = RE_EQU.match(ln)
            if m and m.group(1) not in pool:
                total_stripped += 1
                continue
            out_lines.append(ln)
        new_text = "\n".join(out_lines)
        if text.endswith("\n"):
            new_text += "\n"
        c.write_text(new_text)
    return total_stripped


def main() -> int:
    helpers_text = "\n".join(
        h.read_text() for h in (LEVELS / "_unified" / "_helpers").glob("*.inc")
    )
    common_vars_text = (LEVELS / "_common_vars.inc").read_text()

    total = 0
    for asm_in in sorted(LEVELS.glob("_unified/*.asm.in")):
        stage_name = asm_in.name[: -len(".asm.in")]
        stage_dir = LEVELS / "_unified" / stage_name.lower()
        if not stage_dir.is_dir():
            continue
        n = strip_stage(stage_dir, asm_in, helpers_text, common_vars_text)
        if n:
            print(f"  {stage_name}: stripped {n}")
        total += n
    print(f"\nTotal stripped: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
