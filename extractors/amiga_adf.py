"""Amiga ADF disk-image extractor.

Delegates to the Rust `adf-extract` binary in AWVM_Tools. The binary
reads OFS/FFS Amiga disk images and writes every contained file to
the output directory.

Two archive layouts are supported:

- **bare ADFs** (e.g. `amiga-archive-org/`): the archive directory
  itself contains `*.adf` files; we hand each one to `adf-extract`.

- **double-zipped retro-presskit** (`5dca377e0e15.../AnotherWorld-Retro-presskit.zip`):
  the outer zip contains `Amiga_version_BONUS.zip` which contains
  the two `.adf` files. We unpack the outer zip, then the inner
  zip, into a working directory, then run `adf-extract`.

Output layout under `work_dir/`:
  bin/   <- every file from every ADF (banks + memlist.bin etc.)
  manifest.json

The bin/ directory is the raw on-disk layout of the AW game files.
For the retro-presskit ADFs (the no-logo / no-protection build),
this yields `bank01..bank0D` plus `memlist.bin` plus a startup
binary — the same generation as the bank-format DOS release, with
`memlist.bin` already present (unlike the Atari ST 1991 release
where the memlist is embedded inside START.PRG).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO.parent / "AnotherWorld_VMTools" / "target" / "release" / "adf-extract"


def _stage_adfs(archive_dir: Path, staging: Path) -> list[Path]:
    """Return a list of `.adf` paths, materialising them inside `staging`
    if they're nested in zip(s)."""
    bare = sorted(archive_dir.glob("*.adf"))
    if bare:
        return bare

    # No bare ADFs: peel zips. We support up to one level of nested zip
    # (which covers the AW retro-presskit's outer→inner layout).
    staging.mkdir(parents=True, exist_ok=True)
    for outer in archive_dir.glob("*.zip"):
        with zipfile.ZipFile(outer) as zf:
            zf.extractall(staging)

    inner_zips = list(staging.rglob("*.zip"))
    for inner in inner_zips:
        with zipfile.ZipFile(inner) as zf:
            zf.extractall(staging)

    found = sorted(staging.rglob("*.adf"))
    if not found:
        raise FileNotFoundError(f"amiga-adf: no ADF found in {archive_dir} or its zips")
    return found


def extract(release_meta, archive_dir: Path, work_dir: Path) -> dict:
    if not TOOL.is_file():
        raise RuntimeError(
            f"amiga-adf: AWVM_Tools adf-extract binary not built at {TOOL} "
            "(run `cargo build --release` in AnotherWorld_VMTools)"
        )

    work_dir.mkdir(parents=True, exist_ok=True)
    staging = work_dir / "_staging"
    if staging.exists():
        shutil.rmtree(staging)

    adfs = _stage_adfs(archive_dir, staging)

    bin_dir = work_dir / "bin"
    if bin_dir.exists():
        shutil.rmtree(bin_dir)
    bin_dir.mkdir()

    # adf-extract's CLI takes all input ADFs followed by the output dir
    # last (the binary's printed usage line is misleading on this point).
    cli = [str(TOOL), *[str(p) for p in adfs], str(bin_dir)]
    subprocess.run(cli, check=True)

    if staging.exists():
        shutil.rmtree(staging)

    files = sorted(p.relative_to(work_dir).as_posix()
                   for p in work_dir.rglob("*") if p.is_file())
    manifest = {
        "format": "amiga-adf",
        "source_adfs": [p.name for p in adfs],
        "resource_count": len(files),
        "files": files,
    }
    (work_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
