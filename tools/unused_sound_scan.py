#!/usr/bin/env python3
"""Naive unused-SOUND scanner for a DOS-format port.

Approach (no reachability analysis — that's issue #0058):
  - Enumerate SOUND resources from the port's `manifest.json`.
  - Scan disasm for `play id=N` opcodes (direct playback).
  - Scan disasm for `load id=N` opcodes (preload — might be a music
    instrument or a sound-effect preload).
  - Subtract: defined - (play | load) = candidate unused sounds.

Caveat: a `load id=N` inside dead code (like LAKE's `jmp` over the
0x89 preload — see issue #0076) still counts as "used" by this
naive scanner. Definitive unused-sound results require reachability
analysis (issue #0058).

Usage:
    python3 tools/unused_sound_scan.py <work-dir>

where `<work-dir>` contains both `manifest.json` (with SOUND
resource indices) and `disasm/` (per-level disassembly).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("work_dir", type=Path,
                   help="path to a port's work-dir (has manifest.json + disasm/)")
    args = p.parse_args()

    manifest = json.loads((args.work_dir / "manifest.json").read_text())
    sound_resources = {
        r["index"]: r for r in manifest.get("resources", [])
        if r.get("type") == "SOUND"
    }
    music_resources = {
        r["index"]: r for r in manifest.get("resources", [])
        if r.get("type") == "MUSIC"
    }
    defined_sound = set(sound_resources.keys())
    defined_music = set(music_resources.keys())

    # Find the disasm root. Could be at the same level as manifest.json
    # or at a sibling tmp/output dir; try both.
    disasm_root = args.work_dir / "disasm"
    if not disasm_root.is_dir():
        # Try archaeology-style tmp/output/<slug>/disasm
        slug = manifest.get("slug", "")
        # Slug -> archaeology output-dir mapping
        slug_to_output = {"dos": "msdos", "amiga": "amiga"}
        for outdir in [slug_to_output.get(slug, slug), slug]:
            candidate = Path("tmp/output") / outdir / "disasm"
            if candidate.is_dir():
                disasm_root = candidate
                break

    if not disasm_root.is_dir():
        print(f"error: no disasm/ found under {args.work_dir} or tmp/output/{slug}/",
              file=sys.stderr)
        return 1

    play_ids: set[int] = set()
    load_ids: set[int] = set()
    song_ids: set[int] = set()

    re_play = re.compile(r"\bplay\s+id=(0x[0-9A-Fa-f]+|\d+)")
    re_load = re.compile(r"\bload\s+id=(0x[0-9A-Fa-f]+|\d+)")
    re_song = re.compile(r"\bsong\s+id=(0x[0-9A-Fa-f]+|\d+)")

    for asm in disasm_root.rglob("*.asm"):
        text = asm.read_text()
        for m in re_play.finditer(text):
            s = m.group(1)
            play_ids.add(int(s, 0) if s.startswith("0x") else int(s))
        for m in re_load.finditer(text):
            s = m.group(1)
            load_ids.add(int(s, 0) if s.startswith("0x") else int(s))
        for m in re_song.finditer(text):
            s = m.group(1)
            song_ids.add(int(s, 0) if s.startswith("0x") else int(s))

    print(f"Port: {manifest.get('slug', '?')}")
    print(f"  Disasm: {disasm_root}")
    print()
    print(f"  SOUND resources defined: {len(defined_sound)}")
    print(f"  MUSIC resources defined: {len(defined_music)}")
    print(f"  `play id=` opcodes: {len(play_ids)} unique IDs")
    print(f"  `load id=` opcodes: {len(load_ids)} unique IDs (all types)")
    print(f"  `song id=` opcodes: {len(song_ids)} unique IDs")
    print()
    sound_used = defined_sound & (play_ids | load_ids)
    sound_unused = defined_sound - (play_ids | load_ids)
    sound_unused_nonempty = [
        i for i in sorted(sound_unused) if sound_resources[i]["size"] > 0
    ]
    print(f"  SOUND used (play | load): {len(sound_used)}")
    print(f"  SOUND NEVER play'd OR loaded: {len(sound_unused)}")
    print(f"    (with non-empty content): {len(sound_unused_nonempty)}")
    if sound_unused_nonempty:
        print()
        print("  Unused SOUND resources (with non-empty content):")
        for idx in sound_unused_nonempty:
            r = sound_resources[idx]
            print(f"    0x{idx:02X}  size={r['size']:>6d}  packed={r['packed_size']:>6d}  "
                  f"md5={r['md5']}")

    music_used = defined_music & (song_ids | load_ids)
    music_unused = defined_music - (song_ids | load_ids)
    music_unused_nonempty = [
        i for i in sorted(music_unused) if music_resources[i]["size"] > 0
    ]
    print()
    print(f"  MUSIC used (song | load): {len(music_used)}")
    print(f"  MUSIC NEVER song'd OR loaded: {len(music_unused)}")
    print(f"    (with non-empty content): {len(music_unused_nonempty)}")
    if music_unused_nonempty:
        print()
        print("  Unused MUSIC resources (with non-empty content):")
        for idx in music_unused_nonempty:
            r = music_resources[idx]
            print(f"    0x{idx:02X}  size={r['size']:>6d}  md5={r['md5']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
