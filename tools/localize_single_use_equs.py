#!/usr/bin/env python3
"""For each `_unified/<STAGE>.asm.in`, find EQU declarations whose
defined symbol is referenced by **exactly one** chunk under
`_unified/<stage>/`, and move that EQU to the top of the chunk file.

Per-branch scope is preserved: if the EQU is defined inside a
`;@if BRANCH ==` block in `.asm.in`, that block (with its
condition) is reproduced at the top of the chunk file.

Symbols considered: any EQU whose name starts with `CINEMATIC_` or
`COMMON_VIDEO_` (these are stage-internal and have per-branch values
that vary; they're the bulk of the candidates).

Verification: caller runs verify_unified after; expects 27/27.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

from _paths import AW_SRC

SRC_ROOT = AW_SRC
LEVELS = SRC_ROOT / "src/levels"
ALL_BRANCHES = frozenset({"chahi_amiga_1991", "cartridge_1992",
                          "dos_1992", "gba_2004"})

RE_EQU = re.compile(
    r"^\s*([A-Z_][A-Z_0-9]*)\s+EQU\s+(.*?)(?:\s*;.*)?\s*$"
)
RE_INCLUDE = re.compile(r'^\s*;@include\s+"([^"]+)"\s*(?:;.*)?$')


def parse_cond(expr: str) -> frozenset[str]:
    """Parse `BRANCH == "x"` / `BRANCH in ("a","b")` to set of branches."""
    expr = expr.strip()
    m = re.fullmatch(r'BRANCH\s*==\s*"([^"]+)"', expr)
    if m:
        return frozenset({m.group(1)})
    m = re.fullmatch(r'BRANCH\s*!=\s*"([^"]+)"', expr)
    if m:
        return ALL_BRANCHES - {m.group(1)}
    m = re.fullmatch(r'BRANCH\s+in\s+\((.*)\)', expr)
    if m:
        items = [s.strip().strip('"') for s in m.group(1).split(",")]
        return frozenset(items)
    raise ValueError(f"unparseable BRANCH cond: {expr!r}")


def walk_branch_context(lines: list[str]):
    """Yield (line_index, line, active_branches_frozenset) for each line.
    `active_branches` reflects the `;@if`/`;@elif`/`;@else` stack."""
    stack: list[tuple[frozenset, frozenset]] = []
    # stack entry: (active_set, ever_taken_set) — ever_taken is the
    # union of conditions matched so far in this if/elif chain;
    # `;@else` activates whatever's NOT in ever_taken.
    base = ALL_BRANCHES
    for idx, ln in enumerate(lines, start=1):
        s = ln.strip()
        if s.startswith(";@if "):
            cond = parse_cond(s[len(";@if "):])
            outer = stack[-1][0] if stack else base
            new_active = outer & cond
            stack.append((new_active, cond))
            yield idx, ln, new_active
            continue
        if s.startswith(";@elif "):
            cond = parse_cond(s[len(";@elif "):])
            outer = stack[-2][0] if len(stack) >= 2 else base
            ever = stack[-1][1]
            new_active = (outer & cond) - ever
            stack[-1] = (new_active, ever | cond)
            yield idx, ln, new_active
            continue
        if s == ";@else":
            outer = stack[-2][0] if len(stack) >= 2 else base
            ever = stack[-1][1]
            new_active = outer - ever
            stack[-1] = (new_active, ALL_BRANCHES)
            yield idx, ln, new_active
            continue
        if s == ";@endif":
            stack.pop()
            active = stack[-1][0] if stack else base
            yield idx, ln, active
            continue
        active = stack[-1][0] if stack else base
        yield idx, ln, active


def collect_equs(asm_in: Path):
    """Return list of (line_index, name, value, branches) and map
    name → list of (line_index, value, branches)."""
    lines = asm_in.read_text().splitlines()
    equ_list = []
    name_to_decls = defaultdict(list)
    for idx, ln, branches in walk_branch_context(lines):
        m = RE_EQU.match(ln)
        if not m:
            continue
        name, value = m.group(1), m.group(2).strip()
        equ_list.append((idx, name, value, branches))
        name_to_decls[name].append((idx, value, branches))
    return equ_list, name_to_decls


def collect_chunk_refs(stage_dir: Path, names: set[str]) -> dict[str, set[Path]]:
    """For each name in `names`, find chunks that contain a textual
    reference to the symbol."""
    refs: dict[str, set[Path]] = {n: set() for n in names}
    for chunk in sorted(stage_dir.glob("*.inc")):
        text = chunk.read_text()
        # Quick screening: split into "words" and intersect.
        # Use a regex finditer of identifier-like tokens.
        words = set(re.findall(r"\b([A-Z_][A-Z_0-9]+)\b", text))
        for n in names & words:
            refs[n].add(chunk)
    return refs


def localize_stage(asm_in: Path) -> tuple[int, int, int]:
    """Returns (n_eqs_relocated, n_chunks_modified, n_lines_dropped)."""
    # asm_in is `<STAGE>.asm.in`; `.stem` only strips `.in`, leaving
    # `<STAGE>.asm`. Strip both extensions explicitly.
    stage_name = asm_in.name
    if stage_name.endswith(".asm.in"):
        stage_name = stage_name[: -len(".asm.in")]
    stage_lower = stage_name.lower()
    stage_dir = asm_in.parent / stage_lower
    if not stage_dir.is_dir():
        return 0, 0, 0

    equ_list, name_to_decls = collect_equs(asm_in)
    candidate_names = {
        n for n in name_to_decls
        if (n.startswith("CINEMATIC_") or n.startswith("COMMON_VIDEO_"))
        # `_UNUSED_` EQUs are pinned at the top-level intentionally —
        # they document cinematic-bank slots that are present in the
        # resource ROM but never invoked by the game bytecode. They
        # serve as research flags and must stay visible alongside
        # the file's banner.
        and "_UNUSED_" not in n
    }
    if not candidate_names:
        return 0, 0, 0

    refs = collect_chunk_refs(stage_dir, candidate_names)
    # We also need to exclude names referenced by the .asm.in itself
    # outside of EQU declarations. The .asm.in's body (e.g.
    # `video type=1, offset=CINEMATIC_X`) counts as a use.
    asm_in_text = asm_in.read_text()
    asm_in_words = set(re.findall(r"\b([A-Z_][A-Z_0-9]+)\b", asm_in_text))
    # But of course the EQU declarations themselves include the name.
    # Subtract names whose only occurrences are EQU declarations.
    # Simpler heuristic: count occurrences NOT as `^name\s+EQU`.
    asm_in_lines = asm_in_text.splitlines()
    asm_in_body_uses: set[str] = set()
    for ln in asm_in_lines:
        if RE_EQU.match(ln):
            continue
        for w in re.findall(r"\b([A-Z_][A-Z_0-9]+)\b", ln):
            asm_in_body_uses.add(w)

    # Determine chunk include-order from the .asm.in (so we can pick
    # the FIRST referencing chunk as the EQU owner when multiple
    # chunks use it).
    include_order: dict[str, int] = {}
    inc_re = re.compile(
        rf'^\s*;@include\s+"{stage_lower}/([^"]+)"\s*(?:;.*)?$'
    )
    for i, ln in enumerate(asm_in_lines):
        m = inc_re.match(ln)
        if m:
            include_order.setdefault(m.group(1), i)

    relocatable: dict[str, Path] = {}
    for name, chunk_set in refs.items():
        if name in asm_in_body_uses:
            continue  # used directly by .asm.in; can't relocate
        if len(chunk_set) == 0:
            continue
        # Pick the chunk that appears EARLIEST in the .asm.in's
        # include order — that ensures the EQU is in scope for any
        # later chunk that also references it.
        chunks_with_order = [
            (include_order.get(c.name, 10**9), c) for c in chunk_set
        ]
        chunks_with_order.sort()
        relocatable[name] = chunks_with_order[0][1]

    if not relocatable:
        return 0, 0, 0

    # Group by chunk
    by_chunk: dict[Path, list[str]] = defaultdict(list)
    for name, chunk in relocatable.items():
        by_chunk[chunk].append(name)

    # Build the .asm.in modification: drop the EQU lines that are now
    # relocated. An EQU line is dropped if its `name` is in the
    # `relocatable` set.
    drop_indexes: set[int] = set()
    decls_to_relocate: dict[str, list[tuple[int, str, frozenset]]] = defaultdict(list)
    for name in relocatable:
        for line_idx, value, branches in name_to_decls[name]:
            drop_indexes.add(line_idx)
            decls_to_relocate[name].append((line_idx, value, branches))

    # Filter the .asm.in: drop the relocated lines.
    new_asm_in_lines = [
        ln for i, ln in enumerate(asm_in_lines, start=1)
        if i not in drop_indexes
    ]
    asm_in.write_text("\n".join(new_asm_in_lines) +
                      ("\n" if asm_in_text.endswith("\n") else ""))

    n_chunks_modified = 0
    for chunk_path, names in by_chunk.items():
        # Build a header: per-branch-arm group of EQU defines for the
        # names that go into THIS chunk.
        branch_to_lines: dict[frozenset[str], list[str]] = defaultdict(list)
        for name in sorted(names):  # deterministic order
            for _, value, branches in decls_to_relocate[name]:
                branch_to_lines[branches].append(f"{name}\t\tEQU {value}")

        header_chunks: list[str] = []
        for branches in sorted(branch_to_lines.keys(), key=lambda b: sorted(b)):
            equs = branch_to_lines[branches]
            if branches == ALL_BRANCHES:
                header_chunks.extend(equs)
            else:
                br_list = ", ".join(f'"{b}"' for b in sorted(branches))
                if len(branches) == 1:
                    header_chunks.append(f';@if BRANCH == {br_list}')
                else:
                    header_chunks.append(f';@if BRANCH in ({br_list})')
                header_chunks.extend(equs)
                header_chunks.append(';@endif')
        header = "\n".join(header_chunks) + "\n\n"

        chunk_text = chunk_path.read_text()
        chunk_path.write_text(header + chunk_text)
        n_chunks_modified += 1

    return len(relocatable), n_chunks_modified, len(drop_indexes)


def main() -> int:
    total_eqs = 0
    total_chunks = 0
    total_lines = 0
    for asm_in in sorted(LEVELS.glob("_unified/*.asm.in")):
        eqs, chunks_mod, lines = localize_stage(asm_in)
        if eqs:
            print(f"  {asm_in.name}: relocated {eqs} EQUs to "
                  f"{chunks_mod} chunks ({lines} lines moved)")
        total_eqs += eqs
        total_chunks += chunks_mod
        total_lines += lines
    print(f"\nTotal: {total_eqs} EQUs relocated to {total_chunks} chunk files "
          f"({total_lines} EQU lines moved out of .asm.in)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
