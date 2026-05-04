#!/usr/bin/env python3
"""Per-chunk rename of collision-suffering label definitions.

For each chunk that defines a label name L which is ALSO defined
in other chunks (a collision), rename this chunk's `L:` to a
unique scope-specific name based on the chunk's path, AND update
every reference to `L` WITHIN THE SAME CHUNK to use the new name.

References from OTHER chunks to `L` are not touched (they continue
to resolve via whatever non-renamed definition remains in scope).

Verification: assemble each consumer (asm.in, port) before and
after the rename. If bytes don't match, restore the chunk.

Goal: unblock the 386 literal-address sites #0087 by making each
collision-suffering definition uniquely accessible by name. After
this pass, `tools/resymbolize_literals.py` can re-symbolise more
literals.

Usage:
  python3 tools/rename_collision_labels.py [--dry-run] [--chunk PATH]
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


def all_label_defs() -> dict[str, list[Path]]:
    """name → list of chunk files defining this label."""
    out: dict[str, list[Path]] = defaultdict(list)
    for path in (LEVELS / "_unified").rglob("*.inc"):
        try:
            text = path.read_text()
        except OSError:
            continue
        for m in RE_LABEL_DEF.finditer(text):
            out[m.group(1)].append(path)
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


def chunk_descriptor(chunk: Path) -> str:
    """Generate a short scope tag from chunk path.

    e.g., src/levels/_unified/prison/prison_inline_setters_and_init.inc
       → 'PRISON_INLINE_SETTERS_AND_INIT'
    """
    stem = chunk.stem
    parent = chunk.parent.name
    if parent == "_helpers":
        return f"HELPER_{stem}".upper()
    return stem.upper()


def rename_in_chunk(
    text: str, old_name: str, new_name: str
) -> str:
    """Rename `old_name` → `new_name` everywhere in `text`. Uses
    word-boundary matching to avoid touching substring matches."""
    pattern = re.compile(rf"\b{re.escape(old_name)}\b")
    return pattern.sub(new_name, text)


def process_chunk(
    chunk: Path,
    label_to_chunks: dict[str, list[Path]],
    consumers: list[tuple[Path, str]],
    dry_run: bool,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    text = chunk.read_text()

    # Find all label definitions in this chunk; identify
    # collision-suffering ones (defined in >1 chunk).
    defs_here = [
        m.group(1)
        for m in RE_LABEL_DEF.finditer(text)
    ]
    collisions = [
        n
        for n in defs_here
        if len(label_to_chunks.get(n, [])) > 1
    ]
    if not collisions:
        return counts

    # Skip names that look auto-generated (LABEL_HHHH) — those are
    # placeholders the disasm assigned without semantic meaning;
    # the rename approach still works but it's not a readability
    # win, just adds noise.
    collisions = [
        n for n in collisions if not re.fullmatch(r"LABEL_[0-9A-F]+", n)
    ]
    if not collisions:
        return counts

    # Compute baseline bytes per consumer.
    baseline_bytes: dict[tuple[Path, str], bytes] = {}
    try:
        for asm_in, port in consumers:
            baseline_bytes[(asm_in, port)] = assemble_for_port(
                asm_in, port, f"{chunk.stem}__{port}_b"
            )
    except subprocess.CalledProcessError:
        return counts

    # Rename each collision label INDEPENDENTLY — try one at a
    # time, verify, keep on success. This way one bad rename
    # doesn't poison the whole chunk.
    cur_text = text
    chunk_tag = chunk_descriptor(chunk)
    for original in collisions:
        new_name = f"{original}__{chunk_tag}"
        # Avoid double-renaming if a previous run already applied
        # this name (idempotence).
        if new_name in cur_text:
            continue
        candidate_text = rename_in_chunk(cur_text, original, new_name)
        if candidate_text == cur_text:
            continue
        chunk.write_text(candidate_text)
        ok = True
        for asm_in, port in consumers:
            try:
                new_b = assemble_for_port(
                    asm_in, port, f"{chunk.stem}__{port}_v"
                )
            except subprocess.CalledProcessError:
                ok = False
                break
            if new_b != baseline_bytes[(asm_in, port)]:
                ok = False
                break
        if ok:
            cur_text = candidate_text
            counts["renamed"] = counts.get("renamed", 0) + 1
        else:
            counts["restored"] = counts.get("restored", 0) + 1
            chunk.write_text(cur_text)

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

    print("indexing label definitions…", flush=True)
    label_to_chunks = all_label_defs()
    collision_count = sum(
        1 for n, c in label_to_chunks.items() if len(c) > 1
    )
    print(f"  collision-suffering labels: {collision_count}", flush=True)

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
        counts = process_chunk(
            chunk, label_to_chunks, consumers, args.dry_run
        )
        if counts.get("renamed"):
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
