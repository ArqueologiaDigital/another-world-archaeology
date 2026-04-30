"""Cartridge-format release extractor (SNES / Genesis / GBA).

Cartridge releases ship a single ROM file with the AW VM resources
embedded as hardcoded byte chunks at known offsets, plus per-release
font / chargen tables. AWVM_Tools' `awvm-disasm` already knows how to
walk these chunks (see `prepare_cartridge_romset` and the per-release
data tables in `awvm/src/releases/`); this extractor just stages the
ROM under the AWVM_Tools-expected filename and shells out to the
binary.

Output layout under `work_dir/`:
  romset/                 <- bytecode.rom + chargen / str_index / str_data
  disasm/level_<N>/       <- per-level disassembled .asm
  manifest.json

Per the engine constants in AWVM_Tools, the level count is 2 for
SNES/Genesis/GBA (vs 8 for bank-format DOS/Amiga) — those cartridge
ports are based on the abridged 2-level "demo" build of the engine.

The disasm prints non-fatal warnings about the cinematic decoder
("No such file or directory") because polygon data isn't present in
cartridge ports — this is a known limitation and does not prevent
bytecode disassembly from completing.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO.parent / "AnotherWorld_VMTools" / "target" / "release" / "awvm-disasm"

# Per-format ⇒ (AWVM-Tools-release-slug, expected-filename).
# AWVM_Tools' `prepare_cartridge_romset` opens this exact filename
# from its input_dir, so we stage the actual ROM under that name in
# the work directory before invoking the binary.
#
# `snes-rom` and `gba-rom` need slug disambiguation by region — the
# region-specific dispatch is handled in `_pick_target` below.
CARTRIDGE_TARGETS = {
    "snes-rom": {
        # Filename suffix on the actual ROM (lowercased) → (slug, expected name)
        ".sfc-eu": ("snes-eu", "Another World (Europe).sfc"),
        ".sfc-us": ("snes",    "Out of This World (USA).sfc"),
    },
    "genesis-rom": {".md": ("genesis_europe", "Another World (Europe).md")},
    "gba-rom":     {".gba": ("gba_usa", "Another World (Prototype) # GBA.GBA")},
}


def _extract_rom_to(zip_path: Path, work_dir: Path) -> Path:
    """Unzip the first ROM-like payload from `zip_path` into work_dir."""
    import zipfile
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if name.lower().endswith((".gba", ".sfc", ".smc", ".bin", ".rom", ".md", ".gen")):
                target = work_dir / Path(name).name
                with zf.open(name) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                return target
    raise FileNotFoundError(f"cartridge_rom: no ROM payload inside {zip_path}")


def _find_rom(archive_dir: Path, work_dir: Path) -> Path:
    """Return the ROM path. Either a bare ROM in archive_dir, or extract
    one out of a single zip into work_dir/. Never writes into the archive."""
    for ext in (".gba", ".sfc", ".smc", ".bin", ".rom", ".md", ".gen"):
        for p in archive_dir.glob(f"*{ext}"):
            return p
    zips = list(archive_dir.glob("*.zip"))
    if zips:
        return _extract_rom_to(zips[0], work_dir)
    raise FileNotFoundError(f"cartridge_rom: no ROM under {archive_dir}")


def _pick_target(fmt: str, rom_path: Path, release_meta: dict) -> tuple[str, str]:
    """Select (awvm_slug, expected_name) for a format + actual ROM."""
    table = CARTRIDGE_TARGETS[fmt]
    if fmt == "snes-rom":
        # SNES has region variants — read from metadata slug if present
        # ("snes-eu", "snes-usa"), else inspect filename for "(Europe)" /
        # "(USA)".
        slug = release_meta.get("slug", "")
        name = rom_path.name.lower()
        if "snes-eu" in slug or "(europe)" in name:
            return table[".sfc-eu"]
        return table[".sfc-us"]
    # Single-region formats
    return next(iter(table.values()))


def extract(release_meta, archive_dir: Path, work_dir: Path) -> dict:
    fmt = release_meta.get("format")
    if fmt not in CARTRIDGE_TARGETS:
        raise ValueError(f"cartridge_rom: unsupported format {fmt!r}")

    if not TOOL.is_file():
        raise RuntimeError(
            f"cartridge_rom: AWVM_Tools awvm-disasm binary not built at {TOOL} "
            "(run `cargo build --release` in AnotherWorld_VMTools)"
        )

    work_dir.mkdir(parents=True, exist_ok=True)
    rom_path = _find_rom(archive_dir, work_dir)
    awvm_slug, expected_name = _pick_target(fmt, rom_path, release_meta)

    # Stage the ROM under the AWVM_Tools-expected filename.
    staging = work_dir / "_staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir()
    staged_rom = staging / expected_name
    shutil.copy(rom_path, staged_rom)

    # awvm-disasm writes to <CWD>/output/<slug>/, so cd into work_dir.
    subprocess.run(
        [str(TOOL), str(staging), "all_levels", awvm_slug],
        check=True,
        cwd=work_dir,
    )

    # The output we care about is at work_dir/output/<slug>/{romset,disasm}.
    # Move it up so the per-release output is at work_dir/{romset,disasm}.
    awvm_out = work_dir / "output" / awvm_slug
    if not awvm_out.is_dir():
        raise RuntimeError(
            f"cartridge_rom: awvm-disasm produced no output at {awvm_out}"
        )
    for sub in ("romset", "disasm"):
        src = awvm_out / sub
        dst = work_dir / sub
        if dst.exists():
            shutil.rmtree(dst)
        if src.is_dir():
            shutil.move(str(src), str(dst))
    shutil.rmtree(work_dir / "output", ignore_errors=True)
    shutil.rmtree(staging)

    files = sorted(p.relative_to(work_dir).as_posix()
                   for p in work_dir.rglob("*") if p.is_file())
    manifest = {
        "format": fmt,
        "awvm_release_slug": awvm_slug,
        "source_rom": rom_path.name,
        "resource_count": len(files),
        "files": files,
    }
    (work_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
