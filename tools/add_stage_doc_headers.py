#!/usr/bin/env python3
"""Phase 2: prepend stage-narrative documentation headers to each
`_unified/<STAGE>.asm.in` file.

The header is a `;`-comment block that explains:
  - The gameplay sequence this stage corresponds to
  - The branches and ports that ship this stage
  - Notable bytecode features (entry point conventions, dispatchers)
  - Where to find more context (walkthrough, archive)

Idempotent: skips files that already start with a `; STAGE <name>:`
header marker.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC_ROOT = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
LEVELS = SRC_ROOT / "src/levels"

# Stage narratives sourced from
# references/walkthroughs/2026-04-29-gamefaqs-aw-78570.txt and from
# the archaeology project's accumulated context (CLAUDE.md, issue
# tracker, prior rename rounds).
HEADERS: dict[str, str] = {
    "INTRO": """\
; STAGE INTRO: Particle-physics lab scene + transport-to-alien-world.
;
; Gameplay role: opening cinematic. Lester Chaykin arrives at his
; lab one stormy night to run an experiment with a particle
; accelerator. Lightning hits the building, the experiment goes
; haywire, and Lester is transported to the alien world. The stage
; ends with him appearing underwater in the LAKE pool.
;
; Branches that ship INTRO:
;   chahi_amiga_1991, dos_1992, cartridge_1992 (snes_eu, genesis_eu),
;   gba_2004 (foxy port).
;
; This is THE LONGEST cinematic in the game, and most ports use
; identical bytecode aside from EQU-table reordering. AWVM_Tools
; mislabels the cartridge/GBA INTRO chunk as "Code-wheel screen" —
; cartridges have no codewheel, so that label is a known artifact.
;
; The unified file is structured as 14 named chapter chunks
; (intro/intro_*.inc) — each chunk corresponds to a coherent scene
; or routine cluster. Chapter ordering follows byte-address order in
; the cart-bytecode arm.
""",

    "LAKE": """\
; STAGE LAKE: "Arrival in a Strange World" — opening playable level.
;
; Gameplay role: this is the FIRST stage where the player has
; control. Lester wakes underwater in a pool with a tentacle monster
; rising from below. Player must:
;   1. Swim up before the tentacle reaches the surface (LESTER drowns
;      otherwise — see project_lake_scene_narrative.md).
;   2. Run right past worms (slide-kick to kill them).
;   3. Avoid being eaten by the black beast that ambushes from the
;      next screen — must run BACK left, grab a hanging vine, swing
;      across the cliff edge, and let the natives capture the beast.
;   4. Get captured by the alien natives (cinematic ending).
;
; Branches that ship LAKE:
;   chahi_amiga_1991, dos_1992, cartridge_1992 (snes_eu, genesis_eu),
;   gba_2004 (foxy port).
;
; Note on tone: routines named DROPLET_*, TENTACLE_*, SNEAKY_TENTACLE
; etc. all relate to this OPENING sequence — LAKE is a tense scene,
; not a calm later area.
;
; Structure: chapter chunks named by scene element
; (lake/blit_loops.inc, lake/lester_at_pool_animations.inc, etc.) —
; ordered by byte-address in the cart-bytecode arm.
""",

    "PRISON": """\
; STAGE PRISON: alien cell, cage break-out, gun pickup, jailbreak.
;
; Gameplay role: after capture in LAKE, player wakes up caged
; alongside another prisoner (the alien friend). Player must:
;   1. Swing the cage left/right alternately to break it off.
;   2. Pick up the dropped pistol from a stunned guard.
;   3. Shoot guards across several screens, using shields when
;      needed (charge-shot mechanics introduced here).
;   4. Reach the elevator, descend, destroy the power-source on the
;      lower wall, ride back up, super-blast a door.
;   5. Use teleporters to reach the vent panel — alien friend opens
;      the floor panel and Lester drops into the ventilation shafts.
;
; Branches that ship PRISON:
;   chahi_amiga_1991, dos_1992, cartridge_1992 (genesis_eu only —
;   snes_eu and gba_2004 stop at LAKE).
;
; Notable per-arm divergence:
;   - cart bytecode has FEWER sub-anim dispatch cases than dos/amiga
;     (issue 0079) — only 2 single-case dispatchers vs 4 cases each
;     elsewhere. This is concrete evidence cart was built from a
;     simplified or earlier source revision.
""",

    "CAVES": """\
; STAGE CAVES: ventilation shafts + cave system + floor-mauler maze.
;
; Gameplay role: after dropping into the vents in PRISON, Lester:
;   1. Rolls through ventilation shafts dodging timed gas-bursts.
;   2. Drops out of the vents into a cave system.
;   3. Falls down successive pits into a graveyard of bones.
;   4. Navigates falling-boulder corridors (timing-based).
;   5. Battles "stranglers" (ceiling vines) and "floor maulers"
;      (suction holes) across multiple screens.
;   6. Super-blasts a wall to set up a later flooding event,
;      then back-tracks. Eventually meets up with the alien friend
;      again to flood the cave system.
;
; Branches that ship CAVES:
;   chahi_amiga_1991, dos_1992, cartridge_1992 (genesis_eu).
;
; This is the largest unified stage by chunk count (264 folded
; bodies) — many routines handle per-screen physics, so the chunk
; tree is deep. CAVES + ENDING currently have empty post-fold chunks
; that block the empty-chunk removal pass (issue tracked).
""",

    "CAPSULE": """\
; STAGE CAPSULE: alien city, capsule ride, escape sequences.
;
; Gameplay role: after the cave-flooding rescue, Lester is in the
; alien city. He boards a flying capsule (or is captured into one)
; and traverses the city. Includes:
;   - Multiple alien character animations (sub-anim dispatchers
;     for hero AND alien sprites — see issue 0080 for divergent
;     CIN ranges between cart/dos/amiga arms).
;   - Capsule travel sequence with parallax scrolling.
;   - Setup for the TANK arena combat that follows.
;
; Branches that ship CAPSULE:
;   chahi_amiga_1991, dos_1992, cartridge_1992 (genesis_eu).
;
; Notable per-arm divergence: the alien sprite uses entirely
; different cinematic indices in amiga 1991 vs cart/dos 1992 —
; suggesting the 1992 ports renumbered indices rather than preserving
; the 1991 layout (issue 0080).
""",

    "TANK": """\
; STAGE TANK: alien arena tank-combat sequence.
;
; Gameplay role: Lester pilots an alien tank in an arena, fighting
; enemy tanks and obstacles. The smallest of the action stages.
;
; Branches that ship TANK:
;   chahi_amiga_1991, dos_1992, cartridge_1992 (genesis_eu).
;
; Structure: only 24 folded shared bodies (vs 264 in CAVES) — the
; bytecode is tightly focused on tank movement, projectile state
; machines, and HUD updates. Most of the per-arm divergence is
; concentrated in initial banker setups and music marks.
""",

    "ENDING": """\
; STAGE ENDING: final cinematic + escape on the pteranodon-creature.
;
; Gameplay role: closing cinematic after all gameplay stages
; complete. The alien friend rescues Lester one last time and they
; ride off together on a giant flying creature.
;
; Branches that ship ENDING:
;   chahi_amiga_1991, dos_1992, cartridge_1992 (genesis_eu).
;
; Structure: only 28 folded bodies. Mostly DRAW_CIN_<N>_TO_<M>
; sequences and PALETTE_FADE animations. Like CAVES, has empty
; post-fold chunks blocking the cleanup pass.
""",

    "PASSCODE": """\
; STAGE PASSCODE: password-entry screen for save-state restoration.
;
; Gameplay role: shown before the game starts (or between sessions)
; to let players resume from a stored checkpoint. Hashes the entered
; characters into per-stage save vectors. Replaces the checkpoint
; system on platforms without battery-backed save.
;
; Branches that ship PASSCODE:
;   chahi_amiga_1991, dos_1992, cartridge_1992 (genesis_eu).
;
; Smallest unified file (only 6 folded bodies). The hashing logic
; (SUM_HASH_VARS_TO_VAR_37) is one of the most analyzed routines
; in the genealogy work — it's structurally identical across all
; three branches.
""",

    "CODE_WHEEL": """\
; STAGE CODE_WHEEL: anti-piracy code-wheel protection screen.
;
; Gameplay role: shown before INTRO on amiga 1991 and dos 1992. The
; player rotated a paper code-wheel that came with the game and
; entered the matching symbols on screen. NOT present on cartridge
; ports (snes/genesis) or GBA — those use ROM-baked content with no
; protection layer.
;
; Branches that ship CODE_WHEEL:
;   chahi_amiga_1991, dos_1992 (cartridge ports skip this stage).
;
; Structure: 14 folded bodies dominated by palette fades
; (PAL_FADE_*) and resource loads — the actual code-check logic is
; small. Resource 13 holds the wheel imagery.
""",
}


HEADER_MARKER = "; STAGE "


def add_header(asm_in: Path, header: str) -> bool:
    """Prepend `header` to `asm_in` if not already present.
    Returns True if the file was modified."""
    text = asm_in.read_text()
    if HEADER_MARKER in text.splitlines()[0] if text.splitlines() else "":
        return False
    if text.startswith("; STAGE "):
        return False
    new = header.rstrip() + "\n;\n" + text
    asm_in.write_text(new)
    return True


BRANCH_LABELS = {
    "cartridge_1992": "cartridge_1992 (Heineman SNES + Genesis port)",
    "dos_1992": "dos_1992 (Daniel Morais MS-DOS port)",
    "chahi_amiga_1991": "chahi_amiga_1991 (Eric Chahi original Amiga release)",
    "gba_2004": "gba_2004 (Foxy Game Boy Advance port)",
}


def per_branch_header(stage: str, branch: str) -> str:
    body = HEADERS.get(stage)
    if body is None:
        return ""
    # Replace the "Branches that ship STAGE" block with a single
    # this-branch line. Match from "; Branches that ship" to either
    # "; Notable" or end of the indented block.
    lines = body.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("; Branches that ship"):
            out.append(f"; This file: {BRANCH_LABELS.get(branch, branch)}")
            out.append(";")
            # Skip until a blank or start-of-section line
            i += 1
            while i < len(lines):
                nxt = lines[i]
                # Stop at the next blank `;` line or a `; ` paragraph
                # boundary that starts with a non-indented `;`.
                if nxt.strip() == ";" or (
                    nxt.startswith("; ") and not nxt.startswith(";   ")
                ):
                    break
                i += 1
            continue
        out.append(ln)
        i += 1
    return "\n".join(out)


def main() -> int:
    n_added = 0
    for stage, header in HEADERS.items():
        path = LEVELS / "_unified" / f"{stage}.asm.in"
        if not path.is_file():
            print(f"  {stage}: SKIP (no .asm.in)")
            continue
        if add_header(path, header):
            n_added += 1
            print(f"  {stage}: header added ({len(header.splitlines())} lines)")
        else:
            print(f"  {stage}: already had header")
    print(f"\nHeaders added to {n_added} unified files.")

    # Per-branch sources: src/levels/<branch>/<STAGE>.asm
    n_per_branch = 0
    for asm in sorted(LEVELS.glob("*/*.asm")):
        if asm.parent.name in {"_unified", "_canonicalized"}:
            continue
        branch = asm.parent.name
        stage = asm.stem
        hdr = per_branch_header(stage, branch)
        if not hdr:
            continue
        if add_header(asm, hdr):
            n_per_branch += 1
            print(f"  {branch}/{stage}: header added")
    print(f"Headers added to {n_per_branch} per-branch files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
