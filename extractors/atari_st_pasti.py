"""Atari ST 1991 release extractor — Pasti `.stx` ⇒ flat `.st` ⇒ FAT12.

The 1991 Atari ST release is shipped as two Pasti-format disk images
(`another_world_disk_1.stx`, `another_world_disk_2.stx`) inside a single
zip. Pasti is a track-level disk image format that preserves the
copy-protection sectors in addition to the standard MFM data; for
extraction we only need the standard sectors.

Pipeline:
  1. Unzip the package.
  2. For each `.stx`: walk track records, pull the clean 512-byte
     sector content out of the post-descriptors data area, lay it
     out into a flat 720 KiB `.st` image.
  3. Parse FAT12 from the flat image and recursively extract every
     file (root + `AUTO/`).

Output layout under `work_dir/`:
  another_world_disk_1/   <- flat copy of disk 1 contents (BANK01, BANK02, …)
  another_world_disk_2/   <- flat copy of disk 2 contents (BANK03, BANK04, …)
  manifest.json

The bank files (`BANK01`…`BANK0D`) use the same engine resource
format as the Amiga release, but there is no `memlist.bin` on the
floppies — the resource directory is embedded in `START.PRG`.
Mapping these bank files back to canonical AW resource indices is
left for a follow-up research step.
"""

from __future__ import annotations

import json
import struct
import zipfile
from pathlib import Path
from typing import Iterable


def stx_to_st(stx_bytes: bytes) -> bytes:
    """Convert a Pasti `.stx` byte stream to a flat 720 KiB `.st` image."""
    if stx_bytes[:4] != b"RSY\0":
        raise ValueError("not a Pasti .stx file")

    SECTORS_PER_TRACK = 9
    SECTOR_SIZE = 512
    SIDES = 2
    TRACKS = 80

    out = bytearray(TRACKS * SIDES * SECTORS_PER_TRACK * SECTOR_SIZE)

    pos = 16  # past Pasti header
    while pos + 16 <= len(stx_bytes):
        (record_size, fuzzy_count, sector_count,
         _track_flags, _track_length, track_number, _track_type) = \
            struct.unpack("<IIHHHBB", stx_bytes[pos : pos + 16])
        if record_size < 16:
            break

        side = (track_number >> 7) & 1
        track = track_number & 0x7F

        if sector_count > 0 and track < TRACKS:
            descs_off = pos + 16 + fuzzy_count
            sec_data_base = descs_off + sector_count * 16
            for i in range(sector_count):
                sd = stx_bytes[descs_off + i * 16 : descs_off + (i + 1) * 16]
                (data_offset, _bit_pos, _read_time,
                 _am_t, _am_s, am_r, am_n, _am_crc,
                 _fdc, _reserved) = struct.unpack("<IHHBBBBHBB", sd)

                # Standard 512-byte sector; ignore fuzzy / weak / non-standard sizes.
                if am_n == 2 and 1 <= am_r <= SECTORS_PER_TRACK:
                    src = sec_data_base + data_offset
                    if src + SECTOR_SIZE <= len(stx_bytes):
                        lba = (track * SIDES + side) * SECTORS_PER_TRACK + (am_r - 1)
                        out[lba * SECTOR_SIZE : (lba + 1) * SECTOR_SIZE] = \
                            stx_bytes[src : src + SECTOR_SIZE]

        pos += record_size

    return bytes(out)


class Fat12Reader:
    """Minimal FAT12 reader for 720 KiB Atari ST floppies.

    Only handles what the AW Atari ST release actually uses:
    standard short filenames, root + one level of subdirectory,
    no long-filename extensions, no FAT16/32.
    """

    def __init__(self, image: bytes):
        self.image = image
        self.bps = struct.unpack("<H", image[0x0B : 0x0D])[0]
        self.spc = image[0x0D]
        self.reserved = struct.unpack("<H", image[0x0E : 0x10])[0]
        self.num_fats = image[0x10]
        self.root_entries = struct.unpack("<H", image[0x11 : 0x13])[0]
        self.spf = struct.unpack("<H", image[0x16 : 0x18])[0]

        if self.bps != 512:
            raise ValueError(f"unsupported bytes-per-sector {self.bps}")

        self.cluster_size = self.spc * self.bps
        self.fat_start = self.reserved * self.bps
        self.root_start = (self.reserved + self.num_fats * self.spf) * self.bps
        self.root_size = self.root_entries * 32
        self.data_start = self.root_start + self.root_size

    def _fat12_entry(self, idx: int) -> int:
        fat = self.image[self.fat_start : self.fat_start + self.spf * self.bps]
        off = (idx * 3) // 2
        val = struct.unpack("<H", fat[off : off + 2])[0]
        return (val & 0xFFF) if (idx & 1) == 0 else (val >> 4)

    def _cluster_chain(self, start_cluster: int) -> Iterable[int]:
        c = start_cluster
        while 2 <= c < 0xFF8:
            yield c
            c = self._fat12_entry(c)

    def _read_cluster(self, cluster_n: int) -> bytes:
        off = self.data_start + (cluster_n - 2) * self.cluster_size
        return self.image[off : off + self.cluster_size]

    def read_file(self, start_cluster: int, size: int) -> bytes:
        out = bytearray()
        for c in self._cluster_chain(start_cluster):
            out.extend(self._read_cluster(c))
            if len(out) >= size:
                break
        return bytes(out[:size])

    def list_dir(self, start_cluster: int = 0, size: int | None = None) -> list[dict]:
        """List directory entries. Pass start_cluster=0 for the root dir."""
        if start_cluster == 0:
            data = self.image[self.root_start : self.root_start + self.root_size]
        else:
            # Subdirs have no fixed size on disk; walk the cluster chain
            # until we hit a 0x00-marker entry.
            data = bytearray()
            for c in self._cluster_chain(start_cluster):
                data.extend(self._read_cluster(c))
            data = bytes(data)

        entries = []
        for i in range(len(data) // 32):
            e = data[i * 32 : (i + 1) * 32]
            if e[0] == 0:
                break
            if e[0] == 0xE5:
                continue
            if e[0x0B] & 0x08:  # volume label
                continue
            name_raw = e[0:8].rstrip(b" ").decode("ascii", errors="replace")
            ext_raw = e[8:11].rstrip(b" ").decode("ascii", errors="replace")
            if name_raw in (".", ".."):
                continue
            attrs = e[0x0B]
            cluster = struct.unpack("<H", e[0x1A : 0x1C])[0]
            file_size = struct.unpack("<I", e[0x1C : 0x20])[0]
            label = name_raw + "." + ext_raw if ext_raw else name_raw
            entries.append({
                "name": label,
                "is_dir": bool(attrs & 0x10),
                "cluster": cluster,
                "size": file_size,
            })
        return entries


def _extract_fat12_to(reader: Fat12Reader, out_dir: Path, written: list[Path],
                      cluster: int = 0, size: int = 0) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for entry in reader.list_dir(cluster, size):
        target = out_dir / entry["name"]
        if entry["is_dir"]:
            _extract_fat12_to(reader, target, written, entry["cluster"], entry["size"])
        else:
            content = reader.read_file(entry["cluster"], entry["size"])
            target.write_bytes(content)
            written.append(target)


def synthesize_memlist_from_start_prg(start_prg: bytes) -> bytes:
    """Extract the embedded resource directory from `START.PRG`.

    The Atari ST 1991 release does not ship a `memlist.bin` on disk —
    the resource directory is embedded inside `AUTO/START.PRG` (the
    boot loader, also present at the disk root as `START.PRG`).

    Embedded layout:
      offset:  `0x7ef2` in `START.PRG`
      stride:  20 bytes per entry
      length:  walked until `state == 0xFF` terminator

    Each entry uses big-endian fields (68000 native order):

        offset  field
        0       state (1)        — 0x00 valid, 0xFF terminator
        1       type (1)         — same enum as Amiga: SOUND=0,
                                   MUSIC=1, POLY_ANIM=2, PALETTE=3,
                                   BYTECODE=4, POLY_CINEMATIC=5,
                                   UNKNOWN=6
        2-5     bufPtr (4)
        6       rankNum (1)
        7       bankId (1)       — 1-indexed bank file (BANK01..)
        8-11    bankOffset (4)
        12-13   unkC (2)
        14-15   packedSize (2)
        16-17   unkE (2)
        18-19   size (2)

    This function returns the raw embedded bytes (BE) including the
    terminator, suitable for storage as `memlist.bin`. AWVM_Tools'
    `awvm-disasm` does NOT yet understand this layout for the Atari
    ST format (only DOS little-endian is supported); registering an
    `atari_st` release in AWVM_Tools is gated on owner review per
    the project's external-tool change policy. The synthesised file
    is preserved here so cross-port checksum comparisons against the
    Amiga release (which uses the same format) work without re-
    parsing START.PRG every time.

    See archaeology issue #0004 for the cross-port verification
    that confirmed this offset and format.
    """
    MEMLIST_OFFSET = 0x7EF2
    ENTRY_SIZE = 20
    if len(start_prg) < MEMLIST_OFFSET + ENTRY_SIZE:
        raise ValueError(
            f"atari-st-pasti: START.PRG is {len(start_prg)} bytes, "
            f"too short to hold the memlist at 0x{MEMLIST_OFFSET:04X}"
        )
    out = bytearray()
    pos = MEMLIST_OFFSET
    while pos + ENTRY_SIZE <= len(start_prg):
        entry = start_prg[pos : pos + ENTRY_SIZE]
        out.extend(entry)
        if entry[0] == 0xFF:
            return bytes(out)
        pos += ENTRY_SIZE
    raise ValueError(
        f"atari-st-pasti: walked off the end of START.PRG without "
        f"finding the 0xFF terminator (started at 0x{MEMLIST_OFFSET:04X})"
    )


def extract(release_meta, archive_dir: Path, work_dir: Path) -> dict:
    zip_files = [f for f in release_meta.get("files", [])
                 if f.get("name", "").lower().endswith(".zip")]
    # The metadata lists the .stx files (inside the zip), but the package on
    # disk is the zip itself — find the actual zip in the archive directory.
    zip_paths = list(archive_dir.glob("*.zip"))
    if not zip_paths:
        raise FileNotFoundError(f"atari-st-pasti: no zip in {archive_dir}")
    zip_path = zip_paths[0]

    work_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    with zipfile.ZipFile(zip_path) as zf:
        stx_names = [n for n in zf.namelist() if n.lower().endswith(".stx")]
        if not stx_names:
            raise ValueError(f"atari-st-pasti: no .stx inside {zip_path}")
        for stx_name in sorted(stx_names):
            stx_bytes = zf.read(stx_name)
            st_bytes = stx_to_st(stx_bytes)
            disk_label = Path(stx_name).stem  # e.g. "another_world_disk_1"
            disk_out = work_dir / disk_label
            reader = Fat12Reader(st_bytes)
            _extract_fat12_to(reader, disk_out, written)

    # Synthesise memlist.bin from the embedded resource directory in
    # START.PRG (disk 1, AUTO/ folder).
    start_prg_path = work_dir / "another_world_disk_1" / "AUTO" / "START.PRG"
    if not start_prg_path.is_file():
        # Fall back to disk root copy (the two are byte-identical).
        start_prg_path = work_dir / "another_world_disk_1" / "START.PRG"
    memlist_synthesised = False
    if start_prg_path.is_file():
        memlist_bytes = synthesize_memlist_from_start_prg(start_prg_path.read_bytes())
        memlist_path = work_dir / "memlist.bin"
        memlist_path.write_bytes(memlist_bytes)
        written.append(memlist_path)
        memlist_synthesised = True

    # Extract per-resource bytes into bin/0x<HH>-<TYPE>.bin (matching
    # the DOS package layout). Compressed entries are depacked via
    # the AW VM unpacker (port of AnotherWorld_VMTools' Rust
    # `awvm::unpacker::unpack`); see tools/aw_unpacker.py for the
    # reference port + validation.
    bin_dir = work_dir / "bin"
    resources_extracted = 0
    resources_metadata: list[dict] = []
    if memlist_synthesised:
        # Late-bind the unpacker so the extractor still works if
        # the archaeology repo isn't on sys.path.
        try:
            import sys as _sys
            _archeo = Path(__file__).resolve().parent.parent
            _sys.path.insert(0, str(_archeo))
            from tools.aw_unpacker import unpack as _aw_unpack  # noqa
        except Exception:
            _aw_unpack = None  # depack unavailable; extract uncompressed only

        TYPE_NAMES = {
            0: "SOUND",
            1: "MUSIC",
            2: "POLY_ANIM",
            3: "PALETTE",
            4: "BYTECODE",
            5: "POLY_CINEMATIC",
            6: "UNKNOWN",
        }

        # Open all bank files (across both disks)
        banks: dict[int, bytes] = {}
        for disk in ["another_world_disk_1", "another_world_disk_2"]:
            disk_dir = work_dir / disk
            if not disk_dir.is_dir():
                continue
            for f in disk_dir.iterdir():
                if f.name.startswith("BANK") and len(f.name) == 6:
                    try:
                        bid = int(f.name[4:6], 16)
                    except ValueError:
                        continue
                    if bid not in banks:
                        banks[bid] = f.read_bytes()

        bin_dir.mkdir(parents=True, exist_ok=True)
        ENTRY_SIZE = 20
        for i in range(len(memlist_bytes) // ENTRY_SIZE):
            e = memlist_bytes[i * ENTRY_SIZE : (i + 1) * ENTRY_SIZE]
            if e[0] == 0xFF:
                break
            rtype = e[1]
            bankId = e[7]
            bankOffset = struct.unpack(">I", e[8:12])[0]
            packedSize = struct.unpack(">H", e[14:16])[0]
            size = struct.unpack(">H", e[18:20])[0]
            if size == 0 or packedSize == 0 or bankId not in banks:
                continue
            bank = banks[bankId]
            if bankOffset + packedSize > len(bank):
                continue
            raw = bank[bankOffset : bankOffset + packedSize]
            if packedSize != size:
                if _aw_unpack is None:
                    continue  # skip compressed when depacker unavailable
                unpacked = _aw_unpack(raw)
                if unpacked is None:
                    continue
                raw = unpacked
            type_label = TYPE_NAMES.get(rtype, f"TYPE_{rtype:02X}")
            out_path = bin_dir / f"0x{i:x}-{type_label}.bin"
            out_path.write_bytes(raw)
            written.append(out_path)
            resources_extracted += 1
            resources_metadata.append({
                "index": i,
                "filename": f"0x{i:x}-{type_label}.bin",
                "type": type_label,
                "type_id": rtype,
                "bank_id": bankId,
                "bank_offset": bankOffset,
                "packed_size": packedSize,
                "size": size,
                "md5": __import__("hashlib").md5(raw).hexdigest(),
            })

    rel_files = sorted(p.relative_to(work_dir).as_posix() for p in written)
    manifest = {
        "format": "atari-st-pasti",
        "resource_count": len(rel_files),
        "files": rel_files,
        "memlist_synthesised": memlist_synthesised,
        "resources_extracted_to_bin": resources_extracted,
    }
    if resources_metadata:
        # Same shape as the DOS-bank manifest's `resources[]` array,
        # so cross_release_md5_index.py can consume it.
        manifest["resources"] = resources_metadata
    if memlist_synthesised:
        manifest["memlist_source"] = "AUTO/START.PRG offset 0x7EF2 (big-endian, 20-byte entries)"
    (work_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
