#!/usr/bin/env python3
"""Phase 4 / Round 8: 13 more FOLD_BODY routines named from body shape.

Catches step+draw walk-cycles, var-arithmetic helpers, and a few
miscellaneous routines that escaped previous rounds (89B, 93B were
inspected but accidentally not included earlier).
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
    # Var-arithmetic helpers.
    "FOLD_BODY_89B_E0F8C267": "MASK_VAR11_NOSIGN_INCR_VAR21_BY_14",
    "FOLD_BODY_93B_2C2B4311": "COPY_PAGE0_TO_3_AND_VAR66_TO_VAR65",
    "FOLD_BODY_99B_913256B4": "COMPUTE_VAR22_AS_VAR40_MINUS_28",
    "FOLD_BODY_219B_89086759": "MUL_VAR6B_BY_11_INTO_VAR21",

    # Single-step + draw + reposition.
    "FOLD_BODY_206B_44F9C1BD": "STEP_DRAW_CV352_LEFT4_RIGHT1",
    "FOLD_BODY_206B_F444FCB9": "DRAW_CV352_STEP_RIGHT3",
    "FOLD_BODY_203B_06F694A2": "STEP_DRAW_CIN555_LEFT4_RIGHT1",
    "FOLD_BODY_203B_4BED9F88": "DRAW_CIN555_STEP_RIGHT3",

    # Multi-frame walk cycles.
    "FOLD_BODY_223B_DDF457BD": "STEP_LEFT4_DRAW_CV140_LEFT4",
    "FOLD_BODY_358B_6F629262": "WALK_RIGHT_DRAW_CV142_MULTISTEP",
    "FOLD_BODY_358B_DF9AE0DF": "WALK_LEFT_DRAW_CV140_MULTISTEP",

    # 2-frame video sequences.
    "FOLD_BODY_261B_43CF2CB1": "STEP_DRAW_CV329_THEN_CV335",
    "FOLD_BODY_261B_7A9CE2F7": "STEP_DRAW_CV336_THEN_CV340",
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
