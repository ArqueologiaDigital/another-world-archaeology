#!/usr/bin/env python3
"""Phase 4 / Round 6: 37 more FOLD_BODY routines named from body shape.

Same machinery as round_5: substitutes references in `.asm.in` and
`.inc` files (word-boundary AND embedded-in-include-path), then
renames per-arm chunk filenames containing the old routine name.
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
    # Single-instruction var ops.
    "FOLD_BODY_39B_1F847B0B": "ADD_VAR11_TO_VAR34",
    "FOLD_BODY_39B_42136843": "ADD_VAR2C_TO_VAR22",
    "FOLD_BODY_56B_4EE7BD2B": "RESET_HERO_POS_UP_DOWN",
    "FOLD_BODY_61B_7F8B309C": "COPY_HACK67_TO_VAR66",

    # HACK_VAR_67 modifiers.
    "FOLD_BODY_66B_160F1222": "ADD_HACK67_BY_20",
    "FOLD_BODY_66B_46DFEAE8": "DECR_HACK67_BY_1",
    "FOLD_BODY_66B_53AF86AC": "SUB_HACK67_BY_20",
    "FOLD_BODY_66B_F424839D": "INCR_HACK67_BY_1",

    # Page copy / load helpers.
    "FOLD_BODY_50B_2E2F4B8F": "LOAD_RES44_AND_RET",
    "FOLD_BODY_53B_52FF562C": "COPY_PAGE3_TO_PAGE0",
    "FOLD_BODY_53B_A9F04A42": "COPY_PAGE0_TO_PAGE_FF",

    # Set + killChannel pairs.
    "FOLD_BODY_62B_70C62EFD": "COPY_VAR51_TO_VAR02_KILL_CHANNEL",
    "FOLD_BODY_62B_8F5AB86B": "COPY_VAR52_TO_VAR02_KILL_CHANNEL",
    "FOLD_BODY_67B_A547ACF5": "SET_VAR01_TO_6E_KILL_CHANNEL",
    "FOLD_BODY_67B_EB770918": "SET_VARE6_TO_64_KILL_CHANNEL",
    "FOLD_BODY_76B_D2CE1407": "COPY_PAGE0_TO_FF_KILL_CHANNEL",

    # Inline init bundles.
    "FOLD_BODY_79B_5AA87B0D": "COMPUTE_VARF8_AS_VAR22_MINUS_VAR09",
    "FOLD_BODY_84B_8EB32F8E": "INIT_VAR09_TO_7_VAR08_FROM_VAR22",
    "FOLD_BODY_84B_B02DE811": "INIT_VAR08_FROM_VARE9_VAR09_TO_4",
    "FOLD_BODY_89B_5CFB4923": "ADD_VAR43_VAR47_BY_20",
    "FOLD_BODY_94B_44BEEF04": "COMPUTE_VAR26_AS_VAR21_MINUS_VAR22",

    # 96B_*: draw a single CINEMATIC at (var21,var22)/(var03,var04)/etc.
    "FOLD_BODY_96B_8BB50141": "DRAW_CIN036_AT_X03_Y04",
    "FOLD_BODY_96B_28B75A30": "DRAW_CIN039_AT_X03_Y04",
    "FOLD_BODY_96B_B594DD37": "DRAW_CIN042_AT_X03_Y04",
    "FOLD_BODY_96B_08D73B81": "DRAW_CIN045_AT_X03_Y04",
    "FOLD_BODY_96B_FC4E0356": "DRAW_CIN048_AT_X03_Y04",
    "FOLD_BODY_96B_3E51165F": "DRAW_CIN051_AT_X03_Y04",
    "FOLD_BODY_96B_1558398F": "DRAW_CIN054_AT_X03_Y04",
    "FOLD_BODY_96B_D2F4C2E9": "DRAW_CIN057_AT_X03_Y04",
    "FOLD_BODY_96B_BEDD0A4B": "DRAW_CIN060_AT_X03_Y04",
    "FOLD_BODY_96B_8FDF7DB5": "DRAW_CIN063_AT_X03_Y04",
    "FOLD_BODY_96B_C7EF291A": "DRAW_CIN066_AT_X03_Y04",
    "FOLD_BODY_96B_787FEDD5": "DRAW_CIN069_AT_X03_Y04",
    "FOLD_BODY_96B_B0A5B60F": "DRAW_CIN072_AT_X03_Y04",
    "FOLD_BODY_96B_7EA5CCF5": "DRAW_CIN075_AT_X03_Y04",
    "FOLD_BODY_96B_2FC90B25": "DRAW_CIN657_AT_X1A_Y1B",
    "FOLD_BODY_96B_9BEF2C97": "DRAW_CIN505_AT_X21_Y27",
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
