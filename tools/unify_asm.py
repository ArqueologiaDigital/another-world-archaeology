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


def _parse_top_level_blocks(
    lines: list[str],
) -> list[tuple[int, int, list[tuple[int, int, str]]]]:
    """Parse top-level `;@if/.../;@endif` blocks.

    Returns a list of (start, end, sections) where:
    - start, end: indices of the `;@if` and matching `;@endif` lines.
    - sections: list of (header_idx, body_start_idx, condition_str).
      The first section is the `;@if`, subsequent are `;@elif` /
      `;@else`. `body_start_idx` is the line right after the header;
      a section's body runs until the next section's `header_idx`
      or the block's `end`.
    """
    out = []
    i = 0
    n = len(lines)
    while i < n:
        s = lines[i].lstrip()
        if s.startswith(";@if "):
            depth = 1
            sections = [(i, i + 1, lines[i].strip())]
            j = i + 1
            while j < n:
                ss = lines[j].lstrip()
                if ss.startswith(";@if "):
                    depth += 1
                elif ss.startswith(";@endif"):
                    depth -= 1
                    if depth == 0:
                        break
                elif depth == 1 and (
                    ss.startswith(";@elif ") or ss.startswith(";@else")
                ):
                    sections.append((j, j + 1, lines[j].strip()))
                j += 1
            if j < n:
                out.append((i, j, sections))
            i = j + 1
        else:
            i += 1
    return out


def _section_body(
    lines: list[str],
    block_start: int,
    block_end: int,
    sections: list[tuple[int, int, str]],
    section_idx: int,
) -> list[str]:
    """Return body lines for one section of a parsed block."""
    _, body_start, _ = sections[section_idx]
    if section_idx + 1 < len(sections):
        body_end = sections[section_idx + 1][0]
    else:
        body_end = block_end
    return lines[body_start:body_end]


def merge_adjacent_blocks(lines: list[str]) -> tuple[list[str], int]:
    """Merge adjacent `;@if/.../;@endif` blocks with identical
    section-header signatures, separated only by blank lines.

    Two blocks merge by concatenating per-arm contents. Operates
    recursively: after merging at the top level, recurse into each
    section's body so inner same-cond blocks also collapse.

    Returns (merged_lines, num_merges).

    Implementation: merges one pair per iteration and re-parses.
    Slower than batch-merging but avoids index-staleness bugs when
    chains of 3+ same-cond blocks need to merge (the i-th merge
    invalidates indices of subsequent merge targets in the original
    parse).
    """
    total_merges = 0
    while True:
        blocks = _parse_top_level_blocks(lines)
        if len(blocks) < 2:
            break
        merged_this_round = False
        # Find FIRST adjacent same-cond pair and merge it. Re-parse
        # in the next loop iteration to pick up the next eligible
        # pair (which may now span a freshly-merged block).
        for k in range(len(blocks) - 1):
            s_prev, e_prev, sec_prev = blocks[k]
            s_cur, e_cur, sec_cur = blocks[k + 1]
            gap = lines[e_prev + 1:s_cur]
            if any(l.strip() for l in gap):
                continue
            sig_prev = tuple(s[2] for s in sec_prev)
            sig_cur = tuple(s[2] for s in sec_cur)
            if sig_prev != sig_cur:
                continue
            # Build merged body per section: concatenate prev's body
            # and cur's body for each matching section.
            merged_segments: list[str] = [lines[s_prev]]  # outer ;@if
            for idx in range(len(sec_prev)):
                if idx > 0:
                    merged_segments.append(lines[sec_prev[idx][0]])
                # Prev body for this section.
                body_end_prev = (
                    sec_prev[idx + 1][0] if idx + 1 < len(sec_prev) else e_prev
                )
                merged_segments.extend(lines[sec_prev[idx][1]:body_end_prev])
                # Cur body for the corresponding section.
                body_end_cur = (
                    sec_cur[idx + 1][0] if idx + 1 < len(sec_cur) else e_cur
                )
                merged_segments.extend(lines[sec_cur[idx][1]:body_end_cur])
            merged_segments.append(lines[e_cur])  # ;@endif
            lines = lines[:s_prev] + merged_segments + lines[e_cur + 1:]
            total_merges += 1
            merged_this_round = True
            break
        if not merged_this_round:
            break
    # Now recurse into each top-level block's section bodies. Inner
    # `;@if` blocks may also have adjacent same-cond pairs that
    # merging at the top level didn't reach (because they're nested).
    out_lines: list[str] = []
    blocks = _parse_top_level_blocks(lines)
    pos = 0
    for s, e, sections in blocks:
        out_lines.extend(lines[pos:s])
        out_lines.append(lines[s])  # ;@if header
        for idx in range(len(sections)):
            if idx > 0:
                out_lines.append(lines[sections[idx][0]])  # ;@elif/else
            body = _section_body(lines, s, e, sections, idx)
            recursed, sub_merges = merge_adjacent_blocks(body)
            total_merges += sub_merges
            out_lines.extend(recursed)
        out_lines.append(lines[e])  # ;@endif
        pos = e + 1
    out_lines.extend(lines[pos:])
    return out_lines, total_merges


RE_BRANCH_LIT = re.compile(r'"([^"]+)"')


def _parse_branch_set(
    directive_line: str, universe: frozenset[str] | None = None
) -> frozenset[str] | None:
    """Parse a `;@if`/`;@elif` directive into the set of branches it
    activates. Returns None for `;@else` (which depends on the
    surrounding section state).

    Supported syntax:
      BRANCH == "x"               → {x}
      BRANCH != "x"               → universe - {x}    (needs universe)
      BRANCH in ("x", "y", ...)   → {x, y, ...}

    Anything else returns None (treat as opaque).
    """
    s = directive_line.strip()
    quoted = RE_BRANCH_LIT.findall(s)
    if " in " in s and quoted:
        return frozenset(quoted)
    if " == " in s and len(quoted) == 1:
        return frozenset(quoted)
    if " != " in s and len(quoted) == 1:
        if universe is None:
            return None
        return universe - frozenset(quoted)
    return None


def _collect_universe(lines: list[str]) -> frozenset[str]:
    """Best-effort universe of branch names: every quoted string
    appearing in any `;@if`/`;@elif` directive."""
    branches: set[str] = set()
    for l in lines:
        s = l.lstrip()
        if s.startswith(";@if ") or s.startswith(";@elif "):
            branches.update(RE_BRANCH_LIT.findall(s))
    return frozenset(branches)


def _absorb_arm_into_outer(
    lines: list[str],
    outer_s: int,
    outer_e: int,
    outer_sections: list[tuple[int, int, str]],
    arm_idx: int,
    universe: frozenset[str],
) -> list[str] | None:
    """If `outer_sections[arm_idx]`'s body is exactly a single nested
    `;@if/elif/.../;@endif` block (modulo blank lines) AND the inner
    arms' branches form a partition of the outer arm's branches,
    replace the outer arm with the inner arms inline (so the outer
    block gains arms; the inner block is absorbed).

    Returns the new lines list, or None if not applicable.

    Saves 2 directives and reduces nesting depth by 1.
    """
    arm_header_idx, arm_body_start, arm_cond = outer_sections[arm_idx]
    arm_body_end = (
        outer_sections[arm_idx + 1][0] if arm_idx + 1 < len(outer_sections)
        else outer_e
    )
    body = lines[arm_body_start:arm_body_end]
    # Strip surrounding blank lines.
    a = 0
    while a < len(body) and not body[a].strip():
        a += 1
    b = len(body)
    while b > a and not body[b - 1].strip():
        b -= 1
    inner = body[a:b]
    if not inner or not inner[0].lstrip().startswith(";@if "):
        return None
    # Verify `inner` is a single complete `;@if/.../;@endif` block.
    depth = 1
    end_idx = -1
    for k in range(1, len(inner)):
        s = inner[k].lstrip()
        if s.startswith(";@if "):
            depth += 1
        elif s.startswith(";@endif"):
            depth -= 1
            if depth == 0:
                end_idx = k
                break
    if end_idx != len(inner) - 1:
        return None
    # Parse inner sections.
    inner_blocks = _parse_top_level_blocks(inner)
    if len(inner_blocks) != 1:
        return None
    inner_s, inner_e, inner_sections = inner_blocks[0]
    # Branch partitioning: union of inner-section branches must equal
    # the outer arm's branches.
    outer_arm_branches = _parse_branch_set(arm_cond, universe)
    if outer_arm_branches is None:
        return None
    inner_union: set[str] = set()
    for sec in inner_sections:
        bs = _parse_branch_set(sec[2], universe)
        if bs is None:
            return None
        if inner_union & bs:
            return None  # not disjoint — can't absorb without overlap
        inner_union |= bs
    if frozenset(inner_union) != outer_arm_branches:
        return None
    # Build the absorbed-arm replacement: each inner section's
    # header (rewritten as `;@elif` if not the first arm in the
    # outer block) followed by its body. Drop the inner `;@if` and
    # `;@endif` directives.
    absorbed: list[str] = []
    inner_section_first_in_outer = (arm_idx == 0)
    for k, (header_idx, body_start, _cond) in enumerate(inner_sections):
        # Determine the inner section's body in `inner`.
        inner_body_start = body_start
        inner_body_end = (
            inner_sections[k + 1][0] if k + 1 < len(inner_sections)
            else inner_e
        )
        inner_body = inner[inner_body_start:inner_body_end]
        # Header line rewriting:
        # - First inner section: if outer arm_idx==0, becomes the
        #   outer ;@if header. Otherwise becomes ;@elif.
        # - Subsequent inner sections: always ;@elif.
        original_header = inner[header_idx]
        if k == 0 and inner_section_first_in_outer:
            absorbed.append(original_header)  # `;@if BRANCH ...`
        else:
            # Convert to `;@elif` form.
            new_header = re.sub(
                r'^(\s*);@if\b', r'\1;@elif', original_header
            )
            new_header = re.sub(
                r'^(\s*);@elif\b', r'\1;@elif', new_header
            )
            absorbed.append(new_header)
        absorbed.extend(inner_body)
    # Now splice: replace the outer arm's [header..body] range with
    # the absorbed content. The outer arm's HEADER is at
    # `arm_header_idx`; its content runs through `arm_body_end - 1`.
    new_lines = (
        lines[:arm_header_idx]
        + absorbed
        + lines[arm_body_end:]
    )
    return new_lines


def flatten_subset_nesting(lines: list[str]) -> tuple[list[str], int]:
    """When an outer single-arm `;@if Y / ... / ;@endif` block has a
    nested `;@if X / ... / ;@endif` at the START or END of its body
    with X ⊆ Y, hoist the inner block out so it sits adjacent to
    (instead of inside) the outer block.

    Same total directive count, but flatter — readers don't need to
    track that the inner condition is implicitly tightened by the
    outer scope.

    Also handles the multi-arm absorption case: if one outer arm's
    body is exactly a single nested `;@if X / ;@elif Y / ;@endif`
    block whose branches partition the outer arm's branches, the
    inner block's arms are absorbed into the outer block as new
    arms (saves 2 directives, reduces depth by 1). Common pattern:
    `;@if BRANCH in ("cart", "gba")` with body
    `;@if BRANCH == "cart" / ... / ;@elif "gba" / ... / ;@endif`
    → flattens to a single-level if/elif/elif over the three branches.

    Recurses into the bodies of remaining blocks so nested cases
    bubble up incrementally.

    Returns (out_lines, num_hoists).
    """
    universe = _collect_universe(lines)
    total_hoists = 0
    while True:
        blocks = _parse_top_level_blocks(lines)
        hoisted = False
        # First pass: try arm-absorption on multi-arm outer blocks.
        for s, e, sections in blocks:
            if len(sections) < 2:
                continue
            for arm_idx in range(len(sections)):
                new_lines = _absorb_arm_into_outer(
                    lines, s, e, sections, arm_idx, universe
                )
                if new_lines is not None:
                    lines = new_lines
                    total_hoists += 1
                    hoisted = True
                    break
            if hoisted:
                break
        if hoisted:
            continue  # re-parse with new layout
        # Second pass: subset-hoist for single-arm outer blocks.
        for s, e, sections in blocks:
            if len(sections) != 1:
                continue
            outer_cond = sections[0][2]
            outer_branches = _parse_branch_set(outer_cond, universe)
            if outer_branches is None:
                continue
            body_start = sections[0][1]
            body_end = e  # the `;@endif` line index

            # Inner-block check at START: skip leading blanks, then
            # the first non-blank line must be `;@if`.
            i = body_start
            while i < body_end and not lines[i].strip():
                i += 1
            inner_at_start = (
                i < body_end and lines[i].lstrip().startswith(";@if ")
            )

            # Inner-block check at END: skip trailing blanks, then
            # the last non-blank line must be `;@endif` whose
            # matching `;@if` is the LAST top-level block in the
            # outer body.
            j = body_end - 1
            while j >= body_start and not lines[j].strip():
                j -= 1
            inner_at_end = (
                j >= body_start and lines[j].lstrip().startswith(";@endif")
            )

            # Re-parse outer body to find inner block boundaries.
            body_blocks = _parse_top_level_blocks(lines[body_start:body_end])
            if not body_blocks:
                continue

            def hoist(inner_block_idx: int, position: str) -> bool:
                """position is 'before' or 'after'."""
                nonlocal lines, total_hoists
                inner_s, inner_e, inner_sections = body_blocks[inner_block_idx]
                # Convert to absolute indices.
                abs_inner_s = body_start + inner_s
                abs_inner_e = body_start + inner_e
                # Check inner sections' branches all ⊆ outer.
                for sec in inner_sections:
                    bs = _parse_branch_set(sec[2], universe)
                    if bs is None or not bs.issubset(outer_branches):
                        return False
                # Inner block's lines.
                inner_lines = lines[abs_inner_s:abs_inner_e + 1]
                # Build new layout:
                #   before-hoist:
                #     before-outer (lines[:s])
                #     outer-header (lines[s])
                #     inner-block (already in body)
                #     ...rest of body...
                #     outer-endif (lines[e])
                #   after-hoist (position='before'):
                #     before-outer (lines[:s])
                #     inner-block
                #     outer-header
                #     ...rest of outer body (excluding the inner-block range)...
                #     outer-endif
                outer_header = lines[s]
                outer_endif = lines[e]
                if position == "before":
                    # Body before the inner: the lines BEFORE abs_inner_s
                    # in the outer body. These are blank gap lines we'd
                    # collected before the inner — drop them, they're
                    # cosmetic.
                    body_after_inner = lines[abs_inner_e + 1:body_end]
                    # Strip leading blanks of body_after_inner — the
                    # blank that originally separated outer-header
                    # from inner is gone now.
                    while body_after_inner and not body_after_inner[0].strip():
                        body_after_inner = body_after_inner[1:]
                    # If the remaining outer body is empty, the outer
                    # block becomes a no-op — drop it entirely.
                    if not body_after_inner:
                        new_segment = inner_lines
                    else:
                        new_segment = (
                            inner_lines
                            + [outer_header]
                            + body_after_inner
                            + [outer_endif]
                        )
                else:  # 'after'
                    body_before_inner = lines[body_start:abs_inner_s]
                    # Strip trailing blanks (cosmetic).
                    while body_before_inner and not body_before_inner[-1].strip():
                        body_before_inner = body_before_inner[:-1]
                    if not body_before_inner:
                        new_segment = inner_lines
                    else:
                        new_segment = (
                            [outer_header]
                            + body_before_inner
                            + [outer_endif]
                            + inner_lines
                        )
                lines = lines[:s] + new_segment + lines[e + 1:]
                total_hoists += 1
                return True

            # Try: inner at start (block_idx=0).
            # Need: before block 0 in body, only blank lines.
            if body_blocks:
                first_s, first_e, _ = body_blocks[0]
                # First block's start is at index first_s in body.
                # Lines before: body[:first_s] (relative).
                pre = lines[body_start:body_start + first_s]
                if all(not l.strip() for l in pre):
                    if hoist(0, "before"):
                        hoisted = True
                        break

            # Try: inner at end (block_idx=last).
            if body_blocks:
                last_s, last_e, _ = body_blocks[-1]
                post = lines[body_start + last_e + 1:body_end]
                if all(not l.strip() for l in post):
                    if hoist(len(body_blocks) - 1, "after"):
                        hoisted = True
                        break
        if not hoisted:
            break
    # Recurse into remaining top-level blocks' bodies (in case there
    # are deeply nested subset-flatten opportunities).
    out_lines: list[str] = []
    blocks = _parse_top_level_blocks(lines)
    pos = 0
    for s, e, sections in blocks:
        out_lines.extend(lines[pos:s])
        out_lines.append(lines[s])
        for idx in range(len(sections)):
            if idx > 0:
                out_lines.append(lines[sections[idx][0]])
            body = _section_body(lines, s, e, sections, idx)
            recursed, sub_hoists = flatten_subset_nesting(body)
            total_hoists += sub_hoists
            out_lines.extend(recursed)
        out_lines.append(lines[e])
        pos = e + 1
    out_lines.extend(lines[pos:])
    return out_lines, total_hoists


def promote_safe_label_defs(lines: list[str]) -> tuple[list[str], int]:
    """Drop the `;@if/.../;@endif` wrapper around single-arm blocks
    whose only content is a `LABEL_xxxx:` definition, when that label
    is exclusively referenced inside `;@if` blocks that share the
    same branch set.

    Such a label, when promoted to unconditional, becomes an unused
    label in the OTHER branches (the ones outside the original
    `;@if` clause's branch set). Unused labels emit no bytecode so
    byte-match is preserved. Net win: -1 `;@if` and -1 `;@endif`
    per promotion.

    Safety conditions:
    - The block must be a single-arm `;@if BRANCH ... / LABEL_xxx: / ;@endif`
      (no `;@elif`, no other content).
    - The LABEL_xxx token must NOT appear anywhere outside the same
      single-arm `;@if` clause's branch set in the rest of the file.
      This ensures we're not creating a duplicate definition or a
      stray reference for a branch that already has the label
      somewhere else.

    Returns (out_lines, num_promotions).
    """
    RE_LABEL_TOKEN = re.compile(r'\bLABEL_[A-Fa-f0-9]+\b')
    blocks = _parse_top_level_blocks(lines)
    # Index every LABEL token's positions: list of (line_idx, in_block,
    # block_branches). For each token occurrence, record what branch set
    # the wrapping `;@if` (if any) restricts it to. If no wrapper,
    # `block_branches` is None (unconditional).
    # Build a map line_idx → (block_idx, branch_set or None).
    line_block_map: dict[int, tuple[int, frozenset[str] | None]] = {}
    for k, (s, e, sections) in enumerate(blocks):
        for sec_idx in range(len(sections)):
            body_start = sections[sec_idx][1]
            body_end = (
                sections[sec_idx + 1][0] if sec_idx + 1 < len(sections)
                else e
            )
            cond = sections[sec_idx][2]
            # Extract branch names from the directive.
            branches = frozenset(re.findall(r'"([^"]+)"', cond))
            if not branches:
                branches = None  # ;@else; treat as "all-but-listed" — too
                                 # complex to reason about; skip.
            for li in range(body_start, body_end):
                line_block_map[li] = (k, branches)

    label_positions: dict[str, list[tuple[int, frozenset[str] | None]]] = {}
    for li, line in enumerate(lines):
        for token in RE_LABEL_TOKEN.findall(line):
            entry = line_block_map.get(li)
            label_positions.setdefault(token, []).append(
                (li, entry[1] if entry else None)
            )

    # Find candidate single-arm LABEL_def blocks.
    promote: list[tuple[int, int]] = []  # (block_start, block_end) to drop
    promoted = 0
    for s, e, sections in blocks:
        if len(sections) != 1:
            continue
        body_start = sections[0][1]
        body_lines = [
            lines[t] for t in range(body_start, e) if lines[t].strip()
        ]
        if len(body_lines) != 1:
            continue
        m = re.match(r'^([A-Z][A-Z_0-9]*):\s*$', body_lines[0].strip())
        if not m:
            continue
        label = m.group(1)
        if not label.startswith("LABEL_"):
            continue
        # Get the block's branch set.
        cond = sections[0][2]
        branches = frozenset(re.findall(r'"([^"]+)"', cond))
        if not branches:
            continue
        # Check every other occurrence of `label` in the file: it must
        # be inside an `;@if` whose branch set is a SUBSET of `branches`
        # (so the label is exclusive to those branches everywhere).
        positions = label_positions.get(label, [])
        ok = True
        for li, occ_branches in positions:
            # Skip the definition itself.
            if body_start <= li < e:
                continue
            if occ_branches is None:
                # Unconditional reference — present in ALL branches.
                # Promotion would create a label collision IF some
                # branch has its own definition for `label`. We don't
                # track that; conservative skip.
                ok = False
                break
            if not occ_branches.issubset(branches):
                ok = False
                break
        if not ok:
            continue
        promote.append((s, e))
        promoted += 1
    # Apply promotions from end backwards so indices stay valid.
    for s, e in reversed(promote):
        body_start = s + 1
        # Find the LABEL line inside; emit only that line, drop the
        # `;@if` and `;@endif` directives.
        body_lines = [
            lines[t] for t in range(body_start, e) if lines[t].strip()
        ]
        # Also keep ONE blank line after for readability.
        new_segment = body_lines  # just the label line(s)
        lines = lines[:s] + new_segment + lines[e + 1:]
    return lines, promoted


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

    # Post-process: merge adjacent same-condition blocks. The diff
    # algorithm emits a fresh `;@if/.../;@endif` block at every diff
    # opcode, so two opcodes separated only by a blank line (which
    # difflib classifies as `equal`) become two adjacent blocks with
    # the same condition signature. Collapsing them into one keeps
    # byte-match identical while reducing directive noise. Recurses
    # into nested blocks.
    pre_merge_block_count = sum(
        1 for l in out_lines if l.lstrip().startswith(";@if ")
    )
    out_lines, n_merges = merge_adjacent_blocks(out_lines)
    out_lines, n_label_promotions = promote_safe_label_defs(out_lines)
    # A second merge pass: promoting safe labels can leave NEW
    # adjacent same-cond blocks that didn't exist before (the promoted
    # label-def block was sitting between them).
    out_lines, n_merges_2 = merge_adjacent_blocks(out_lines)
    n_merges += n_merges_2
    out_lines, n_flattens = flatten_subset_nesting(out_lines)
    # Re-merge after flattening: hoisted blocks might end up adjacent
    # to other same-condition blocks at the top level.
    out_lines, n_merges_3 = merge_adjacent_blocks(out_lines)
    n_merges += n_merges_3
    post_merge_block_count = sum(
        1 for l in out_lines if l.lstrip().startswith(";@if ")
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(out_lines) + "\n")

    print(f"sources: {len(sources)}")
    for br, lines in sources:
        print(f"  {br}: {len(lines)} lines")
    print(f"\nstats: diff_blocks={stats['diff_blocks']}")
    print(f"  merged adjacent same-cond blocks: {n_merges}")
    print(f"  promoted safe LABEL_def blocks:   {n_label_promotions}")
    print(f"  flattened subset-nested blocks:   {n_flattens}")
    print(f"  ;@if count {pre_merge_block_count} → {post_merge_block_count}")
    print(f"\nwrote {args.output}: {len(out_lines)} lines")
    largest_input = max(len(s[1]) for s in sources)
    overhead = len(out_lines) - largest_input
    print(f"  overhead vs largest source: {overhead} lines "
          f"({100 * overhead / len(out_lines):.1f}%)")


if __name__ == "__main__":
    main()
