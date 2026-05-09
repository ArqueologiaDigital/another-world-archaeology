#!/usr/bin/env python3
"""Find routines defined byte-identically in 2+ chunks within the
SAME stage (typically across the per-arm chunks
`<arm>__post_X.inc` / `<arm>__post_Y.inc` / etc.).

Companion to `tools/scan_cross_stage_helpers.py` — the cross-stage
scanner groups by stage and only flags labels appearing in 2+
*different* stages, so it misses the case where a routine is
duplicated across multiple arm-gated chunks within ONE stage.

This scanner reports those intra-stage duplicates, which are
candidates for hoisting into either a stage-local helper file
(`<stage>/<helper>.inc`) or `_unified/_helpers/<NAME>.inc`. Each
hoist removes ~3-6 lines of source duplication per routine.

Surfaced from issue #0095. The body-comparison + jump-free filter
matches `scan_cross_stage_helpers.py` to keep tooling decisions
consistent.

Usage:

    python3 tools/scan_intra_stage_duplicates.py
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from _paths import AW_SRC

SRC_ROOT = AW_SRC
LEVELS = SRC_ROOT / "src/levels"

RE_LABEL = re.compile(r"^([A-Za-z_][A-Za-z_0-9]*):$")
RE_DIRECTIVE = re.compile(r"^\s*;@")

# Mnemonics that resolve to absolute addresses. Routines containing
# any of these can't be safely hoisted because the operand bytes
# would differ per arm even when the source text matches.
JUMP_MNEMONICS = {"call", "jmp", "je", "jne", "jl", "jg", "jle", "jge",
                  "djnz", "setup", "song", "load", "play"}


def parse_routines(text: str) -> list[tuple[str, str]]:
    """Return list of (label, body_text). Closes a routine on the next
    label, on any `;@`-directive boundary, or at EOF."""
    out = []
    cur_label = None
    cur_body: list[str] = []
    for ln in text.splitlines():
        if RE_DIRECTIVE.match(ln):
            if cur_label is not None:
                out.append((cur_label, "\n".join(cur_body)))
                cur_label = None
                cur_body = []
            continue
        m = RE_LABEL.match(ln)
        if m:
            if cur_label is not None:
                out.append((cur_label, "\n".join(cur_body)))
            cur_label = m.group(1)
            cur_body = []
            continue
        if cur_label is None:
            continue
        cur_body.append(ln)
    if cur_label is not None:
        out.append((cur_label, "\n".join(cur_body)))
    return out


def normalize_body(body: str) -> str:
    """Strip `;@raw=` annotations, inline comments, and blank lines."""
    out = []
    for ln in body.splitlines():
        s = re.sub(r"\s*;@raw=.*$", "", ln)
        s = re.sub(r"\s*;.*$", "", s).rstrip()
        if not s:
            continue
        out.append(s.strip())
    return "\n".join(out)


def has_jumps(body: str) -> bool:
    for ln in body.splitlines():
        s = ln.strip()
        if not s:
            continue
        word = s.split()[0] if s.split() else ""
        if word.lower() in JUMP_MNEMONICS:
            return True
    return False


def main() -> int:
    # (stage, label) -> {body_normalized: [chunk_filenames]}
    by_stage_label: dict[tuple[str, str], dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for chunk in sorted(LEVELS.glob("_unified/*/*.inc")):
        stage = chunk.parent.name.upper()
        if stage == "_HELPERS":
            continue
        text = chunk.read_text()
        for label, body in parse_routines(text):
            body_norm = normalize_body(body)
            if not body_norm.strip() or has_jumps(body_norm):
                continue
            by_stage_label[(stage, label)][body_norm].append(chunk.name)

    candidates: list[tuple[int, int, str, str, list[str], str]] = []
    # (n_files, body_len, stage, label, files, body)
    for (stage, label), bodies in by_stage_label.items():
        if len(bodies) != 1:
            continue  # divergent bodies — not a clean duplicate
        body, files = next(iter(bodies.items()))
        if len(files) < 2:
            continue
        candidates.append((len(files), len(body), stage, label, files, body))

    candidates.sort(key=lambda c: (-c[0], -c[1], c[2], c[3]))

    print(f"Intra-stage duplicate routine definitions (jump-free, "
          f"byte-identical across 2+ chunks in the same stage):")
    print(f"  Total candidates: {len(candidates)}\n")

    # Group by stage for the summary
    by_stage: dict[str, int] = defaultdict(int)
    for n, _, stage, _, _, _ in candidates:
        by_stage[stage] += 1
    print("Per-stage count:")
    for stage in sorted(by_stage, key=lambda s: -by_stage[s]):
        print(f"  {stage:<12s} {by_stage[stage]}")
    print()

    # Sample the top candidates
    print("Top candidates (highest file-count first, then longest body):")
    for n_files, body_len, stage, label, files, body in candidates[:30]:
        first_line = body.splitlines()[0].strip() if body else "(empty)"
        print(f"  {label:<40s} stage={stage:<10s} n={n_files}  files={files[:3]}{'...' if n_files > 3 else ''}")
        print(f"      first: {first_line[:80]}")
    if len(candidates) > 30:
        print(f"\n  ... and {len(candidates) - 30} more.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
