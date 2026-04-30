#!/usr/bin/env python3
"""Per-target round-trip test for AW VM bytecode.

For each level of a port, this driver:

1. Reads the original BYTECODE resource (from `<output>/<port>/resources/`).
2. Reads the disassembled .asm (from `<output>/<port>/disasm/level_N/`).
3. Re-assembles the .asm with `awvm-asm`.
4. Truncates the assembler's 64 KB output to the original size.
5. Compares md5 of the truncated output to the original.

Reports per-level match status.

Usage:
    python3 tools/roundtrip_bytecode.py --port amiga --output-root /tmp/output/amiga
    python3 tools/roundtrip_bytecode.py --port msdos --output-root /tmp/output/msdos
    python3 tools/roundtrip_bytecode.py --all
"""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AWVM_ASM = Path(
    "/home/fsanches/compartilhado/AnotherWorld_VMTools/target/release/awvm-asm"
)

# Per-port BYTECODE resource indices (one per level), copied from
# AWVM_Tools/awvm/src/releases/<port>.rs `BYTECODE` constant.
# Used for resource-bin format ports (DOS, Amiga, Atari ST).
BYTECODE_PER_LEVEL: dict[str, list[int | None]] = {
    "amiga":    [0x15, 0x18, 0x1B, 0x1E, 0x21, 0x24, 0x27, 0x2A, 0x7E],
    "msdos":    [0x15, 0x18, 0x1B, 0x1E, 0x21, 0x24, 0x27, 0x2A, 0x7E],
    "atari_st": [0x15, 0x18, 0x1B, 0x1E, 0x21, 0x24, 0x27, 0x2A, 0x7E],
}

# Cartridge-format ports: bytecode.rom is N concatenated 64-KB chunks.
# Each chunk is the padded output of awvm-asm for that level.
CARTRIDGE_PORTS: dict[str, int] = {
    # port → number of 64KB chunks (= number of levels with bytecode)
    "genesis_europe": 7,
    "snes_eu":        2,  # only 2 levels disasm currently
    "snes-eu":        2,
    "gba_usa":        2,
}
CHUNK_SIZE = 0x10000  # 64 KB per AW-VM bytecode chunk

# Default output-root location keyed by port slug. For cartridge ports,
# the round-trip driver reads bytecode.rom from <root>/romset/.
DEFAULT_OUTPUT_ROOT: dict[str, Path] = {
    "amiga":          Path("/tmp/output/amiga"),
    "msdos":          Path("/tmp/output/msdos"),
    "gba_usa":        Path("/tmp/output/gba_usa"),
    "genesis_europe": Path("work/f15f23e1e0fa8d827c4b045d7ce3cf90"),
    "snes_eu":        Path("work/f65e3d6efe35900c0015bcb751ee567e"),
}


def assemble(asm_path: Path) -> bytes:
    """Run awvm-asm on `asm_path` and return the produced .bin bytes."""
    if not AWVM_ASM.is_file():
        sys.exit(f"awvm-asm binary not found at {AWVM_ASM}")
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        local_asm = td / asm_path.name
        shutil.copyfile(asm_path, local_asm)
        result = subprocess.run(
            [str(AWVM_ASM), local_asm.name],
            cwd=td,
            check=True,
            capture_output=True,
            text=True,
        )
        bin_name = local_asm.with_suffix(".bin")
        if not bin_name.is_file():
            sys.exit(
                f"awvm-asm did not produce {bin_name} for input {asm_path}\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return bin_name.read_bytes()


def find_disasm(port: str, output_root: Path, level: int) -> Path | None:
    """Locate the disassembled .asm for a level in this port's output tree."""
    cands = list((output_root / "disasm" / f"level_{level}").glob("*.asm"))
    return cands[0] if cands else None


def find_resource(output_root: Path, resource_idx: int) -> Path | None:
    """Locate a resource .bin file by index."""
    p = output_root / "resources" / f"resource-0x{resource_idx:02x}.bin"
    return p if p.is_file() else None


def roundtrip_one(port: str, level: int, asm_path: Path,
                  resource_path: Path) -> tuple[bool, dict]:
    """Round-trip one level. Returns (ok, info)."""
    original = resource_path.read_bytes()
    assembled = assemble(asm_path)
    truncated = assembled[: len(original)]

    # Bytes after the original length should ideally be all zeros (padding);
    # we don't gate on that.
    tail = assembled[len(original):]
    tail_nonzero = sum(1 for b in tail if b != 0)

    ok = truncated == original
    return ok, {
        "asm": str(asm_path),
        "resource": str(resource_path),
        "orig_size": len(original),
        "orig_md5": hashlib.md5(original).hexdigest(),
        "assembled_size": len(assembled),
        "truncated_md5": hashlib.md5(truncated).hexdigest(),
        "tail_nonzero_bytes": tail_nonzero,
        "match": ok,
    }


def roundtrip_one_cartridge(port: str, level: int, asm_path: Path,
                            chunk_bytes: bytes) -> tuple[bool, dict]:
    """Round-trip one level of a cartridge port. Compares assembled output
    (always 64 KB) to the corresponding chunk in bytecode.rom."""
    assembled = assemble(asm_path)
    ok = assembled == chunk_bytes
    return ok, {
        "asm": str(asm_path),
        "chunk_size": len(chunk_bytes),
        "chunk_md5": hashlib.md5(chunk_bytes).hexdigest(),
        "assembled_size": len(assembled),
        "assembled_md5": hashlib.md5(assembled).hexdigest(),
        "match": ok,
    }


def roundtrip_port(port: str, output_root: Path) -> list[tuple[int, bool, dict]]:
    if port in CARTRIDGE_PORTS:
        # Cartridge format: bytecode.rom is N×64KB chunks.
        bcrom = output_root / "romset" / "bytecode.rom"
        if not bcrom.is_file():
            print(f"  no bytecode.rom at {bcrom}")
            return []
        rom_bytes = bcrom.read_bytes()
        n_chunks = CARTRIDGE_PORTS[port]
        results = []
        for level in range(n_chunks):
            asm = find_disasm(port, output_root, level)
            if asm is None:
                print(f"  level {level}: skip (no asm)")
                continue
            chunk = rom_bytes[level * CHUNK_SIZE: (level + 1) * CHUNK_SIZE]
            if len(chunk) != CHUNK_SIZE:
                print(f"  level {level}: chunk truncated ({len(chunk)} bytes)")
                continue
            ok, info = roundtrip_one_cartridge(port, level, asm, chunk)
            results.append((level, ok, info))
        return results

    if port not in BYTECODE_PER_LEVEL:
        sys.exit(f"unknown port {port!r}; known: "
                 f"{list(BYTECODE_PER_LEVEL) + list(CARTRIDGE_PORTS)}")

    indices = BYTECODE_PER_LEVEL[port]
    results = []
    for level, idx in enumerate(indices):
        if idx is None:
            continue
        asm = find_disasm(port, output_root, level)
        resource = find_resource(output_root, idx)
        if asm is None or resource is None:
            print(f"  level {level}: skip (asm={asm}, resource={resource})")
            continue
        ok, info = roundtrip_one(port, level, asm, resource)
        results.append((level, ok, info))
    return results


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--port", help="port slug (e.g. amiga, msdos)")
    p.add_argument("--output-root", type=Path, help="path to <output>/<port>/")
    p.add_argument("--all", action="store_true",
                   help="run for every port that has a default output-root")
    args = p.parse_args()

    targets: list[tuple[str, Path]] = []
    if args.all:
        for port, root in DEFAULT_OUTPUT_ROOT.items():
            if root.is_dir():
                targets.append((port, root))
    elif args.port:
        root = args.output_root or DEFAULT_OUTPUT_ROOT.get(args.port)
        if root is None or not root.is_dir():
            sys.exit(f"need --output-root for port {args.port}")
        targets.append((args.port, root))
    else:
        sys.exit("specify --port or --all")

    grand_match = grand_total = 0
    for port, root in targets:
        print(f"\n=== port={port} root={root} ===")
        results = roundtrip_port(port, root)
        match = sum(1 for _, ok, _ in results if ok)
        total = len(results)
        grand_match += match
        grand_total += total
        for level, ok, info in results:
            status = "OK" if ok else "MISMATCH"
            if "chunk_size" in info:
                # Cartridge format: full 64KB chunk compared.
                print(f"  level_{level}: {status:8s}  "
                      f"chunk={info['chunk_size']:6d}  "
                      f"md5={info['chunk_md5'][:12]}")
            else:
                tail_note = ""
                if info["tail_nonzero_bytes"] > 0:
                    tail_note = f"  (tail: {info['tail_nonzero_bytes']} non-zero after pad)"
                print(f"  level_{level}: {status:8s}  "
                      f"size={info['orig_size']:6d}  "
                      f"md5={info['orig_md5'][:12]}{tail_note}")
        print(f"  total: {match}/{total} levels round-trip byte-identically")

    if grand_total:
        print(f"\nGRAND TOTAL: {grand_match}/{grand_total} levels round-trip "
              f"byte-identically across {len(targets)} port(s)")


if __name__ == "__main__":
    main()
