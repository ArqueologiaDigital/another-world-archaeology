#!/usr/bin/env python3
"""Strip redundant `;@raw=` annotations from per-arm chunks
under `src/levels/_unified/`.

Companion to `strip_redundant_raw_annotations.py`. That tool
operates on per-branch `.asm` sources; this one operates on the
chunk files included by unified `.asm.in` files. Per-arm chunks
(`<arm>__*.inc`) are only consumed by a single port, so the audit
runs that one port's preprocess+assemble pipeline.

Shared chunks (chapter chunks like `<stage>/<stage>_<theme>.inc`,
helpers in `_helpers/`) are NOT handled here — they require
multi-port verification and are tracked separately in #0084.

Method per chunk:
  1. Map chunk path → (arm, port, parent `<STAGE>.asm.in`).
  2. Compute baseline bytes by preprocessing the parent for that
     port and assembling.
  3. Strip every `;@raw=` in the chunk; rewrite chunk file in
     place.
  4. Re-compute bytes; if they match baseline, the strip stands.
  5. Otherwise restore the chunk and bisect on annotation rank
     to find the redundant subset; rewrite with only those
     stripped.
  6. Verify (assemble matches baseline) before final write; on
     any error, restore original.

Usage:
  python3 tools/strip_redundant_raw_unified_chunks.py [--all]
                                                     [--stage STAGE]
                                                     [--arm ARM]
                                                     [--no-bisect]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path("/home/fsanches/compartilhado/another-world-archaeology")
SRC_TREE = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
LEVELS = SRC_TREE / "src" / "levels"
RELEASES = SRC_TREE / "releases"
AWVM_ASM = Path(
    "/home/fsanches/compartilhado/AnotherWorld_VMTools/target/release/awvm-asm"
)
AWVM_PREPROCESS = REPO_ROOT / "tools" / "awvm_preprocess.py"

RE_RAW = re.compile(r"\s*;@raw=([0-9a-fA-FxX,\s]+)\s*$")
ARM_PREFIX = re.compile(r"^(amiga|dos|cart|gba)__.*\.inc$")

# arm prefix → port name. cart maps to a representative cart port
# (genesis_europe); since genesis_europe and snes_eu share byte-
# identical bytecode (research/05), one is enough.
ARM_TO_PORT = {
    "amiga": "amiga",
    "dos": "msdos",
    "cart": "genesis_europe",
    "gba": "gba_usa",
}


def stage_from_chunk(chunk: Path) -> str:
    """e.g. .../caves/dos__entry.inc → 'CAVES'."""
    return chunk.parent.name.upper()


def parent_asm_in(chunk: Path) -> Path:
    return LEVELS / "_unified" / f"{stage_from_chunk(chunk)}.asm.in"


def arm_of(chunk: Path) -> str | None:
    m = ARM_PREFIX.match(chunk.name)
    return m.group(1) if m else None


def preprocess_and_assemble(asm_in: Path, port: str, hint: str) -> bytes:
    flags = RELEASES / f"{port}.flags"
    if not flags.is_file():
        raise FileNotFoundError(f"{flags}")
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        out_asm = td / f"{hint}.asm"
        subprocess.run(
            [
                "python3",
                str(AWVM_PREPROCESS),
                str(asm_in),
                str(flags),
                "-o",
                str(out_asm),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [str(AWVM_ASM), out_asm.name],
            cwd=td,
            check=True,
            capture_output=True,
            text=True,
        )
        return out_asm.with_suffix(".bin").read_bytes()


def apply_strip_mask(text: str, ranks: set[int]) -> str:
    out = []
    rank = 0
    for line in text.splitlines(keepends=True):
        if RE_RAW.search(line):
            if rank in ranks:
                m = RE_RAW.search(line)
                stripped = line[: m.start()].rstrip()
                if line.endswith("\n"):
                    stripped += "\n"
                line = stripped
            rank += 1
        out.append(line)
    return "".join(out)


def bisect(
    chunk: Path,
    asm_in: Path,
    port: str,
    annotation_count: int,
    baseline: bytes,
    original_text: str,
    hint_prefix: str,
) -> set[int]:
    redundant: set[int] = set()

    def recurse(group: list[int]) -> None:
        if not group:
            return
        try_set = set(group) | redundant
        try:
            chunk.write_text(apply_strip_mask(original_text, try_set))
            out = preprocess_and_assemble(asm_in, port, hint_prefix)
        except subprocess.CalledProcessError:
            if len(group) == 1:
                return
            mid = len(group) // 2
            recurse(group[:mid])
            recurse(group[mid:])
            return
        if out == baseline:
            redundant.update(group)
            return
        if len(group) == 1:
            return
        mid = len(group) // 2
        recurse(group[:mid])
        recurse(group[mid:])

    recurse(list(range(annotation_count)))
    return redundant


def process_chunk(chunk: Path, allow_bisect: bool) -> tuple[int, int]:
    arm = arm_of(chunk)
    if arm not in ARM_TO_PORT:
        return (0, 0)
    port = ARM_TO_PORT[arm]
    asm_in = parent_asm_in(chunk)
    if not asm_in.is_file():
        return (0, 0)

    original_text = chunk.read_text()
    annotation_count = sum(
        1 for line in original_text.splitlines() if RE_RAW.search(line)
    )
    if annotation_count == 0:
        return (0, 0)

    rel = chunk.relative_to(SRC_TREE)
    print(f"  {rel} ({arm}→{port}, {annotation_count} ann)…", flush=True)

    try:
        baseline = preprocess_and_assemble(asm_in, port, chunk.stem + "_b")
    except subprocess.CalledProcessError as e:
        print(
            f"    baseline assemble failed: {e.stderr[:120]}",
            file=sys.stderr,
        )
        return (annotation_count, annotation_count)

    # Try stripping all
    try:
        chunk.write_text(
            apply_strip_mask(original_text, set(range(annotation_count)))
        )
        stripped_full = preprocess_and_assemble(
            asm_in, port, chunk.stem + "_s"
        )
    except subprocess.CalledProcessError:
        stripped_full = None

    if stripped_full == baseline:
        print(f"    ALL_REDUNDANT ({annotation_count} stripped)")
        return (annotation_count, 0)

    if not allow_bisect:
        chunk.write_text(original_text)
        print(f"    bytes_differ — restored (use without --no-bisect)")
        return (annotation_count, annotation_count)

    # Restore before bisecting
    chunk.write_text(original_text)
    redundant = bisect(
        chunk,
        asm_in,
        port,
        annotation_count,
        baseline,
        original_text,
        chunk.stem + "_bi",
    )

    # Apply final strip; verify; on any failure restore
    final_text = apply_strip_mask(original_text, redundant)
    chunk.write_text(final_text)
    try:
        verify = preprocess_and_assemble(asm_in, port, chunk.stem + "_v")
    except subprocess.CalledProcessError as e:
        print(
            f"    post-strip assemble failed; restoring. err={e.stderr[:120]}",
            file=sys.stderr,
        )
        chunk.write_text(original_text)
        return (annotation_count, annotation_count)
    if verify != baseline:
        print(f"    post-strip bytes differ from baseline; restoring.")
        chunk.write_text(original_text)
        return (annotation_count, annotation_count)

    kept = annotation_count - len(redundant)
    print(f"    stripped {len(redundant)}, kept {kept} load-bearing")
    return (annotation_count, kept)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all", action="store_true", help="process every per-arm chunk"
    )
    parser.add_argument(
        "--stage",
        type=str,
        help="restrict to one stage dir (e.g. caves)",
    )
    parser.add_argument(
        "--arm",
        type=str,
        help="restrict to one arm prefix (e.g. dos)",
        choices=list(ARM_TO_PORT.keys()),
    )
    parser.add_argument("--no-bisect", action="store_true")
    args = parser.parse_args()

    chunks: list[Path] = []
    base = LEVELS / "_unified"
    if args.stage:
        base = base / args.stage.lower()
    for chunk in sorted(base.rglob("*.inc")):
        if not arm_of(chunk):
            continue  # skip shared chunks
        if args.arm and arm_of(chunk) != args.arm:
            continue
        chunks.append(chunk)

    if not chunks:
        print("no chunks selected", file=sys.stderr)
        return 1

    total_before = 0
    total_after = 0
    for chunk in chunks:
        before, after = process_chunk(chunk, allow_bisect=not args.no_bisect)
        total_before += before
        total_after += after

    print(
        f"\ntotal annotations: {total_before} → {total_after} "
        f"(stripped: {total_before - total_after})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
