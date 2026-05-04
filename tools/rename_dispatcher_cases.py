#!/usr/bin/env python3
"""Phase 3: rename `LABEL_<HEX>` case-targets of named dispatchers.

Per-FILE scope (NOT global) — `LABEL_<HEX>` names are
bytecode-address-derived, so the same hex string can refer to
unrelated routines in different per-branch source files. We never
rename across file boundaries.

For each scoping unit (per-branch `<branch>/<STAGE>.asm`, or unified
arm = `<stage>/<arm>__*.inc` + the matching `;@if BRANCH ==` block in
`_unified/<STAGE>.asm.in`), we:
  1. Locate routines whose label contains `DISPATCH`.
  2. Find `je [V], C, LABEL_<HEX>` case lines inside each dispatcher.
  3. If `LABEL_<HEX>` is a case-target of EXACTLY ONE (dispatcher,
     constant) pair within the scope, propose
     `<DISPATCHER>_CASE_<C>` as its new name.
  4. Skip if the proposed name already exists in the scope.
  5. Apply renames within that scope only.

Implementation note: per-branch sources are processed as standalone
files. Unified sources use a more complex scoping scheme — left as
a TODO for a follow-up tool. For now, only per-branch is wired up.
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

RE_DISPATCHER_LABEL = re.compile(
    r"^([A-Z_][A-Z_0-9]*(?:DISPATCH|DISPATCHER)[A-Z_0-9]*):$"
)
RE_OTHER_LABEL = re.compile(r"^([A-Z_][A-Z_0-9]*):$")
RE_JE_CASE = re.compile(
    r"^\s*je\s+\[([^\]]+)\]\s*,\s*([0-9A-Fa-fxX]+)\s*,\s*(LABEL_[0-9A-Fa-f]+)\b"
)


def parse_int_lit(s: str) -> int | None:
    s = s.strip()
    try:
        return int(s, 0)
    except ValueError:
        return None


def collect_per_file_renames(text: str) -> dict[str, str]:
    """Walk `text`, identify dispatcher cases, return rename map."""
    cases: dict[str, set[tuple[str, int]]] = defaultdict(set)
    cur_dispatcher = None
    for ln in text.splitlines():
        m = RE_DISPATCHER_LABEL.match(ln.rstrip())
        if m:
            cur_dispatcher = m.group(1)
            continue
        m2 = RE_OTHER_LABEL.match(ln.rstrip())
        if m2:
            cur_dispatcher = None
            continue
        if cur_dispatcher is None:
            continue
        m3 = RE_JE_CASE.match(ln)
        if not m3:
            continue
        const = parse_int_lit(m3.group(2))
        if const is None:
            continue
        target = m3.group(3)
        cases[target].add((cur_dispatcher, const))

    # Existing labels in this file (avoid name collision)
    existing = set()
    for ln in text.splitlines():
        m = re.match(r"^([A-Z_][A-Z_0-9]+):$", ln.rstrip())
        if m:
            existing.add(m.group(1))

    renames: dict[str, str] = {}
    for label, sources in cases.items():
        if len(sources) != 1:
            continue
        dispatcher, const = next(iter(sources))
        new_name = f"{dispatcher}_CASE_{const:02X}"
        if new_name in existing:
            continue
        renames[label] = new_name
    return renames


def rename_per_branch_files() -> tuple[int, int]:
    """Apply renames to per-branch source files. Returns
    (files_changed, total_renames)."""
    files_changed = 0
    total_renames = 0
    for asm in sorted(LEVELS.glob("*/*.asm")):
        if asm.parent.name in {"_unified", "_canonicalized"}:
            continue
        text = asm.read_text()
        renames = collect_per_file_renames(text)
        if not renames:
            continue
        new = text
        for old, new_name in renames.items():
            new = re.sub(rf"\b{re.escape(old)}\b", new_name, new)
        asm.write_text(new)
        files_changed += 1
        total_renames += len(renames)
        print(f"  {asm.relative_to(LEVELS)}: {len(renames)} renames")
    return files_changed, total_renames


def collect_arm_chunks(stage_dir: Path, arm: str) -> list[Path]:
    """Return all per-arm chunk files for the given stage + arm."""
    out: list[Path] = []
    out += sorted(stage_dir.glob(f"{arm}__entry.inc"))
    out += sorted(stage_dir.glob(f"{arm}__post_*.inc"))
    return out


def rename_unified_arm_scope() -> tuple[int, int]:
    """Apply per-(stage, arm) renames to unified chunks. Returns
    (chunks_changed, total_renames)."""
    chunks_changed = 0
    total_renames = 0
    for stage_dir in sorted((LEVELS / "_unified").glob("*")):
        if not stage_dir.is_dir():
            continue
        for arm in ("amiga", "cart", "dos"):
            chunks = collect_arm_chunks(stage_dir, arm)
            if not chunks:
                continue
            joined = "\n".join(c.read_text() for c in chunks)
            renames = collect_per_file_renames(joined)
            if not renames:
                continue
            # Apply renames to each chunk individually
            for chunk in chunks:
                text = chunk.read_text()
                new = text
                local = 0
                for old, new_name in renames.items():
                    count = len(re.findall(rf"\b{re.escape(old)}\b", new))
                    if count == 0:
                        continue
                    new = re.sub(rf"\b{re.escape(old)}\b", new_name, new)
                    local += count
                if local:
                    chunk.write_text(new)
                    chunks_changed += 1
                    total_renames += local
            print(f"  {stage_dir.name}/{arm}: {len(renames)} unique renames "
                  f"applied across {len(chunks)} chunks")
    return chunks_changed, total_renames


def main() -> int:
    print("Per-branch dispatcher case-target renames:")
    n_files, n_renames = rename_per_branch_files()
    print(f"  -> {n_renames} renames across {n_files} per-branch sources")

    print("\nUnified per-arm dispatcher case-target renames:")
    n_chunks, n_unified_renames = rename_unified_arm_scope()
    print(f"  -> {n_unified_renames} substitutions across {n_chunks} chunks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
