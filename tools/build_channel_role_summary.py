#!/usr/bin/env python3
"""Inferred channel-role summary, complementing
`tools/build_channel_map.py`'s flat per-stage tables.

For each (stage, channel) the build_channel_map output lists
every routine that's setup-called on that channel. This tool
infers a SINGLE primary role per (stage, channel) by binning
routine names against well-known prefix patterns and picking
the dominant bin.

Output: a compact stage × channel matrix where each cell
shows the inferred role (or `?` for channels dominated by
unnamed `LABEL_HHHH` placeholders, where there's no semantic
signal yet).

Categories:
  blit       — `BLIT_*`, `LOOP_BLIT_*`
  cin-draw   — `DRAW_CIN_*`, `DRAW_CINEMATIC_*`
  cv-draw    — `DRAW_CV_*`, `INLINE_DRAW_CV_*`
  cleanup    — `KILL_CHANNEL_*`, `KILL_CHAN_*`
  init       — `INIT_*`, `SETUP_*`, `INLINE_SET_*`
  framebuf   — `CLEAR_*`, `FILL_*`, `COPY_PAGE_*`,
               `COPY_VIDEO_PAGE_*`, `BLIT_FROM_PAGE_*`
  actor      — `HERO_*`, `BEAST_*`, `BEETLE_*`,
               `LESTER_*`, `ENEMY_*`
  anim       — `*_LOOP`, `ANIM_*`, `*_ANIMATE_*`,
               `*_DRIFT_*`, `LOOP_*`
  music      — `MUSIC_*`, `PLAY_*`, `SONG_*`, `SFX_*`
  delay      — `DELAY_*`, `WAIT_*`, `PAUSE_*`
  scroll     — `SCROLL_*`
  unnamed    — `LABEL_HHHH` placeholders only
  mixed      — multiple categories with similar counts
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from _paths import AW_SRC, REPO_ROOT

SRC_TREE = AW_SRC
LEVELS = SRC_TREE / "src" / "levels"
UNIFIED = LEVELS / "_unified"

RE_SETUP = re.compile(
    r"^\s*setup\s+channel=(?P<ch>0x[0-9A-Fa-f]+|\d+)\s*,\s*"
    r"address=(?P<addr>\S+)\s*$"
)


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


# Order matters — first match wins. More specific patterns first.
ROLE_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("unnamed",  re.compile(r"^(LABEL|JUNK)_+[0-9A-F]+(?:_AT_[0-9A-F]+)?$")),
    ("cleanup",  re.compile(r"^(KILL_CHANNEL_|KILL_CHAN_|DELETE_CHANNELS_|DELETE_ALL_CHANS_)")),
    ("cv-draw",  re.compile(r"(^|_)(DRAW_CV[_0-9]|INLINE_DRAW_CV_|GUARDED_DRAW_CV_|DRAW_COMMON_VIDS?_|STEP_DRAW_CV)")),
    ("cin-draw", re.compile(r"(^|_)(DRAW_CIN(?:EMATIC)?S?[_0-9]|HANG_DRAW_CIN_|DRAW_CITY_|DRAW_INTRO_DECOR_|FILL_AND_DRAW_CIN_|FILL_FF_AND_DRAW_|DRAW_LAKE_|DRAW_STARS_|DRAW_BEAST_|HANG_DRAWING_)")),
    ("blit",     re.compile(r"(^|_)(BLIT(_|TER_|TER$)|RENDER_FRAME_|HANG_BLITTING_|SHOW_PAGE_)")),
    ("framebuf", re.compile(r"(^|_)(CLEAR_|FILL_|COPY_PAGE|COPY_VIDEO_PAGE_|BLIT_FROM_PAGE_|COPY_BG_PAGE_|COPY_FF_|SET_PAL_|FADE_PAL_|PAL_FADE_|PALETTE_FADE_|PALETTE_FLASH_|SET_PALETTE_)")),
    ("scroll",   re.compile(r"(^|_)SCROLL_")),
    ("music",    re.compile(r"(^|_)(MUSIC_|PLAY_(?:SFX|SONG|FX|MUSIC|BG_AUDIO)|SONG_|SFX_|AMBIENT_)")),
    ("delay",    re.compile(r"(^|_)(DELAY_|WAIT_|PAUSE_|HOLD_|BREAK_LOOP)")),
    ("actor",    re.compile(r"(^|_)(HERO_|BEAST_|BEETLE_|LESTER_|ENEMY_|TENTACLE_|SLUG_|SOLDIER_|MUTANT_|GUARD_|ALIEN_|BIRD_|TANK_|GETTING_OUT_)")),
    ("text",     re.compile(r"(^|_)(DISPLAY_TEXT_|TEXT_|SHOW_TEXT_|SUBTITLE_)")),
    ("init",     re.compile(r"(^|_)(INIT_|SETUP_|INLINE_SET_|SET_VAR|RESET_|BANK\d+_|BANK_INIT|BANKSWITCH_|ENTRY_POINT_|LEVEL_INIT$|TRANSITION_)")),
    ("ambient",  re.compile(r"(^|_)(BUBBLES_|DECOR_|DROPLET_|SPARKLE_|SCATTER_(DOTS|3DOT|8DOT)|SMOKE_|FIRE_|BG$|_BG_|BACKGROUND_|SCENE_|GOO_|VINE_|CALM_|POOL_|LAB_|CONSOLE_|SINKING_|PARTICLE_|GLARE_|UPDATE_POSITION_OF_|SCHEDULE_(?:LAKE|INTRO)_DEC|WAVY_)")),
    ("anim",     re.compile(r"(_LOOP$|^ANIM_|_ANIMATE_|_ANIM_|_DRIFT_|^LOOP_|_STEP_RIGHT|_STEP_LEFT|^ALTERNATE_|^ANIMATE_|_TIMING$|_FADE_|_CYCLE|_ANIMATION$|_ANIMATION_)")),
    ("dispatch", re.compile(r"(^|_)(DISPATCH_|DISPATCHER_|HANDLE_)")),
    ("counter",  re.compile(r"(^|_)(INCREMENT_VAR|DECREMENT_VAR|COMPUTE_|ACCUMULATE_|TWEEN_|RAMP_|MARK_VAR)")),
    ("actor",    re.compile(r"(^|_)(WALK_|RESUME_WALK|MAYBE_RESUME_WALK)")),
    ("cin-draw", re.compile(r"(^|_)(ZOOM_LOOP_CIN|ZOOM_CIN_)")),
]


def categorize(name: str) -> str:
    for cat, rx in ROLE_PATTERNS:
        if rx.search(name):
            return cat
    return "other"


def classify_channel(addrs: list[str]) -> str:
    """Single role label for a (stage, channel). Returns 'mixed' when
    the top two roles tie (within 30%); otherwise the dominant role."""
    if not addrs:
        return "?"
    counts = Counter(categorize(a) for a in addrs)
    most_common = counts.most_common()
    if len(most_common) == 1:
        return most_common[0][0]
    if most_common[0][1] >= 2 * most_common[1][1]:
        return most_common[0][0]
    return "mixed"


def collect_setups() -> dict[tuple[str, int], list[str]]:
    """{(stage, channel): [routine_name, ...]}."""
    out: dict[tuple[str, int], list[str]] = defaultdict(list)
    for path in sorted(UNIFIED.rglob("*.asm.in")):
        stage = stage_of(path)
        if not stage:
            continue
        for line in path.read_text().splitlines():
            m = RE_SETUP.match(line)
            if m:
                out[(stage, int(m.group("ch"), 0))].append(m.group("addr"))
    for path in sorted(UNIFIED.rglob("*.inc")):
        stage = stage_of(path)
        if not stage:
            continue
        for line in path.read_text().splitlines():
            m = RE_SETUP.match(line)
            if m:
                out[(stage, int(m.group("ch"), 0))].append(m.group("addr"))
    return out


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
        help="path to research/17 doc; the role-summary section "
        "is regenerated at the bottom of the file under a known "
        "marker",
    )
    args = parser.parse_args()

    setups = collect_setups()
    stages = sorted({s for s, _ in setups.keys()})
    channels = sorted({c for _, c in setups.keys()})

    md: list[str] = []
    md.append("## Channel role inference (per stage)")
    md.append("")
    md.append(
        "Compact heatmap: for each (stage, channel) the routine "
        "names setup-called on that channel are binned by "
        "well-known prefix patterns; the dominant category is "
        "shown. Empty cells mean the stage doesn't use that "
        "channel; `?` means every routine on that channel is a "
        "`LABEL_HHHH` placeholder (no semantic signal yet)."
    )
    md.append("")
    md.append("Categories: `blit` (BLIT_*), `cin-draw` (DRAW_CIN_*),")
    md.append("`cv-draw` (DRAW_CV_* / INLINE_DRAW_CV_*),")
    md.append("`framebuf` (CLEAR_/FILL_/COPY_PAGE_*),")
    md.append("`actor` (HERO_/BEAST_/…), `anim` (*_LOOP, ANIM_*),")
    md.append("`init` (INIT_/SETUP_/INLINE_SET_), `cleanup` (KILL_CHANNEL_*),")
    md.append("`music` (MUSIC_/SFX_/PLAY_*), `delay`, `scroll`,")
    md.append("`unnamed` (only LABEL_HHHH), `mixed` (no clear winner).")
    md.append("")

    # Header row
    header = ["channel"] + stages
    md.append("| " + " | ".join(header) + " |")
    md.append("| " + " | ".join(["---"] * len(header)) + " |")
    for ch in channels:
        row = [f"`0x{ch:02X}`"]
        for stage in stages:
            addrs = setups.get((stage, ch), [])
            row.append(classify_channel(addrs) if addrs else "")
        md.append("| " + " | ".join(row) + " |")

    md.append("")

    # Read existing doc, replace the role section if present (idempotent).
    if args.out.exists():
        existing = args.out.read_text()
        marker = "## Channel role inference (per stage)"
        if marker in existing:
            head = existing.split(marker, 1)[0].rstrip() + "\n\n"
            text = head + "\n".join(md) + "\n"
        else:
            text = existing.rstrip() + "\n\n" + "\n".join(md) + "\n"
        args.out.write_text(text)
        print(f"updated {args.out}")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text("\n".join(md) + "\n")
        print(f"wrote {args.out}")

    print(f"  {len(stages)} stages × {len(channels)} channels")
    print(f"  {len(setups)} (stage, channel) cells with data")
    return 0


if __name__ == "__main__":
    sys.exit(main())
