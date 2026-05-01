#!/usr/bin/env python3
"""Generate a unified .asm.in source from two divergent per-branch .asm files.

Uses difflib.SequenceMatcher to find matching/divergent line blocks
between two .asm files. Emits a unified file where:
- matching blocks appear once verbatim
- divergent blocks are wrapped in `;@if BRANCH == "<branch_a>"` /
  `;@elif BRANCH == "<branch_b>"` / `;@endif`

The output passes through `tools/awvm_preprocess.py` to recover
either branch's original source, then `awvm-asm` to produce the
byte-matching bytecode.

Usage:
    python3 tools/unify_asm.py \\
        --a src/levels/heineman_cartridge/INTRO.asm --branch-a heineman_cartridge \\
        --b src/levels/foxy_gba_2004/INTRO.asm --branch-b foxy_gba_2004 \\
        -o src/levels/_unified/INTRO.asm.in
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path


RE_RAW_COMMENT = re.compile(r'\s*;@raw=[0-9A-Fa-fx,]+\s*$')


def normalize_for_diff(line: str) -> str:
    """Strip non-semantic content for diff purposes.

    The `;@raw=...` annotation tells the disassembler what bytes the
    instruction encoded; the assembler IGNORES it (it computes the
    bytes from the instruction itself). Two lines that differ only in
    `;@raw=` will assemble to the same bytes for the same target. So
    we treat them as equal during unification.

    We don't strip other comment styles (e.g., `; "string"` annotations
    inside text opcodes) because those frequently differ between
    branches' string tables and we want to preserve them per-branch.
    """
    return RE_RAW_COMMENT.sub('', line)


def unify(a_lines: list[str], b_lines: list[str],
          branch_a: str, branch_b: str,
          strip_raw_comments: bool = False) -> tuple[list[str], dict]:
    """Return (output_lines, stats).

    If `strip_raw_comments` is True, normalize each line by stripping
    `;@raw=...` annotations before diffing. Output uses the canonical
    (post-normalization) form, so the unified file has no `;@raw=`
    annotations — those are pure disassembler-output documentation
    that wouldn't be byte-correct for both branches anyway.
    """
    if strip_raw_comments:
        a_for_diff = [normalize_for_diff(l) for l in a_lines]
        b_for_diff = [normalize_for_diff(l) for l in b_lines]
        emit_a = a_for_diff
        emit_b = b_for_diff
    else:
        a_for_diff = a_lines
        b_for_diff = b_lines
        emit_a = a_lines
        emit_b = b_lines

    sm = difflib.SequenceMatcher(None, a_for_diff, b_for_diff, autojunk=False)
    out = []
    stats = {
        "equal_lines": 0,
        "a_only_lines": 0,
        "b_only_lines": 0,
        "diff_blocks": 0,
    }
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            out.extend(emit_a[i1:i2])
            stats["equal_lines"] += i2 - i1
        else:
            stats["diff_blocks"] += 1
            stats["a_only_lines"] += i2 - i1
            stats["b_only_lines"] += j2 - j1
            out.append(f';@if BRANCH == "{branch_a}"')
            out.extend(emit_a[i1:i2])
            out.append(f';@elif BRANCH == "{branch_b}"')
            out.extend(emit_b[j1:j2])
            out.append(";@endif")
    return out, stats


def unify_n(sources: list[tuple[str, list[str]]]) -> tuple[list[str], dict]:
    """N-way unification by progressive 2-way merging.

    sources: list of (branch_name, lines) tuples.
    Folds left: merge sources[0] with sources[1] → result; then result
    with sources[2]; etc. Each round produces a unified file with
    nested ;@if blocks where input differs.

    The 2-way unify treats the LEFT input as if it were a single branch
    (preserving any existing ;@if directives inside it as opaque content).
    For clean output, we sort the input lines so directives stay grouped.
    """
    if not sources:
        raise ValueError("need at least one source")
    if len(sources) == 1:
        return list(sources[0][1]), {"equal_lines": len(sources[0][1]),
                                       "diff_blocks": 0}

    # Start with first source; progressively merge others.
    branch_a, current = sources[0]
    total_blocks = 0
    for branch_b, b_lines in sources[1:]:
        merged, st = unify(current, b_lines, branch_a, branch_b)
        total_blocks += st["diff_blocks"]
        current = merged
        # Subsequent merges: left side is the unified output, treated as
        # a single "<combined>" branch. Re-running unify on it would
        # generate `;@if BRANCH == "<combined>"` which is wrong.
        # So flatten left-side `;@if BRANCH == "branch_a"` blocks back to
        # bare lines for that branch only — which means: drop other branches'
        # blocks. That's not quite right either.
        # Pragmatic fix: keep as-is and trust difflib to align across
        # subsequent merges. The directives become part of the diff's
        # "equal lines" (they appear in current but not in next b_lines),
        # so they get wrapped under `;@if BRANCH == branch_a_combined`.
        # For 3-way, the cleanest approach is below.
        branch_a = f"<merged>"  # placeholder; not used for 3-way

    return current, {"diff_blocks": total_blocks}


def unify_three(a: list[str], b: list[str], c: list[str],
                ba: str, bb: str, bc: str) -> tuple[list[str], dict]:
    """Three-way unification using difflib's pairwise opcodes.

    Strategy: do an A-vs-B diff; for divergent blocks, also check C's
    contribution by comparing C's matching range to A's and B's.
    Since difflib doesn't natively do 3-way, we approximate:
      1. Merge A and B into AB
      2. Re-merge AB with C, treating AB's `;@if` blocks as opaque
    """
    ab, _ = unify(a, b, ba, bb)
    # Now merge AB with C. Lines in AB that are EQUAL across A and B
    # (no ;@if wrapper) compare directly to C; differing AB lines get
    # nested ;@if treatment.
    abc, stats = unify(ab, c, "<ab>", bc)
    # Replace `<ab>` in the output with the actual `BRANCH in ("ba", "bb")`
    out = []
    for line in abc:
        out.append(line.replace(
            ';@if BRANCH == "<ab>"',
            f';@if BRANCH in ("{ba}", "{bb}")'
        ))
    return out, stats


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--source", "-s", action="append", default=[],
                   metavar="BRANCH=PATH",
                   help="source spec; repeat for N-way unify (BRANCH=path/to.asm)")
    # Backward-compat
    p.add_argument("--a", type=Path, help="first .asm (legacy 2-way mode)")
    p.add_argument("--b", type=Path, help="second .asm (legacy 2-way mode)")
    p.add_argument("--branch-a", help="branch name for first .asm")
    p.add_argument("--branch-b", help="branch name for second .asm")
    p.add_argument("-o", "--output", type=Path, required=True,
                   help="output .asm.in path")
    p.add_argument("--strip-raw-comments", action="store_true",
                   help="strip ;@raw= annotations during diff. The unified "
                        "output is cleaner (no per-branch byte annotations) "
                        "and produces fewer ;@if blocks.")
    args = p.parse_args()

    sources: list[tuple[str, list[str]]] = []
    if args.source:
        for spec in args.source:
            if "=" not in spec:
                sys.exit(f"bad --source spec (need BRANCH=path): {spec!r}")
            br, _, path_str = spec.partition("=")
            sources.append((br, Path(path_str).read_text().splitlines()))
    elif args.a and args.b:
        sources.append((args.branch_a, args.a.read_text().splitlines()))
        sources.append((args.branch_b, args.b.read_text().splitlines()))
    else:
        sys.exit("specify --source BRANCH=path repeated, OR --a + --b + --branch-a + --branch-b")

    if len(sources) == 2:
        out_lines, stats = unify(
            sources[0][1], sources[1][1],
            sources[0][0], sources[1][0],
            strip_raw_comments=args.strip_raw_comments,
        )
    else:
        # 3-way+ unification by progressive folding has subtle issues:
        # the directives emitted by the first merge become "lines" that
        # the second merge tries to align, producing wrong wrapping.
        # A correct N-way unifier needs a synchronised matcher across
        # all N inputs simultaneously (or post-processing of the
        # progressive output to clean up directive nesting). Deferred
        # for future work.
        sys.exit(f"only 2-way unification supported (got {len(sources)} "
                 "sources). N-way needs a synchronised matcher.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(out_lines) + "\n")

    print(f"sources: {len(sources)}")
    for br, lines in sources:
        print(f"  {br}: {len(lines)} lines")
    print(f"\nstats: diff_blocks={stats['diff_blocks']}")
    print(f"\nwrote {args.output}: {len(out_lines)} lines")
    largest_input = max(len(s[1]) for s in sources)
    overhead = len(out_lines) - largest_input
    print(f"  overhead vs largest source: {overhead} lines "
          f"({100 * overhead / len(out_lines):.1f}%)")


if __name__ == "__main__":
    main()
