"""DOS-format extractor: `memlist.bin` + `bank<NN>` files.

The DOS release of Another World packages every resource as an entry
in `memlist.bin`, pointing at a (bank file, byte offset, packed size,
unpacked size, type) tuple. Compressed entries use a custom LZ-ish
bit-stream that this module decodes verbatim from the original engine
sources — note in particular that the decoder consumes its input
buffer BACKWARDS from the end (`_iBuf` decrements; `_oBuf` decrements).
"""

import enum
import hashlib
import json
import zipfile
from pathlib import Path


class ResourceType(enum.IntEnum):
    SOUND = 0
    MUSIC = 1
    POLY_ANIM = 2
    PALETTE = 3
    BYTECODE = 4
    POLY_CINEMATIC = 5
    UNKNOWN = 6


def _ord2(v):
    return v[0] << 8 | v[1]


def _ord4(v):
    return v[0] << 24 | v[1] << 16 | v[2] << 8 | v[3]


class _Bank:
    def __init__(self, data_dir: Path):
        self._data_dir = Path(data_dir)

    def read(self, entry: dict) -> bytes:
        bank_path = self._data_dir / ("bank%02x" % entry["bankId"])
        with open(bank_path, "rb") as f:
            f.seek(entry["bankOffset"])
            if entry["packedSize"] == entry["size"]:
                return f.read(entry["packedSize"])
            self._buf = list(f.read(entry["packedSize"]))
            self._buf.extend([0] * (entry["size"] - entry["packedSize"]))
            self._iBuf = entry["packedSize"] - 4
            return self._unpack()

    def _read_be_uint32(self, i: int) -> int:
        return (
            self._buf[i] << 24
            | self._buf[i + 1] << 16
            | self._buf[i + 2] << 8
            | self._buf[i + 3]
        )

    def _unpack(self):
        self._crc = 0
        self._size = 0
        self._datasize = self._read_be_uint32(self._iBuf)
        self._iBuf -= 4
        self._oBuf = self._datasize - 1
        self._crc = self._read_be_uint32(self._iBuf)
        self._iBuf -= 4
        self._chk = self._read_be_uint32(self._iBuf)
        self._iBuf -= 4
        self._crc ^= self._chk
        while self._datasize > 0:
            if not self._next_chunk():
                self._size = 1
                if not self._next_chunk():
                    self._dec_unk1(3, 0)
                else:
                    self._dec_unk2(8)
            else:
                c = self._get_code(2)
                if c == 3:
                    self._dec_unk1(8, 8)
                elif c < 2:
                    self._size = c + 2
                    self._dec_unk2(c + 9)
                else:
                    self._size = self._get_code(8)
                    self._dec_unk2(12)
        if self._crc != 0:
            return None
        return bytes(self._buf)

    def _dec_unk1(self, num_chunks: int, add_count: int):
        count = self._get_code(num_chunks) + add_count + 1
        self._datasize -= count
        while count:
            count -= 1
            assert self._oBuf >= self._iBuf and self._oBuf >= 0
            self._buf[self._oBuf] = self._get_code(8)
            self._oBuf -= 1

    def _dec_unk2(self, num_chunks: int):
        i = self._get_code(num_chunks)
        count = self._size + 1
        self._datasize -= count
        while count:
            count -= 1
            assert self._oBuf >= self._iBuf and self._oBuf >= 0
            self._buf[self._oBuf] = self._buf[self._oBuf + i]
            self._oBuf -= 1

    def _get_code(self, num_chunks: int) -> int:
        c = 0
        while num_chunks:
            num_chunks -= 1
            c <<= 1
            if self._next_chunk():
                c |= 1
        return c

    def _next_chunk(self) -> int:
        cf = self._rcr(False)
        if self._chk == 0:
            assert self._iBuf >= 0
            self._chk = self._read_be_uint32(self._iBuf)
            self._iBuf -= 4
            self._crc ^= self._chk
            cf = self._rcr(True)
        return cf

    def _rcr(self, cf_in: bool) -> int:
        rcf = self._chk & 1
        self._chk >>= 1
        if cf_in:
            self._chk |= 0x80000000
        return rcf


def _read_mem_entries(memlist_path: Path) -> list:
    entries = []
    with open(memlist_path, "rb") as f:
        while True:
            entry = {}
            entry["state"] = ord(f.read(1))
            entry["type"] = ord(f.read(1))
            f.read(2)  # bufPtr (skip)
            f.read(2)  # unk4 (skip)
            entry["rankNum"] = ord(f.read(1))
            entry["bankId"] = ord(f.read(1))
            entry["bankOffset"] = _ord4(f.read(4))
            f.read(2)  # unkC (skip)
            entry["packedSize"] = _ord2(f.read(2))
            f.read(2)  # unk10 (skip)
            entry["size"] = _ord2(f.read(2))
            if entry["state"] == 0:
                entries.append(entry)
            else:
                break
    return entries


def _md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def _unpack_zip(zip_path: Path, target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)


def extract(release_meta: dict, cache_dir: Path, work_dir: Path) -> dict:
    cache_dir = Path(cache_dir)
    work_dir = Path(work_dir)
    slug = release_meta.get("slug", "?")

    cached_files = sorted(p for p in cache_dir.iterdir() if p.is_file())
    if not cached_files:
        raise FileNotFoundError(
            f"release {slug!r}: no cached source file in {cache_dir}"
        )
    if len(cached_files) > 1:
        raise RuntimeError(
            f"release {slug!r}: expected exactly one cached file in {cache_dir}, "
            f"found {len(cached_files)}: {[p.name for p in cached_files]}"
        )
    source = cached_files[0]

    expected_md5 = release_meta.get("md5sum")
    if expected_md5:
        actual_md5 = hashlib.md5(source.read_bytes()).hexdigest()
        if actual_md5 != expected_md5:
            raise RuntimeError(
                f"release {slug!r}: md5 mismatch on {source.name}: "
                f"got {actual_md5}, expected {expected_md5}"
            )

    original_dir = work_dir / "original"
    bin_dir = work_dir / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    if source.suffix.lower() == ".zip":
        _unpack_zip(source, original_dir)
    else:
        raise NotImplementedError(
            f"release {slug!r}: source file {source.name!r} is not a zip; "
            f"this extractor currently only handles zip-packaged DOS releases"
        )

    rootdir = release_meta.get("rootdir", ".")
    bank_dir = original_dir / rootdir
    memlist_path = bank_dir / "memlist.bin"
    if not memlist_path.is_file():
        raise FileNotFoundError(
            f"release {slug!r}: no memlist.bin at {memlist_path}"
        )

    entries = _read_mem_entries(memlist_path)
    bank = _Bank(bank_dir)

    resources = []
    for index, entry in enumerate(entries):
        try:
            type_name = ResourceType(entry["type"]).name
        except ValueError:
            type_name = "UNKNOWN"
        filename = f"0x{index:x}-{type_name}.bin"
        out_path = bin_dir / filename
        data = bank.read(entry)
        if data is None:
            raise RuntimeError(
                f"release {slug!r}: failed to unpack resource {index} "
                f"(bank={entry['bankId']:#x}, offset={entry['bankOffset']:#x})"
            )
        out_path.write_bytes(data)
        resources.append(
            {
                "index": index,
                "filename": filename,
                "type": type_name,
                "type_id": entry["type"],
                "bank_id": entry["bankId"],
                "bank_offset": entry["bankOffset"],
                "packed_size": entry["packedSize"],
                "size": entry["size"],
                "md5": _md5(data),
            }
        )

    manifest = {
        "slug": slug,
        "package_md5": expected_md5,
        "format": "dos-bank",
        "source_file": source.name,
        "resource_count": len(resources),
        "resources": resources,
    }
    manifest_path = work_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return manifest
