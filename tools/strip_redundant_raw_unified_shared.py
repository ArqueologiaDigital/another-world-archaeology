#!/usr/bin/env python3
"""Strip redundant `;@raw=` annotations from shared unified chunks.

Companion to `strip_redundant_raw_unified_chunks.py`. That tool
operates on per-arm chunks (`<arm>__*.inc`); this one operates on
the shared chunks — chapter chunks like
`<stage>/<stage>_<theme>.inc` and helpers under `_helpers/`.

Shared chunks are included by multiple ports through their parent
`<STAGE>.asm.in`, so a strip is only safe when EVERY consuming
port's preprocess+assemble pipeline still produces the
byte-identical output. The audit per chunk:

  1. For each `<STAGE>.asm.in` that (transitively) includes the
     chunk, identify the set of consuming ports.
  2. Compute baseline bytes for each (asm.in, port) pair.
  3. Strip every `;@raw=` in the chunk; rewrite chunk file in place.
  4. Re-compute bytes for each (asm.in, port) pair. If ALL match
     baseline, the strip stands.
  5. Otherwise restore the chunk and bisect on annotation rank,
     verifying each candidate strip across every consuming port.
  6. Verify before final write; on any failure, restore.

Usage:
  python3 tools/strip_redundant_raw_unified_shared.py [--all]
                                                     [--chunk PATH]
                                                     [--no-bisect]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
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

RE_RAW = re.compile(r"\s*;@raw=([0-9a-fA-FxX,\s]+)\s*$")
RE_INCLUDE = re.compile(r'^\s*;@include\s+"([^"]+)"', re.MULTILINE)
ARM_PREFIX_RE = re.compile(r"^(amiga|dos|cart|gba)__.*\.inc$")

# Maps each port to its flag file. We verify against the lowest-
# overhead representative port per branch (cartridge_1992 is shared
# between genesis_europe and snes_eu so we only verify one).
PORT_FLAGS = {
    "amiga": RELEASES / "amiga.flags",
    "msdos": RELEASES / "msdos.flags",
    "genesis_europe": RELEASES / "genesis_europe.flags",
    "gba_usa": RELEASES / "gba_usa.flags",
}

# `<STAGE>.asm.in` → sequence of consuming ports. From verify_unified.PORTS.
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


def is_shared_chunk(path: Path) -> bool:
    """True if `path` is under `_unified/` AND is NOT a per-arm chunk
    (filename doesn't match `<arm>__*.inc`)."""
    if "_unified" not in path.parts:
        return False
    if path.suffix != ".inc":
        return False
    return not bool(ARM_PREFIX_RE.match(path.name))


def find_consuming_asm_ins(chunk: Path) -> list[Path]:
    """List of `<STAGE>.asm.in` files that transitively `;@include`
    this chunk."""
    out: list[Path] = []
    unified = LEVELS / "_unified"
    for asm_in in unified.glob("*.asm.in"):
        visited: set[Path] = set()

        def walk(p: Path) -> bool:
            if p in visited:
                return False
            visited.add(p)
            try:
                text = p.read_text()
            except OSError:
                return False
            for m in RE_INCLUDE.finditer(text):
                target = (p.parent / m.group(1)).resolve()
                if target == chunk.resolve():
                    return True
                if target.suffix == ".inc" and walk(target):
                    return True
            return False

        if walk(asm_in):
            out.append(asm_in)
    return out


def stage_from_asm_in(p: Path) -> str:
    return p.stem  # `LAKE.asm` from `LAKE.asm.in`? No — Path.stem strips .in
    # Hmm, wait. `LAKE.asm.in`.stem = `LAKE.asm`. Not what we want.


def stage_name_from_asm_in(p: Path) -> str:
    """e.g. LAKE.asm.in → 'LAKE'."""
    name = p.name
    if name.endswith(".asm.in"):
        return name[: -len(".asm.in")]
    return p.stem


def preprocess_and_assemble(
    asm_in: Path, port: str, hint: str
) -> bytes:
    flags = PORT_FLAGS[port]
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


def apply_strip_mask(text: str, ranks: set[int]) -> str:
    out = []
    rank = 0
    for line in text.splitlines(keepends=True):
        if RE_RAW.search(line):
            if rank in ranks:
                m = RE_RAW.search(line)
                stripped = line[: m.start()].rstrip()
                if line.endswith("\n"):
                    stripped += "\n"
                line = stripped
            rank += 1
        out.append(line)
    return "".join(out)


def assemble_for_all_ports(
    consumers: list[tuple[Path, str]],
    hint_prefix: str,
) -> dict[tuple[Path, str], bytes]:
    """Returns {(asm_in, port): bytes}. Raises CalledProcessError on
    any failure."""
    out: dict[tuple[Path, str], bytes] = {}
    for asm_in, port in consumers:
        h = f"{hint_prefix}_{stage_name_from_asm_in(asm_in)}_{port}"
        out[(asm_in, port)] = preprocess_and_assemble(asm_in, port, h)
    return out


def bisect_shared(
    chunk: Path,
    consumers: list[tuple[Path, str]],
    annotation_count: int,
    baselines: dict[tuple[Path, str], bytes],
    original_text: str,
    hint_prefix: str,
) -> set[int]:
    redundant: set[int] = set()

    def recurse(group: list[int]) -> None:
        if not group:
            return
        try_set = set(group) | redundant
        try:
            chunk.write_text(apply_strip_mask(original_text, try_set))
            outs = assemble_for_all_ports(consumers, hint_prefix)
        except subprocess.CalledProcessError:
            if len(group) == 1:
                return
            mid = len(group) // 2
            recurse(group[:mid])
            recurse(group[mid:])
            return
        if outs == baselines:
            redundant.update(group)
            return
        if len(group) == 1:
            return
        mid = len(group) // 2
        recurse(group[:mid])
        recurse(group[mid:])

    recurse(list(range(annotation_count)))
    return redundant


def process_chunk(chunk: Path, allow_bisect: bool) -> tuple[int, int]:
    if not is_shared_chunk(chunk):
        return (0, 0)

    original_text = chunk.read_text()
    annotation_count = sum(
        1 for line in original_text.splitlines() if RE_RAW.search(line)
    )
    if annotation_count == 0:
        return (0, 0)

    asm_ins = find_consuming_asm_ins(chunk)
    if not asm_ins:
        # Orphan chunk — no parent .asm.in includes it.
        # Conservative: leave annotations alone.
        return (annotation_count, annotation_count)

    consumers: list[tuple[Path, str]] = []
    for asm_in in asm_ins:
        stage = stage_name_from_asm_in(asm_in)
        for port in STAGE_PORTS.get(stage, []):
            consumers.append((asm_in, port))

    if not consumers:
        return (annotation_count, annotation_count)

    rel = chunk.relative_to(SRC_TREE)
    print(
        f"  {rel} ({annotation_count} ann, "
        f"{len(consumers)} (.asm.in, port) pairs)…",
        flush=True,
    )

    try:
        baselines = assemble_for_all_ports(consumers, chunk.stem + "_b")
    except subprocess.CalledProcessError as e:
        print(
            f"    baseline assemble failed: {e.stderr[:120]}",
            file=sys.stderr,
        )
        return (annotation_count, annotation_count)

    try:
        chunk.write_text(
            apply_strip_mask(original_text, set(range(annotation_count)))
        )
        stripped = assemble_for_all_ports(consumers, chunk.stem + "_s")
    except subprocess.CalledProcessError:
        stripped = None

    if stripped == baselines:
        print(f"    ALL_REDUNDANT ({annotation_count} stripped)")
        return (annotation_count, 0)

    if not allow_bisect:
        chunk.write_text(original_text)
        print(f"    bytes_differ — restored")
        return (annotation_count, annotation_count)

    chunk.write_text(original_text)
    redundant = bisect_shared(
        chunk,
        consumers,
        annotation_count,
        baselines,
        original_text,
        chunk.stem + "_bi",
    )

    final_text = apply_strip_mask(original_text, redundant)
    chunk.write_text(final_text)
    try:
        verify = assemble_for_all_ports(consumers, chunk.stem + "_v")
    except subprocess.CalledProcessError as e:
        print(
            f"    post-strip assemble failed; restoring. err={e.stderr[:120]}",
            file=sys.stderr,
        )
        chunk.write_text(original_text)
        return (annotation_count, annotation_count)
    if verify != baselines:
        print(f"    post-strip bytes differ; restoring.")
        chunk.write_text(original_text)
        return (annotation_count, annotation_count)

    kept = annotation_count - len(redundant)
    print(f"    stripped {len(redundant)}, kept {kept} load-bearing")
    return (annotation_count, kept)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--chunk", type=Path)
    parser.add_argument("--no-bisect", action="store_true")
    args = parser.parse_args()

    chunks: list[Path] = []
    if args.chunk:
        chunks = [args.chunk]
    elif args.all:
        for p in sorted((LEVELS / "_unified").rglob("*.inc")):
            if is_shared_chunk(p):
                # Only process chunks that have annotations.
                if ";@raw=" in p.read_text():
                    chunks.append(p)
    else:
        parser.error("--all or --chunk required")

    total_before = 0
    total_after = 0
    for chunk in chunks:
        before, after = process_chunk(chunk, allow_bisect=not args.no_bisect)
        total_before += before
        total_after += after

    print(
        f"\ntotal annotations: {total_before} → {total_after} "
        f"(stripped: {total_before - total_after})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
