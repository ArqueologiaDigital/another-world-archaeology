#!/usr/bin/env python3
"""Phase 4 / Round 9: 24 more FOLD_BODY routines named from body shape.

This pass tackles the long-tail screen-position projection family
(144B / 189B) where each routine differs only in its constants —
they all compute `var22 = <base> ± ((var21 ± <K>) [>><S>])`. Names
encode the formula directly so callers can read them without
chasing the body.

Skipped: a handful of routines with ambiguous bodies (overwriting
the same var, two-entry-point patterns, or arithmetic mixing 4+
variables in non-standard ways) — those need archaeological
context that body-shape alone doesn't provide.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _paths import AW_SRC

SRC_ROOT = AW_SRC
LEVELS = SRC_ROOT / "src/levels"

RENAMES: dict[str, str] = {
    # 144B family — linear projections `var22 = base ± (var21 ± K)`.
    "FOLD_BODY_144B_40C2B933": "PROJ_VAR22_AC_MINUS_VAR21_MINUS_CA",
    "FOLD_BODY_144B_552673A7": "PROJ_VAR22_B0_PLUS_VAR21_MINUS_69",
    "FOLD_BODY_144B_5C7E9C90": "INIT_VAR29_FROM_VAR50_PLUS_A_VAR2F_10",
    "FOLD_BODY_144B_7EE4E4CB": "PROJ_VAR22_B0_PLUS_VAR21_MINUS_9A",
    "FOLD_BODY_144B_B5377D0B": "PROJ_VAR22_37_PLUS_VAR21_PLUS_A",
    "FOLD_BODY_144B_FF58C6C8": "PROJ_VAR22_85_PLUS_VAR21_MINUS_56",

    # 189B family — projections with shr/shl scaling.
    "FOLD_BODY_189B_04CB328E": "PROJ_VAR22_2F_MINUS_VAR21_MINUS_ED_SHR1",
    "FOLD_BODY_189B_1A09E69C": "PROJ_VAR22_A7_MINUS_VAR21_MINUS_125_SHR3",
    "FOLD_BODY_189B_3714FA4E": "PROJ_VAR22_49_MINUS_VAR21_MINUS_113_SHR4",
    "FOLD_BODY_189B_38FD38E3": "PROJ_VAR22_17_MINUS_VAR21_MINUS_F0_SHL3",
    "FOLD_BODY_189B_41906E76": "PROJ_VAR22_A8_MINUS_VAR21_MINUS_112_SHR4",
    "FOLD_BODY_189B_4CB9AFF5": "PROJ_VAR22_9E_MINUS_VAR21_MINUS_121_SHR3",
    "FOLD_BODY_189B_57569B89": "PROJ_VAR22_53_PLUS_VAR21_MINUS_106_SHR3",
    "FOLD_BODY_189B_615E7707": "PROJ_VAR22_76_MINUS_VAR21_MINUS_108_SHR5",
    "FOLD_BODY_189B_69E7A9C1": "PROJ_VAR22_75_MINUS_VAR21_MINUS_FD_SHR6",
    "FOLD_BODY_189B_79EC0326": "PROJ_VAR22_68_MINUS_VAR21_MINUS_F2_SHR4",
    "FOLD_BODY_189B_A75D286E": "PROJ_VAR22_B3_MINUS_VAR21_MINUS_109_SHR3",
    "FOLD_BODY_189B_C4F9E873": "PROJ_VAR22_AA_MINUS_VAR21_MINUS_115_SHR3",
    "FOLD_BODY_189B_E4233737": "PROJ_VAR22_7E_MINUS_VAR21_MINUS_11B_SHR4",

    # 189B_794E4590 — different shape: a 1-pixel-shifted CV draw.
    "FOLD_BODY_189B_794E4590": "DRAW_CV204_AT_X07_PLUS1_Y08",

    # Per-scene setup bundles (long var-init routines).
    "FOLD_BODY_245B_6670034A": "SETUP_67_4B_VARS_B0_3_01_50_AF_58_B1",
    "FOLD_BODY_290B_04233270": "SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3",
    "FOLD_BODY_291B_CAF21FBB": "SETUP_67_AF_VARS_01_A_02_82_BE_3_BD_7",
    "FOLD_BODY_467B_FEBF74B5": "SETUP_VARS_01_B0_02_B6_06_C7_28_FROM_01",

    # TANK scene-init.
    "FOLD_BODY_186B_85A3A196": "INIT_VARS_52_17C_53_75_54_40_55_8",

    # Audio + var increment.
    "FOLD_BODY_216B_BFBF5829": "INCR_VARE6_PLAY_FX55_2X_CH0_CH2",

    # Flag setup with bit-OR markers.
    "FOLD_BODY_237B_F9B523AC": "SETUP_VAR8B_6E_VAR97_B7_VAR96_0",

    # Single-instruction setters.
    "FOLD_BODY_44B_2015915F": "SET_VAREF_TO_6",
    "FOLD_BODY_44B_A2D1E16F": "SET_VARE6_TO_A",

    # Tween: 8 stepwise sub-VARE8 with break yields.
    "FOLD_BODY_326B_82B23B8C": "TWEEN_VARE8_DOWN_8_STEPS",

    # Resource preload (8 load-id calls).
    "FOLD_BODY_446B_2519A417": "PRELOAD_RES_6A_77_6D_6E_74_76_78_7C",
}


def main() -> int:
    targets: list[Path] = []
    targets += sorted(LEVELS.glob("_unified/*.asm.in"))
    targets += sorted(LEVELS.glob("_unified/*/*.inc"))
    targets += sorted(LEVELS.glob("_unified/_helpers/*.inc"))

    n_files_changed = 0
    n_substitutions = 0
    for path in targets:
        text = path.read_text()
        new = text
        local = 0
        for old_name, new_name in RENAMES.items():
            count = len(re.findall(rf"\b{re.escape(old_name)}\b", new))
            new = re.sub(rf"\b{re.escape(old_name)}\b", new_name, new)
            n_path = new.count(f"_post_{old_name}.")
            new = new.replace(f"_post_{old_name}.", f"_post_{new_name}.")
            local += count + n_path
        if local:
            path.write_text(new)
            n_files_changed += 1
            n_substitutions += local

    n_files_renamed = 0
    for old_name, new_name in RENAMES.items():
        # Per-arm chunks: `<arm>__post_<NAME>.inc`
        for chunk in sorted(LEVELS.glob(f"_unified/*/*__post_{old_name}.inc")):
            new_path = chunk.with_name(
                chunk.name.replace(f"post_{old_name}", f"post_{new_name}")
            )
            chunk.rename(new_path)
            n_files_renamed += 1
        # Cross-stage helpers: `_helpers/<NAME>.inc`
        helper = LEVELS / "_unified" / "_helpers" / f"{old_name}.inc"
        if helper.is_file():
            helper.rename(helper.with_name(f"{new_name}.inc"))
            n_files_renamed += 1

    print(f"Substitutions: {n_substitutions} across {n_files_changed} files")
    print(f"Files renamed: {n_files_renamed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
