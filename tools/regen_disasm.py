#!/usr/bin/env python3
"""Regenerate `tmp/output/<port>/disasm/` for a given port by running
`awvm-disasm` over the unpacked game files.

Implements the `make disasm` Makefile target — previously
unimplemented (CLAUDE.md).

Background: the legacy disasm tree under `tmp/output/<port>/disasm/`
predates the `;@raw=` -> `;@enc=` migration. Current `awvm-disasm`
emits cleaner output (no annotations needed); re-running it
produces a tree that `awvm-asm` can re-assemble, which is what
`make verify-all` round-trips. Tracked as issue #0094.

Usage:

    python3 tools/regen_disasm.py <port>      # one port
    python3 tools/regen_disasm.py --all       # every supported port

Currently supports `msdos`. Other ports (amiga, snes_eu,
genesis_europe, gba_usa) call the format-specific path inside
their respective extractors during `make extract`; for those, run
extract instead.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from _paths import AWVM_TOOLS, REPO_ROOT


AWVM_DISASM = AWVM_TOOLS / "target" / "release" / "awvm-disasm"

# Per-port input layout. Each entry: (input_dir relative to package
# work-dir, awvm-disasm release slug). The work-dir is
# `work/<package_md5>/...`; we expect `make extract` to have already
# populated it.
PORT_LAYOUTS = {
    # msdos: bank files at original/aworld/aworld/
    "msdos": ("original/aworld/aworld", "msdos"),
    # amiga: bank files at bin/
    "amiga": ("bin", "amiga"),
}


def _package_md5_for_port(port: str) -> str | None:
    """Return the package md5 directory name for a port by reading
    metadata.json. None if no such release."""
    import json
    metadata = json.loads((REPO_ROOT / "metadata.json").read_text())
    # metadata is a list of release dicts; the field name for the
    # md5sum is `md5sum` not `package_md5`. Slug naming uses platform
    # prefixes (e.g. "dos" for the dos1992 release), so we map the
    # awvm slug to the metadata slug below.
    METADATA_SLUG = {"msdos": "dos", "amiga": "amiga-retro-presskit"}
    target_slug = METADATA_SLUG.get(port, port)
    if isinstance(metadata, list):
        for release in metadata:
            if release.get("slug") == target_slug:
                return release.get("md5sum")
    return None


def regen_port(port: str) -> int:
    if port not in PORT_LAYOUTS:
        print(f"regen_disasm: unsupported port {port!r}", file=sys.stderr)
        print(f"  Supported: {', '.join(PORT_LAYOUTS.keys())}", file=sys.stderr)
        return 2
    if not AWVM_DISASM.is_file():
        print(f"regen_disasm: awvm-disasm not built at {AWVM_DISASM}",
              file=sys.stderr)
        print("  cd ../AnotherWorld_VMTools && cargo build --release",
              file=sys.stderr)
        return 2

    pkg_md5 = _package_md5_for_port(port)
    if pkg_md5 is None:
        print(f"regen_disasm: no package_md5 for port {port!r}",
              file=sys.stderr)
        return 2

    in_subpath, awvm_slug = PORT_LAYOUTS[port]
    work_dir = REPO_ROOT / "work" / pkg_md5
    in_dir = work_dir / in_subpath
    if not in_dir.is_dir():
        print(f"regen_disasm: input dir not found at {in_dir}", file=sys.stderr)
        print(f"  run `make extract` first to populate work/{pkg_md5}/",
              file=sys.stderr)
        return 2

    # awvm-disasm writes to <CWD>/output/<slug>/disasm/...; we run it
    # in a scratch dir then move the disasm tree under
    # tmp/output/<port>/disasm/.
    scratch = REPO_ROOT / "tmp" / "_regen_disasm_scratch"
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)

    print(f"regen_disasm: running awvm-disasm for {port}...")
    rc = subprocess.run(
        [str(AWVM_DISASM), str(in_dir), "all_levels", awvm_slug],
        cwd=scratch,
    ).returncode

    # awvm-disasm can panic on a downstream step (e.g. amiga common_video
    # aggregation crashes with `pdata_offset out of bounds`) AFTER
    # successfully writing all per-level disasm outputs. Treat that
    # case as success-with-warning rather than failure.
    src_disasm = scratch / "output" / awvm_slug / "disasm"
    n_level_dirs = (
        sum(1 for _ in src_disasm.glob("level_*")) if src_disasm.is_dir() else 0
    )
    if rc != 0:
        if n_level_dirs > 0:
            print(
                f"regen_disasm: awvm-disasm exited {rc} but {n_level_dirs} "
                f"level disasm dir(s) were written — treating as partial "
                f"success. (Likely upstream bug in awvm-disasm; per-level "
                f"output is fine.)",
                file=sys.stderr,
            )
        else:
            print(f"regen_disasm: awvm-disasm exited {rc} with no output",
                  file=sys.stderr)
            return rc

    if not src_disasm.is_dir():
        print(f"regen_disasm: no disasm output at {src_disasm}",
              file=sys.stderr)
        return 1
    dst_disasm = REPO_ROOT / "tmp" / "output" / port / "disasm"
    if dst_disasm.exists():
        shutil.rmtree(dst_disasm)
    dst_disasm.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src_disasm), str(dst_disasm))

    shutil.rmtree(scratch)
    n_levels = sum(1 for _ in dst_disasm.glob("level_*"))
    print(f"regen_disasm: {port} -> {dst_disasm} ({n_levels} level(s))")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("port", nargs="?", help="port slug (e.g. msdos)")
    ap.add_argument("--all", action="store_true", help="regen every supported port")
    args = ap.parse_args()

    if args.all:
        ports = list(PORT_LAYOUTS.keys())
    elif args.port:
        ports = [args.port]
    else:
        ap.error("specify a port or --all")

    rc = 0
    for port in ports:
        port_rc = regen_port(port)
        if port_rc != 0:
            rc = port_rc
    return rc


if __name__ == "__main__":
    sys.exit(main())
