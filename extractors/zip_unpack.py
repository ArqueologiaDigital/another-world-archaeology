"""Generic zip-unpack extractor.

For releases distributed as a zip whose payload doesn't fit any
existing format-specific extractor, we just unpack the zip into
`work_dir/contents/` so the contained files are available for
downstream investigation. Used by:

- `nds-rom` — Alekmaul's Nintendo DS homebrew, distributed as a zip
  containing the .nds binary plus a `wheel/` of codewheel JPEGs.
  The .nds itself doesn't carry the canonical AW resources — it
  loads user-supplied DOS bank01..bankNN at runtime — so for now
  this just exposes the package contents.

- `apple-ii-demake` — Vince Weaver's Apple II 8-bit demake, a zip
  containing two DOS 3.3 .dsk floppy images (140K each) plus
  documentation. The .dsks hold the demake's own assets, NOT
  canonical AW resource files (this is a very different engine).

Output layout under `work_dir/`:
  contents/   <- everything unpacked from the zip, preserving paths
  manifest.json
"""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path


def extract(release_meta, archive_dir: Path, work_dir: Path) -> dict:
    zips = list(archive_dir.glob("*.zip"))
    if not zips:
        raise FileNotFoundError(
            f"zip_unpack: no .zip in {archive_dir} for {release_meta.get('slug')!r}"
        )
    zip_path = zips[0]

    out_dir = work_dir / "contents"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(out_dir)

    files = sorted(p.relative_to(out_dir).as_posix()
                   for p in out_dir.rglob("*") if p.is_file())
    manifest = {
        "format": release_meta.get("format"),
        "source_zip": zip_path.name,
        "resource_count": len(files),
        "files": files,
    }
    (work_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
