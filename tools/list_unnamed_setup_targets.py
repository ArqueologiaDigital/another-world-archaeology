#!/usr/bin/env python3
"""List `LABEL_HHHH` placeholder routines that are setup-targets,
grouped by stage. These are candidates for semantic rename
rounds.

For each `LABEL_HHHH:` that's referenced from a `setup channel=N,
address=LABEL_HHHH` opcode AND whose name is still the disasm's
default placeholder, we surface:
  - the channel(s) it's set up on
  - the stage(s) its callers are in
  - the chunk file + line where the label is defined
  - the FIRST 3 lines of the routine body (a "what does it do"
    hint useful for choosing a semantic name)

Output: a Markdown working list at
`docs/unnamed_setup_targets.md` ordered by stage and channel.
The list is meant to be consumed by whoever runs the next
semantic-rename round — they'll skim, pick names that fit, and
apply via the existing rename tools.

Usage:
  python3 tools/list_unnamed_setup_targets.py
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

from _paths import AW_SRC, REPO_ROOT

SRC_TREE = AW_SRC
LEVELS = SRC_TREE / "src" / "levels"
UNIFIED = LEVELS / "_unified"

RE_SETUP = re.compile(
    r"^\s*setup\s+channel=(?P<ch>0x[0-9A-Fa-f]+|\d+)\s*,\s*"
    r"address=(?P<addr>LABEL_[0-9A-F]+)\s*$"
)
RE_LABEL_DEF = re.compile(r"^(LABEL_[0-9A-F]+):", re.MULTILINE)


def stage_of(path: Path) -> str | None:
    rel = path.relative_to(UNIFIED)
    if not rel.parts:
        return None
    first = rel.parts[0]
    if first.endswith(".asm.in"):
        return first[: -len(".asm.in")].upper()
    if first.startswith("_"):
        return None
    return first.upper()


def collect_setup_targets() -> dict[
    str, list[tuple[str, int, str]]
]:
    """name → [(stage, channel, source_loc), ...]"""
    out: dict[str, list[tuple[str, int, str]]] = defaultdict(list)
    for path in sorted(UNIFIED.rglob("*.asm.in")):
        stage = stage_of(path)
        if not stage:
            continue
        for i, line in enumerate(path.read_text().splitlines(), 1):
            m = RE_SETUP.match(line)
            if m:
                out[m.group("addr")].append(
                    (
                        stage,
                        int(m.group("ch"), 0),
                        f"{path.relative_to(SRC_TREE)}:{i}",
                    )
                )
    for path in sorted(UNIFIED.rglob("*.inc")):
        stage = stage_of(path)
        if not stage:
            continue
        for i, line in enumerate(path.read_text().splitlines(), 1):
            m = RE_SETUP.match(line)
            if m:
                out[m.group("addr")].append(
                    (
                        stage,
                        int(m.group("ch"), 0),
                        f"{path.relative_to(SRC_TREE)}:{i}",
                    )
                )
    return out


def build_label_def_index() -> dict[str, tuple[Path, int, list[str]]]:
    """Single-pass scan of every `.inc` to build name → (path, line, body)
    map. Each label's body is the first 3 non-blank, non-directive lines
    after the `name:` line."""
    out: dict[str, tuple[Path, int, list[str]]] = {}
    for path in UNIFIED.rglob("*.inc"):
        try:
            lines = path.read_text().splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines):
            m = re.match(r"^(LABEL_[0-9A-F]+):\s*$", line)
            if not m:
                continue
            name = m.group(1)
            if name in out:
                # already cached; first def wins
                continue
            body: list[str] = []
            for offset in range(1, 8):
                if i + offset >= len(lines):
                    break
                ln = lines[i + offset]
                if not ln.strip():
                    continue
                if ln.lstrip().startswith(";@"):
                    continue
                body.append(ln.strip())
                if len(body) >= 3:
                    break
            out[name] = (path, i + 1, body)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "docs" / "unnamed_setup_targets.md",
    )
    args = parser.parse_args()

    targets = collect_setup_targets()
    label_defs = build_label_def_index()

    by_stage: dict[
        str, list[tuple[int, str, str, list[tuple[str, str]]]]
    ] = defaultdict(list)
    for name, callers in targets.items():
        defn = label_defs.get(name)
        if defn is None:
            continue
        path, line_no, body = defn
        # Group callers by stage, keep track of channel(s).
        per_stage_chans: dict[str, set[int]] = defaultdict(set)
        per_stage_locs: dict[str, list[str]] = defaultdict(list)
        for stage, ch, loc in callers:
            per_stage_chans[stage].add(ch)
            per_stage_locs[stage].append(loc)
        for stage, chs in per_stage_chans.items():
            for ch in chs:
                by_stage[stage].append(
                    (
                        ch,
                        name,
                        f"{path.relative_to(SRC_TREE)}:{line_no}",
                        [(b, loc) for b in body for loc in [None]],
                    )
                )

    md: list[str] = []
    md.append("# Unnamed setup-target inventory")
    md.append("")
    md.append(
        "Working list for the next semantic-rename round. Each "
        "entry below is a `LABEL_HHHH:` placeholder routine that "
        "is setup-called from somewhere — i.e., a thread the "
        "engine starts at runtime, with a name the disasm "
        "auto-generated by address. Picking a meaningful name "
        "for each (per the routine body's hint) replaces the "
        "placeholder across the unified source tree."
    )
    md.append("")
    md.append(
        "Stages are listed in walkthrough order. Channels per "
        "stage are sorted ascending. Definitions cite the chunk "
        "file + line; first 3 body lines are shown as a "
        "naming hint."
    )
    md.append("")

    STAGE_ORDER = [
        "INTRO",
        "LAKE",
        "PRISON",
        "CAVES",
        "TANK",
        "CODE_WHEEL",
        "PASSCODE",
        "CAPSULE",
        "ENDING",
    ]
    for stage in STAGE_ORDER:
        entries = by_stage.get(stage, [])
        if not entries:
            continue
        md.append(f"## {stage}")
        md.append("")
        md.append(f"{len(entries)} unnamed setup-targets.")
        md.append("")
        # Sort by channel, then by name
        entries.sort(key=lambda e: (e[0], e[1]))
        for ch, name, defn_loc, body in entries:
            md.append(f"### `0x{ch:02X}` — `{name}`")
            md.append("")
            md.append(f"Defined at `{defn_loc}`.")
            md.append("")
            md.append("```")
            for b, _ in body:
                md.append(b)
            md.append("```")
            md.append("")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(md) + "\n")
    print(f"wrote {args.out}")
    print(f"  {sum(len(v) for v in by_stage.values())} entries across {len(by_stage)} stages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
