#!/usr/bin/env python3
"""Phase 4 / Round 7: 29 more FOLD_BODY routines named from body shape."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _paths import AW_SRC

SRC_ROOT = AW_SRC
LEVELS = SRC_ROOT / "src/levels"

RENAMES: dict[str, str] = {
    # 99B_*: single common-video draw at (var01,var02) or (var07,var08).
    "FOLD_BODY_99B_3B6BC4B3": "DRAW_CV261_AT_X07_Y08",
    "FOLD_BODY_99B_3F1B076D": "DRAW_CV249_AT_X07_Y08",
    "FOLD_BODY_99B_535C94C0": "DRAW_CV263_AT_X07_Y08",
    "FOLD_BODY_99B_5D0924A3": "DRAW_CV139_AT_X01_Y02",
    "FOLD_BODY_99B_6E4C0150": "DRAW_CV101_AT_X01_Y02",
    "FOLD_BODY_99B_76C60EB2": "DRAW_CV275_AT_X07_Y08",
    "FOLD_BODY_99B_79867FEB": "DRAW_CV111_AT_X01_Y02",
    "FOLD_BODY_99B_8CB26FD2": "DRAW_CV107_AT_X01_Y02",
    "FOLD_BODY_99B_903D2AE1": "DRAW_CV097_AT_X01_Y02",
    "FOLD_BODY_99B_95D61F48": "DRAW_CV246_AT_X07_Y08",
    "FOLD_BODY_99B_A1B2ECF4": "DRAW_CV099_AT_X01_Y02",
    "FOLD_BODY_99B_AA083516": "DRAW_CV113_AT_X01_Y02",
    "FOLD_BODY_99B_B1A35EFA": "DRAW_CV109_AT_X01_Y02",
    "FOLD_BODY_99B_C53D6EC4": "DRAW_CV105_AT_X01_Y02",
    "FOLD_BODY_99B_C6015BD9": "DRAW_CV204_AT_X07_Y08",
    "FOLD_BODY_99B_D1658A70": "DRAW_CV259_AT_X07_Y08",
    "FOLD_BODY_99B_D8CF1AF9": "DRAW_CV224_AT_X07_Y08",
    "FOLD_BODY_99B_DC229063": "DRAW_CV103_AT_X01_Y02",

    # 200B_*: draw a common-video frame, then play SFX 0x60 with
    # parametric freq/vol/channel.
    "FOLD_BODY_200B_12AD66EF": "DRAW_CV108_PLAY_60_F0F_V2A_C0",
    "FOLD_BODY_200B_1AFE2B0B": "DRAW_CV078_PLAY_60_F0B_V22_C1",
    "FOLD_BODY_200B_37F93421": "DRAW_CV108_PLAY_60_F0F_V2A_C1",
    "FOLD_BODY_200B_44886950": "DRAW_CV098_PLAY_60_F0A_V2A_C1",
    "FOLD_BODY_200B_5D805D1F": "DRAW_CV070_PLAY_60_F14_V20_C1",
    "FOLD_BODY_200B_FF681770": "DRAW_CV098_PLAY_60_F0F_V2A_C0",

    # 156B_*: per-scene setups (HACK_67 + assorted vars).
    "FOLD_BODY_156B_189DA618": "SETUP_67_25_VAR06_0_VARB1_NOSIGN",
    "FOLD_BODY_156B_579DE25B": "SETUP_67_45_VAR01_46_VARB1_NOSIGN",
    "FOLD_BODY_156B_62098AC6": "SETUP_67_67_VAR01_1E_VARBE_3",

    # Misc.
    "FOLD_BODY_97B_E091A810": "INIT_VAR6F_TO_A_PAUSE_3",
    "FOLD_BODY_84B_B2820056": "TOGGLE_SIGN_VAR26_INIT_VAR25_FROM_VAR44",
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
