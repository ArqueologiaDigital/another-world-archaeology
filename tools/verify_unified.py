#!/usr/bin/env python3
"""Verify the unified `.asm.in` → preprocess → assemble path byte-matches
expected port bytecode.

Sister tool to `verify_stage.py`, which only exercises the per-branch
source path. The unified file is a SEPARATE source-of-truth (used by
docs builds and any future N-way pipelines), and can drift from
per-branch sources in ways `verify_stage.py` will not catch — see
issue #0074 (orphan top-level CINEMATIC_<NNN> EQUs that masked
amiga's missing semantic-name EQUs after a branch-aware rename
round).

For each unified `.asm.in` file in src/levels/_unified/, this tool:
  1. preprocesses for every port that has a stage_id mapping in PORTS,
  2. expands FILL macros via awvm_preprocess,
  3. invokes awvm-asm,
  4. compares output bytes against the same expected bytecode that
     verify_stage.py compares per-branch sources against.

Usage:
    python3 tools/verify_unified.py \\
        --src-tree /path/to/another-world-source-reconstruction/src/levels
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

# Reuse verify_stage's PORTS + paths
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_stage import PORTS, AWVM_ASM, expected_bytes, CHUNK_SIZE  # noqa: E402


def preprocess_and_assemble(unified_asm_in: Path, flags_file: Path) -> bytes:
    """Preprocess a unified .asm.in for the given port's flags, expand
    FILL macros, and assemble with awvm-asm. Returns the resulting bytes."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        out_asm = td / unified_asm_in.with_suffix(".asm").name
        # awvm_preprocess.py handles ;@if BRANCH directives; FILL-macro
        # expansion happens inside it too via expand_fill_macros.
        subprocess.run(
            ["python3", str(Path(__file__).parent / "awvm_preprocess.py"),
             str(unified_asm_in), str(flags_file), "-o", str(out_asm)],
            check=True, capture_output=True, text=True,
        )
        subprocess.run([str(AWVM_ASM), out_asm.name], cwd=td,
                       check=True, capture_output=True, text=True)
        return out_asm.with_suffix(".bin").read_bytes()


def stage_from_unified_path(p: Path) -> str:
    """e.g. src/levels/_unified/LAKE.asm.in → 'LAKE'."""
    return p.stem.replace(".asm", "")


def unified_supports_branch(unified: Path, branch: str) -> bool:
    """Return True iff the unified file mentions this branch in a
    `;@if BRANCH ==` (or `;@elif BRANCH ==` / `;@if BRANCH in (...)`)
    directive. A unified file built for cart+gba only will not contain
    `chahi_amiga_1991` or `dos_1992`, and trying to preprocess it for
    those branches just emits the unified file's top-level body, which
    will not byte-match unless coincidence."""
    text = unified.read_text()
    return f'"{branch}"' in text  # simplest: branch name appears as a quoted token


def verify_unified_one(unified: Path, src_tree: Path) -> tuple[int, int]:
    """Returns (passes, fails)."""
    stage = stage_from_unified_path(unified)
    print(f"  {stage}:")
    p_count, f_count = 0, 0
    for port, spec in PORTS.items():
        if stage not in spec["stages"]:
            continue
        branch = spec["branch"]
        if not unified_supports_branch(unified, branch):
            print(f"    {port}: SKIP (unified file is not built for branch {branch})")
            continue
        # Find the flags file for this port.
        # Convention: source-reconstruction repo has
        #   src/levels/  ← this is `src_tree`
        #   releases/<port>.flags
        # so go up two parents then into releases/.
        flags_file = src_tree.parent.parent / "releases" / f"{port}.flags"
        if not flags_file.is_file():
            print(f"    {port}: SKIP (no {flags_file.name})")
            continue
        expected = expected_bytes(port, stage)
        if expected is None:
            continue
        try:
            assembled = preprocess_and_assemble(unified, flags_file)
        except subprocess.CalledProcessError as e:
            print(f"    {port}: ASSEMBLE-FAIL ({e.stderr.strip()[:80]})")
            f_count += 1
            continue
        if spec["format"] == "resource-bin":
            actual = assembled[: len(expected)]
        else:
            actual = assembled
        if actual == expected:
            p_count += 1
            print(f"    {port}: OK")
        else:
            f_count += 1
            print(f"    {port}: MISMATCH (expected={hashlib.md5(expected).hexdigest()[:12]} "
                  f"actual={hashlib.md5(actual).hexdigest()[:12]})")
    return p_count, f_count


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--src-tree", type=Path, required=True,
                   help="root of src/levels/<branch>/<stage>.asm tree")
    args = p.parse_args()

    unified_dir = args.src_tree / "_unified"
    if not unified_dir.is_dir():
        sys.exit(f"no _unified/ dir at {unified_dir}")

    total_p, total_f = 0, 0
    for unified in sorted(unified_dir.glob("*.asm.in")):
        print(f"\n=== unified: {unified.name} ===")
        p_, f_ = verify_unified_one(unified, args.src_tree)
        total_p += p_
        total_f += f_

    print(f"\nTOTAL: {total_p}/{total_p+total_f} (unified, port) byte-matches")
    if total_f:
        sys.exit(1)


if __name__ == "__main__":
    main()
