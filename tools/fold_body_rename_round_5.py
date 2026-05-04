#!/usr/bin/env python3
"""Phase 4 / Round 5: rename FOLD_BODY routines whose 3-instruction
bodies have a clearly recognizable role.

Each entry below was hand-derived by inspecting the body of the
routine in `_unified/<STAGE>.asm.in`. Renames are applied across
every `.asm.in` and `_unified/<stage>/*.inc` file. Per-arm chunk
filenames containing the old name are also renamed.

Verification: caller runs verify_unified after, expects 27/27.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC_ROOT = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
LEVELS = SRC_ROOT / "src/levels"

RENAMES: dict[str, str] = {
    # Per-frame coordinate steppers.
    "FOLD_BODY_104B_04347EF0": "STEP_VAR1A_DOWN5_VAR1B_UP2",
    "FOLD_BODY_104B_1F1C2592": "RESET_VAR09_AND_INCR_VAR08_BY_2",
    "FOLD_BODY_104B_DD7FE6E8": "RESET_VAR09_AND_DECR_VAR08_BY_4",
    "FOLD_BODY_104B_F18A2F7D": "STEP_VAR29_DOWN10_SET_VAR2F_11",
    # Resource and audio helpers.
    "FOLD_BODY_104B_FC3A9361": "COPY_PAGE0_TO_3_LOAD_RES45",
    "FOLD_BODY_108B_0013C19A": "PLAY_FX_6B_THEN_KILL_CHANNEL",
    "FOLD_BODY_140B_B5EAC4C0": "LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91",
    # Inline init bundles.
    "FOLD_BODY_124B_BC056530": "INIT_VAR2B_2C_FROM_VAR01_VAR29_10",
    "FOLD_BODY_127B_F42DCE4F": "RESET_HERO_ACTION_KEEP_POS_4LSB",
    "FOLD_BODY_129B_767CC053": "BREAK_5X_THEN_INIT_VAR03_14",
    "FOLD_BODY_134B_B0E8D936": "STEP_VARE9_UP10_VARE8_DOWN1_RESET_VAREC_6",
    "FOLD_BODY_159B_CB73A242": "COPY_VARE6E7_TO_VARE8_E9_EA_EB",
    # SFX setters with var-EE/ED prelude.
    "FOLD_BODY_130B_4DFBAD53": "PLAY_FX_56_CH3_SET_VAREE_F",
    "FOLD_BODY_130B_6E856A94": "PLAY_FX_30_CH2_VOL_C_SET_VARED_A",
    "FOLD_BODY_130B_E4F6665A": "PLAY_FX_52_CH3_SET_VARED_A",
    "FOLD_BODY_130B_ED8A3E7F": "PLAY_FX_30_CH2_LOUD_SET_VARED_5",
    # Scrolling helpers.
    "FOLD_BODY_153B_C643A158": "SCROLL_UP_16_VAR14_VAR18_AND_SCROLL_Y",
    # Cinematic draws.
    "FOLD_BODY_156B_9635F3D1": "DRAW_CIN473_AT_X21_Y27_ZOOM_40",
    "FOLD_BODY_156B_C0A1A8CA": "DRAW_CIN489_AT_X21_Y27_ZOOM_40",
}


def main() -> int:
    targets: list[Path] = []
    targets += sorted(LEVELS.glob("_unified/*.asm.in"))
    targets += sorted(LEVELS.glob("_unified/*/*.inc"))

    n_files_changed = 0
    n_substitutions = 0
    for path in targets:
        text = path.read_text()
        new = text
        local = 0
        for old_name, new_name in RENAMES.items():
            # Word-boundary substitution catches label / call / jmp uses.
            count = len(re.findall(rf"\b{re.escape(old_name)}\b", new))
            new, n_label = re.subn(
                rf"\b{re.escape(old_name)}\b", new_name, new)
            # Embedded substitution catches occurrences inside chunk
            # filenames in `;@include` paths (e.g.
            # `cart__post_FOLD_BODY_X.inc`) where the leading `_` and
            # trailing `.` block standard `\b` matching.
            n_path = new.count(f"_post_{old_name}.")
            new = new.replace(f"_post_{old_name}.", f"_post_{new_name}.")
            local += n_label + n_path
        if local:
            path.write_text(new)
            n_files_changed += 1
            n_substitutions += local

    n_files_renamed = 0
    for old_name, new_name in RENAMES.items():
        for chunk in sorted(LEVELS.glob(f"_unified/*/*__post_{old_name}.inc")):
            new_path = chunk.with_name(
                chunk.name.replace(f"post_{old_name}", f"post_{new_name}")
            )
            chunk.rename(new_path)
            n_files_renamed += 1

    print(f"Substitutions: {n_substitutions} across {n_files_changed} files")
    print(f"Files renamed: {n_files_renamed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
