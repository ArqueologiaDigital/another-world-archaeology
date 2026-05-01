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
RE_INLINE_COMMENT = re.compile(r';(?!@raw=)[^\t\n]*')
RE_LINE_MNEMONIC = re.compile(r'^\s*([a-zA-Z][a-zA-Z]*)\b')

# Recognised AW VM assembly instructions/directives. Used to
# distinguish real-code lines from incidental string-continuation
# lines (which the disasm produces for multi-line `text id=... ; "…"`
# annotations whose string content contains a `\n`).
KNOWN_MNEMONICS = frozenset({
    "mov", "add", "sub", "and", "or", "shl", "shr",
    "call", "ret", "break", "jmp", "setup", "djnz",
    "je", "jne", "jl", "jle", "jg", "jge",
    "setPalette", "freezeChannels", "unfreezeChannels", "deleteChannels",
    "selectVideoPage", "fill", "copyVideoPage", "blitFramebuffer",
    "killChannel", "text", "play", "load", "song", "video",
    "bankSwitch",
    "db", "dw", "FILL", "EQU", "org",
})

RE_LABEL_DEF = re.compile(r'^[A-Z][A-Z_0-9]*:\s*$')
RE_EQU_LINE = re.compile(r'^[A-Z][A-Z_0-9]*\s+EQU\s+0x[0-9A-Fa-f]+\s*$')


def is_real_code_line(line: str) -> bool:
    """Heuristic: does `line` look like real assembly code, vs.
    decorative content (blank, pure comment, or a string-continuation
    line emitted by the disasm for a multi-line `text` comment)?

    Returns True if the line starts with a recognised mnemonic /
    directive, OR is a label definition, OR is an EQU constant
    definition. Returns False otherwise (blank, `;` comment, string
    continuation, etc.).
    """
    s = line.strip()
    if not s:
        return False
    if s.startswith(";"):  # comment
        return False
    if RE_LABEL_DEF.match(line):
        return True
    # `NAME EQU 0x...` lines define assembler constants. They start
    # with the constant name (NOT a mnemonic) so the leading-token
    # check below misclassifies them as decorative; recognise them
    # explicitly here. Without this, blocks containing only divergent
    # EQU lines get classified as `is_cosmetic_continuation` and
    # silently dropped instead of being wrapped in `;@if`/`;@elif`.
    if RE_EQU_LINE.match(s):
        return True
    m = RE_LINE_MNEMONIC.match(line)
    if not m:
        return False
    return m.group(1) in KNOWN_MNEMONICS
# A "pure-comment" line is whitespace + `;` followed by anything (and
# crucially NOT `;@<directive>` like ;@if/;@elif/;@else/;@endif which
# the preprocessor handles separately, NOR `;@raw=...` annotations).
# These lines are author-written prose explaining the surrounding code
# and must survive the diff/strip pass intact.
RE_PURE_COMMENT_LINE = re.compile(r'^\s*;(?!@)')

# Mnemonics whose lines mis-encode without a `;@raw=` annotation.
# Discovered empirically (per-mnemonic survey): see #0066.
# Note: `bankSwitch` is also buggy, but we run a pre-canonicalization
# step that converts `bankSwitch N` → `load id=...` (which encodes
# correctly without any override). So we don't need it here anymore.
#
# `setPalette` always needs `;@raw=` (the encoder mis-handles a
# "waste byte" — see issue #0066).
#
# `video` is more nuanced: only the **alt-form** (bit-6-set opcodes
# 0x40-0x7F, parsed when the source line includes `zoom=…`) needs
# `;@raw=`. The disasm output for those is lossy: bits 3-2 (y
# encoding mode) and bits 1-0 (zoom encoding mode) each have two
# distinct opcode-byte patterns that decode to identical text, but
# the asm encoder only ever emits ONE of the two. The
# **compact-form** video opcodes (bit-7-set 0x80-0xFF, no `zoom=`
# keyword in the disasm output) round-trip cleanly through the
# encoder. So we only require `;@raw=` for alt-form video.
RAW_REQUIRED_MNEMONICS = frozenset({"setPalette", "video"})


RE_RAW_FIRST_BYTE = re.compile(r';@raw=0x([0-9A-Fa-f]{1,2})')
RE_RAW_BYTES = re.compile(r';@raw=((?:0x[0-9A-Fa-f]+,?)+)')


def line_requires_raw(line: str, mnemonic: str) -> bool:
    """Decide whether `line` needs to keep its `;@raw=…` annotation
    for byte-level round-trip through awvm-asm.

    For most "raw-required" mnemonics, the encoder mis-handles
    SOME inputs but is correct for the canonical case. We inspect
    the existing `;@raw=` bytes and only keep the annotation when
    the encoder would actually produce different output. This
    minimises the visual noise of `;@raw=` in the unified source
    while preserving byte-level round-trip.

    Per-mnemonic rules:

    - `setPalette N` encodes as `0x0B, N, 0xFF` (the 3rd byte is a
      "waste byte" that the disasm discards). The encoder always
      emits `0xFF` for that byte. If the original raw bytes have a
      non-0xFF waste byte, the line needs `;@raw=`; otherwise the
      encoder reproduces them correctly.

    - `video` has two forms:
      * Compact (opcode 0x80-0xFF, bit 7 set, no `zoom=` in the
        disasm output) — encoder is fully bijective; strip safely.
      * Alt-form (opcode 0x40-0x7F, bit 6 set, with `zoom=`):
        bits 5-4 (x), 3-2 (y), 1-0 (zoom) each encode 4 states. The
        encoder uses 3 of the 4 states for y and 2 of the 4 for
        zoom. Disasm decoding is many-to-one for those, so non-
        canonical opcode bits need `;@raw=`.

    Anything else in `RAW_REQUIRED_MNEMONICS` that we haven't
    inspected returns True conservatively.
    """
    if mnemonic not in RAW_REQUIRED_MNEMONICS:
        return False
    if mnemonic == "setPalette":
        m = RE_RAW_BYTES.search(line)
        if not m:
            return False
        bs = [int(b, 0) for b in m.group(1).split(',') if b.strip()]
        # 3 bytes: 0x0B, palette, waste. Encoder produces waste=0xFF.
        if len(bs) == 3 and bs[2] == 0xFF:
            return False
        return True
    if mnemonic == "video":
        if " zoom=" not in line:
            return False
        m = RE_RAW_FIRST_BYTE.search(line)
        if not m:
            return False
        op = int(m.group(1), 16)
        non_canonical_y = (op & 0x08) and (op & 0x04)
        non_canonical_zoom = bool(op & 0x02)
        return bool(non_canonical_y or non_canonical_zoom)
    return True


def normalize_for_diff(line: str, strip_raw: bool = True) -> str:
    """Strip non-semantic content for diff purposes.

    Strips two kinds of comments:
    - **Inline `;<text>`** comments BEFORE `;@raw=` (e.g.,
      `bankSwitch 1; Prison ;@raw=...` → strip `; Prison`). These are
      port-specific stage names / string-table contents that differ
      cosmetically between branches without affecting assembled bytes.
    - **`;@raw=...`** annotations on lines OUTSIDE
      `RAW_REQUIRED_MNEMONICS` — the assembler computes correct
      bytes for those mnemonics from the instruction alone, so the
      `;@raw=` is redundant.

    Both kinds of stripping are safe: the assembled bytes don't change
    when these comments are absent (verified empirically per #0066).
    """
    if not strip_raw:
        return line
    # Pure-comment lines (whitespace + `;` + prose) are author-written
    # documentation and must pass through unchanged. They participate
    # in the diff like any other line — when both branches have the
    # same comment at the same position, it appears in the unified
    # output. This is how cross-branch annotations get committed to
    # the unified source.
    if RE_PURE_COMMENT_LINE.match(line):
        return line
    # First strip inline ;<comment> (not ;@raw=). The negative-
    # lookahead in RE_INLINE_COMMENT ensures we don't strip ;@raw=.
    line = RE_INLINE_COMMENT.sub('', line).rstrip()
    # Now decide if we keep ;@raw=.
    m = RE_LINE_MNEMONIC.match(line)
    if m and line_requires_raw(line, m.group(1)):
        return line
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
        a_for_diff = [normalize_for_diff(l, strip_raw=True) for l in a_lines]
        b_for_diff = [normalize_for_diff(l, strip_raw=True) for l in b_lines]
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
            a_block = emit_a[i1:i2]
            b_block = emit_b[j1:j2]
            # Drop diffs that are blank/comment-only on BOTH sides:
            # cosmetic-only divergence (e.g., one branch has an extra
            # blank line that the other doesn't). Blank lines don't
            # assemble to bytes, so we can keep ANY whitespace from
            # either side without affecting byte-match.
            def is_blank_only(block: list[str]) -> bool:
                return all(not l.strip() for l in block)
            # Cosmetic continuation: lines that are JUST string
            # content for a multi-line `text id=... ; "long
            # multi-line string"` annotation. The disasm splits such
            # strings across multiple physical lines; the
            # continuation lines have no `;@raw=` (the raw bytes are
            # on the line above), no mnemonic, and end with a closing
            # quote. They're commentary, not code, so they're safe to
            # emit unconditionally — both branches' bytecode is
            # identical for the same `text id=...`, only the rendered
            # comment differs (different translations / port-specific
            # string-table content).
            def is_cosmetic_continuation(block: list[str]) -> bool:
                """True if `block` contains only decorative lines
                (blank, `;` comment, or string-continuation lines like
                `   PRESS START FOR CODE ENTRY"` that come from a
                multi-line `text id=... ; "..."` whose string body has
                an embedded `\\n`).

                A "decorative" line has no `;@raw=` byte annotation
                AND isn't recognised as real code (no mnemonic, no
                directive, no label definition). The disasm emits
                such lines as continuation of the previous line's
                inline comment; awvm-asm tolerates them as no-ops, so
                they're safe to share across branches even when the
                rendered string differs port-to-port.
                """
                if not block:
                    return False
                saw_continuation = False
                for l in block:
                    if not l.strip():
                        continue
                    if l.lstrip().startswith(";"):
                        continue
                    # Real code → not cosmetic.
                    if is_real_code_line(l):
                        return False
                    # Has a `;@raw=` annotation → carries instruction
                    # bytes → not cosmetic.
                    if ";@raw=" in l:
                        return False
                    saw_continuation = True
                return saw_continuation
            a_blank = is_blank_only(a_block)
            b_blank = is_blank_only(b_block)
            a_cosmetic = a_blank or is_cosmetic_continuation(a_block)
            b_cosmetic = b_blank or is_cosmetic_continuation(b_block)
            if a_cosmetic and b_cosmetic:
                # Both sides are decorative (blank lines, comments, or
                # multi-line text-comment continuations). Emit the
                # longer side as shared content, no `;@if`. Doesn't
                # affect byte-match either way.
                out.extend(a_block if len(a_block) >= len(b_block) else b_block)
                continue
            # Collapse one-sided diffs: if one branch contributes no
            # lines (insert/delete from difflib's perspective), emit
            # a single `;@if BRANCH == "<other>"` block instead of an
            # `;@if`/`;@elif` pair with one side empty. The empty side
            # would just be deadweight noise in the unified source.
            if not a_block and b_block:
                # If the b-only content is purely decorative, just
                # emit the lines as shared (no `;@if` needed).
                if b_cosmetic:
                    out.extend(b_block)
                else:
                    out.append(f';@if BRANCH == "{branch_b}"')
                    out.extend(b_block)
                    out.append(";@endif")
            elif a_block and not b_block:
                if a_cosmetic:
                    out.extend(a_block)
                else:
                    out.append(f';@if BRANCH == "{branch_a}"')
                    out.extend(a_block)
                    out.append(";@endif")
            else:
                # Both sides have content. If one side is purely
                # decorative continuation (e.g., cart has a multi-line
                # string-comment that gba doesn't), the bytes are the
                # same — emit the longer-decorative side as shared
                # before/after the meaningful content. For now, just
                # emit both as a `;@if`/`;@elif` block.
                out.append(f';@if BRANCH == "{branch_a}"')
                out.extend(a_block)
                out.append(f';@elif BRANCH == "{branch_b}"')
                out.extend(b_block)
                out.append(";@endif")
    return out, stats


def _collapse_directive_blocks(
    lines: list[str],
) -> tuple[list[str], list[list[str]]]:
    """Collapse each `;@if/.../;@endif` block into a single
    `__AB_BLOCK_<n>__` placeholder line.

    Returns (collapsed_lines, blocks) where `blocks[n]` is the
    original list of lines for placeholder n (including the
    surrounding `;@if` and `;@endif`).

    Used to make difflib's pairwise diff treat each preprocessor
    block as an atomic token — necessary when folding a previously-
    unified A+B output into an A+B+C merge. Without this, difflib
    can split an `;@if/.../;@endif` block across `equal` and
    `replace` opcodes, producing malformed nested output.

    Nested `;@if`s are tracked: a placeholder spans from the
    OUTER `;@if` to its matching outer `;@endif`.
    """
    out: list[str] = []
    blocks: list[list[str]] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.lstrip()
        if stripped.startswith(";@if "):
            # Find matching `;@endif` (track nesting depth).
            depth = 1
            j = i + 1
            while j < n:
                s = lines[j].lstrip()
                if s.startswith(";@if "):
                    depth += 1
                elif s.startswith(";@endif"):
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if j >= n:
                # Unterminated block — emit as-is, let preprocessor
                # complain. (Should never happen for well-formed
                # input from `unify()`.)
                out.append(line)
                i += 1
                continue
            block_lines = lines[i:j + 1]
            placeholder = f"__AB_BLOCK_{len(blocks)}__"
            blocks.append(block_lines)
            out.append(placeholder)
            i = j + 1
            continue
        out.append(line)
        i += 1
    return out, blocks


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
    elif len(sources) == 3:
        # 3-way unification via progressive folding (A+B → AB, then
        # AB+C → ABC). Naive folding has a fatal nesting bug: the
        # AB step emits `;@if/.../;@endif` blocks for cart↔gba
        # divergence, then difflib in step 2 treats those directives
        # as ordinary lines and freely splits an `;@if/.../;@endif`
        # block across "equal" and "replace" opcodes. The result is
        # unbalanced nesting (e.g., outer `;@if` opened in one diff
        # block, closed in a later one).
        #
        # Fix: collapse each `;@if/.../;@endif` block in AB into a
        # single placeholder line BEFORE the second diff. Difflib
        # then sees one atomic token per AB-divergent region. After
        # difflib produces opcodes, expand the placeholders back to
        # the original block contents in the output. This guarantees
        # that an AB block is either kept whole (in an `equal`
        # opcode) or wrapped whole (in a `replace` opcode) — never
        # split across opcodes.
        a, b, c = sources
        ab_lines, ab_stats = unify(
            a[1], b[1], a[0], b[0],
            strip_raw_comments=args.strip_raw_comments,
        )
        ab_collapsed, ab_blocks = _collapse_directive_blocks(ab_lines)
        c_lines = c[1]
        if args.strip_raw_comments:
            c_lines = [normalize_for_diff(l, strip_raw=True) for l in c_lines]
        ab_sentinel = "<ab>"
        merged, c_stats = unify(
            ab_collapsed, c_lines, ab_sentinel, c[0],
            strip_raw_comments=False,  # already normalised
        )
        in_clause = f'BRANCH in ("{a[0]}", "{b[0]}")'
        rewritten: list[str] = []
        for line in merged:
            # Expand any AB block placeholders back to their original
            # multi-line contents.
            if line.startswith("__AB_BLOCK_") and line.endswith("__"):
                idx = int(line[len("__AB_BLOCK_"):-len("__")])
                rewritten.extend(ab_blocks[idx])
                continue
            # Rewrite the `<ab>` sentinel emitted by the second merge.
            line = line.replace(
                f';@if BRANCH == "{ab_sentinel}"',
                f';@if {in_clause}',
            )
            line = line.replace(
                f';@elif BRANCH == "{ab_sentinel}"',
                f';@elif {in_clause}',
            )
            rewritten.append(line)
        out_lines = rewritten
        stats = {
            "diff_blocks": ab_stats["diff_blocks"] + c_stats["diff_blocks"],
            "ab_diff_blocks": ab_stats["diff_blocks"],
            "abc_diff_blocks": c_stats["diff_blocks"],
        }
    else:
        sys.exit(f"only 2- or 3-way unification supported (got {len(sources)} "
                 "sources). N>3 needs a synchronised matcher.")

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
