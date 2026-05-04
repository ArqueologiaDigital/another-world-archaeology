#!/usr/bin/env python3
"""Detect setup-then-overwrite gates in AW VM bytecode.

The gate pattern:

  setup channel=N, address=X        ; queue X to run on channel N
  setup channel=N, address=Y        ; immediately override with Y;
                                    ; X never runs.

When two `setup channel=N` instructions execute in the SAME
straight-line block (no intervening `break`, `ret`, `killChannel`,
`bankSwitch`, `freezeChannel`, or unconditional `jmp`), the
second overrides the first. The engine processes the channel-
queue per scheduler tick, and only the LAST `setup` for that
channel survives — so the first setup's target is unreachable
under runtime semantics, even though static control-flow has an
edge to it.

This is the mechanism behind the kick-detector / beetle gates
documented in research/05. It's also the key hook for the
broader reachability oracle tracked in #0058.

This tool is the FIRST PASS — the simple linear-block detector.
A complete reachability oracle would also walk control flow
across `je`/`jne`/`call`/`ret` edges to mark code unreachable
because no entry point reaches it. That deeper analysis is
follow-up work; this tool catches the specific gate idiom
that's been observed empirically.

Output: a JSON report grouped by port + level, listing each
gate site as `(file:line, channel, gated_address, surviving_address)`.

Usage:
  python3 tools/detect_setup_gates.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path("/home/fsanches/compartilhado/another-world-archaeology")
SRC_TREE = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
LEVELS = SRC_TREE / "src" / "levels"

# Branches to scan (their `.asm` file = per-port disasm output).
BRANCHES = ["cartridge_1992", "chahi_amiga_1991", "dos_1992", "gba_2004"]

RE_SETUP = re.compile(
    r"^\s*setup\s+channel=(?P<ch>0x[0-9A-Fa-f]+|\d+)\s*,\s*"
    r"address=(?P<addr>\S+)\s*$"
)
# Instructions that terminate the current straight-line block.
# Once we see one, prior `setup` opcodes can't overwrite via fall-through.
# Match end-of-line (`break\n`) AND followed-by-space variants
# (`bankSwitch 6 ; comment`).
RE_BLOCK_END = re.compile(
    r"^\s*(break|ret|killChannel|bankSwitch|freezeChannel|jmp)(\s|$)"
)
# A label definition also restarts the block (control flow can
# jump into here from elsewhere; prior setup state is unknown).
RE_LABEL_DEF = re.compile(r"^[A-Z_][A-Z0-9_]+:\s*$")
# An `;@if` directive boundary also ends a straight-line block:
# branches are mutually exclusive at preprocess time; one arm's
# tail can't fall through to the next.
RE_DIRECTIVE = re.compile(r"^\s*;@(?:if|elif|else|endif)\b")


def _is_killer(name: str) -> bool:
    """Is `name` a routine that kills its channel? Either an
    explicit `KILL_CHANNEL_*` routine, or a name ending in `_KILL`
    or containing `THEN_KILL` (the deferred-kill idiom — wait for
    a condition, then kill the channel)."""
    if name.startswith("KILL_CHANNEL"):
        return True
    if name.endswith("_KILL"):
        return True
    if "_THEN_KILL" in name:
        return True
    return False


def classify_gate(gated: str, surviving: str) -> str:
    """Classify a gate by what's being gated:
        - silencer:    substantive → killer (the surviving routine
                       kills the channel, possibly after a delay;
                       the gated substantive routine never runs).
                       Likely deliberate cut-content (research/05).
        - reschedule:  killer → substantive (self-killer gets
                       replaced by a real routine — common idiom
                       for "tear down then start fresh on this
                       channel").
        - swap:        substantive → substantive (changed mind;
                       both are real game logic, only the second
                       runs).
        - other:       at least one side is a `LABEL_HHHH`
                       placeholder whose role hasn't been
                       semantically identified yet.
    """
    is_kill_g = _is_killer(gated)
    is_kill_s = _is_killer(surviving)
    if is_kill_s and not is_kill_g:
        return "silencer"
    if is_kill_g and not is_kill_s:
        return "reschedule"
    if not is_kill_g and not is_kill_s:
        if (
            re.fullmatch(r"LABEL_[0-9A-F]+", gated)
            or re.fullmatch(r"LABEL_[0-9A-F]+", surviving)
        ):
            return "other"
        return "swap"
    return "other"


def scan_file(path: Path) -> list[dict]:
    """Return [{file, line, channel, gated, surviving, category}, ...]."""
    out: list[dict] = []
    lines = path.read_text().splitlines()
    # Track per-channel: (line_no, address) of the last setup that
    # could still be overwritten in this block.
    pending: dict[int, tuple[int, str]] = {}
    for i, line in enumerate(lines, 1):
        # Block-end resets state.
        if RE_BLOCK_END.match(line):
            pending.clear()
            continue
        if RE_LABEL_DEF.match(line):
            pending.clear()
            continue
        if RE_DIRECTIVE.match(line):
            pending.clear()
            continue
        m = RE_SETUP.match(line)
        if not m:
            continue
        ch = int(m.group("ch"), 0)
        addr = m.group("addr")
        if ch in pending:
            prev_line, prev_addr = pending[ch]
            if prev_addr != addr:
                out.append(
                    {
                        "file": str(path.relative_to(SRC_TREE)),
                        "channel": f"0x{ch:02X}",
                        "gated_line": prev_line,
                        "gated_address": prev_addr,
                        "surviving_line": i,
                        "surviving_address": addr,
                        "category": classify_gate(prev_addr, addr),
                    }
                )
        pending[ch] = (i, addr)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "docs" / "setup_gate_inventory.json",
    )
    parser.add_argument(
        "--md",
        type=Path,
        default=REPO_ROOT / "docs" / "setup_gate_inventory.md",
    )
    args = parser.parse_args()

    # Group by branch → list of gates.
    by_branch: dict[str, list[dict]] = defaultdict(list)
    for branch in BRANCHES:
        branch_dir = LEVELS / branch
        if not branch_dir.is_dir():
            continue
        for asm in sorted(branch_dir.glob("*.asm")):
            gates = scan_file(asm)
            for g in gates:
                g["branch"] = branch
                g["stage"] = asm.stem
            by_branch[branch].extend(gates)

    # JSON output (machine-readable).
    json_out = {b: gates for b, gates in by_branch.items()}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(json_out, indent=2) + "\n")

    # Markdown summary.
    md: list[str] = []
    md.append("# Setup-then-overwrite gate inventory")
    md.append("")
    md.append(
        "Static scan for the AW VM gate pattern — two `setup "
        "channel=N` instructions in the same straight-line block, "
        "where the second's address overrides the first's. The "
        "first's target is then unreachable under runtime "
        "semantics even though static control-flow has an edge to "
        "it. See research/05 (beetle in the lake) for the "
        "canonical example."
    )
    md.append("")
    md.append(
        "First-pass detector: scans only same-block consecutive "
        "setups separated by no `break`/`ret`/`killChannel`/"
        "`bankSwitch`/`freezeChannel`/`jmp`/label/`;@if` boundary. "
        "A complete reachability oracle (#0058) needs additional "
        "control-flow analysis."
    )
    md.append("")
    total = sum(len(g) for g in by_branch.values())
    md.append(f"**Total gates detected: {total}.**")
    md.append("")

    # Cross-branch category breakdown — silencers are the highest-
    # interest cases (deliberate cut-content per research/05).
    md.append("## Category breakdown (cross-branch)")
    md.append("")
    md.append(
        "Each gate is classified by what it's gating:\n\n"
        "- **silencer** — substantive routine → `KILL_CHANNEL_*`.\n"
        "  The surviving address kills the channel; the gated\n"
        "  routine never runs. Likely deliberate cut-content\n"
        "  (research/05).\n"
        "- **reschedule** — `KILL_CHANNEL_*` → substantive.\n"
        "  The gated kill-self gets replaced by a real routine —\n"
        "  common idiom for tearing down and starting fresh on\n"
        "  the same channel.\n"
        "- **swap** — substantive → substantive. Both are real\n"
        "  game logic; only the second runs (the first was a\n"
        "  changed mind).\n"
        "- **other** — at least one side is a `LABEL_HHHH`\n"
        "  placeholder whose role hasn't been semantically\n"
        "  identified yet.\n"
    )
    cat_totals: dict[str, int] = defaultdict(int)
    for gates in by_branch.values():
        for g in gates:
            cat_totals[g["category"]] += 1
    md.append("| Category | Count |")
    md.append("| --- | ---: |")
    for cat in ("silencer", "reschedule", "swap", "other"):
        md.append(f"| `{cat}` | {cat_totals.get(cat, 0)} |")
    md.append("")

    for branch, gates in sorted(by_branch.items()):
        md.append(f"## `{branch}`")
        md.append("")
        md.append(f"{len(gates)} gates across {len({g['stage'] for g in gates})} stages.")
        md.append("")
        if not gates:
            continue
        md.append("| Stage | Channel | Gated → Surviving | Category | Source |")
        md.append("| --- | :---: | --- | :---: | --- |")
        for g in sorted(
            gates, key=lambda x: (x["stage"], int(x["channel"], 16))
        ):
            md.append(
                f"| {g['stage']} | `{g['channel']}` | "
                f"`{g['gated_address']}` → `{g['surviving_address']}` | "
                f"`{g['category']}` | "
                f"{g['file']}:{g['gated_line']}-{g['surviving_line']} |"
            )
        md.append("")

    args.md.write_text("\n".join(md) + "\n")
    print(f"wrote {args.out}")
    print(f"wrote {args.md}")
    print(f"  {total} gates across {sum(1 for v in by_branch.values() if v)} branches")
    return 0


if __name__ == "__main__":
    sys.exit(main())
