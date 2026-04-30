"""Macintosh classic StuffIt + resource-fork extractor.

Two-stage pipeline:

1. **mac-stuffit-extract** (Rust binary in AWVM_Tools): unpacks the
   StuffIt 5 archive, decompresses each entry's data fork + resource
   fork, writes them as `<safe_name>.data` / `<safe_name>.rsrc`.

2. **mac-rsrc-walk** (Rust binary in AWVM_Tools): for each non-empty
   `.rsrc` file, parses the Mac resource fork map and emits one file
   per individual resource, named `<TYPE>_<ID>[_<safe_name>].bin`.

For the 1993 Mac OOTW fixture (`out_of_this_world.sit`, 3.7 MiB):

- StuffIt stage yields **141 entries** including three application
  builds (v1.0, v1.0.2, v1.0.3), two updater apps, codewheel JPEGs,
  solve text, MacPlay branding pictures, and per-version
  `Data/FILE0020..FILE0146` files (the data-fork-side AW resource
  blobs — these are byte-identical between versions, since they
  carry the platform-independent VM resources).
- Resource-fork-walk stage yields **395+ per-resource files per app
  version**, including 7 `CODE` segments (68k engine code, the
  Mac-specific part), 192 `Estr` strings, 97 `snd` resources,
  several `PICT`s, custom `OOTW` copyright stamps, and the standard
  Mac UI flotsam (`ALRT`, `DITL`, `DLOG`, `MENU`, `WIND`, `vers`,
  etc.).

Output layout under `work_dir/`:
  contents/                <- StuffIt stage: <name>.data + <name>.rsrc per entry
  rsrc/<safe_app_name>/    <- rsrc-walk stage: per-resource bins
  manifest.json
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL_SIT = REPO.parent / "AnotherWorld_VMTools" / "target" / "release" / "mac-stuffit-extract"
TOOL_RSRC = REPO.parent / "AnotherWorld_VMTools" / "target" / "release" / "mac-rsrc-walk"


def _safe(name: str) -> str:
    """Filesystem-safe name preserving alnum + .-_  ."""
    return "".join(c if (c.isalnum() or c in "._- ") else "_" for c in name)


def extract(release_meta, archive_dir: Path, work_dir: Path) -> dict:
    sits = list(archive_dir.glob("*.sit"))
    if not sits:
        raise FileNotFoundError(f"mac-classic: no .sit in {archive_dir}")
    sit_path = sits[0]

    for tool in (TOOL_SIT, TOOL_RSRC):
        if not tool.is_file():
            raise RuntimeError(
                f"mac-classic: AWVM_Tools binary not built at {tool} "
                "(run `cargo build --release` in AnotherWorld_VMTools)"
            )

    work_dir.mkdir(parents=True, exist_ok=True)
    contents_dir = work_dir / "contents"
    if contents_dir.exists():
        shutil.rmtree(contents_dir)
    contents_dir.mkdir()

    # Stage 1: StuffIt unpack
    subprocess.run(
        [str(TOOL_SIT), str(sit_path), str(contents_dir)],
        check=True,
    )

    # Stage 2: Walk every resource fork. We name each per-app rsrc
    # subfolder with a slug derived from the .rsrc filename's stem,
    # trimmed to the bit before the first underscore-prefixed
    # subpath component (to keep names readable when stuffit's
    # safe-naming injected underscores for slashes).
    rsrc_root = work_dir / "rsrc"
    if rsrc_root.exists():
        shutil.rmtree(rsrc_root)
    rsrc_root.mkdir()

    rsrc_walked = 0
    for rsrc_file in sorted(contents_dir.glob("*.rsrc")):
        stem = rsrc_file.stem
        out_sub = rsrc_root / _safe(stem)
        out_sub.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [str(TOOL_RSRC), str(rsrc_file), str(out_sub)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            # Non-fatal — some .rsrc files might be MacBinary-wrapped or
            # otherwise non-standard. Log and continue.
            print(f"  WARN: mac-rsrc-walk failed on {rsrc_file.name}: "
                  f"{result.stderr.strip().splitlines()[-1] if result.stderr else result.returncode}")
        else:
            rsrc_walked += 1

    # Build manifest
    files = sorted(p.relative_to(work_dir).as_posix()
                   for p in work_dir.rglob("*") if p.is_file())
    rsrc_count = sum(1 for f in files if f.startswith("contents/") and f.endswith(".rsrc"))
    per_resource_count = sum(1 for f in files if f.startswith("rsrc/"))

    manifest = {
        "format": "mac-classic",
        "source_sit": sit_path.name,
        "resource_count": len(files),
        "rsrc_fork_count": rsrc_count,
        "rsrc_walked_count": rsrc_walked,
        "per_resource_count": per_resource_count,
        "files": files,
    }
    (work_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
