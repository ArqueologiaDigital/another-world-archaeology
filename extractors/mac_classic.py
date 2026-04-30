"""Macintosh classic StuffIt + resource-fork extractor.

Delegates to AWVM_Tools' `mac-stuffit-extract` Rust binary, which
parses StuffIt 5 archives via the `stuffit` crate and writes each
entry's data fork + resource fork to the output directory as
`<safe_name>.data` and `<safe_name>.rsrc`.

For the 1993 Mac fixture (`out_of_this_world.sit`, 3.7 MiB), this
yields **141 entries** including:

- **Three application builds** (v1.0, v1.0.2, v1.0.3) each with its
  own ~525 KB resource fork. The AW VM bytecode and engine code
  live in these resource forks — a 68k Mac sibling to the Anniversary
  engine codebase.
- **Two updater apps** (v1.0→1.0.3, "mv" v1.0→1.0.3) — patch deltas
  worth diffing.
- **AW data files** matching a `Data/FILE0020..FILE0146` pattern,
  per-version. Likely holds the AW resource banks in a Mac-flavour
  layout (potentially mappable to the canonical AW resource indices).
- Codewheel JPEGs, solve text, MacPlay branding pictures.

Output layout under `work_dir/`:
  contents/   <- one .data file per entry, plus .rsrc when non-empty
  manifest.json

The resource forks need a separate **rsrc walker** to surface
individual Mac resources (TYPE+ID-keyed: 'BANK', 'POLY', 'PICT',
etc.). That's the next step; the `macbinary` crate is already in
the workspace dependencies for it.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO.parent / "AnotherWorld_VMTools" / "target" / "release" / "mac-stuffit-extract"


def extract(release_meta, archive_dir: Path, work_dir: Path) -> dict:
    sits = list(archive_dir.glob("*.sit"))
    if not sits:
        raise FileNotFoundError(f"mac-classic: no .sit in {archive_dir}")
    sit_path = sits[0]

    if not TOOL.is_file():
        raise RuntimeError(
            f"mac-classic: AWVM_Tools mac-stuffit-extract binary not built at {TOOL} "
            "(run `cargo build --release` in AnotherWorld_VMTools)"
        )

    work_dir.mkdir(parents=True, exist_ok=True)
    out_dir = work_dir / "contents"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir()

    subprocess.run(
        [str(TOOL), str(sit_path), str(out_dir)],
        check=True,
    )

    files = sorted(p.relative_to(out_dir).as_posix()
                   for p in out_dir.rglob("*") if p.is_file())
    rsrc_count = sum(1 for f in files if f.endswith(".rsrc"))

    manifest = {
        "format": "mac-classic",
        "source_sit": sit_path.name,
        "resource_count": len(files),
        "rsrc_fork_count": rsrc_count,
        "files": files,
    }
    (work_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
