#!/usr/bin/env python3
"""Phase 6 prep: find routines defined in 2+ stages with byte-identical
source AND no internal jumps/calls.

Output a candidate list sorted by:
  1. Number of stages that share the routine (more = higher impact).
  2. Routine length (longer = more savings).

Reasoning: AW VM bytecode uses 2-byte absolute addresses for
jumps/calls, so a routine with internal flow control would emit
different bytes per stage even from identical source text. We only
extract jump/call-free routines.
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

# Mnemonics that resolve to absolute addresses. Routines containing
# any of these can't be safely shared across stages because the
# operand bytes would differ per stage.
JUMP_MNEMONICS = {"call", "jmp", "je", "jne", "jl", "jg", "jle", "jge",
                  "djnz", "setup", "song", "load", "play"}


def parse_routines(text: str) -> list[tuple[str, str]]:
    """Return list of (label, body_text). Body is normalized: stripped
    of trailing comments and `;@raw=` annotations."""
    out = []
    cur_label = None
    cur_body: list[str] = []
    for ln in text.splitlines():
        if RE_DIRECTIVE.match(ln):
            # Hitting a `;@if`/`;@elif`/`;@else`/`;@endif` boundary
            # closes the current routine (we don't recurse into
            # branch-conditional bodies).
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
    """Strip trailing whitespace, drop blank lines, drop `;@raw=`
    annotations and inline comments."""
    out = []
    for ln in body.splitlines():
        # Drop `;@raw=` and any inline comment after it
        s = re.sub(r"\s*;@raw=.*$", "", ln)
        s = re.sub(r"\s*;.*$", "", s).rstrip()
        if not s:
            continue
        out.append(s.strip())
    return "\n".join(out)


def has_jumps(body: str) -> bool:
    """True if the body contains any jump/call/load mnemonic."""
    for ln in body.splitlines():
        s = ln.strip()
        if not s:
            continue
        word = s.split()[0] if s.split() else ""
        if word.lower() in JUMP_MNEMONICS:
            return True
    return False


def main() -> int:
    by_name_per_stage: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    # by_name_per_stage[label][stage] = {body_normalized}

    for asm_in in sorted(LEVELS.glob("_unified/*.asm.in")):
        stage = asm_in.name[: -len(".asm.in")]
        text = asm_in.read_text()
        for label, body in parse_routines(text):
            by_name_per_stage[label][stage].add(normalize_body(body))

    # Also examine chunks
    for chunk in sorted(LEVELS.glob("_unified/*/*.inc")):
        stage = chunk.parent.name.upper()
        text = chunk.read_text()
        for label, body in parse_routines(text):
            by_name_per_stage[label][stage].add(normalize_body(body))

    candidates: list[tuple[int, int, str, str, set[str]]] = []
    # (n_stages, body_len, label, body_normalized, stages_set)
    for label, per_stage in by_name_per_stage.items():
        if len(per_stage) < 2:
            continue
        # Need byte-identical body across all stages
        all_bodies: set[str] = set()
        for bodies in per_stage.values():
            all_bodies |= bodies
        if len(all_bodies) != 1:
            continue
        body = next(iter(all_bodies))
        if not body.strip():
            continue
        if has_jumps(body):
            continue
        candidates.append((len(per_stage), len(body),
                          label, body, set(per_stage.keys())))

    candidates.sort(key=lambda c: (-c[0], -c[1]))
    print(f"Candidate cross-stage shared helpers (jump-free, "
          f"byte-identical body, present in 2+ stages):")
    print(f"  Total candidates: {len(candidates)}\n")
    for n_stages, body_len, label, body, stages in candidates[:30]:
        first_line = body.splitlines()[0].strip() if body else "(empty)"
        print(f"  {label:<60s} stages={n_stages} ({', '.join(sorted(stages))})")
        print(f"      first: {first_line[:80]}")
    if len(candidates) > 30:
        print(f"\n  ... and {len(candidates) - 30} more.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
