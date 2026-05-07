#!/usr/bin/env python3
"""Per-port verification that all extracted resources match expected md5s.

For Amiga-style and DOS-style ports (resource-bin format), this scans
every `<output_root>/resources/resource-0xNN.bin` and checks its md5
against a manifest.

For cartridge-style ports, the .rom files in `<output_root>/romset/`
serve as the raw assets. Each .rom file's md5 is checked against the
manifest.

Bytecode is verified separately (via tools/roundtrip_bytecode.py).
This driver focuses on **non-bytecode raw assets**:
  POLY_CINEMATIC, POLY_ANIM, PALETTE, SOUND, MUSIC, UNKNOWN.

The manifest format is JSON:

    {
      "port": "amiga",
      "resources": {
        "resource-0x14.bin": {"md5": "...", "size": 2048, "type": "PALETTE"},
        ...
      }
    }

If a manifest doesn't exist, this driver can `--bootstrap` one from
the current contents of the output directory — useful for first-time
populating the source-reconstruction repo's reference data.

Usage:
    python3 tools/verify_resources.py --port amiga --output-root tmp/output/amiga
    python3 tools/verify_resources.py --port amiga --output-root tmp/output/amiga --bootstrap
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Repo-local scratch dir for per-port disasm outputs. Survives VM
# reboots (unlike /tmp/) but is gitignored. Path is relative to this
# script's location: <repo>/tools/<this>.py → <repo>/tmp/.
TMP_ROOT = Path(__file__).resolve().parent.parent / "tmp"


# Default output-root (mirrors roundtrip_bytecode.py).
DEFAULT_OUTPUT_ROOT: dict[str, Path] = {
    "amiga":          TMP_ROOT / "output" / "amiga",
    "msdos":          TMP_ROOT / "output" / "msdos",
    "gba_usa":        TMP_ROOT / "output" / "gba_usa",
    "genesis_europe": Path("work/f15f23e1e0fa8d827c4b045d7ce3cf90"),
    "snes_eu":        Path("work/f65e3d6efe35900c0015bcb751ee567e"),
}


def hash_file(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def collect_resources(output_root: Path) -> dict[str, dict]:
    """Collect all extracted resource files from <output_root>/."""
    out: dict[str, dict] = {}

    # Amiga/DOS-style: <output_root>/resources/resource-0xNN.bin
    res_dir = output_root / "resources"
    if res_dir.is_dir():
        for f in sorted(res_dir.glob("resource-0x*.bin")):
            out[f"resources/{f.name}"] = {
                "md5": hash_file(f),
                "size": f.stat().st_size,
            }

    # Cartridge-style: <output_root>/romset/*.rom
    rom_dir = output_root / "romset"
    if rom_dir.is_dir():
        for f in sorted(rom_dir.glob("*.rom")):
            out[f"romset/{f.name}"] = {
                "md5": hash_file(f),
                "size": f.stat().st_size,
            }

    return out


def verify(port: str, output_root: Path, manifest_path: Path) -> int:
    """Verify resources against manifest. Returns number of mismatches."""
    if not manifest_path.is_file():
        sys.exit(f"manifest {manifest_path} not found; run with --bootstrap first")
    manifest = json.loads(manifest_path.read_text())
    expected = manifest.get("resources", {})
    actual = collect_resources(output_root)

    print(f"port={port}, manifest={manifest_path.name}")
    print(f"  expected resources: {len(expected)}")
    print(f"  found  resources: {len(actual)}")

    mismatches = 0
    missing = 0
    extra = 0

    for rel_path, exp_info in sorted(expected.items()):
        if rel_path not in actual:
            print(f"  MISSING   {rel_path}  (expected md5 {exp_info['md5'][:12]})")
            missing += 1
            continue
        act_info = actual[rel_path]
        if act_info["md5"] != exp_info["md5"]:
            print(f"  MISMATCH  {rel_path}  exp={exp_info['md5'][:12]} act={act_info['md5'][:12]}")
            mismatches += 1
        else:
            # Pass — silent unless --verbose
            pass

    for rel_path in sorted(set(actual) - set(expected)):
        print(f"  EXTRA     {rel_path}  ({actual[rel_path]['md5'][:12]})")
        extra += 1

    matched = len(expected) - mismatches - missing
    print(f"  OK={matched}  mismatch={mismatches}  missing={missing}  extra={extra}")
    return mismatches + missing


def bootstrap(port: str, output_root: Path, manifest_path: Path) -> None:
    """Generate a manifest from the current state of `output_root`."""
    actual = collect_resources(output_root)
    manifest = {"port": port, "resources": actual}
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    print(f"wrote {manifest_path} with {len(actual)} resource(s)")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--port", required=True, help="port slug")
    p.add_argument("--output-root", type=Path,
                   help="path to <output>/<port>/ (defaults to per-port table)")
    p.add_argument("--manifest", type=Path,
                   help="path to manifest JSON (defaults to "
                        "another-world-source-reconstruction/releases/<port>.resources.json)")
    p.add_argument("--bootstrap", action="store_true",
                   help="generate a manifest from the current output instead of verifying")
    p.add_argument("--all", action="store_true",
                   help="run for every default port")
    args = p.parse_args()

    if args.all:
        ports = list(DEFAULT_OUTPUT_ROOT)
    else:
        ports = [args.port]

    grand_fail = 0
    for port in ports:
        root = args.output_root or DEFAULT_OUTPUT_ROOT.get(port)
        if root is None or not root.is_dir():
            print(f"\n[{port}] skip: no output_root")
            continue
        manifest = args.manifest or (
            Path(__file__).resolve().parent.parent.parent
            / "another-world-source-reconstruction" / "releases"
            / f"{port}.resources.json"
        )
        print()
        if args.bootstrap:
            bootstrap(port, root, manifest)
        else:
            grand_fail += verify(port, root, manifest)

    if not args.bootstrap:
        if grand_fail:
            print(f"\nFAILURE: {grand_fail} resources don't match")
            sys.exit(1)
        print("\nALL OK")


if __name__ == "__main__":
    main()
