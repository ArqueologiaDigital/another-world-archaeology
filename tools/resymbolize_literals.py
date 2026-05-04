#!/usr/bin/env python3
"""Re-symbolise literal-address operands inserted by
`tools/resolve_raw_collisions.py` back to labelled form.

The collision resolver replaced 366 `;@raw=`-overridden symbols
with literal hex addresses (e.g., `je SHARED_RET ;@raw=…0x53,0x3A`
became `je 0x533A`). That made the source `;@raw=`-free at the cost
of readability. This tool walks the same source, looks up which
label(s) resolve to each literal address (per consuming port's
preprocess+assemble), and rewrites the literal back to a unique
symbol.

How it works per literal:
  1. Find the chunk file containing the literal.
  2. Identify the consuming `(.asm.in, port)` pairs.
  3. For each pair, run preprocess + awvm-asm; harvest the
     `<output>.symbols.txt` sidecar (every label definition with
     its bytecode address).
  4. Find labels defined at the literal's address. The set of
     labels MUST be identical across every consuming port
     (otherwise the chunk can't share a single symbolic name).
  5. Pick a unique name from the set. Preference order:
        (a) a name that's already defined exactly once across
            all consumer ports (no collisions).
        (b) any name (the encoder will hit `last-wins` and pick
            the address-matching one anyway, though this can
            shadow other defs — review the result).
  6. Replace the literal with the chosen name.

Verifies after every rewrite that bytes still match. Restores on
any failure.

Usage:
  python3 tools/resymbolize_literals.py [--dry-run] [--asm-in PATH]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path("/home/fsanches/compartilhado/another-world-archaeology")
SRC_TREE = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
LEVELS = SRC_TREE / "src" / "levels"
RELEASES = SRC_TREE / "releases"
AWVM_ASM = Path(
    "/home/fsanches/compartilhado/AnotherWorld_VMTools/target/release/awvm-asm"
)
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


def build_chunk_to_pairs() -> dict[Path, list[tuple[Path, str]]]:
    """Build a chunk → consumer-pairs map by walking each `.asm.in`'s
    include tree exactly once. Much faster than repeatedly walking
    per chunk."""
    unified = LEVELS / "_unified"
    chunk_to_asmins: dict[Path, set[Path]] = defaultdict(set)

    for asm_in in unified.glob("*.asm.in"):
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
                    chunk_to_asmins[target].add(asm_in)
                    stack.append(target)

    out: dict[Path, list[tuple[Path, str]]] = {}
    for chunk, asm_ins in chunk_to_asmins.items():
        pairs: list[tuple[Path, str]] = []
        is_per_arm = ARM_PREFIX_RE.match(chunk.name)
        target_port = (
            ARM_TO_PORT[is_per_arm.group(1)] if is_per_arm else None
        )
        for asm_in in asm_ins:
            stage = asm_in.name[: -len(".asm.in")]
            for port in STAGE_PORTS.get(stage, []):
                if target_port and port != target_port:
                    continue
                pairs.append((asm_in, port))
        if pairs:
            out[chunk] = pairs
    return out


def assemble_for_port(
    asm_in: Path, port: str, hint: str
) -> tuple[bytes, dict[int, set[str]]]:
    """Return (bytes, address→{labels at that addr}) by running
    awvm-asm and parsing its .symbols.txt sidecar."""
    flags = RELEASES / f"{port}.flags"
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        out_asm = td / f"{hint}.asm"
        subprocess.run(
            [
                "python3",
                str(AWVM_PREPROCESS),
                str(asm_in),
                str(flags),
                "-o",
                str(out_asm),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [str(AWVM_ASM), out_asm.name],
            cwd=td,
            check=True,
            capture_output=True,
            text=True,
        )
        bin_data = out_asm.with_suffix(".bin").read_bytes()
        sym_path = out_asm.with_suffix(".symbols.txt")
        addr_to_labels: dict[int, set[str]] = defaultdict(set)
        for line in sym_path.read_text().splitlines():
            if not line.strip():
                continue
            addr_str, name = line.split("\t", 1)
            addr = int(addr_str, 16)
            addr_to_labels[addr].add(name)
        return bin_data, dict(addr_to_labels)


# Regex patterns for literals to re-symbolise.
# Each entry: (line-detector regex, capture-group of hex literal,
# substitution callable (line, new_name) → new_line).
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


def parse_literal_lines(
    lines: list[str],
) -> list[tuple[int, int, str]]:
    """Return [(line_index, addr, kind), …] for every literal-address
    operand. `kind` ∈ {'target', 'video_offset'}."""
    out = []
    for i, line in enumerate(lines):
        for rx, kind in (
            (RE_JUMP_LIT, "target"),
            (RE_JMP_LIT, "target"),
            (RE_DJNZ_LIT, "target"),
            (RE_SETUP_LIT, "target"),
            (RE_VIDEO_LIT, "video_offset"),
        ):
            m = rx.match(line)
            if m:
                out.append((i, int(m.group("addr"), 16), kind))
                break
    return out


def replace_literal_in_line(
    line: str, new_name: str
) -> str | None:
    for rx in (RE_JUMP_LIT, RE_JMP_LIT, RE_DJNZ_LIT, RE_SETUP_LIT, RE_VIDEO_LIT):
        m = rx.match(line)
        if m:
            start, end = m.span("addr")
            return line[:start] + new_name + line[end:]
    return None


def pick_canonical_name(
    addr: int,
    consumer_tables: list[dict[int, set[str]]],
) -> str | None:
    """Choose a label name that:
       1. Resolves to `addr` (i.e., is defined there) in EVERY
          consumer port.
       2. Has its LAST definition (in source order) at `addr` in
          EVERY consumer port — otherwise the encoder's
          last-wins rule would resolve the name to a different
          address.

    Returns None if no name satisfies both. We can't safely use a
    name whose name-collisions place its last definition at
    another address; encoder would emit the wrong bytes.
    """
    if not consumer_tables:
        return None
    candidate_sets = [t.get(addr, set()) for t in consumer_tables]
    common = set.intersection(*candidate_sets) if candidate_sets else set()
    if not common:
        return None

    def is_unique_in(name: str, table: dict[int, set[str]]) -> bool:
        # Defined at exactly one address (no collisions).
        addrs = [a for a, names in table.items() if name in names]
        return len(addrs) == 1

    unique_names = [
        n
        for n in common
        if all(is_unique_in(n, t) for t in consumer_tables)
    ]
    if not unique_names:
        # No collision-free name available.
        return None

    # Tiebreak: prefer non-LABEL_HHHH names (those are auto-gen
    # placeholders), then shorter, then alphabetic.
    unique_names.sort(key=lambda n: (n.startswith("LABEL_"), len(n), n))
    return unique_names[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--chunk",
        type=Path,
        action="append",
        default=[],
        help="restrict to specific chunk(s)",
    )
    args = parser.parse_args()

    if args.chunk:
        chunks = [Path(p).resolve() for p in args.chunk]
    else:
        chunks = sorted((LEVELS / "_unified").rglob("*.inc"))

    # Pre-build the (asm.in, port) → symbol-table cache ONCE for
    # every consumer pair the chunks touch. Avoids re-running
    # awvm-asm per-chunk; rebuild per-chunk only after a write
    # (to verify byte-match).
    pair_cache: dict[tuple[Path, str], dict[int, set[str]]] = {}
    pair_baseline_bytes: dict[tuple[Path, str], bytes] = {}

    chunk_to_pairs = build_chunk_to_pairs()
    chunks_with_literals: list[tuple[Path, list[tuple[Path, str]]]] = []
    seen_pairs: set[tuple[Path, str]] = set()
    for chunk in chunks:
        try:
            text = chunk.read_text()
        except OSError:
            continue
        if not re.search(r"0x[0-9A-Fa-f]{4}", text):
            continue
        pairs = chunk_to_pairs.get(chunk.resolve(), [])
        if not pairs:
            continue
        chunks_with_literals.append((chunk, pairs))
        for p in pairs:
            seen_pairs.add(p)

    print(
        f"chunks with literal candidates: {len(chunks_with_literals)}; "
        f"unique consumer pairs: {len(seen_pairs)}",
        flush=True,
    )

    # Build baseline tables.
    for asm_in, port in sorted(seen_pairs):
        try:
            b, t = assemble_for_port(asm_in, port, f"{asm_in.stem}_{port}")
        except subprocess.CalledProcessError as e:
            print(
                f"  baseline failed for {asm_in.name}/{port}: "
                f"{e.stderr[:120]}",
                file=sys.stderr,
            )
            continue
        pair_cache[(asm_in, port)] = t
        pair_baseline_bytes[(asm_in, port)] = b

    aggregate: dict[str, int] = {}
    files_changed = 0
    for chunk, pairs in chunks_with_literals:
        text = chunk.read_text()
        lines = text.splitlines(keepends=True)
        candidates = parse_literal_lines(lines)
        if not candidates:
            continue
        consumer_tables = [pair_cache.get(p, {}) for p in pairs]

        new_lines = list(lines)
        per_chunk: dict[str, int] = {}
        for line_idx, addr, _ in candidates:
            name = pick_canonical_name(addr, consumer_tables)
            if not name:
                per_chunk["unsymbolisable"] = (
                    per_chunk.get("unsymbolisable", 0) + 1
                )
                continue
            new_line = replace_literal_in_line(new_lines[line_idx], name)
            if new_line is None:
                per_chunk["replace_failed"] = (
                    per_chunk.get("replace_failed", 0) + 1
                )
                continue
            new_lines[line_idx] = new_line
            per_chunk["resymbolised"] = (
                per_chunk.get("resymbolised", 0) + 1
            )

        for k, v in per_chunk.items():
            aggregate[k] = aggregate.get(k, 0) + v

        if not per_chunk.get("resymbolised") or args.dry_run:
            continue

        # Write & verify. On any byte mismatch, restore.
        new_text = "".join(new_lines)
        chunk.write_text(new_text)
        ok = True
        for asm_in, port in pairs:
            try:
                new_b, _ = assemble_for_port(
                    asm_in, port, f"{chunk.stem}__{port}_v"
                )
            except subprocess.CalledProcessError as e:
                print(
                    f"  {chunk.relative_to(SRC_TREE)}: post-rewrite "
                    f"assemble failed for ({asm_in.name}, {port}); "
                    f"err={e.stderr[:120]}",
                    file=sys.stderr,
                )
                ok = False
                break
            if new_b != pair_baseline_bytes.get((asm_in, port)):
                print(
                    f"  {chunk.relative_to(SRC_TREE)}: post-rewrite "
                    f"bytes differ for ({asm_in.name}, {port}).",
                    file=sys.stderr,
                )
                ok = False
                break
        if not ok:
            chunk.write_text(text)
            aggregate["resymbolised"] = (
                aggregate.get("resymbolised", 0)
                - per_chunk["resymbolised"]
            )
            aggregate["restored"] = aggregate.get("restored", 0) + 1
            continue

        files_changed += 1
        print(
            f"  {chunk.relative_to(SRC_TREE)}: "
            + ", ".join(f"{k}={v}" for k, v in per_chunk.items()),
            flush=True,
        )

    print(f"\nfiles changed: {files_changed}")
    for k, v in sorted(aggregate.items()):
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
