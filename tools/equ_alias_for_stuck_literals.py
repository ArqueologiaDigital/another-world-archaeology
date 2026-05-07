#!/usr/bin/env python3
"""For each literal-address operand that `resymbolize_literals.py`
left as a literal (because every label resolving to that address
has a name collision that the encoder's last-defined-before-here
rule shadows), define an EQU alias and use it instead.

The EQU bypasses the label-resolution issue entirely:
`<UNIQUE_NAME> EQU 0xNNNN` is a parse-time constant, not a label
address that depends on encoder pass-2 position.

For each stuck literal:
  1. Find a meaningful "hint" — a label at the target address
     in any consumer port's symbol table (even if collision-
     suffering).
  2. Generate a unique EQU name: `<HINT>_AT_<ADDR>` (e.g.,
     `SHARED_RET_AT_533A`).
  3. Add the EQU to a per-stage helpers file
     `_unified/<stage>/<stage>_equ_aliases.inc`.
  4. Replace the literal with the EQU name.

EQUs at the top of an `.asm.in` are global — defined before any
chunk processes, so all references resolve cleanly regardless of
encoder pass position.

Verify byte-match per consumer; restore on failure.

Usage:
  python3 tools/equ_alias_for_stuck_literals.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

from _paths import AWVM_ASM, AW_SRC, REPO_ROOT

SRC_TREE = AW_SRC
LEVELS = SRC_TREE / "src" / "levels"
RELEASES = SRC_TREE / "releases"
AWVM_PREPROCESS = REPO_ROOT / "tools" / "awvm_preprocess.py"

ARM_PREFIX_RE = re.compile(r"^(amiga|dos|cart|gba)__.*\.inc$")
ARM_TO_PORT = {
    "amiga": "amiga",
    "dos": "msdos",
    "cart": "genesis_europe",
    "gba": "gba_usa",
}
STAGE_PORTS: dict[str, list[str]] = {
    "INTRO": ["amiga", "msdos", "genesis_europe", "gba_usa"],
    "LAKE": ["amiga", "msdos", "genesis_europe", "gba_usa"],
    "TANK": ["amiga", "msdos", "genesis_europe"],
    "PASSCODE": ["amiga", "msdos", "genesis_europe"],
    "CODE_WHEEL": ["amiga", "msdos"],
    "CAPSULE": ["amiga", "msdos", "genesis_europe"],
    "CAVES": ["amiga", "msdos", "genesis_europe"],
    "PRISON": ["amiga", "msdos", "genesis_europe"],
    "ENDING": ["amiga", "msdos", "genesis_europe"],
}
RE_INCLUDE = re.compile(r'^\s*;@include\s+"([^"]+)"', re.MULTILINE)

# Same regexes as resymbolize_literals.py
RE_JUMP_LIT = re.compile(
    r"^(?P<lead>\s*)(?P<mn>je|jne|jg|jge|jl|jle)\s+(?P<a>\[?[^,]+\]?),\s*"
    r"(?P<b>\[?[^,]+\]?),\s*(?P<addr>0x[0-9A-Fa-f]{4})\s*$"
)
RE_JMP_LIT = re.compile(
    r"^(?P<lead>\s*)(?P<mn>jmp|call)\s+(?P<addr>0x[0-9A-Fa-f]{4})\s*$"
)
RE_DJNZ_LIT = re.compile(
    r"^(?P<lead>\s*)djnz\s+(?P<a>\[?[^,]+\]?),\s*(?P<addr>0x[0-9A-Fa-f]{4})\s*$"
)
RE_SETUP_LIT = re.compile(
    r"^(?P<lead>\s*)setup\s+channel=(?P<ch>\S+),\s*"
    r"address=(?P<addr>0x[0-9A-Fa-f]{4})\s*$"
)
RE_VIDEO_LIT = re.compile(
    r"^(?P<lead>\s*)video\s+(?P<rest_a>type=[^,]+,\s*offset=)"
    r"(?P<addr>0x[0-9A-Fa-f]{4})(?P<rest_b>(,[^\n]*)?)$"
)


def chunk_to_asmins() -> dict[Path, set[Path]]:
    out: dict[Path, set[Path]] = defaultdict(set)
    for asm_in in (LEVELS / "_unified").glob("*.asm.in"):
        visited: set[Path] = set()
        stack: list[Path] = [asm_in]
        while stack:
            p = stack.pop()
            if p in visited:
                continue
            visited.add(p)
            try:
                text = p.read_text()
            except OSError:
                continue
            for m in RE_INCLUDE.finditer(text):
                target = (p.parent / m.group(1)).resolve()
                if target.suffix == ".inc":
                    out[target].add(asm_in)
                    stack.append(target)
    return out


def find_consumers(chunk: Path, c2a: dict[Path, set[Path]]) -> list[tuple[Path, str]]:
    pairs: list[tuple[Path, str]] = []
    is_per_arm = ARM_PREFIX_RE.match(chunk.name)
    target_port = (
        ARM_TO_PORT[is_per_arm.group(1)] if is_per_arm else None
    )
    for asm_in in c2a.get(chunk.resolve(), set()):
        stage = asm_in.name[: -len(".asm.in")]
        for port in STAGE_PORTS.get(stage, []):
            if target_port and port != target_port:
                continue
            pairs.append((asm_in, port))
    return pairs


def assemble(asm_in: Path, port: str, hint: str) -> tuple[bytes, dict[int, set[str]]]:
    flags = RELEASES / f"{port}.flags"
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        out_asm = td / f"{hint}.asm"
        subprocess.run(
            ["python3", str(AWVM_PREPROCESS), str(asm_in), str(flags), "-o", str(out_asm)],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            [str(AWVM_ASM), out_asm.name],
            cwd=td, check=True, capture_output=True, text=True,
        )
        bin_data = out_asm.with_suffix(".bin").read_bytes()
        sym_path = out_asm.with_suffix(".symbols.txt")
        addr_to_labels: dict[int, set[str]] = defaultdict(set)
        for line in sym_path.read_text().splitlines():
            if not line.strip():
                continue
            addr_str, name = line.split("\t", 1)
            addr_to_labels[int(addr_str, 16)].add(name)
        return bin_data, dict(addr_to_labels)


def find_literals(text: str) -> list[tuple[int, int]]:
    """Return [(line_idx, addr), …] for literal-address operand lines."""
    out = []
    for i, line in enumerate(text.splitlines()):
        for rx in (RE_JUMP_LIT, RE_JMP_LIT, RE_DJNZ_LIT, RE_SETUP_LIT, RE_VIDEO_LIT):
            m = rx.match(line)
            if m:
                out.append((i, int(m.group("addr"), 16)))
                break
    return out


def replace_literal(line: str, new_token: str) -> str | None:
    for rx in (RE_JUMP_LIT, RE_JMP_LIT, RE_DJNZ_LIT, RE_SETUP_LIT, RE_VIDEO_LIT):
        m = rx.match(line)
        if m:
            start, end = m.span("addr")
            return line[:start] + new_token + line[end:]
    return None


def stage_of_chunk(chunk: Path) -> str | None:
    """Return the stage name (lowercase) for a chunk under
    `_unified/<stage>/...`. For chunks under `_unified/_helpers/...`,
    returns the special tag `_helpers` so the tool can route their
    EQUs into a shared cross-stage aliases file."""
    parts = chunk.relative_to(LEVELS / "_unified").parts
    if not parts:
        return None
    if parts[0] == "_helpers":
        return "_helpers"
    if parts[0].startswith("_"):
        return None
    return parts[0]


def stage_aliases_path(stage: str) -> Path:
    if stage == "_helpers":
        return LEVELS / "_unified" / "_helpers" / "_helpers_equ_aliases.inc"
    return LEVELS / "_unified" / stage / f"{stage}_equ_aliases.inc"


def hint_from_address(addr: int, consumer_tables: list[dict[int, set[str]]]) -> str:
    """Pick a label name to use as a hint for the EQU name."""
    for t in consumer_tables:
        names = t.get(addr, set())
        non_label = [n for n in names if not re.fullmatch(r"LABEL_[0-9A-F]+", n)]
        if non_label:
            return sorted(non_label, key=lambda n: (len(n), n))[0]
        if names:
            return sorted(names, key=lambda n: (len(n), n))[0]
    return f"ADDR"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("indexing chunk → asm.in mapping…", flush=True)
    c2a = chunk_to_asmins()

    # Build symbol tables for each (asm.in, port) pair.
    seen_pairs: set[tuple[Path, str]] = set()
    chunks_with_lits: list[Path] = []
    for chunk in (LEVELS / "_unified").rglob("*.inc"):
        try:
            text = chunk.read_text()
        except OSError:
            continue
        if not re.search(r"0x[0-9A-Fa-f]{4}", text):
            continue
        pairs = find_consumers(chunk, c2a)
        if not pairs:
            continue
        chunks_with_lits.append(chunk)
        for p in pairs:
            seen_pairs.add(p)

    print(f"  {len(chunks_with_lits)} chunks with literals; {len(seen_pairs)} pairs", flush=True)

    pair_tables: dict[tuple[Path, str], dict[int, set[str]]] = {}
    pair_baselines: dict[tuple[Path, str], bytes] = {}
    print("baseline assembly…", flush=True)
    for asm_in, port in sorted(seen_pairs):
        try:
            b, t = assemble(asm_in, port, f"{asm_in.stem}_{port}_b")
        except subprocess.CalledProcessError as e:
            print(f"  baseline failed: {asm_in.name}/{port}: {e.stderr[:120]}", file=sys.stderr)
            continue
        pair_tables[(asm_in, port)] = t
        pair_baselines[(asm_in, port)] = b

    # Per-stage: collect stuck literals → set of (addr, hint).
    stage_aliases: dict[str, dict[int, str]] = defaultdict(dict)
    chunk_rewrites: list[tuple[Path, list[tuple[int, str]]]] = []  # (chunk, [(line_idx, new_token), ...])

    aggregate: dict[str, int] = {}

    for chunk in chunks_with_lits:
        stage = stage_of_chunk(chunk)
        if not stage:
            continue
        consumers = find_consumers(chunk, c2a)
        if not consumers:
            continue
        consumer_tables = [pair_tables.get(p, {}) for p in consumers]

        text = chunk.read_text()
        literals = find_literals(text)
        if not literals:
            continue

        rewrites: list[tuple[int, str]] = []
        for line_idx, addr in literals:
            # Skip literals that resymbolize_literals would already
            # handle — we only want STUCK ones.
            from resymbolize_literals import pick_canonical_name as picker
            existing = picker(addr, consumer_tables)
            if existing:
                continue
            # Reserve an EQU name for this address.
            if addr not in stage_aliases[stage]:
                hint = hint_from_address(addr, consumer_tables)
                # Sanitize hint: drop ___MULTIPLE_SUFFIXES, keep first ~30 chars
                hint = re.sub(r"__.*$", "", hint)
                stage_aliases[stage][addr] = f"{hint}_AT_{addr:04X}"
            new_token = stage_aliases[stage][addr]
            rewrites.append((line_idx, new_token))

        if rewrites:
            chunk_rewrites.append((chunk, rewrites))
            aggregate["literals_to_alias"] = aggregate.get("literals_to_alias", 0) + len(rewrites)

    print(f"\nstuck literals to alias: {aggregate.get('literals_to_alias', 0)}")
    for stage, aliases in sorted(stage_aliases.items()):
        print(f"  {stage}: {len(aliases)} unique aliases")

    if args.dry_run:
        return 0

    # Apply: write EQU aliases per stage + rewrite chunks + verify.
    for stage, aliases in sorted(stage_aliases.items()):
        if not aliases:
            continue
        path = stage_aliases_path(stage)
        lines = [
            f"; Auto-generated EQU aliases for stuck literal-address operands.",
            f"; Each name maps a target bytecode address to a stable symbolic",
            f"; identifier so source readers see `je SOMETHING_AT_ADDR` instead",
            f"; of `je 0xADDR`. The hint prefix is taken from any label that",
            f"; resolves to the address (collision-suffering names are accepted",
            f"; here — the EQU bypasses the label collision via parse-time",
            f"; constant resolution).",
            "",
        ]
        for addr in sorted(aliases):
            name = aliases[addr]
            lines.append(f"{name}\tEQU 0x{addr:04X}")
        path.write_text("\n".join(lines) + "\n")
        # Wire the include in. For per-stage aliases, into
        # <STAGE>.asm.in. For `_helpers`, into EVERY stage's
        # `.asm.in` (since any stage can include any helper).
        if stage == "_helpers":
            target_asm_ins = list((LEVELS / "_unified").glob("*.asm.in"))
            include_line = ';@include "_helpers/_helpers_equ_aliases.inc"'
        else:
            target_asm_ins = [LEVELS / "_unified" / f"{stage.upper()}.asm.in"]
            include_line = f';@include "{stage}/{stage}_equ_aliases.inc"'
        for asm_in in target_asm_ins:
            text = asm_in.read_text()
            if include_line in text:
                continue
            common_idx = text.find('_common_vars.inc')
            if common_idx != -1:
                line_end = text.find("\n", common_idx)
                text = (
                    text[: line_end + 1]
                    + include_line
                    + "\n"
                    + text[line_end + 1 :]
                )
            else:
                text = include_line + "\n" + text
            asm_in.write_text(text)

    # Apply chunk rewrites.
    for chunk, rewrites in chunk_rewrites:
        text = chunk.read_text()
        lines = text.splitlines(keepends=True)
        for line_idx, new_token in rewrites:
            line = lines[line_idx]
            had_nl = line.endswith("\n")
            body = line[:-1] if had_nl else line
            new_body = replace_literal(body, new_token)
            if new_body is None:
                continue
            lines[line_idx] = new_body + ("\n" if had_nl else "")
        chunk.write_text("".join(lines))

    # Verify each consumer pair; if anything broke, restore everything.
    failures: list[tuple[Path, str, str]] = []
    for (asm_in, port), expected in pair_baselines.items():
        try:
            actual, _ = assemble(asm_in, port, f"{asm_in.stem}_{port}_v")
        except subprocess.CalledProcessError as e:
            failures.append((asm_in, port, f"assemble error: {e.stderr[:120]}"))
            continue
        if actual != expected:
            failures.append((asm_in, port, "byte mismatch"))

    if failures:
        print(f"\nFAIL: {len(failures)} byte-mismatches; reverting all changes.", file=sys.stderr)
        for asm_in, port, reason in failures[:5]:
            print(f"  {asm_in.name}/{port}: {reason}", file=sys.stderr)
        # Revert via git
        subprocess.run(
            ["git", "checkout", "src/levels/_unified"],
            cwd=SRC_TREE, check=False,
        )
        return 1

    print(f"\nOK — applied {aggregate.get('literals_to_alias', 0)} aliases across "
          f"{len([a for a in stage_aliases.values() if a])} stages.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    sys.exit(main())
