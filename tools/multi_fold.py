#!/usr/bin/env python3
"""Multi-fold helper. v2: respects per-routine fold-arm sets.

Given a stage and an ordered list of routine names, this script:
  1. Reads each per-arm .inc file (amiga/cart/dos) for the stage.
  2. For each routine, determines which arms are fold-safe (passed via
     CLI as ROUTINE:arm1,arm2,...).
  3. For arms in the fold-safe set: splits the arm at the routine
     boundary (so the routine is removed from that arm's chunk).
  4. For arms NOT in the fold-safe set: leaves the routine inline in
     the arm's chunk (no split for that routine).
  5. Writes the chunk files.
  6. Prints the unified <STAGE>.asm.in body to stdout.

Usage:
  python3 /tmp/multi_fold.py STAGE \\
    "ROUTINE_A:amiga,cart,dos" \\
    "ROUTINE_B:amiga,dos" \\
    ...

Routines are emitted in given order; must be byte-address-order
within each fold-safe arm.

Existing chunk-file naming: chunks are numbered chunk_0, chunk_1, etc.
For each arm: chunk_K spans from "after the K-th split-point in the
arm" to "before the (K+1)-th split-point in the arm". A split-point
is a routine that the arm contributes to a fold.
"""
import os
import re
import sys
from pathlib import Path

if len(sys.argv) < 3:
    sys.exit(__doc__)

STAGE = sys.argv[1].upper()

# Parse "ROUTINE:arm1,arm2,..." entries
ROUTINES = []  # list of (routine_name, fold_arm_set)
for spec in sys.argv[2:]:
    if ":" not in spec:
        sys.exit(f"FATAL: spec must be ROUTINE:arms, got {spec!r}")
    name, arm_csv = spec.split(":", 1)
    arms = set(arm_csv.split(","))
    if not arms.issubset({"amiga", "cart", "dos"}):
        sys.exit(f"FATAL: invalid arms in {spec!r}")
    ROUTINES.append((name, arms))

AW_SRC = Path(os.environ.get(
    "AW_SRC",
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
))
STAGE_DIR = AW_SRC / "src/levels/_unified" / STAGE.lower()

ARMS = ["amiga", "cart", "dos"]


def find_orig_inc(arm):
    p = STAGE_DIR / f"{arm}.inc"
    if p.is_file():
        return p
    sys.exit(f"FATAL: expected un-split {p}")


def find_routine_lines(text, routine):
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines, start=1):
        if ln.strip() == f"{routine}:":
            start = i
            break
    if start is None:
        return None
    for i, ln in enumerate(lines[start:], start=start + 1):
        if re.match(r'^[A-Za-z_][A-Za-z_0-9]*:$', ln.strip()):
            return (start, i)
    return (start, len(lines) + 1)


def main():
    arm_data = {}
    for arm in ARMS:
        path = find_orig_inc(arm)
        text = path.read_text()
        # Per-arm split points: routines that are fold-safe FOR this arm
        # AND present in this arm's source.
        splits = []  # list of (routine_idx, start_line, end_line)
        for idx, (rname, fold_arms) in enumerate(ROUTINES):
            if arm not in fold_arms:
                continue
            rng = find_routine_lines(text, rname)
            if rng is None:
                sys.exit(f"FATAL: {rname} listed as fold-safe in {arm} but "
                         f"not found in {arm}.inc")
            splits.append((idx, rng[0], rng[1]))
        # Verify ascending order
        prev = 0
        for _, s, _ in splits:
            if s < prev:
                sys.exit(f"FATAL: in {arm}, splits not in ascending line order")
            prev = s
        arm_data[arm] = (path, text, splits)

    # Read each routine body from the FIRST fold-safe arm that has it
    bodies = {}
    for r, fold_arms in ROUTINES:
        for arm in ["amiga", "cart", "dos"]:
            if arm not in fold_arms:
                continue
            text = arm_data[arm][1]
            rng = find_routine_lines(text, r)
            if rng:
                lines = text.splitlines()
                bodies[r] = "\n".join(lines[rng[0] - 1:rng[1] - 1]).rstrip()
                break

    # For each arm, write chunks
    for arm, (path, text, splits) in arm_data.items():
        lines = text.splitlines()
        cursor = 1
        for chunk_idx, (_, start, end) in enumerate(splits):
            chunk_lines = lines[cursor - 1:start - 1]
            out = STAGE_DIR / f"{arm}_chunk_{chunk_idx}.inc"
            out.write_text("\n".join(chunk_lines).rstrip() + "\n")
            print(f"wrote {out.relative_to(AW_SRC)} ({len(chunk_lines)} lines)",
                  file=sys.stderr)
            cursor = end
        # Final chunk
        chunk_idx = len(splits)
        chunk_lines = lines[cursor - 1:]
        out = STAGE_DIR / f"{arm}_chunk_{chunk_idx}.inc"
        out.write_text("\n".join(chunk_lines).rstrip() + "\n")
        print(f"wrote {out.relative_to(AW_SRC)} ({len(chunk_lines)} lines)",
              file=sys.stderr)

    BR = {"amiga": "chahi_amiga_1991",
          "cart": "cartridge_1992",
          "dos": "dos_1992"}

    # Generate the unified body. For each "global slot" (between routines):
    # each arm's chunk index advances when the arm has a split point at
    # the corresponding global routine.
    print(f"; Unified source for {STAGE} with {len(ROUTINES)} folded shared bodies.")
    print(";")
    print("; Folded routines (in byte-address order):")
    for r, fa in ROUTINES:
        print(f";   {r}  ({len(fa)}-arm: {', '.join(sorted(fa))})")
    print()

    arm_chunk_idx = {arm: 0 for arm in ARMS}

    def emit_arm_block(emit_arms_chunks):
        """Emit ;@if/elif including chunk for each arm in arms_chunks dict."""
        prefix = "if"
        emitted_any = False
        for arm in ARMS:
            if arm in emit_arms_chunks:
                ci = emit_arms_chunks[arm]
                print(f';@{prefix} BRANCH == "{BR[arm]}"')
                print(f';@include "{STAGE.lower()}/{arm}_chunk_{ci}.inc"')
                prefix = "elif"
                emitted_any = True
        if emitted_any:
            print(";@endif")

    # Emit pre-first chunk
    emit_arm_block({arm: 0 for arm in ARMS})
    print()

    for slot_idx, (rname, fold_arms) in enumerate(ROUTINES):
        # Emit body
        if len(fold_arms) < 3:
            br_list = ", ".join(f'"{BR[a]}"' for a in sorted(fold_arms))
            print(f";@if BRANCH in ({br_list})")
        print(bodies[rname])
        if len(fold_arms) < 3:
            print(";@endif")
        print()

        # Advance arms: arms that just emitted move to next chunk
        next_arms_chunks = {}
        for arm in ARMS:
            if arm in fold_arms:
                arm_chunk_idx[arm] += 1
                next_arms_chunks[arm] = arm_chunk_idx[arm]
            # arms NOT in fold_arms keep current chunk_idx — no separate
            # emission needed because they stay in the same chunk
        if next_arms_chunks:
            emit_arm_block(next_arms_chunks)
            print()


if __name__ == "__main__":
    main()
