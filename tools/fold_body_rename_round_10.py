#!/usr/bin/env python3
"""Phase 4 / Round 10: name 2 more FOLD_BODY routines I had skipped
earlier as ambiguous. Re-examined now that the chapter-split sweep
made the surrounding context easier to read.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from _paths import AW_SRC

SRC_ROOT = AW_SRC
LEVELS = SRC_ROOT / "src/levels"

RENAMES: dict[str, str] = {
    # 4-instruction scene-init bundle: increment var07 + set 2 flag
    # bits + initialize var29 to 0x10. Clear "set up scene state".
    "FOLD_BODY_177B_6AEF7E27": "INCR_VAR07_OR_VARBB_VAR73_INIT_VAR29",
    # Bit-math: derives varF8 from low bits of varB1 + low bits of
    # varB2 plus 0x29. Looks like an index computation for some
    # downstream lookup.
    "FOLD_BODY_254B_838374D1": "DERIVE_VARF8_FROM_VARB1_LO5_VARB2_LO2_PLUS_29",
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
        for chunk in sorted(LEVELS.glob(f"_unified/*/*__post_{old_name}.inc")):
            new_path = chunk.with_name(
                chunk.name.replace(f"post_{old_name}", f"post_{new_name}")
            )
            chunk.rename(new_path)
            n_files_renamed += 1
        helper = LEVELS / "_unified" / "_helpers" / f"{old_name}.inc"
        if helper.is_file():
            helper.rename(helper.with_name(f"{new_name}.inc"))
            n_files_renamed += 1

    print(f"Substitutions: {n_substitutions} across {n_files_changed} files")
    print(f"Files renamed: {n_files_renamed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
