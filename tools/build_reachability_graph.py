#!/usr/bin/env python3
"""Build a static reachability graph for an AW VM port's bytecode.

This is the core of the reachability oracle tracked in #0058.
Given a port's full per-stage disassembly, we trace which labels
are *live* — reachable via static control flow from at least one
entry point, with the setup-then-overwrite gate adjustments
applied.

How reachability is computed:

  1. **Build label-target index**: for each label (definition),
     record every reference site (`call`/`jmp`/`je`/`jne`/`jg`/
     `jge`/`jl`/`jle`/`djnz`/`setup channel=N, address=X`).

  2. **Identify entry points**: every `setup channel=N,
     address=X` is a scheduler entry — the engine queues X to
     run on channel N. The level-entry script is also an entry
     (the bytes preceding the first label definition).

  3. **Propagate reachability**: starting from each entry point
     label, walk forward through instructions until a
     control-flow terminator (`break`, `ret`, `killChannel`,
     `bankSwitch`, `freezeChannel`, unconditional `jmp`).
     At each instruction, follow:
        - `call X` — recurse into X (return-edge handled by `ret`)
        - `jmp X` — follow X, do NOT continue past
        - `je`/`jne`/etc. — both targets are reachable: the
          branch target AND the fall-through.
        - `setup channel=N, address=X` — X is reachable on
          channel N. We treat this as a separate entry-point
          discovery, not an immediate edge from the current
          flow, since X runs on a different channel.

  4. **Apply gate adjustments**: for each silencer gate
     `(channel=N, gated=Y, surviving=Z)` where Y and Z appear
     in the same block with no intervening control flow,
     remove Y as a live entry point (it's queued but
     immediately overridden). If Y has no other live setup
     references, mark it dead.

Output: a JSON document grouped by stage, listing each label
as live / dead / unreferenced.

Limitations of this first cut:
  - Per-stage scope: cross-stage edges (rare in AW) are not
    followed. The scheduler runs each stage's bytecode in
    isolation.
  - No `ret` modeling: `call`/`ret` returns are tracked via a
    simplified "fall-through after call" model — the
    instruction after `call X` is considered reachable iff the
    callee can return (which is true for any callee that
    contains a `ret` or doesn't have a control-flow
    terminator). For the AW VM this is fine since `ret`
    routines always return.

Usage:
  python3 tools/build_reachability_graph.py
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

# We focus on dos_1992 first since it's the most complete and
# best-named branch.
DEFAULT_BRANCH = "dos_1992"

RE_LABEL_DEF = re.compile(r"^([A-Z_][A-Z0-9_]+):\s*$")
RE_SETUP = re.compile(
    r"^\s*setup\s+channel=(?P<ch>0x[0-9A-Fa-f]+|\d+)\s*,\s*"
    r"address=(?P<addr>\S+)\s*$"
)
RE_CALL = re.compile(r"^\s*call\s+(?P<addr>[A-Z_][A-Z0-9_]+)\s*$")
RE_JMP = re.compile(r"^\s*jmp\s+(?P<addr>[A-Z_][A-Z0-9_]+)\s*$")
RE_BRANCH = re.compile(
    r"^\s*(je|jne|jg|jge|jl|jle|djnz)\s+.*?,\s*"
    r"(?P<addr>[A-Z_][A-Z0-9_]+)\s*$"
)
# Terminators that end a fall-through walk.
#
# `break` is intentionally NOT a terminator: it yields control
# to the scheduler for one tick, then execution resumes at the
# NEXT instruction. So fall-through across `break` is real and
# routine, common in AW VM code (e.g. animation tick loops).
#
# `freezeChannel` IS a terminator — it pauses the channel
# indefinitely. The channel can be unstuck only by an external
# `setup` from another channel. Treating it as a terminator is
# slightly conservative (some labels could be reached via
# re-schedule), but it's the right call for first-pass static
# reachability.
RE_TERM = re.compile(
    r"^\s*(ret|killChannel|bankSwitch|freezeChannel)\s*$"
)


def parse_stage(path: Path) -> dict:
    """Parse one stage `.asm` file into a structured representation:

    {
      "labels": {LABEL_NAME: {"line": int, "instrs": [(line, text), ...]}},
      "label_order": [LABEL_NAME, ...] — definition order
    }
    """
    lines = path.read_text().splitlines()
    labels: dict[str, dict] = {}
    label_order: list[str] = []
    cur: str | None = None
    for i, line in enumerate(lines, 1):
        m = RE_LABEL_DEF.match(line)
        if m:
            cur = m.group(1)
            labels[cur] = {"line": i, "instrs": []}
            label_order.append(cur)
            continue
        if cur is None:
            continue
        s = line.strip()
        if not s or s.startswith(";"):
            continue
        labels[cur]["instrs"].append((i, line))
    return {"labels": labels, "label_order": label_order}


def collect_entry_points(stage: dict) -> set[str]:
    """All labels that appear as a `setup` target — these are the
    scheduler entry points the engine can queue."""
    entries: set[str] = set()
    for label, body in stage["labels"].items():
        for _line, instr in body["instrs"]:
            m = RE_SETUP.match(instr)
            if m:
                entries.add(m.group("addr"))
    return entries


def collect_referenced(stage: dict) -> set[str]:
    """Every label name referenced from any opcode (setup, call,
    jmp, je/jne/etc.). Doesn't include label definitions
    themselves."""
    refs: set[str] = set()
    for body in stage["labels"].values():
        for _line, instr in body["instrs"]:
            for re_ in (RE_SETUP, RE_CALL, RE_JMP, RE_BRANCH):
                m = re_.match(instr)
                if m:
                    refs.add(m.group("addr"))
                    break
    return refs


def reachable_from(start: str, stage: dict, gates: set[str]) -> set[str]:
    """Walk forward from `start`, returning the set of labels
    reachable (transitively, following call/jmp/conditional-branch
    edges, and falling through label boundaries when no terminator
    is hit). Stops at control-flow terminators and at gate-silenced
    setup targets.

    Labels in AW VM bytecode are addressable byte offsets, not
    routine boundaries. Many labels are mid-routine targets that
    fall through into the next label without a terminator. The
    walker tracks fall-through across label boundaries via
    `label_order`."""
    visited: set[str] = set()
    label_order = stage["label_order"]
    label_idx = {name: i for i, name in enumerate(label_order)}
    queue: list[str] = [start]
    while queue:
        label = queue.pop()
        if label in visited:
            continue
        if label not in stage["labels"]:
            # Out-of-stage reference (e.g., constant import) —
            # skip but don't fail.
            continue
        visited.add(label)
        terminated = False
        for _line, instr in stage["labels"][label]["instrs"]:
            if RE_TERM.match(instr):
                terminated = True
                break
            m = RE_JMP.match(instr)
            if m:
                if m.group("addr") not in visited:
                    queue.append(m.group("addr"))
                terminated = True  # unconditional — no fall-through
                break
            m = RE_CALL.match(instr)
            if m:
                if m.group("addr") not in visited:
                    queue.append(m.group("addr"))
                continue  # fall-through after call
            m = RE_BRANCH.match(instr)
            if m:
                if m.group("addr") not in visited:
                    queue.append(m.group("addr"))
                continue  # fall-through after conditional branch
            m = RE_SETUP.match(instr)
            if m:
                # setup queues a routine on a different channel —
                # add to entry-point set if not gate-silenced.
                addr = m.group("addr")
                if addr not in gates and addr not in visited:
                    queue.append(addr)
                continue
        if not terminated:
            # Fall through to the next label in the file.
            i = label_idx.get(label, -1)
            if i >= 0 and i + 1 < len(label_order):
                nxt = label_order[i + 1]
                if nxt not in visited:
                    queue.append(nxt)
    return visited


class ReachabilityOracle:
    """Programmatic reachability oracle for #0058.

    Used by the asset-scan family (#0054–#0057) to filter
    out references that come from dead bytecode. Build once
    per branch; queries are O(1) set lookups.

    Usage:
      oracle = ReachabilityOracle(branch="dos_1992")
      oracle.is_live("LAKE", "BEETLE_INIT_POS_THEN_WALK_LEFT")  # False
      oracle.classify("LAKE", "BEETLE_KICK_DETECTOR")           # "dead-by-gate"
      oracle.live_labels("LAKE")                                # set[str]
      oracle.transitively_dead("LAKE")                          # set[str]
    """

    def __init__(self, branch: str = DEFAULT_BRANCH):
        self.branch = branch
        self._stages = self._build(branch)

    @staticmethod
    def _load_gates(branch: str) -> set[str]:
        gate_path = REPO_ROOT / "docs" / "setup_gate_inventory.json"
        gated_silenced: set[str] = set()
        if gate_path.exists():
            gates_data = json.loads(gate_path.read_text())
            for b, gates in gates_data.items():
                if b != branch:
                    continue
                for g in gates:
                    if g["category"] == "silencer":
                        gated_silenced.add(g["gated_address"])
        return gated_silenced

    @classmethod
    def _build(cls, branch: str) -> dict[str, dict]:
        branch_dir = LEVELS / branch
        if not branch_dir.is_dir():
            raise FileNotFoundError(f"branch dir not found: {branch_dir}")
        gated_silenced = cls._load_gates(branch)
        out: dict[str, dict] = {}
        for asm in sorted(branch_dir.glob("*.asm")):
            stage = parse_stage(asm)
            entries = collect_entry_points(stage) - gated_silenced
            referenced = collect_referenced(stage)
            if stage["label_order"]:
                entries.add(stage["label_order"][0])
            live: set[str] = set()
            for entry in entries:
                live |= reachable_from(entry, stage, gated_silenced)
            all_labels = set(stage["labels"].keys())
            unreferenced = all_labels - referenced
            dead_by_gate = gated_silenced & all_labels - live
            transitively_dead = (
                all_labels - live - unreferenced - dead_by_gate
            )
            out[asm.stem] = {
                "live": live,
                "dead_by_gate": dead_by_gate,
                "transitively_dead": transitively_dead,
                "unreferenced": unreferenced,
                "all_labels": all_labels,
            }
        return out

    def stages(self) -> list[str]:
        """All stage names in this branch."""
        return sorted(self._stages.keys())

    def classify(self, stage: str, label: str) -> str:
        """Return one of: 'live', 'dead-by-gate',
        'transitively-dead', 'unreferenced', 'unknown'."""
        s = self._stages.get(stage)
        if s is None or label not in s["all_labels"]:
            return "unknown"
        if label in s["live"]:
            return "live"
        if label in s["dead_by_gate"]:
            return "dead-by-gate"
        if label in s["transitively_dead"]:
            return "transitively-dead"
        if label in s["unreferenced"]:
            return "unreferenced"
        return "unknown"

    def is_live(self, stage: str, label: str) -> bool:
        """True iff `label` is reachable from a live entry."""
        s = self._stages.get(stage)
        return s is not None and label in s["live"]

    def is_dead(self, stage: str, label: str) -> bool:
        """True iff `label` is dead-by-gate or transitively-dead."""
        return self.classify(stage, label) in (
            "dead-by-gate",
            "transitively-dead",
        )

    def live_labels(self, stage: str) -> set[str]:
        s = self._stages.get(stage)
        return set(s["live"]) if s else set()

    def dead_by_gate(self, stage: str) -> set[str]:
        s = self._stages.get(stage)
        return set(s["dead_by_gate"]) if s else set()

    def transitively_dead(self, stage: str) -> set[str]:
        s = self._stages.get(stage)
        return set(s["transitively_dead"]) if s else set()

    def unreferenced(self, stage: str) -> set[str]:
        s = self._stages.get(stage)
        return set(s["unreferenced"]) if s else set()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--branch",
        default=DEFAULT_BRANCH,
        help="Branch directory under src/levels (e.g. dos_1992)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="JSON output path (default: docs/reachability_graph_<branch>.json)",
    )
    parser.add_argument(
        "--md",
        type=Path,
        default=None,
        help="Markdown output path (default: docs/reachability_graph_<branch>.md)",
    )
    args = parser.parse_args()
    if args.out is None:
        args.out = REPO_ROOT / "docs" / f"reachability_graph_{args.branch}.json"
    if args.md is None:
        args.md = REPO_ROOT / "docs" / f"reachability_graph_{args.branch}.md"

    branch_dir = LEVELS / args.branch
    if not branch_dir.is_dir():
        print(f"branch dir not found: {branch_dir}", file=sys.stderr)
        return 1

    # Load gate inventory to suppress silencer gated targets.
    gate_path = REPO_ROOT / "docs" / "setup_gate_inventory.json"
    gated_silenced: set[str] = set()
    if gate_path.exists():
        gates_data = json.loads(gate_path.read_text())
        for branch, gates in gates_data.items():
            if branch != args.branch:
                continue
            for g in gates:
                if g["category"] == "silencer":
                    gated_silenced.add(g["gated_address"])

    by_stage: dict[str, dict] = {}
    for asm in sorted(branch_dir.glob("*.asm")):
        stage = parse_stage(asm)
        entries = collect_entry_points(stage) - gated_silenced
        referenced = collect_referenced(stage)
        # The first label of each stage is the engine's
        # implicit entry point — at runtime, the AW VM scheduler
        # starts every stage's bytecode at offset 0 regardless of
        # whether any `setup` opcode targets it. Add it.
        if stage["label_order"]:
            entries.add(stage["label_order"][0])
        # Live: reachable from some entry point (transitively).
        # Note: we still need to traverse — `reachable_from`
        # follows setup edges (other entry points) too, so each
        # entry's transitive closure includes setups it reaches.
        live: set[str] = set()
        for entry in entries:
            live |= reachable_from(entry, stage, gated_silenced)
        all_labels = set(stage["labels"].keys())
        unreferenced = all_labels - referenced
        # statically reachable but dead-by-gate:
        dead_by_gate = gated_silenced & all_labels - live
        # Referenced but not reachable from any live entry — the
        # transitive cut-content set. These labels ARE referenced
        # (from somewhere), but tracing forward from every live
        # entry-point setup never reaches them. Most are reached
        # only from dead-by-gate routines (beetle AI subgraph,
        # for instance) or from unreachable subgraphs.
        transitively_dead = (
            all_labels - live - unreferenced - dead_by_gate
        )
        by_stage[asm.stem] = {
            "total_labels": len(all_labels),
            "live": sorted(live),
            "unreferenced": sorted(unreferenced),
            "dead_by_gate": sorted(dead_by_gate),
            "transitively_dead": sorted(transitively_dead),
            "entry_points": sorted(entries),
            "n_live": len(live),
            "n_unreferenced": len(unreferenced),
            "n_dead_by_gate": len(dead_by_gate),
            "n_transitively_dead": len(transitively_dead),
            "n_total": len(all_labels),
        }

    # JSON output.
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(by_stage, indent=2) + "\n")

    # Markdown summary.
    md: list[str] = []
    md.append(f"# Reachability graph — `{args.branch}`")
    md.append("")
    md.append(
        "Static reachability analysis: for each label, is it "
        "reachable from any live setup entry point via call/jmp/"
        "branch edges, with silencer-gate suppression applied? "
        "See research/18 and #0058 for context."
    )
    md.append("")
    md.append("## Per-stage summary")
    md.append("")
    md.append(
        "Each label classified by static analysis:"
    )
    md.append("")
    md.append(
        "- **Live**: reachable from some live entry point via "
        "call/jmp/branch/setup edges and label-fall-through.\n"
        "- **Dead-by-gate**: explicitly silenced by a `setup-then-"
        "overwrite` gate (research/18); the label is queued but "
        "the queue entry is overwritten before scheduler "
        "dispatches.\n"
        "- **Transitively-dead**: referenced by other labels "
        "(typically via call/branch from inside a dead-by-gate "
        "subgraph or a stand-alone never-entered island), but "
        "no live entry-point trace reaches them.\n"
        "- **Unreferenced**: not the target of any opcode in the "
        "stage's source — pure orphans."
    )
    md.append("")
    md.append(
        "| Stage | Total | Live | Dead-by-gate | Transitively-dead | Unreferenced |"
    )
    md.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for stage, data in sorted(by_stage.items()):
        md.append(
            f"| {stage} | {data['n_total']} | {data['n_live']} "
            f"| {data['n_dead_by_gate']} "
            f"| {data['n_transitively_dead']} "
            f"| {data['n_unreferenced']} |"
        )
    md.append("")

    args.md.write_text("\n".join(md) + "\n")
    print(f"wrote {args.out}")
    print(f"wrote {args.md}")
    total_labels = sum(d["n_total"] for d in by_stage.values())
    total_live = sum(d["n_live"] for d in by_stage.values())
    total_unref = sum(d["n_unreferenced"] for d in by_stage.values())
    total_dead = sum(d["n_dead_by_gate"] for d in by_stage.values())
    print(
        f"  {total_labels} labels: {total_live} live, "
        f"{total_dead} dead-by-gate, {total_unref} unreferenced"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
