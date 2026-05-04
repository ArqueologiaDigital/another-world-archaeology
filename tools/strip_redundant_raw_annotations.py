#!/usr/bin/env python3
"""Strip `;@raw=` annotations whose presence does not change the
assembled byte stream.

Companion to `tools/audit_raw_annotations.py`. The audit reports
which whole .asm files are `all_redundant` — every `;@raw=` in them
can be deleted with no byte-level effect. This script does the
deletion.

For files that are NOT all_redundant, it falls back to a
per-annotation bisect: strip half the annotations, reassemble; if
output matches baseline, that half is redundant and the cut sticks;
otherwise recurse into both halves. Annotations that survive the
bisect are load-bearing.

Usage:
  python3 tools/strip_redundant_raw_annotations.py --file PATH [--no-bisect]
  python3 tools/strip_redundant_raw_annotations.py --branch dos_1992
  python3 tools/strip_redundant_raw_annotations.py --all
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path("/home/fsanches/compartilhado/another-world-archaeology")
SRC_ROOT = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
AWVM_ASM = Path(
    "/home/fsanches/compartilhado/AnotherWorld_VMTools/target/release/awvm-asm"
)

sys.path.insert(0, str(REPO_ROOT / "tools"))

RE_RAW = re.compile(r"\s*;@raw=([0-9a-fA-FxX,\s]+)\s*$")


def assemble_text(text: str, hint: str) -> bytes:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        f = td / f"{hint}.asm"
        f.write_text(text)
        subprocess.run(
            [str(AWVM_ASM), f.name],
            cwd=td,
            check=True,
            capture_output=True,
            text=True,
        )
        return f.with_suffix(".bin").read_bytes()


def apply_strip_mask(source_text: str, strip_ranks: set[int]) -> str:
    """Return source text with the k-th annotations (k in
    `strip_ranks`) removed. Annotation rank is the 0-based index in
    encounter order.
    """
    out = []
    rank = 0
    for line in source_text.splitlines(keepends=True):
        if RE_RAW.search(line):
            if rank in strip_ranks:
                m = RE_RAW.search(line)
                stripped = line[: m.start()].rstrip()
                if line.endswith("\n"):
                    stripped += "\n"
                line = stripped
            rank += 1
        out.append(line)
    return "".join(out)


def assemble_source(source_text: str, asm_path: Path, hint: str) -> bytes:
    """Expand `;@include`s using `asm_path`'s parent dir as anchor
    so that `;@include "../_common_vars.inc"` resolves correctly,
    then assemble."""
    from awvm_preprocess import expand_includes, expand_fill_macros
    expanded = expand_includes(source_text, asm_path.resolve().parent)
    expanded = expand_fill_macros(expanded)
    return assemble_text(expanded, hint)


def bisect_strip(
    source_text: str,
    asm_path: Path,
    annotation_count: int,
    baseline: bytes,
    hint_prefix: str,
) -> set[int]:
    """Return the set of annotation-RANKS (0..annotation_count-1)
    that ARE redundant (safe to strip). Uses divide-and-conquer.
    """
    redundant: set[int] = set()

    def recurse(group: list[int]) -> None:
        if not group:
            return
        try_set = set(group) | redundant
        try:
            stripped_text = apply_strip_mask(source_text, try_set)
            out = assemble_source(stripped_text, asm_path, hint_prefix)
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


def process_file(path: Path, allow_bisect: bool) -> tuple[int, int]:
    """Returns (annotations_before, annotations_after)."""
    source_text = path.read_text()
    annotation_count = sum(
        1 for line in source_text.splitlines() if RE_RAW.search(line)
    )
    if annotation_count == 0:
        print(f"  {path.name}: no annotations in source")
        return (0, 0)

    try:
        baseline = assemble_source(source_text, path, path.stem + "_base")
    except subprocess.CalledProcessError as e:
        print(
            f"  {path.name}: baseline assemble failed: {e.stderr[:120]}",
            file=sys.stderr,
        )
        return (annotation_count, annotation_count)

    # First try: strip everything in source
    try:
        all_stripped_text = apply_strip_mask(
            source_text, set(range(annotation_count))
        )
        stripped_full = assemble_source(
            all_stripped_text, path, path.stem + "_strip"
        )
    except subprocess.CalledProcessError:
        stripped_full = None

    if stripped_full == baseline:
        path.write_text(all_stripped_text)
        print(
            f"  {path.name}: ALL_REDUNDANT "
            f"({annotation_count} annotations stripped)"
        )
        return (annotation_count, 0)

    if not allow_bisect:
        print(
            f"  {path.name}: bytes_differ — skipped "
            f"(use without --no-bisect to bisect)"
        )
        return (annotation_count, annotation_count)

    print(
        f"  {path.name}: bisecting {annotation_count} annotations…",
        flush=True,
    )
    redundant = bisect_strip(
        source_text, path, annotation_count, baseline, path.stem
    )
    if not redundant:
        print(
            f"  {path.name}: bisect found 0 redundant of "
            f"{annotation_count} (all load-bearing??)"
        )
        return (annotation_count, annotation_count)

    new_text = apply_strip_mask(source_text, redundant)
    # Sanity check: the post-strip source must still assemble to baseline.
    try:
        verify = assemble_source(new_text, path, path.stem + "_verify")
    except subprocess.CalledProcessError as e:
        print(
            f"  {path.name}: post-strip assemble FAILED, NOT writing. "
            f"err={e.stderr[:120]}",
            file=sys.stderr,
        )
        return (annotation_count, annotation_count)
    if verify != baseline:
        print(
            f"  {path.name}: post-strip bytes differ from baseline; "
            f"NOT writing.",
            file=sys.stderr,
        )
        return (annotation_count, annotation_count)

    path.write_text(new_text)
    print(
        f"  {path.name}: stripped {len(redundant)} redundant of "
        f"{annotation_count} "
        f"({annotation_count - len(redundant)} load-bearing kept)"
    )
    return (annotation_count, annotation_count - len(redundant))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, action="append", default=[])
    parser.add_argument("--branch", type=str)
    parser.add_argument("--all", action="store_true")
    parser.add_argument(
        "--no-bisect",
        action="store_true",
        help="for files that aren't all_redundant, skip the bisect "
        "analysis (just report and continue)",
    )
    args = parser.parse_args()

    files: list[Path] = []
    if args.file:
        files.extend(args.file)
    if args.branch:
        d = SRC_ROOT / "src" / "levels" / args.branch
        files.extend(sorted(d.glob("*.asm")))
    if args.all:
        for branch_dir in sorted(
            (SRC_ROOT / "src" / "levels").iterdir()
        ):
            if branch_dir.is_dir() and not branch_dir.name.startswith("_"):
                files.extend(sorted(branch_dir.glob("*.asm")))
    if not files:
        parser.error("--file, --branch, or --all required")

    total_before = 0
    total_after = 0
    for f in files:
        before, after = process_file(f, allow_bisect=not args.no_bisect)
        total_before += before
        total_after += after

    print(
        f"\ntotal annotations: {total_before} → {total_after} "
        f"(stripped: {total_before - total_after})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
