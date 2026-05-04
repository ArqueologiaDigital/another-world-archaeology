#!/usr/bin/env python3
"""Disambiguate intra-chunk duplicate label definitions.

After the per-chunk collision-rename pass (#0087), some chunks
ended up with the SAME renamed label defined multiple times in
the same chunk (e.g., `DEDUP_CAVES_5B_007__PRISON_INLINE_SETTERS_AND_INIT`
appears at 3 different addresses inside
`prison_inline_setters_and_init.inc`). The encoder's last-wins
resolution picks the LAST one, so any literal jump pointing to
the OTHER addresses can't be re-symbolised — there's no
uniquely-named target.

This tool gives each occurrence a counter suffix:
  `LABEL_NAME` → `LABEL_NAME_001`, `LABEL_NAME_002`, ...

Same-chunk references to the original name (which the encoder
resolved to the last def) are updated to the LAST counter
suffix. The byte stream is unchanged.

After this pass, every label inside the chunk has a unique name
mapped to a unique address, and `tools/resymbolize_literals.py`
can find the right counter for each literal target.

Usage:
  python3 tools/disambiguate_intra_chunk_dups.py [--dry-run] [--chunk PATH]
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
RE_LABEL_DEF = re.compile(r"^([A-Z_][A-Z0-9_]*):", re.MULTILINE)


def build_chunk_to_pairs() -> dict[Path, list[tuple[Path, str]]]:
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


def assemble_for_port(asm_in: Path, port: str, hint: str) -> bytes:
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
        return out_asm.with_suffix(".bin").read_bytes()


def find_intra_chunk_dups(text: str) -> dict[str, int]:
    """Return {label_name: count} for labels defined more than
    once in the chunk."""
    counts: dict[str, int] = defaultdict(int)
    for m in RE_LABEL_DEF.finditer(text):
        counts[m.group(1)] += 1
    return {n: c for n, c in counts.items() if c > 1}


def disambiguate(text: str, name: str, count: int) -> str:
    """Replace the K occurrences of `<name>:` with
    `<name>_001:`, `<name>_002:`, …, in source order. Updates
    SAME-CHUNK references to `<name>` (in jump-family operands or
    similar) to use the LAST suffix (which is what the encoder's
    last-wins picked before the rename — preserves byte output).
    """
    last_suffix = f"{name}_{count:03d}"
    out: list[str] = []
    occurrence = 0
    label_def_re = re.compile(rf"^(\s*){re.escape(name)}:(.*)$")
    for line in text.splitlines(keepends=True):
        if line.endswith("\n"):
            body, nl = line[:-1], "\n"
        else:
            body, nl = line, ""
        m = label_def_re.match(body)
        if m:
            occurrence += 1
            new_name = f"{name}_{occurrence:03d}"
            out.append(f"{m.group(1)}{new_name}:{m.group(2)}{nl}")
        else:
            out.append(line)
    new_text = "".join(out)
    # Update same-chunk references: any `\bNAME\b` not followed by ":"
    # → `<name>_<last>`. Use a negative lookahead.
    ref_re = re.compile(rf"\b{re.escape(name)}\b(?!:)")
    new_text = ref_re.sub(last_suffix, new_text)
    return new_text


def process_chunk(
    chunk: Path,
    consumers: list[tuple[Path, str]],
    dry_run: bool,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    text = chunk.read_text()
    dups = find_intra_chunk_dups(text)
    if not dups:
        return counts

    # Skip auto-generated `LABEL_HHHH` placeholders (rename adds
    # noise without semantic gain).
    dups = {n: c for n, c in dups.items() if not re.fullmatch(r"LABEL_[0-9A-F]+", n)}
    if not dups:
        return counts

    try:
        baseline = {
            (a, p): assemble_for_port(a, p, f"{chunk.stem}__{p}_b")
            for a, p in consumers
        }
    except subprocess.CalledProcessError:
        return counts

    cur_text = text
    for name, count in dups.items():
        candidate_text = disambiguate(cur_text, name, count)
        if candidate_text == cur_text:
            continue
        chunk.write_text(candidate_text)
        ok = True
        for a, p in consumers:
            try:
                new_b = assemble_for_port(
                    a, p, f"{chunk.stem}__{p}_v"
                )
            except subprocess.CalledProcessError:
                ok = False
                break
            if new_b != baseline[(a, p)]:
                ok = False
                break
        if ok:
            cur_text = candidate_text
            counts["disambiguated"] = counts.get("disambiguated", 0) + 1
            counts["new_labels"] = counts.get("new_labels", 0) + count
        else:
            chunk.write_text(cur_text)
            counts["restored"] = counts.get("restored", 0) + 1

    if dry_run:
        chunk.write_text(text)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--chunk", type=Path, action="append", default=[]
    )
    args = parser.parse_args()

    print("indexing consumer pairs…", flush=True)
    chunk_to_pairs = build_chunk_to_pairs()

    chunks: list[Path]
    if args.chunk:
        chunks = [Path(p).resolve() for p in args.chunk]
    else:
        chunks = sorted((LEVELS / "_unified").rglob("*.inc"))

    aggregate: dict[str, int] = {}
    files_changed = 0
    for chunk in chunks:
        consumers = chunk_to_pairs.get(chunk.resolve(), [])
        if not consumers:
            continue
        # Quick reject: skip chunks with no intra-chunk duplicate.
        text = chunk.read_text()
        if not find_intra_chunk_dups(text):
            continue
        counts = process_chunk(chunk, consumers, args.dry_run)
        if counts.get("disambiguated"):
            files_changed += 1
            print(
                f"  {chunk.relative_to(SRC_TREE)}: "
                + ", ".join(f"{k}={v}" for k, v in counts.items()),
                flush=True,
            )
        for k, v in counts.items():
            aggregate[k] = aggregate.get(k, 0) + v

    print(f"\nfiles changed: {files_changed}")
    for k, v in sorted(aggregate.items()):
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
