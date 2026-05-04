#!/usr/bin/env python3
"""Unused-SOUND scanner with reachability filtering (post-#0058).

Successor to `unused_sound_scan.py`, which used a naive regex
over all disasm files. This version uses the `ReachabilityOracle`
from #0058 to filter out `play`/`load`/`song` references inside
dead code (gates, transitively-dead subgraphs).

Why this matters: research/11 (music 0x89) found that LAKE
preloads music 0x89 inside an unreachable code block — the naive
scanner counted 0x89 as "used" (because `load id=0x0089` appears
in the bytecode), but research/11 confirmed it's actually cut
content via runtime testing. The reachability oracle automates
that distinction: any `load`/`play`/`song` in a dead-by-gate or
transitively-dead label doesn't count.

Operates against the source-reconstruction tree's per-port
`.asm` files (which have semantic label names) rather than
disasm files. Output: per-resource (SOUND, MUSIC) used-vs-unused
classification with reachability filtering applied.

Usage:
    python3 tools/unused_sound_scan_v2.py <work-dir> [--branch dos_1992]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path("/home/fsanches/compartilhado/another-world-archaeology")
SRC_TREE = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
LEVELS = SRC_TREE / "src" / "levels"

sys.path.insert(0, str(REPO_ROOT / "tools"))
from build_reachability_graph import (  # noqa: E402
    parse_stage,
    ReachabilityOracle,
)

RE_PLAY = re.compile(r"\bplay\s+id=(0x[0-9A-Fa-f]+|\d+)")
RE_LOAD = re.compile(r"\bload\s+id=(0x[0-9A-Fa-f]+|\d+)")
RE_SONG = re.compile(r"\bsong\s+id=(0x[0-9A-Fa-f]+|\d+)")
# Within-label terminators: after these, fall-through is dead.
# Note `break` is NOT here — it yields and resumes next tick.
RE_INTRA_TERM = re.compile(
    r"^\s*(ret|killChannel|bankSwitch|freezeChannel|jmp\b)"
)


def parse_id(s: str) -> int:
    return int(s, 0) if s.startswith("0x") else int(s)


def collect_refs_in_stage(
    stage_data: dict, oracle: ReachabilityOracle, stage_name: str
) -> dict:
    """For one stage, scan every label's instructions for play/load/song
    opcodes. Separate live and dead references."""
    plays_live: set[int] = set()
    plays_dead: set[int] = set()
    loads_live: set[int] = set()
    loads_dead: set[int] = set()
    songs_live: set[int] = set()
    songs_dead: set[int] = set()

    for label, body in stage_data["labels"].items():
        is_live = oracle.is_live(stage_name, label)
        # Within a label, walk instructions until the first
        # intra-label terminator (jmp/ret/killChannel/...). After
        # the terminator, instructions are unreachable WITHIN this
        # label (no incoming label can land mid-label since labels
        # are split at every definition). This is the key fix that
        # lets the scanner see `load id=0x89` after `jmp` as dead.
        for _line, instr in body["instrs"]:
            for m in RE_PLAY.finditer(instr):
                idx = parse_id(m.group(1))
                (plays_live if is_live else plays_dead).add(idx)
            for m in RE_LOAD.finditer(instr):
                idx = parse_id(m.group(1))
                (loads_live if is_live else loads_dead).add(idx)
            for m in RE_SONG.finditer(instr):
                idx = parse_id(m.group(1))
                (songs_live if is_live else songs_dead).add(idx)
            if RE_INTRA_TERM.match(instr):
                # Mark subsequent instructions as DEAD by switching
                # the per-iteration is_live flag.
                is_live = False
    return {
        "play_live": plays_live,
        "play_dead": plays_dead,
        "load_live": loads_live,
        "load_dead": loads_dead,
        "song_live": songs_live,
        "song_dead": songs_dead,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "work_dir",
        type=Path,
        help="path to a port's work-dir (has manifest.json)",
    )
    p.add_argument(
        "--branch",
        default="dos_1992",
        help="source-reconstruction branch (default: dos_1992)",
    )
    args = p.parse_args()

    manifest = json.loads((args.work_dir / "manifest.json").read_text())
    sound_resources = {
        r["index"]: r
        for r in manifest.get("resources", [])
        if r.get("type") == "SOUND"
    }
    music_resources = {
        r["index"]: r
        for r in manifest.get("resources", [])
        if r.get("type") == "MUSIC"
    }

    oracle = ReachabilityOracle(branch=args.branch)
    branch_dir = LEVELS / args.branch

    play_live: set[int] = set()
    play_dead: set[int] = set()
    load_live: set[int] = set()
    load_dead: set[int] = set()
    song_live: set[int] = set()
    song_dead: set[int] = set()

    for asm in sorted(branch_dir.glob("*.asm")):
        stage_data = parse_stage(asm)
        stage = asm.stem
        refs = collect_refs_in_stage(stage_data, oracle, stage)
        play_live |= refs["play_live"]
        play_dead |= refs["play_dead"]
        load_live |= refs["load_live"]
        load_dead |= refs["load_dead"]
        song_live |= refs["song_live"]
        song_dead |= refs["song_dead"]

    print(f"Port: {manifest.get('slug', '?')}")
    print(f"  Branch: {args.branch}")
    print(f"  SOUND resources defined: {len(sound_resources)}")
    print(f"  MUSIC resources defined: {len(music_resources)}")
    print()
    print(f"  Live `play  id=`: {len(play_live)} unique")
    print(f"  Dead `play  id=`: {len(play_dead - play_live)} unique (only in dead code)")
    print(f"  Live `load  id=`: {len(load_live)} unique")
    print(f"  Dead `load  id=`: {len(load_dead - load_live)} unique (only in dead code)")
    print(f"  Live `song  id=`: {len(song_live)} unique")
    print(f"  Dead `song  id=`: {len(song_dead - song_live)} unique (only in dead code)")
    print()

    # SOUND classification.
    defined_sound = set(sound_resources.keys())
    used_live_sound = defined_sound & (play_live | load_live)
    # "dead-only" — referenced ONLY from dead code.
    dead_only_sound = (
        defined_sound & (play_dead | load_dead) - used_live_sound
    )
    unreferenced_sound = defined_sound - (
        play_live | play_dead | load_live | load_dead
    )
    unref_nonempty_sound = [
        i for i in sorted(unreferenced_sound) if sound_resources[i]["size"] > 0
    ]

    print(f"  SOUND used (live play|load): {len(used_live_sound)}")
    print(
        f"  SOUND dead-only (referenced ONLY from dead code): "
        f"{len(dead_only_sound)}"
    )
    if dead_only_sound:
        print("    Sound IDs only referenced from dead code:")
        for idx in sorted(dead_only_sound):
            r = sound_resources[idx]
            print(
                f"      0x{idx:02X}  size={r['size']:>6d}  md5={r['md5']}"
            )
    print(f"  SOUND never referenced: {len(unreferenced_sound)}")
    print(f"    (with non-empty content): {len(unref_nonempty_sound)}")
    if unref_nonempty_sound:
        for idx in unref_nonempty_sound:
            r = sound_resources[idx]
            print(
                f"      0x{idx:02X}  size={r['size']:>6d}  md5={r['md5']}"
            )

    # MUSIC classification.
    print()
    defined_music = set(music_resources.keys())
    used_live_music = defined_music & (song_live | load_live)
    dead_only_music = (
        defined_music & (song_dead | load_dead) - used_live_music
    )
    unreferenced_music = defined_music - (
        song_live | song_dead | load_live | load_dead
    )
    unref_nonempty_music = [
        i for i in sorted(unreferenced_music) if music_resources[i]["size"] > 0
    ]
    print(f"  MUSIC used (live song|load): {len(used_live_music)}")
    print(
        f"  MUSIC dead-only (referenced ONLY from dead code): "
        f"{len(dead_only_music)}"
    )
    if dead_only_music:
        print("    Music IDs only referenced from dead code:")
        for idx in sorted(dead_only_music):
            r = music_resources[idx]
            print(
                f"      0x{idx:02X}  size={r['size']:>6d}  md5={r['md5']}"
            )
    print(f"  MUSIC never referenced: {len(unreferenced_music)}")
    print(f"    (with non-empty content): {len(unref_nonempty_music)}")
    if unref_nonempty_music:
        for idx in unref_nonempty_music:
            r = music_resources[idx]
            print(
                f"      0x{idx:02X}  size={r['size']:>6d}  md5={r['md5']}"
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
