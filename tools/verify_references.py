#!/usr/bin/env python3
"""Verify the integrity of every file listed in `references/MANIFEST.sha256`.

The repo's standing policy is that files under `references/` are
**frozen verbatim** once committed: walkthroughs, archived
documentation, primary-source captures. Git itself has no read-only
flag, so this script is the automated infringement detector for that
policy.

It checks three things:

1. **Hash drift** — every file listed in the manifest must hash to the
   recorded sha256.
2. **Missing files** — every path in the manifest must exist on disk.
3. **Extra files** — every file under `references/` (other than the
   manifest itself and any explicitly-marked auxiliary files) must
   appear in the manifest.

Manifest format is the standard `sha256sum` output:

    <64-hex-hash>  <path-relative-to-references/>

Lines starting with `#` and blank lines are ignored.

Exit codes:
    0  all good
    1  one or more violations
    2  manifest itself missing or unreadable
"""

import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REFERENCES_DIR = REPO / "references"
MANIFEST_PATH = REFERENCES_DIR / "MANIFEST.sha256"

# Files inside references/ that are part of the infrastructure rather than
# frozen content — exempt from the "must appear in manifest" rule.
INFRASTRUCTURE_FILES = {"MANIFEST.sha256", "README.md"}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_manifest(text: str):
    entries = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        # Standard sha256sum format: "<hash>  <path>" (two spaces).
        # Tolerate single-space and tab separators too.
        parts = line.split(None, 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise ValueError(
                f"references/MANIFEST.sha256:{lineno}: malformed line: {raw!r}"
            )
        hex_hash, path = parts
        entries.append((hex_hash.lower(), path.lstrip("*").strip()))
    return entries


def main():
    if not MANIFEST_PATH.is_file():
        print(
            f"verify-references: manifest not found at "
            f"{MANIFEST_PATH.relative_to(REPO)}",
            file=sys.stderr,
        )
        return 2

    try:
        entries = parse_manifest(MANIFEST_PATH.read_text(encoding="utf-8"))
    except ValueError as e:
        print(f"verify-references: {e}", file=sys.stderr)
        return 2

    declared_paths = {p for _, p in entries}
    violations = []

    # Check declared entries.
    for expected_hash, rel_path in entries:
        path = REFERENCES_DIR / rel_path
        if not path.is_file():
            violations.append(("missing", rel_path, expected_hash, None))
            continue
        actual_hash = sha256_of(path)
        if actual_hash != expected_hash:
            violations.append(("drift", rel_path, expected_hash, actual_hash))

    # Check for extras.
    if REFERENCES_DIR.is_dir():
        for path in sorted(REFERENCES_DIR.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(REFERENCES_DIR).as_posix()
            if rel in INFRASTRUCTURE_FILES:
                continue
            if rel not in declared_paths:
                violations.append(("extra", rel, None, sha256_of(path)))

    if not violations:
        print(f"verify-references: OK — {len(entries)} file(s) verified")
        return 0

    print(f"verify-references: {len(violations)} violation(s):", file=sys.stderr)
    for kind, rel, expected, actual in violations:
        if kind == "missing":
            print(f"  MISSING  {rel}  (expected sha256 {expected})", file=sys.stderr)
        elif kind == "drift":
            print(
                f"  DRIFT    {rel}\n"
                f"             expected {expected}\n"
                f"             actual   {actual}",
                file=sys.stderr,
            )
        elif kind == "extra":
            print(f"  EXTRA    {rel}  (sha256 {actual}, not in manifest)", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
