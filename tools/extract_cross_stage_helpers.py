#!/usr/bin/env python3
"""Phase 6: extract cross-stage shared helpers to `_unified/_helpers/`.

For each routine that:
  - Is defined in 2+ unified `.asm.in` files
  - Has byte-identical body across all defining stages
  - Has no internal jumps/calls (so the assembled bytes are
    independent of stage-specific address resolution)

Move the body to `_unified/_helpers/<ROUTINE>.inc` and replace each
stage's local definition with `;@include "_helpers/<ROUTINE>.inc"`.

The surrounding `;@if BRANCH ==` block (if any) stays in the
stage's `.asm.in`; the include directive replaces just the routine
body.

Verification: caller runs verify_unified after, expects 27/27.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

SRC_ROOT = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
LEVELS = SRC_ROOT / "src/levels"

RE_LABEL = re.compile(r"^([A-Za-z_][A-Za-z_0-9]*):$")
RE_DIRECTIVE = re.compile(r"^\s*;@")

JUMP_MNEMONICS = {"call", "jmp", "je", "jne", "jl", "jg", "jle", "jge",
                  "djnz", "setup", "song", "load", "play"}


def find_routine_lines(text: str, name: str) -> tuple[int, int] | None:
    """Return (start_line_idx, end_line_idx_exclusive) for the
    routine `name`. Body extends from the label line until the
    next label or `;@` directive."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.rstrip() == f"{name}:":
            # End is first subsequent label or `;@` directive (not
            # counting blank lines)
            for j in range(i + 1, len(lines)):
                stripped = lines[j].rstrip()
                m = RE_LABEL.match(stripped)
                if m:
                    return (i, j)
                if RE_DIRECTIVE.match(stripped):
                    return (i, j)
            return (i, len(lines))
    return None


def extract_routine_body(text: str, name: str) -> str | None:
    """Return the routine's body text (label line + indented body
    lines), or None if not found."""
    rng = find_routine_lines(text, name)
    if rng is None:
        return None
    start, end = rng
    lines = text.splitlines()
    return "\n".join(lines[start:end]).rstrip()


def has_jumps_in_body(body: str) -> bool:
    for ln in body.splitlines():
        s = ln.strip()
        if not s or s.startswith(";"):
            continue
        word = s.split()[0] if s.split() else ""
        if word.lower() in JUMP_MNEMONICS:
            return True
    return False


def normalize_body(body: str) -> str:
    """Strip ;@raw= comments + inline ; comments + blank lines for
    body-equivalence comparison."""
    out = []
    for ln in body.splitlines():
        s = re.sub(r"\s*;@raw=.*$", "", ln)
        s = re.sub(r"\s*;.*$", "", s).rstrip()
        if not s:
            continue
        out.append(s.strip())
    return "\n".join(out)


def main() -> int:
    helpers_dir = LEVELS / "_unified" / "_helpers"
    helpers_dir.mkdir(exist_ok=True)

    # Collect all routines per stage from .asm.in files only (chunks
    # have arm-specific dispatch and aren't sharable across stages
    # in this phase).
    by_label: dict[str, dict[Path, str]] = defaultdict(dict)
    for asm_in in sorted(LEVELS.glob("_unified/*.asm.in")):
        text = asm_in.read_text()
        for m in re.finditer(r"^([A-Za-z_][A-Za-z_0-9]*):$", text, re.M):
            label = m.group(1)
            body = extract_routine_body(text, label)
            if body is None:
                continue
            by_label[label][asm_in] = body

    candidates: list[tuple[str, str, list[Path]]] = []
    for label, per_file in by_label.items():
        if len(per_file) < 2:
            continue
        normalized = {f: normalize_body(b) for f, b in per_file.items()}
        bodies = set(normalized.values())
        if len(bodies) != 1:
            continue
        body_norm = next(iter(bodies))
        if not body_norm.strip():
            continue
        # Must not contain jumps/calls
        if has_jumps_in_body(body_norm):
            continue
        # Use the first file's body verbatim (with `;@raw=` and
        # comments preserved) as the canonical source.
        canonical_file = sorted(per_file.keys())[0]
        candidates.append((label, per_file[canonical_file],
                          sorted(per_file.keys())))

    print(f"Extractable candidates: {len(candidates)}")

    # Apply: for each candidate, write `_helpers/<NAME>.inc` and
    # replace each stage's local definition with `;@include`.
    total_extracted = 0
    total_replacements = 0
    for label, canonical_body, stage_files in candidates:
        helper_path = helpers_dir / f"{label}.inc"
        helper_path.write_text(canonical_body + "\n")
        total_extracted += 1

        for stage_file in stage_files:
            text = stage_file.read_text()
            rng = find_routine_lines(text, label)
            if rng is None:
                continue
            start, end = rng
            lines = text.splitlines()
            replacement = f';@include "_helpers/{label}.inc"'
            new_lines = lines[:start] + [replacement] + lines[end:]
            new_text = "\n".join(new_lines)
            if text.endswith("\n"):
                new_text += "\n"
            stage_file.write_text(new_text)
            total_replacements += 1

    print(f"Extracted: {total_extracted} helpers")
    print(f"Replacements: {total_replacements} (across stage .asm.ins)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
