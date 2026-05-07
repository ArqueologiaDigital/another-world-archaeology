#!/usr/bin/env python3
"""Scan a port's full disassembly tree for asset references — `video`,
`playSound`, `song`, `setPalette` opcodes — and emit per-asset-type
reference sets.

Inputs: a path to `<output>/disasm/`, which contains one directory per
level (e.g. `level_0/`, `level_1/`, …), each holding a `*_level-N.asm`
file emitted by AWVM_Tools' awvm-disasm.

Outputs:
- `references.json` per port: a structured map
    {
      "video": { 1: [list of offsets used with `video type=1, offset=X`] },
      "playSound": [list of sound IDs],
      "song": [list of song IDs],
      "setPalette": {
        "literal": [list of palette indices],
        "variable": int,  # count of `setPalette [varN]` (indeterminate at static analysis)
      },
    }
- A per-level breakdown so #0058 (reachability) can subset references
  by which label they're emitted from.

Usage:
    python3 tools/asset_references.py tmp/output/amiga/disasm \\
        --json-out tmp/amiga_refs.json
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

# Pattern for `video type=N, offset=LABEL_OR_HEX` — captures both forms.
RE_VIDEO = re.compile(
    r"video\s+type=(?P<type>\d+),\s*offset=(?P<offset>[A-Z][A-Z_0-9]*|0x[0-9A-Fa-f]+)"
)

# `play id=N, freq=…, vol=…, channel=…`  (the AW VM SOUND-playing opcode)
RE_PLAYSOUND = re.compile(r"\bplay\s+id=(?P<id>0x[0-9A-Fa-f]+|\d+)")

# `song id=N, ...`
RE_SONG = re.compile(r"\bsong\s+id=(?P<id>0x[0-9A-Fa-f]+|\d+)")

# `setPalette N` — argument can be literal or [var]; the line may have a
# trailing `;@raw=…` comment so we use a word-boundary match.
RE_SETPALETTE_LITERAL = re.compile(r"\bsetPalette\s+(?P<id>0x[0-9A-Fa-f]+|\d+)\b")
RE_SETPALETTE_VAR = re.compile(r"\bsetPalette\s+\[(?P<var>0x[0-9A-Fa-f]+|\d+)\]")

# EQU label resolution:  `LABEL_NAME    EQU 0xOFFSET`
RE_EQU = re.compile(r"^(?P<name>[A-Z][A-Z_0-9]*)\s+EQU\s+(?P<value>0x[0-9A-Fa-f]+)")

# Source label tracking — start of a label's region.
RE_LABEL_START = re.compile(r"^(?P<name>[A-Z][A-Z_0-9]*):\s*$")


def parse_int(s: str) -> int:
    return int(s, 0)


def scan_one_disasm(asm_path: Path) -> dict:
    """Scan a single .asm file. Returns a structured reference dict.

    Each reference entry includes the surrounding label so a downstream
    reachability filter (issue #0058) can mark it live or dead.
    """
    text = asm_path.read_text()
    lines = text.splitlines()

    # Pass 1: build EQU table (label name → offset).
    equs: dict[str, int] = {}
    for line in lines:
        m = RE_EQU.match(line)
        if m:
            equs[m.group("name")] = parse_int(m.group("value"))

    # Pass 2: scan instructions, tracking the surrounding label.
    video_refs: dict[int, list[dict]] = defaultdict(list)
    playsound: list[dict] = []
    song: list[dict] = []
    setpal_literal: list[dict] = []
    setpal_var = 0
    cur_label: str | None = None

    for line_no, line in enumerate(lines, start=1):
        m_label = RE_LABEL_START.match(line)
        if m_label:
            cur_label = m_label.group("name")
            continue

        m = RE_VIDEO.search(line)
        if m:
            ty = int(m.group("type"))
            off_str = m.group("offset")
            if off_str.startswith("0x"):
                offset = parse_int(off_str)
            else:
                offset = equs.get(off_str)
                if offset is None:
                    # Skip unresolved labels (shouldn't happen if disasm is consistent)
                    continue
            video_refs[ty].append({
                "offset": offset,
                "label": off_str if not off_str.startswith("0x") else None,
                "line": line_no,
                "in_label": cur_label,
            })

        m = RE_PLAYSOUND.search(line)
        if m:
            playsound.append({
                "id": parse_int(m.group("id")),
                "line": line_no,
                "in_label": cur_label,
            })

        m = RE_SONG.search(line)
        if m:
            song.append({
                "id": parse_int(m.group("id")),
                "line": line_no,
                "in_label": cur_label,
            })

        m = RE_SETPALETTE_LITERAL.search(line)
        if m:
            setpal_literal.append({
                "id": parse_int(m.group("id")),
                "line": line_no,
                "in_label": cur_label,
            })
        else:
            m = RE_SETPALETTE_VAR.search(line)
            if m:
                setpal_var += 1

    return {
        "asm": str(asm_path),
        "equ_count": len(equs),
        "video": {ty: refs for ty, refs in video_refs.items()},
        "playSound": playsound,
        "song": song,
        "setPalette": {"literal": setpal_literal, "variable_count": setpal_var},
    }


def aggregate_refs(per_level: dict[int, dict]) -> dict:
    """Merge per-level references into port-wide sets.

    Returns:
      {
        "video": { type: { offset: [ {level, label, line}, ... ] } },
        "playSound": { id: [ {level, label, line} ... ] },
        "song": { id: [...] },
        "setPalette": { id: [...], "variable_count": N },
      }
    """
    video = defaultdict(lambda: defaultdict(list))
    playsound = defaultdict(list)
    song = defaultdict(list)
    setpal = defaultdict(list)
    setpal_var = 0

    for lv, lvdata in per_level.items():
        for ty, refs in lvdata["video"].items():
            for r in refs:
                video[ty][r["offset"]].append({
                    "level": lv,
                    "label": r.get("label"),
                    "line": r["line"],
                    "in_label": r.get("in_label"),
                })
        for r in lvdata["playSound"]:
            playsound[r["id"]].append({"level": lv, "line": r["line"], "in_label": r.get("in_label")})
        for r in lvdata["song"]:
            song[r["id"]].append({"level": lv, "line": r["line"], "in_label": r.get("in_label")})
        for r in lvdata["setPalette"]["literal"]:
            setpal[r["id"]].append({"level": lv, "line": r["line"], "in_label": r.get("in_label")})
        setpal_var += lvdata["setPalette"]["variable_count"]

    return {
        "video": {ty: dict(d) for ty, d in video.items()},
        "playSound": dict(playsound),
        "song": dict(song),
        "setPalette": {"literal": dict(setpal), "variable_count": setpal_var},
    }


def find_disasm_files(disasm_root: Path) -> dict[int, Path]:
    """Scan a `disasm/` directory for `level_N/<port>_level-N.asm` files."""
    out = {}
    for level_dir in sorted(disasm_root.glob("level_*")):
        if not level_dir.is_dir():
            continue
        try:
            lv = int(level_dir.name.removeprefix("level_"))
        except ValueError:
            continue
        asm = list(level_dir.glob("*.asm"))
        if not asm:
            continue
        if len(asm) > 1:
            print(f"warning: multiple .asm files in {level_dir}, picking {asm[0]}")
        out[lv] = asm[0]
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("disasm_root", type=Path,
                   help="path to <output>/disasm/ (the dir holding level_N/ subdirs)")
    p.add_argument("--json-out", type=Path, help="emit aggregated references as JSON")
    p.add_argument("--summary", action="store_true", help="print summary only")
    args = p.parse_args()

    asms = find_disasm_files(args.disasm_root)
    print(f"found {len(asms)} level disasm file(s) under {args.disasm_root}")

    per_level = {}
    for lv, asm_path in sorted(asms.items()):
        print(f"  scanning level_{lv}: {asm_path.name}")
        per_level[lv] = scan_one_disasm(asm_path)

    agg = aggregate_refs(per_level)

    print("\naggregate reference counts (across all levels):")
    for ty, by_offset in agg["video"].items():
        print(f"  video type={ty}: {len(by_offset)} unique offsets, "
              f"{sum(len(v) for v in by_offset.values())} total references")
    print(f"  playSound: {len(agg['playSound'])} unique IDs, "
          f"{sum(len(v) for v in agg['playSound'].values())} total references")
    print(f"  song:      {len(agg['song'])} unique IDs, "
          f"{sum(len(v) for v in agg['song'].values())} total references")
    print(f"  setPalette literal: {len(agg['setPalette']['literal'])} unique indices, "
          f"{sum(len(v) for v in agg['setPalette']['literal'].values())} total references")
    print(f"  setPalette variable: {agg['setPalette']['variable_count']} dynamic-index calls")

    if args.json_out:
        # Convert int keys to str for JSON.
        def _stringify(d):
            if isinstance(d, dict):
                return {str(k): _stringify(v) for k, v in d.items()}
            if isinstance(d, list):
                return [_stringify(x) for x in d]
            return d

        out = {
            "disasm_root": str(args.disasm_root),
            "per_level": _stringify(per_level),
            "aggregate": _stringify(agg),
        }
        args.json_out.write_text(json.dumps(out, indent=2))
        print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
