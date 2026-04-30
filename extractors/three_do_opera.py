"""3DO Opera filesystem extractor (`.bin`/`.cue`).

Delegates to the Rust `opera-list` binary in AWVM_Tools, which
reads CD-ROM Mode 1 sectors out of the `.bin` image and walks the
proprietary 3DO Opera filesystem (volume header at sector 0,
hash-tableless directory blocks with linked-list chaining, avatar
mirrors for redundancy).

Output is the on-disc directory tree mirrored under
`work_dir/disc/`. The 3DO release uses the same VM bytecode
engine as the bank-format DOS/Amiga releases, but the resources
are stored as individual files in the filesystem (e.g.
`GameData/File1`, `GameData/song1`, `EndShape1` …) rather than
packed into bank files. Mapping these on-disc files back to the
canonical AW resource indices is a separate research step — for
now we just dump the disc.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO.parent / "AnotherWorld_VMTools" / "target" / "release" / "opera-list"


def extract(release_meta, archive_dir: Path, work_dir: Path) -> dict:
    bin_files = [f for f in release_meta.get("files", []) if f["name"].lower().endswith(".bin")]
    if not bin_files:
        raise FileNotFoundError(
            f"3do-opera: no .bin file listed in metadata for {release_meta.get('slug')!r}"
        )
    bin_path = archive_dir / bin_files[0]["name"]
    if not bin_path.is_file():
        raise FileNotFoundError(f"3do-opera: missing {bin_path}")

    if not TOOL.is_file():
        raise RuntimeError(
            f"3do-opera: AWVM_Tools opera-list binary not built at {TOOL} "
            "(run `cargo build --release` in AnotherWorld_VMTools)"
        )

    out_dir = work_dir / "disc"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    result = subprocess.run(
        [str(TOOL), str(bin_path), "--extract", str(out_dir)],
        check=True,
        capture_output=True,
        text=True,
    )

    extracted = sorted(p.relative_to(out_dir).as_posix() for p in out_dir.rglob("*") if p.is_file())
    manifest = {
        "format": "3do-opera",
        "source": str(bin_path.relative_to(REPO.parent.parent) if bin_path.is_relative_to(REPO.parent.parent) else bin_path),
        "resource_count": len(extracted),
        "files": extracted,
    }
    (work_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
