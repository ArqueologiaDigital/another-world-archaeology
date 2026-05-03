#!/usr/bin/env python3
"""Find byte-identical routine pairs across the per-branch arms of a stage.

The goal is to surface fold candidates for the cross-arm folding tasks
(#95-101 — fold byte-identical cross-arm routines into shared body).

Usage:
    python3 tools/find_foldable_routines.py <stage>

Where <stage> is e.g. CODE_WHEEL, CAPSULE, CAVES, etc. The tool reads
the per-arm .inc files at:
    <src-tree>/_unified/<stage_lower>/{cart,dos,amiga}.inc

For each .inc file, it parses routine bodies (delimited by `LABEL_<X>:`
or named labels) and extracts the raw assembled bytes via the
`;@raw=...` source annotations. It groups routines by their byte
sequence and reports cross-arm pairs/triples whose bodies are
byte-identical.

Such routines are candidates for folding into a shared top-level body
in <stage>.asm.in, since the bytecode doesn't depend on which arm we
preprocess for — only the byte ADDRESS at which the routine is
emitted differs.

Configuration:
    AW_SRC=/path/to/another-world-source-reconstruction (default
    matches the canonical location used by other tools).
"""
import os
import re
import sys
from pathlib import Path

AW_SRC = Path(os.environ.get("AW_SRC",
              "/home/fsanches/compartilhado/another-world-source-reconstruction"))


def parse_routines(path):
    """Yield (label_name, body_lines) for each routine in the file.

    A routine starts at any line matching `^<NAME>:$` and continues
    until the next such line (or EOF). Body lines exclude the label
    line itself.
    """
    text = Path(path).read_text()
    lines = text.splitlines()
    cur_label = None
    cur_body = []
    for ln in lines:
        m = re.match(r'^([A-Z_][A-Z_0-9]*):$', ln)
        if m:
            if cur_label is not None:
                yield cur_label, cur_body
            cur_label = m.group(1)
            cur_body = []
        elif cur_label is not None:
            cur_body.append(ln)
    if cur_label is not None:
        yield cur_label, cur_body


def body_bytes(body_lines):
    """Extract the concatenated raw bytes from a routine body.

    Pulls bytes from `;@raw=0xXX,0xYY,...` annotations on each
    instruction line. Lines without `;@raw=` (e.g., blank lines,
    pure label refs from `db` macros) contribute nothing.
    """
    out = []
    for ln in body_lines:
        m = re.search(r';@raw=([0-9A-Fa-fxX, ]+)', ln)
        if m:
            for b in m.group(1).split(','):
                b = b.strip()
                if b.startswith(('0x', '0X')):
                    out.append(int(b, 16))
    return bytes(out)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    stage = sys.argv[1].upper()
    stage_dir = AW_SRC / "src/levels/_unified" / stage.lower()
    if not stage_dir.is_dir():
        sys.exit(f"FATAL: no per-arm dir at {stage_dir}")

    arms = {}
    for inc in sorted(stage_dir.glob("*.inc")):
        arm = inc.stem
        arms[arm] = list(parse_routines(inc))
        print(f"{arm}: {len(arms[arm])} labels in {inc.name}")

    # Build per-arm byte→label maps
    arm_maps = {}
    for arm, routines in arms.items():
        m = {}
        for label, body in routines:
            bb = body_bytes(body)
            if len(bb) == 0:
                continue
            m.setdefault(bb, []).append(label)
        arm_maps[arm] = m

    # Find pairs / triples of byte-identical routines across arms
    # Use intersection of byte sets across all arm maps
    all_bytes = set()
    for m in arm_maps.values():
        all_bytes |= set(m.keys())

    matches = []
    for bb in all_bytes:
        present_in = {arm: m[bb] for arm, m in arm_maps.items() if bb in m}
        if len(present_in) >= 2:
            matches.append((bb, present_in))

    # Sort by body length (descending — longest fold first)
    matches.sort(key=lambda x: -len(x[0]))

    print(f"\nFound {len(matches)} cross-arm byte-identical routine bodies:")
    print(f"(rows: body_size  arms_present  arm_label / arm_label / ...)")
    total_bytes = 0
    for bb, present_in in matches:
        n_bytes = len(bb)
        # Count fold value: bytes × (arms - 1) since each fold reduces
        # by (arms-1) copies (one source-of-truth remains).
        fold_value = n_bytes * (len(present_in) - 1)
        total_bytes += fold_value
        cells = "  /  ".join(
            f"{arm}={','.join(lbls)}" for arm, lbls in sorted(present_in.items())
        )
        print(f"  {n_bytes:4d}b  {len(present_in)}arms  {cells}")
    print(f"\nTotal foldable bytes: {total_bytes}")


if __name__ == "__main__":
    main()
