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


def body_symbolic(body_lines):
    """Extract the symbolic-source representation of a routine body.

    Strips comments (anything after `;`), blank lines, and trailing
    whitespace. The resulting string is what would assemble — but
    operands are kept SYMBOLIC (e.g., `CINEMATIC_004`, `LABEL_0000`),
    so two routines with the same bytes but different symbolic
    operand names will compare as DIFFERENT.

    This is the safe fold criterion: routines with identical
    `body_symbolic()` can be merged into a shared top-level body
    without altering the assembled output, regardless of EQU table
    differences between branches.
    """
    out = []
    for ln in body_lines:
        # Strip the `;@raw=...` and any trailing comment, but keep the instruction
        s = re.sub(r';.*$', '', ln).rstrip()
        if not s.strip():
            continue
        out.append(s)
    return "\n".join(out)


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

    # Build per-arm symbolic→(label, byte_count) maps. We key on the
    # SYMBOLIC body (post `;`-strip) because that's what fold-safety
    # requires: identical symbolic source between arms is the criterion
    # that survives EQU-table differences between branches. (Two
    # routines with same bytes but different symbolic operand names
    # would NOT be safe to fold — folding renames the operand to one
    # name and the EQU value would differ between branches.)
    arm_maps = {}
    for arm, routines in arms.items():
        m = {}
        for label, body in routines:
            sym = body_symbolic(body)
            if not sym:
                continue
            bb_len = len(body_bytes(body))
            m.setdefault(sym, []).append((label, bb_len))
        arm_maps[arm] = m

    # Find symbolic-equivalent routines across arms
    all_syms = set()
    for m in arm_maps.values():
        all_syms |= set(m.keys())

    matches = []
    for sym in all_syms:
        present_in = {arm: m[sym] for arm, m in arm_maps.items() if sym in m}
        if len(present_in) >= 2:
            # Use byte count from the first arm (all should agree)
            first_lbl, n_bytes = next(iter(present_in.values()))[0]
            matches.append((sym, n_bytes, present_in))

    # Sort by body length (descending — longest fold first)
    matches.sort(key=lambda x: -x[1])

    print(f"\nFound {len(matches)} cross-arm symbolic-equivalent routine bodies "
          "(safe to fold):")
    print(f"(rows: body_size  arms_present  arm_label / arm_label / ...)")
    total_bytes = 0
    for sym, n_bytes, present_in in matches:
        # Count fold value: bytes × (arms - 1) since each fold reduces
        # by (arms-1) copies (one source-of-truth remains).
        fold_value = n_bytes * (len(present_in) - 1)
        total_bytes += fold_value
        cells = "  /  ".join(
            f"{arm}={','.join(lbl for lbl, _ in lbls)}"
            for arm, lbls in sorted(present_in.items())
        )
        print(f"  {n_bytes:4d}b  {len(present_in)}arms  {cells}")
    print(f"\nTotal foldable bytes: {total_bytes}")


if __name__ == "__main__":
    main()
