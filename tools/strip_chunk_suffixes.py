#!/usr/bin/env python3
"""
Strip gratuitous __<ARM>__POST_<NAME> suffixes from labels in
arm-specific chunk files (`<arm>__post_<name>.inc`). The suffix
mirrors the filename and is defensive but unnecessary — `;@if BRANCH ==`
makes arms mutually exclusive at compile time.

For each chunk file `<dir>/<arm>__post_<name>.inc`:
  1. Compute expected suffix: `__<ARM>__POST_<NAME>` (uppercase).
  2. Strip that exact suffix from all label tokens in the file.
  3. Verify the file's labels remain unique after the strip.

Skips files where stripping would create a duplicate label within
the same file (intra-chunk collision).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path


CHUNK_RE = re.compile(r"^(?P<arm>cart|dos|amiga)__post_(?P<name>[A-Z0-9_a-z]+)\.inc$")


def derive_suffix(filename: str) -> str | None:
    m = CHUNK_RE.match(filename)
    if not m:
        return None
    return f"__{m['arm'].upper()}__POST_{m['name'].upper()}"


def collect_label_defs(text: str) -> set[str]:
    """All `LABEL_NAME:` (definitions) — captures only at line start."""
    return set(re.findall(r"^([A-Za-z_][A-Za-z0-9_]*):", text, re.MULTILINE))


def strip_suffix_in_text(text: str, suffix: str) -> tuple[str, int]:
    """Return (new_text, n_replacements). Strips `suffix` from any
    LABEL token (sequence of identifier chars). The suffix only
    appears inside identifier tokens, so a plain string-replace is
    correct as long as the suffix itself is a complete trailing
    segment (which it is: `__ARM__POST_NAME` ends at non-identifier
    boundary)."""
    n = text.count(suffix)
    return text.replace(suffix, ""), n


def process_file(p: Path) -> tuple[bool, int, str]:
    """Returns (changed, n_replacements, message)."""
    suffix = derive_suffix(p.name)
    if suffix is None:
        return False, 0, "filename does not match pattern"
    original = p.read_text()
    if suffix not in original:
        return False, 0, "no suffix occurrences"

    candidate, n = strip_suffix_in_text(original, suffix)

    # Intra-file uniqueness check on label DEFS only.
    new_defs = collect_label_defs(candidate)
    candidate_lines = candidate.splitlines()
    def_count = sum(1 for line in candidate_lines if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", line))
    if def_count != len(new_defs):
        return False, 0, f"would create intra-file duplicate (def_count {def_count} != unique {len(new_defs)})"

    p.write_text(candidate)
    return True, n, "ok"


def main(roots: list[str]) -> int:
    total_files = 0
    changed_files = 0
    total_replacements = 0
    skipped = []

    for root in roots:
        for p in sorted(Path(root).glob("src/levels/_unified/*/*__post_*.inc")):
            total_files += 1
            changed, n, msg = process_file(p)
            if changed:
                changed_files += 1
                total_replacements += n
            elif msg not in {"no suffix occurrences", "filename does not match pattern"}:
                skipped.append((p, msg))

    print(f"Files scanned: {total_files}")
    print(f"Files changed: {changed_files}")
    print(f"Total label-token replacements: {total_replacements}")
    if skipped:
        print(f"Skipped (intra-file collisions): {len(skipped)}")
        for p, msg in skipped[:10]:
            print(f"  {p}: {msg}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: strip_chunk_suffixes.py <src-tree-root> [<more-roots>...]", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
