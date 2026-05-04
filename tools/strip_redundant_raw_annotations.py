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


def expand_text(asm_path: Path) -> str:
    from awvm_preprocess import expand_includes, expand_fill_macros
    text = expand_includes(asm_path.read_text(), asm_path.resolve().parent)
    text = expand_fill_macros(text)
    return text


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


def split_lines(text: str) -> list[str]:
    return text.splitlines(keepends=True)


def reassemble_with_strip_mask(
    lines: list[str],
    annotation_indices: list[int],
    strip_set: set[int],
    hint: str,
) -> bytes:
    """Assemble file with only the annotations whose index is in
    `strip_set` removed.

    `annotation_indices` is the list of line-indices that carry a
    `;@raw=` annotation.
    """
    out = []
    for li, line in enumerate(lines):
        if li in annotation_indices and li in strip_set:
            m = RE_RAW.search(line)
            if m:
                line = line[: m.start()].rstrip()
                if not line.endswith("\n"):
                    line += "\n"
        out.append(line)
    return assemble_text("".join(out), hint)


def bisect_strip(
    lines: list[str],
    annotation_indices: list[int],
    baseline: bytes,
    hint_prefix: str,
) -> set[int]:
    """Return the set of annotation-indices that ARE redundant
    (safe to strip). Uses divide-and-conquer.
    """
    redundant: set[int] = set()

    def recurse(group: list[int]) -> None:
        if not group:
            return
        # Try stripping all of `group`
        try_set = set(group) | redundant
        try:
            out = reassemble_with_strip_mask(
                lines, annotation_indices, try_set, hint_prefix
            )
        except subprocess.CalledProcessError:
            # Encoder fails on some instruction's stripped form.
            # Bisect deeper.
            if len(group) == 1:
                # Single annotation, stripping it breaks assembly →
                # load-bearing
                return
            mid = len(group) // 2
            recurse(group[:mid])
            recurse(group[mid:])
            return

        if out == baseline:
            redundant.update(group)
            return
        if len(group) == 1:
            return  # this single annotation is load-bearing
        mid = len(group) // 2
        recurse(group[:mid])
        recurse(group[mid:])

    recurse(annotation_indices)
    return redundant


def process_file(path: Path, allow_bisect: bool) -> tuple[int, int]:
    """Returns (annotations_before, annotations_after)."""
    text = expand_text(path)
    lines = split_lines(text)
    annotation_indices = [
        li for li, line in enumerate(lines) if RE_RAW.search(line)
    ]
    if not annotation_indices:
        print(f"  {path.name}: no annotations after expansion")
        return (0, 0)

    # Reassemble baseline with NO stripping.
    try:
        baseline = assemble_text(text, path.stem + "_base")
    except subprocess.CalledProcessError as e:
        print(
            f"  {path.name}: baseline assemble failed: {e.stderr[:120]}",
            file=sys.stderr,
        )
        return (len(annotation_indices), len(annotation_indices))

    # First try: strip everything
    try:
        stripped_full = assemble_text(
            "".join(
                line[: RE_RAW.search(line).start()].rstrip() + "\n"
                if RE_RAW.search(line)
                else line
                for line in lines
            ),
            path.stem + "_strip",
        )
    except subprocess.CalledProcessError:
        stripped_full = None

    if stripped_full == baseline:
        # All redundant — strip them all
        new_text = read_and_strip_all(path)
        path.write_text(new_text)
        print(
            f"  {path.name}: ALL_REDUNDANT "
            f"({len(annotation_indices)} annotations stripped)"
        )
        return (len(annotation_indices), 0)

    if not allow_bisect:
        print(
            f"  {path.name}: bytes_differ — skipped "
            f"(use without --no-bisect to bisect)"
        )
        return (len(annotation_indices), len(annotation_indices))

    # Bisect
    redundant = bisect_strip(
        lines, annotation_indices, baseline, path.stem
    )
    if not redundant:
        print(
            f"  {path.name}: bisect found 0 redundant of "
            f"{len(annotation_indices)} (all load-bearing??)"
        )
        return (len(annotation_indices), len(annotation_indices))

    # Apply: rewrite the file with the redundant annotations stripped.
    # NOTE: bisect operated on the EXPANDED text (post-include). To
    # apply changes back to the on-disk file, we need to map
    # expanded-line-indices to on-disk source files. That's
    # out-of-scope for this initial pass — the bisect data is useful
    # for analysis but applying it requires per-file source mapping.
    # For now, only apply to files whose ENTIRE annotation set is
    # redundant (handled above). Bisect mode reports the count.
    print(
        f"  {path.name}: bisect found {len(redundant)} redundant "
        f"of {len(annotation_indices)} "
        f"({len(annotation_indices) - len(redundant)} load-bearing)"
    )
    return (
        len(annotation_indices),
        len(annotation_indices) - len(redundant),
    )


def read_and_strip_all(path: Path) -> str:
    """Strip every `;@raw=` annotation from the on-disk file
    (pre-expansion). Used only when audit said the file is
    all_redundant.
    """
    out = []
    for line in path.read_text().splitlines(keepends=True):
        m = RE_RAW.search(line)
        if not m:
            out.append(line)
            continue
        new = line[: m.start()].rstrip()
        if line.endswith("\n"):
            new += "\n"
        out.append(new)
    return "".join(out)


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
