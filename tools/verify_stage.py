#!/usr/bin/env python3
"""Phase 3a stage-based byte-match verifier.

Given a canonical `<stage>.asm` file in a branch directory, assemble
it and compare against the appropriate cartridge chunk / resource bin
for every port that uses that stage from that branch.

Usage:
    python3 tools/verify_stage.py \\
        --asm /path/to/src/levels/heineman_cartridge/LAKE.asm \\
        --branch heineman_cartridge \\
        --stage LAKE
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

# Per-port: (root-dir, format, stage→level mapping)
# For cartridge format: bytecode is in <root>/romset/bytecode.rom at chunk N×0x10000.
# For resource-bin format: bytecode is at <root>/resources/resource-0xNN.bin.
PORTS = {
    # Heineman cartridge branch
    "snes_eu": {
        "branch": "heineman_cartridge",
        "format": "cartridge",
        "root": Path("work/f65e3d6efe35900c0015bcb751ee567e"),
        # SNES-EU only has 2 disasm levels; level_0 is the INTRO sequence
        # (lab scene with Ferrari + particle accelerator strings), NOT the
        # CODE_WHEEL screen (cartridges don't have codewheel protection).
        # level_1 is the LAKE stage (byte-identical to Genesis-EU level_0).
        "stages": {"INTRO": 0, "LAKE": 1},
    },
    "genesis_europe": {
        "branch": "heineman_cartridge",
        "format": "cartridge",
        "root": Path("work/f15f23e1e0fa8d827c4b045d7ce3cf90"),
        "stages": {
            "LAKE": 0, "PRISON": 1, "CAVES": 2, "TANK": 3,
            "CAPSULE": 4, "ENDING": 5, "PASSCODE": 6,
        },
    },
    # DOS 1992 branch
    "msdos": {
        "branch": "dos_1992",
        "format": "resource-bin",
        "root": Path("/tmp/output/msdos"),
        "stages": {
            "CODE_WHEEL": 0x15, "INTRO": 0x18, "LAKE": 0x1B, "PRISON": 0x1E,
            "CAVES": 0x21, "TANK": 0x24, "CAPSULE": 0x27, "ENDING": 0x2A,
            "PASSCODE": 0x7E,
        },
    },
    # Chahi 1991 branch
    "amiga": {
        "branch": "chahi_1991",
        "format": "resource-bin",
        "root": Path("/tmp/output/amiga"),
        "stages": {
            "CODE_WHEEL": 0x15, "INTRO": 0x18, "LAKE": 0x1B, "PRISON": 0x1E,
            "CAVES": 0x21, "TANK": 0x24, "CAPSULE": 0x27, "ENDING": 0x2A,
            "PASSCODE": 0x7E,
        },
    },
    # Foxy GBA 2004 branch
    "gba_usa": {
        "branch": "foxy_gba_2004",
        "format": "cartridge",
        "root": Path("/tmp/output/gba_usa"),
        # Same as snes_eu: level_0 is INTRO (the lab scene; identical
        # strings and 0.99 structural similarity to snes_eu level_0).
        # AWVM_Tools' STAGE_TITLES labels this "Code-wheel screen" — that's
        # incorrect for the GBA port (cartridge → no codewheel).
        "stages": {"INTRO": 0, "LAKE": 1},
    },
}

CHUNK_SIZE = 0x10000


def assemble(asm_path: Path) -> bytes:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        local = td / asm_path.name
        shutil.copyfile(asm_path, local)
        subprocess.run([str(AWVM_ASM), local.name], cwd=td,
                       check=True, capture_output=True, text=True)
        return local.with_suffix(".bin").read_bytes()


def expected_bytes(port: str, stage: str) -> bytes | None:
    spec = PORTS[port]
    if stage not in spec["stages"]:
        return None
    if spec["format"] == "cartridge":
        bcrom = spec["root"] / "romset" / "bytecode.rom"
        if not bcrom.is_file():
            return None
        rom = bcrom.read_bytes()
        idx = spec["stages"][stage]
        return rom[idx * CHUNK_SIZE: (idx + 1) * CHUNK_SIZE]
    elif spec["format"] == "resource-bin":
        idx = spec["stages"][stage]
        path = spec["root"] / "resources" / f"resource-0x{idx:02x}.bin"
        return path.read_bytes() if path.is_file() else None
    return None


def verify_one(asm: Path, branch: str, stage: str) -> tuple[int, int]:
    """Returns (passes, fails)."""
    targets = [
        port for port, spec in PORTS.items()
        if spec["branch"] == branch and stage in spec["stages"]
    ]
    if not targets:
        print(f"  no ports in branch {branch} have stage {stage}")
        return 0, 0
    assembled = assemble(asm)
    p, f = 0, 0
    for port in targets:
        expected = expected_bytes(port, stage)
        if expected is None:
            continue
        if PORTS[port]["format"] == "resource-bin":
            actual = assembled[: len(expected)]
        else:
            actual = assembled
        if actual == expected:
            p += 1
        else:
            f += 1
            print(f"    {port}.{stage}: MISMATCH")
    return p, f


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--asm", type=Path,
                   help="canonical .asm file to assemble")
    p.add_argument("--branch",
                   help="bytecode branch (e.g. heineman_cartridge)")
    p.add_argument("--stage",
                   help="stage name (e.g. LAKE)")
    p.add_argument("--src-tree", type=Path,
                   help="root of src/levels/<branch>/<stage>.asm tree; "
                        "if given, iterates all (branch, stage) combinations")
    args = p.parse_args()

    if args.src_tree:
        # Iterate over every <branch>/<stage>.asm in the tree
        total_p, total_f, total_combos = 0, 0, 0
        for branch_dir in sorted(args.src_tree.glob("*")):
            if not branch_dir.is_dir():
                continue
            branch = branch_dir.name
            stage_files = sorted(branch_dir.glob("*.asm"))
            print(f"\n=== branch: {branch} ({len(stage_files)} stages) ===")
            for stage_asm in stage_files:
                stage = stage_asm.stem
                p, f = verify_one(stage_asm, branch, stage)
                if p + f == 0:
                    continue
                ports = [
                    port for port, spec in PORTS.items()
                    if spec["branch"] == branch and stage in spec["stages"]
                ]
                total_combos += 1
                if f == 0:
                    print(f"  {stage:<12s} OK ({p} target(s): {', '.join(ports)})")
                else:
                    print(f"  {stage:<12s} FAIL ({p}/{p+f})")
                total_p += p
                total_f += f
        print(f"\nTOTAL: {total_p}/{total_p+total_f} (port, stage) byte-matches "
              f"across {total_combos} canonical .asm files")
        if total_f:
            sys.exit(1)
        return

    if not (args.asm and args.branch and args.stage):
        sys.exit("use --src-tree, OR specify --asm + --branch + --stage")

    print(f"asm: {args.asm}")
    print(f"branch: {args.branch}, stage: {args.stage}")
    if not args.asm.is_file():
        sys.exit(f"asm file not found: {args.asm}")

    # Find ports in this branch that have this stage.
    targets = [
        port for port, spec in PORTS.items()
        if spec["branch"] == args.branch and args.stage in spec["stages"]
    ]
    if not targets:
        sys.exit(f"no ports in branch {args.branch} have stage {args.stage}")
    print(f"targets: {targets}")

    assembled = assemble(args.asm)
    print(f"\nassembled: {len(assembled)} bytes  md5={hashlib.md5(assembled).hexdigest()}")

    fail = 0
    for port in targets:
        expected = expected_bytes(port, args.stage)
        if expected is None:
            print(f"  {port}: SKIP (expected bytes not available)")
            continue
        # For cartridge: expected is 64KB, assembled is 64KB — straight compare.
        # For resource-bin: expected is the exact resource size; truncate assembled.
        if PORTS[port]["format"] == "resource-bin":
            actual = assembled[: len(expected)]
        else:
            actual = assembled
        ok = actual == expected
        status = "OK" if ok else "MISMATCH"
        print(f"  {port:<16}  expected={hashlib.md5(expected).hexdigest()[:12]} "
              f"actual={hashlib.md5(actual).hexdigest()[:12]} ({len(expected)} B)  [{status}]")
        if not ok:
            fail += 1

    if fail:
        sys.exit(f"\nFAIL: {fail} target(s) mismatched")
    print(f"\nALL OK — 1 canonical .asm matches {len(targets)} target(s)")


if __name__ == "__main__":
    main()
