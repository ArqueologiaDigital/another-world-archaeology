"""Format-keyed dispatch for the per-release resource extractors.

Each extractor implements a function

    extract(release_meta: dict, cache_dir: Path, work_dir: Path) -> dict

where:
- `release_meta` is the per-release entry from `metadata.json`,
- `archive_dir` is `original_files/<key>/` (read-only local archive — never deleted),
- `work_dir`    is `work/<package_md5>/` (gitignored regenerable output),

and the return value is the manifest dict (also written to
`work_dir/manifest.json`).

Add a new format by:
1. Creating `extractors/<format>.py` with the function above.
2. Registering it in `EXTRACTORS` below.
3. Adding the `format` field to the relevant entries in `metadata.json`.
"""

from . import (
    amiga_adf,
    atari_st_pasti,
    cartridge_rom,
    dos_bank,
    symbian_sis,
    three_do_opera,
    winxp_pak,
    zip_unpack,
)

EXTRACTORS = {
    "dos-bank": dos_bank.extract,
    "winxp-pak": winxp_pak.extract,
    "amiga-adf": amiga_adf.extract,
    "snes-rom": cartridge_rom.extract,
    "genesis-rom": cartridge_rom.extract,
    "gba-rom": cartridge_rom.extract,
    "3do-cue-bin": three_do_opera.extract,
    "atari-st-pasti": atari_st_pasti.extract,
    "nds-rom": zip_unpack.extract,
    "apple-ii-demake": zip_unpack.extract,
    "symbian-sis": symbian_sis.extract,
}


def extract(release_meta, cache_dir, work_dir):
    fmt = release_meta.get("format")
    if fmt is None:
        raise ValueError(
            f"release {release_meta.get('slug', '?')!r}: no `format` field in metadata.json"
        )
    if fmt not in EXTRACTORS:
        raise ValueError(
            f"release {release_meta.get('slug', '?')!r}: unknown format {fmt!r} "
            f"(known: {sorted(EXTRACTORS)})"
        )
    return EXTRACTORS[fmt](release_meta, cache_dir, work_dir)
