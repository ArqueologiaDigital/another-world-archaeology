#!/usr/bin/env python3
"""Sync semantic renames from ALL `_unified/<stage>/*.inc` chunks
into per-branch `<branch>/<STAGE>.asm` sources.

Existing `tools/sync_stage_renames.py` only reads `<arm>*.inc`
chunks (per-arm fold chunks). LAKE and INTRO use chapter-style
chunks (no arm prefix) — those weren't being picked up.

This tool reads every chunk in the stage directory, collects named
routines, and for each per-branch source's `LABEL_<HEX>` tries to
match by abstracted body against any of the unified named routines.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC_ROOT = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
LEVELS = SRC_ROOT / "src/levels"

ARM_TO_BRANCH = {
    "cart": "cartridge_1992",
    "dos": "dos_1992",
    "amiga": "chahi_amiga_1991",
    "gba": "gba_2004",
}


def parse_routines(text: str):
    lines = text.splitlines()
    cur = None
    cur_body: list[str] = []
    for ln in lines:
        m = re.match(r"^([A-Za-z_][A-Za-z_0-9]*):$", ln)
        if m:
            if cur is not None:
                yield cur, cur_body
            cur = m.group(1)
            cur_body = []
            continue
        if cur is not None:
            if ln.strip().startswith(";@"):
                continue
            cur_body.append(ln)
    if cur is not None:
        yield cur, cur_body


def abstracted_body(body: list[str]) -> str:
    out = []
    for ln in body:
        s = re.sub(r";@raw=[^;]*$", "", ln).rstrip()
        if not s.strip():
            continue
        s = re.sub(r"\b(LABEL_[0-9A-Fa-f]+|JUNK__[0-9A-Fa-f]+)\b", "_LABEL_", s)
        out.append(s.strip())
    return "\n".join(out)


def sync_stage(stage: str) -> dict[str, int]:
    """Returns {branch: rename_count}."""
    stage_dir = LEVELS / "_unified" / stage.lower()
    if not stage_dir.is_dir():
        return {}

    # Collect all named routines across all chunks (no arm filter).
    chunk_text = "\n".join(c.read_text() for c in sorted(stage_dir.glob("*.inc")))
    unified_bodies: dict[str, str] = {}  # abstracted body → name
    for label, body in parse_routines(chunk_text):
        if (label.startswith("LABEL_") or label.startswith("JUNK_")
                or label.startswith("FOLD_BODY_") or label.startswith("DEDUP_")):
            continue
        sym = abstracted_body(body)
        if sym:
            # First-seen wins; if multiple chunks define the same body,
            # keep the first.
            unified_bodies.setdefault(sym, label)

    # Also include the .asm.in's body-defined routines (folded bodies
    # live in the .asm.in itself).
    asm_in = LEVELS / "_unified" / f"{stage}.asm.in"
    if asm_in.is_file():
        for label, body in parse_routines(asm_in.read_text()):
            if (label.startswith("LABEL_") or label.startswith("JUNK_")
                    or label.startswith("FOLD_BODY_") or label.startswith("DEDUP_")):
                continue
            sym = abstracted_body(body)
            if sym:
                unified_bodies.setdefault(sym, label)

    counts = {}
    for arm, branch in ARM_TO_BRANCH.items():
        target = LEVELS / branch / f"{stage}.asm"
        if not target.is_file():
            continue
        text = target.read_text()
        renames: dict[str, str] = {}
        used: set[str] = set()
        for m in re.finditer(r"^([A-Z_][A-Z_0-9]+):", text, re.M):
            used.add(m.group(1))
        # Track abstracted-body signatures we've already mapped within
        # this file. If two LABEL_<HEX> labels have the same abstracted
        # body, only the FIRST gets renamed — otherwise we'd produce
        # duplicate label definitions and the assembler would silently
        # resolve calls to the wrong address.
        per_file_taken_targets: set[str] = set()
        for label, body in parse_routines(text):
            if not label.startswith("LABEL_"):
                continue
            sym = abstracted_body(body)
            if not sym or sym not in unified_bodies:
                continue
            new_name = unified_bodies[sym]
            if new_name in used:
                continue
            if new_name in per_file_taken_targets:
                continue
            renames[label] = new_name
            per_file_taken_targets.add(new_name)

        if not renames:
            counts[branch] = 0
            continue

        new_text = text
        for old, new in renames.items():
            new_text = re.sub(rf"\b{re.escape(old)}\b", new, new_text)
        target.write_text(new_text)
        counts[branch] = len(renames)
        print(f"  {arm} → {branch}: {len(renames)} applied")
    return counts


def main() -> int:
    stages = ["INTRO", "LAKE", "PRISON", "CAVES", "CAPSULE",
              "TANK", "ENDING", "PASSCODE", "CODE_WHEEL"]
    if len(sys.argv) > 1:
        stages = [s.upper() for s in sys.argv[1:]]
    total = 0
    for stage in stages:
        print(f"=== {stage} ===")
        counts = sync_stage(stage)
        total += sum(counts.values())
    print(f"\nTotal: {total} renames applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
