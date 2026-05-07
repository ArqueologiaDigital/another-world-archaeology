#!/usr/bin/env python3
"""Extract a per-stage map of `setup channel=NN, address=…` opcodes
from the unified source tree, then emit a Markdown report.

Each `setup channel=N, address=ADDR` opcode in AW VM bytecode
starts a new "thread" on channel N at routine ADDR. The 64
channels (0x00..0x3F) are the engine's concurrency primitive.

This tool walks every `.asm.in` and `.inc` under
`src/levels/_unified/`, captures each `setup` opcode along with
its enclosing stage and branch (from `;@if BRANCH ==` context),
and groups by (stage, channel). The output Markdown gives one
section per stage with a table of channels and which routines
they're scheduled to.

Reading the result:
- A channel listed once with one routine = single-purpose
  feature thread.
- A channel listed multiple times = the bytecode reassigns it
  during execution (the channel handles a state-changing
  feature).
- Routines named via the project's semantic-rename pass
  (DRAW_CIN_*, INIT_VARS_*, INLINE_SET_*, …) tell you the role
  directly. `LABEL_HHHH` placeholders are still common — they're
  the auto-generated names the disasm assigned.

Usage:
  python3 tools/build_channel_map.py [--out PATH]
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
    r"address=(?P<addr>\S+)\s*$"
)
RE_INCLUDE = re.compile(r'^\s*;@include\s+"([^"]+)"', re.MULTILINE)


def stage_of(path: Path) -> str | None:
    """Stage NAME (uppercase) for a path under `_unified/<stage>/...`,
    or for a top-level `<STAGE>.asm.in`."""
    rel = path.relative_to(UNIFIED)
    if rel.parts:
        first = rel.parts[0]
        if first.endswith(".asm.in"):
            return first[: -len(".asm.in")].upper()
        if first == "_helpers":
            return None  # cross-stage; tracked separately if useful
        if first.startswith("_"):
            return None
        return first.upper()
    return None


def parse_branch_chunk(chunk_name: str) -> str | None:
    """For per-arm chunks (`<arm>__*.inc`), return the implicit
    branch from the arm prefix."""
    m = re.match(r"^(amiga|dos|cart|gba)__", chunk_name)
    if not m:
        return None
    return {
        "amiga": "chahi_amiga_1991",
        "dos": "dos_1992",
        "cart": "cartridge_1992",
        "gba": "gba_2004",
    }[m.group(1)]


# Each tuple: (stage, branch_or_None, channel, address, source_location)
SetupRow = tuple[str, str | None, int, str, str]


def scan_file(path: Path, default_branch: str | None) -> list[SetupRow]:
    rows: list[SetupRow] = []
    stage = stage_of(path)
    if stage is None:
        return rows
    text = path.read_text()
    # Track `;@if BRANCH ==` context as we walk lines.
    branch_stack: list[str | None] = [default_branch]
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        # Pattern: `;@if BRANCH == "<branch>"` or `;@if BRANCH in (…)`
        m_if = re.match(
            r';@if\s+BRANCH\s+==\s+"([^"]+)"', stripped
        )
        m_if_in = re.match(
            r';@if\s+BRANCH\s+in\s+\(([^)]+)\)', stripped
        )
        m_elif = re.match(
            r';@elif\s+BRANCH\s+==\s+"([^"]+)"', stripped
        )
        m_endif = re.match(r';@endif', stripped)
        m_else = re.match(r';@else', stripped)
        if m_if:
            branch_stack.append(m_if.group(1))
            continue
        if m_if_in:
            # multi-branch — we don't single-out a branch here
            branch_stack.append(None)
            continue
        if m_elif:
            if len(branch_stack) > 1:
                branch_stack[-1] = m_elif.group(1)
            continue
        if m_else:
            if len(branch_stack) > 1:
                branch_stack[-1] = None
            continue
        if m_endif:
            if len(branch_stack) > 1:
                branch_stack.pop()
            continue
        m = RE_SETUP.match(line)
        if m:
            ch = int(m.group("ch"), 0)
            addr = m.group("addr")
            rows.append(
                (
                    stage,
                    branch_stack[-1],
                    ch,
                    addr,
                    f"{path.relative_to(SRC_TREE)}:{i}",
                )
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT
        / "docs"
        / "content"
        / "research"
        / "17-vm-channel-map.md",
    )
    args = parser.parse_args()

    # Walk every .asm.in and .inc under _unified/.
    rows: list[SetupRow] = []
    for path in sorted(UNIFIED.rglob("*.asm.in")):
        rows.extend(scan_file(path, default_branch=None))
    for path in sorted(UNIFIED.rglob("*.inc")):
        chunk_branch = parse_branch_chunk(path.name)
        rows.extend(scan_file(path, default_branch=chunk_branch))

    # Group by (stage, channel) → list of (branch, addr, src).
    by_stage_channel: dict[
        tuple[str, int], list[tuple[str | None, str, str]]
    ] = defaultdict(list)
    for stage, branch, ch, addr, src in rows:
        by_stage_channel[(stage, ch)].append((branch, addr, src))

    # Stage order: same as the walkthrough.
    STAGE_ORDER = [
        "INTRO",
        "LAKE",
        "PRISON",
        "CAVES",
        "CITY",
        "ARENA",
        "BATHS",
        "FINAL",
        "CODE_WHEEL",
        "TANK",
        "PASSCODE",
        "CAPSULE",
        "ENDING",
    ]
    seen_stages = sorted(
        {s for s, _ in by_stage_channel.keys()},
        key=lambda s: (
            STAGE_ORDER.index(s) if s in STAGE_ORDER else 100,
            s,
        ),
    )

    md: list[str] = []
    md.append("# 17 — VM thread-channel map (per stage)")
    md.append("")
    md.append(
        "Each AW VM `setup channel=NN, address=ROUTINE` opcode "
        "starts a thread on channel `NN` (one of 64 — `0x00..0x3F`) "
        "running `ROUTINE`. Channels are the engine's concurrency "
        "primitive: actor animation, frame blit, music timing, "
        "cinematic sequencing, and HUD drawing each get their own "
        "channel."
    )
    md.append("")
    md.append(
        "This is a STATIC scan: every `setup` opcode in the unified "
        "source is collected and grouped by stage. A channel listed "
        "with multiple routines means the bytecode REASSIGNS that "
        "channel during execution — the channel hosts a sequence of "
        "features as the level progresses."
    )
    md.append("")
    md.append(f"Total `setup` opcodes scanned: **{len(rows)}**.")
    md.append("")

    # Cross-stage hot-channel summary
    channel_total: dict[int, int] = defaultdict(int)
    for (stage, ch), entries in by_stage_channel.items():
        channel_total[ch] += len(entries)
    md.append("## Channel-usage frequency (across all stages)")
    md.append("")
    md.append(
        "Channels listed with their total `setup` count "
        "across every stage. Channel `0x3C` is canonically the "
        "blit / pause-quantum loop; `0x00`-`0x0F` typically host "
        "actor and HUD threads; `0x3D`-`0x3F` are often reserved."
    )
    md.append("")
    md.append("| channel | total setups |")
    md.append("| ---: | ---: |")
    for ch in sorted(channel_total.keys(), key=lambda c: -channel_total[c]):
        md.append(f"| `0x{ch:02X}` | {channel_total[ch]} |")
    md.append("")

    # Per-stage tables
    for stage in seen_stages:
        md.append(f"## {stage}")
        md.append("")
        chans_in_stage = sorted(
            ch for s, ch in by_stage_channel.keys() if s == stage
        )
        if not chans_in_stage:
            continue
        md.append("| channel | branch | routine | source |")
        md.append("| ---: | --- | --- | --- |")
        for ch in chans_in_stage:
            entries = by_stage_channel[(stage, ch)]
            # Deduplicate by (branch, addr); list source examples.
            from collections import defaultdict as dd

            grouped: dict[tuple[str | None, str], list[str]] = dd(list)
            for branch, addr, src in entries:
                grouped[(branch, addr)].append(src)
            for (branch, addr), sources in sorted(
                grouped.items(),
                key=lambda kv: (kv[0][1] or "", kv[0][0] or ""),
            ):
                br = (
                    {
                        "chahi_amiga_1991": "amiga",
                        "dos_1992": "dos",
                        "cartridge_1992": "cart",
                        "gba_2004": "gba",
                    }.get(branch, "shared")
                    if branch
                    else "shared"
                )
                src_summary = (
                    sources[0]
                    if len(sources) == 1
                    else f"{sources[0]} (+{len(sources)-1} more)"
                )
                md.append(
                    f"| `0x{ch:02X}` | {br} | `{addr}` | "
                    f"{src_summary} |"
                )
        md.append("")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(md) + "\n")
    print(f"wrote {args.out}")
    print(f"  {len(rows)} setup opcodes")
    print(f"  {len(seen_stages)} stages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
