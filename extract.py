#!/usr/bin/env python3
"""Top-level extraction entry point.

Reads `metadata.json`, locates each release's source file in the
local permanent archive at `original_files/<key>/`, dispatches to
the format-specific extractor under `extractors/`, and writes
per-release output to `work/<package_md5>/`. The archive is never
deleted from — it's the project's safety net against upstream
URL churn.

Usage:
    python3 extract.py                # extract every release
    python3 extract.py --slug dos     # extract one release
"""

import argparse
import json
import sys
from pathlib import Path

import extractors

REPO = Path(__file__).resolve().parent
METADATA = REPO / "metadata.json"
ARCHIVE_ROOT = REPO / "original_files"  # local permanent archive (never deleted)
WORK_ROOT = REPO / "work"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument(
        "--slug",
        help="Extract only the release with this slug (default: all releases)",
    )
    args = parser.parse_args()

    metadata = json.loads(METADATA.read_text(encoding="utf-8"))

    if args.slug:
        targets = [m for m in metadata if m.get("slug") == args.slug]
        if not targets:
            print(f"error: no release with slug {args.slug!r} in metadata.json", file=sys.stderr)
            return 2
    else:
        targets = metadata

    failures = 0
    for meta in targets:
        slug = meta.get("slug", "?")
        # `archive_dir` is the authoritative directory name under
        # `original_files/`. Older single-file entries set it to the
        # package md5 (so the two coincide), but newer multi-file
        # entries (e.g. 3DO `.bin/.cue`, Atari ST `.zip` of two `.stx`)
        # use a human-readable slug instead — md5sum is then a
        # checksum *of the package file*, not a directory pointer.
        key = meta.get("archive_dir") or meta.get("md5sum")
        if not key:
            print(f"[{slug}] skip: no archive_dir or md5sum recorded in metadata.json")
            continue

        archive_dir = ARCHIVE_ROOT / key
        work_dir = WORK_ROOT / key

        if not archive_dir.is_dir():
            print(
                f"[{slug}] skip: no archived source under {archive_dir.relative_to(REPO)} "
                f"(run `make fetch` once it is implemented)"
            )
            continue

        print(f"[{slug}] extracting from {archive_dir.relative_to(REPO)}/ ...")
        try:
            manifest = extractors.extract(meta, archive_dir, work_dir)
        except NotImplementedError as e:
            print(f"[{slug}] not implemented: {e}")
            failures += 1
            continue
        except Exception as e:
            print(f"[{slug}] FAILED: {type(e).__name__}: {e}", file=sys.stderr)
            failures += 1
            continue

        print(
            f"[{slug}] wrote {manifest['resource_count']} resources to "
            f"{work_dir.relative_to(REPO)}/"
        )

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
