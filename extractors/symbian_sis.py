"""Symbian SIS (Series 60 1st/2nd Edition installer) — best-effort extractor.

The Symbian SIS format is a Series-60 / EPOC installer wrapper with
a structured header (UIDs, language records, file records, etc.) and
a body of compressed payloads. A complete parser is significant
work; for now we do a best-effort scan that finds zlib-compressed
runs in the file and decompresses each one as a raw blob.

Empirically, on the AW Symbian generic .sis (753,982 bytes) this
yields two payloads:
  payload-00.bin  ~3 KB   — metadata header / language records
  payload-01.bin  ~948 KB — main bundled binary (the AW resources
                            and code live inside; further parsing
                            will identify the AW VM bytecode +
                            polygon banks within)

This is incomplete — the structured SIS field layout is not parsed,
file names from the installer's file-records section are not
recovered, and any LZMA-inner chunking (as seen in the locked
variant which AWVM_Tools targets) isn't unpacked. A future
extractor will replace this with a proper SIS parser.

Output layout under `work_dir/`:
  payloads/payload-NN.bin   <- one blob per zlib stream found
  manifest.json
"""

from __future__ import annotations

import json
import shutil
import zlib
from pathlib import Path

# Minimum decompressed-payload size we care about (bytes). Avoids
# noise hits where a chance 0x78 byte starts a tiny "valid" stream.
MIN_PAYLOAD = 256


def _scan_zlib_payloads(data: bytes) -> list[tuple[int, bytes]]:
    """Find every offset where zlib decompresses to a non-trivial payload.

    Returns a list of (offset, decompressed_bytes), in ascending offset
    order, skipping payloads that overlap with previously-found ones
    (zlib-readable streams nested inside a larger one).
    """
    found: list[tuple[int, bytes]] = []
    consumed_until = 0
    i = 0
    while i < len(data) - 2:
        if i < consumed_until:
            i += 1
            continue
        if data[i] == 0x78 and data[i + 1] in (0x01, 0x5E, 0x9C, 0xDA):
            try:
                d = zlib.decompressobj()
                result = d.decompress(data[i:])
                if len(result) >= MIN_PAYLOAD:
                    consumed_bytes = len(data) - i - len(d.unused_data)
                    found.append((i, result))
                    consumed_until = i + consumed_bytes
            except zlib.error:
                pass
        i += 1
    return found


def extract(release_meta, archive_dir: Path, work_dir: Path) -> dict:
    sis_paths = list(archive_dir.glob("*.sis")) + list(archive_dir.glob("*.SIS"))
    if not sis_paths:
        raise FileNotFoundError(f"symbian-sis: no .sis in {archive_dir}")
    sis_path = sis_paths[0]

    data = sis_path.read_bytes()

    work_dir.mkdir(parents=True, exist_ok=True)
    out_dir = work_dir / "payloads"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir()

    payloads = _scan_zlib_payloads(data)
    written: list[dict] = []
    for idx, (off, blob) in enumerate(payloads):
        name = f"payload-{idx:02d}.bin"
        (out_dir / name).write_bytes(blob)
        written.append({
            "name": f"payloads/{name}",
            "zlib_offset": off,
            "decompressed_size": len(blob),
        })

    manifest = {
        "format": "symbian-sis",
        "source_sis": sis_path.name,
        "source_size": len(data),
        "resource_count": len(written),
        "payloads": written,
        "note": (
            "Best-effort zlib scan; see extractors/symbian_sis.py docstring. "
            "A proper SIS parser would also recover original file names "
            "from the installer's file-records section."
        ),
    }
    (work_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
