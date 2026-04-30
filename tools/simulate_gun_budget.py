#!/usr/bin/env python3
"""Illustrate the gun-energy quota mechanics from research finding #01.

Generates a Markdown report showing how many of each weapon mode a
player can fire from a given starting energy. Output is meant to be
read on its own, or appended verbatim to
`docs/content/research/01-gun-ammo.md` as an appendix.

The numbers are derived directly from the disassembled DOS bytecode
constants documented in research/01:

    tap shot       costs 1 energy
    regular shot   costs 10 energy
    superblast     costs 50 energy in levels 4 and 6
    superblast     costs 100 energy in level 3 (Prison) — anomaly!
    shield         is free (no decrement)
    recharge       clamps energy to 1000 (mov, not add)
    recharge guard fires only when energy <= 990

Per-level entry energy:

    level 3 (Prison Escape):  199
    level 4 (Gas Tunnels):    990
    level 6 (Final Action):   990

In level 4 there are two recharge zones sharing the same handler,
so the level's effective burnable budget can reach 990 + 2 * 1000 =
2990 if the player times both visits with energy at zero.

Usage:
    python3 tools/simulate_gun_budget.py            # print to stdout
    python3 tools/simulate_gun_budget.py --markdown # same (default)
"""

from __future__ import annotations

import argparse
import sys

# Costs per level, derived from the disassembly (see research/01).
COST_TAP = 1
COST_REGULAR = 10
COST_SUPERBLAST_DEFAULT = 50
COST_SUPERBLAST_PRISON = 100

# Per-level entry energy.
ENTRY_ENERGY = {
    3: ("Level 3 — Prison Escape (the level where you find the gun)", 199, COST_SUPERBLAST_PRISON),
    4: ("Level 4 — Gas Tunnels (the level with both recharge zones)", 990, COST_SUPERBLAST_DEFAULT),
    6: ("Level 6 — Final Action", 990, COST_SUPERBLAST_DEFAULT),
}

# The energy after hitting a recharge station — the same in every level.
RECHARGE_TO = 1000


def _bar(n: int, width: int = 40, max_n: int = 1000) -> str:
    """Crude ASCII bar scaled to width. Hits the cap when n == max_n."""
    if max_n <= 0:
        return ""
    filled = max(1, min(width, int(round(n / max_n * width)))) if n > 0 else 0
    return "█" * filled


def pure_action_capacity(starting: int, sup_cost: int) -> dict[str, int]:
    return {
        "tap":         starting // COST_TAP,
        "regular":     starting // COST_REGULAR,
        "superblast":  starting // sup_cost,
    }


def md_pure_actions_table(starting: int, sup_cost: int) -> list[str]:
    caps = pure_action_capacity(starting, sup_cost)
    rows = [
        ("Tap shot",        COST_TAP,    caps["tap"]),
        ("Regular shot",    COST_REGULAR, caps["regular"]),
        ("Superblast",      sup_cost,    caps["superblast"]),
        ("Shield (free)",   0,           "∞"),
    ]
    out = [
        "| Mode | Cost | Pure-mode capacity |",
        "|---|---|---|",
    ]
    for name, cost, count in rows:
        out.append(f"| {name} | {cost} | {count} |")
    return out


def mixed_strategy_examples(energy: int, sup_cost: int) -> list[tuple[str, int, int, int, int]]:
    """Return a list of (label, S, R, T, used) for illustrative mixes
    that just barely stay inside `energy`."""
    examples: list[tuple[str, int, int, int, int]] = []

    def add(label: str, s: int, r: int, t: int):
        used = s * sup_cost + r * COST_REGULAR + t * COST_TAP
        if used <= energy:
            examples.append((label, s, r, t, used))

    add("Pure tap (panic-fire)",        0, 0, energy // COST_TAP)
    add("Pure regular",                 0, energy // COST_REGULAR, 0)
    add("Pure superblast",              energy // sup_cost, 0, 0)
    # Cautious: half regulars, the rest taps
    half_regs = (energy // 2) // COST_REGULAR
    add("Cautious (no superblast)",     0, half_regs, energy - half_regs * COST_REGULAR)
    # Balanced
    s = max(1, energy // (sup_cost * 4))
    rem = energy - s * sup_cost
    r = rem // (COST_REGULAR * 2)
    rem -= r * COST_REGULAR
    add("Balanced 25/25/50",            s, r, rem)
    # Heavy combat
    s = max(1, energy // (sup_cost * 2))
    rem = energy - s * sup_cost
    r = rem // (COST_REGULAR * 2)
    rem -= r * COST_REGULAR
    add("Heavy combat (~50% energy on superblasts)", s, r, rem)
    # Sniper
    s = energy // (sup_cost * 4)
    rem = energy - s * sup_cost
    r = rem // COST_REGULAR
    add("Sniper (no taps)",             s, r, 0)
    return examples


def md_mixed_strategy_table(energy: int, sup_cost: int) -> list[str]:
    rows = mixed_strategy_examples(energy, sup_cost)
    out = [
        f"| Strategy | Superblasts (×{sup_cost}) | Regular (×{COST_REGULAR}) | Tap (×{COST_TAP}) | Total spent |",
        "|---|---:|---:|---:|---:|",
    ]
    for label, s, r, t, used in rows:
        out.append(f"| {label} | {s} | {r} | {t} | {used} / {energy} |")
    return out


def md_level_block(level: int) -> list[str]:
    name, entry_e, sup_cost = ENTRY_ENERGY[level]
    out: list[str] = []
    out.append(f"### {name}")
    out.append("")
    out.append(f"- Entry energy: **{entry_e}**")
    out.append(f"- Superblast cost in this level: **{sup_cost}**")
    if level == 4:
        out.append(f"- Recharge zones: **2** (both clamp to {RECHARGE_TO})")
        out.append(f"- Theoretical maximum burnable energy if both zones are visited at energy = 0: **{entry_e + 2 * RECHARGE_TO}**")
    else:
        out.append(f"- Recharge zones: **0** in this level")
    out.append("")

    out.append("**At level entry (no recharge yet):**")
    out.append("")
    out.extend(md_pure_actions_table(entry_e, sup_cost))
    out.append("")
    out.append("**Mixed-strategy budgets at level entry:**")
    out.append("")
    out.extend(md_mixed_strategy_table(entry_e, sup_cost))
    out.append("")

    if level == 4:
        out.append("**Immediately after a recharge (energy = 1000):**")
        out.append("")
        out.extend(md_pure_actions_table(RECHARGE_TO, sup_cost))
        out.append("")
        out.append("**Mixed-strategy budgets after recharge:**")
        out.append("")
        out.extend(md_mixed_strategy_table(RECHARGE_TO, sup_cost))
        out.append("")
    return out


def md_visual_capacity_chart() -> list[str]:
    """An at-a-glance bar chart of pure-mode capacity at full charge."""
    out = [
        "After a full recharge in level 4 or 6 (energy = 1000, superblast cost = 50):",
        "",
        "```",
    ]
    full = 1000
    for label, cost in [("Tap shot     ", COST_TAP),
                        ("Regular shot ", COST_REGULAR),
                        ("Superblast   ", COST_SUPERBLAST_DEFAULT)]:
        n = full // cost
        # Scale the bar by *count*, not energy: tap=1000 gets a full bar;
        # superblast=20 gets a tiny bar — visual emphasis on how cheap
        # taps are vs superblasts.
        bar = _bar(n, width=40, max_n=full)
        out.append(f"  {label} {bar:<40} {n:>5}")
    out += [
        "```",
        "",
        "And under the level-3 anomaly (entry energy 199, superblast cost 100):",
        "",
        "```",
    ]
    e = 199
    for label, cost in [("Tap shot     ", COST_TAP),
                        ("Regular shot ", COST_REGULAR),
                        ("Superblast   ", COST_SUPERBLAST_PRISON)]:
        n = e // cost
        bar = _bar(n, width=40, max_n=e)
        out.append(f"  {label} {bar:<40} {n:>5}")
    out.append("```")
    return out


def md_full_report() -> str:
    out: list[str] = []
    out.append("# Gun energy budget — illustrative simulations")
    out.append("")
    out.append("Generated by `tools/simulate_gun_budget.py` from the cost")
    out.append("constants documented in [research finding 01](#/research/01-gun-ammo).")
    out.append("All numbers are derived from the disassembled DOS bytecode and")
    out.append("are byte-stable across DOS / Amiga / Genesis-EU.")
    out.append("")
    out.append("## At-a-glance pure-mode capacity")
    out.append("")
    out.extend(md_visual_capacity_chart())
    out.append("")
    out.append("## Per-level breakdown")
    out.append("")
    for level in (3, 4, 6):
        out.extend(md_level_block(level))
    out.append("## Anomaly: level 3 superblast costs *2×* the others")
    out.append("")
    out.append("In every other shooting level (4 and 6) a superblast costs 50.")
    out.append("In the Prison Escape (level 3) it costs **100** — the level where")
    out.append("Lester just acquired the gun and starts with only 199 energy.")
    out.append("That asymmetry means **the player can afford only 1 superblast**")
    out.append("in the entire Prison level (with 99 energy left over — enough for")
    out.append("9 regular shots, or 99 taps, but **not** another superblast).")
    out.append("")
    out.append("This irregularity persists byte-for-byte across DOS, Amiga, and")
    out.append("Genesis-EU — strong evidence that the porters worked from a")
    out.append("snapshot of the bytecode rather than re-deriving balance numbers.")
    out.append("")
    out.append("## Recharge multiplier in level 4")
    out.append("")
    out.append("Level 4 is the only level with recharge zones — and there are two")
    out.append("of them, sharing one handler (see")
    out.append("[issue #0006](#/issues/0006-locate-second-recharge-zone-scene)).")
    out.append("The handler is a **clamp to 1000**, not an additive top-up:")
    out.append("hitting a recharge sets the meter to 1000 regardless of where")
    out.append("it was. So total burnable energy in level 4 ranges from **990**")
    out.append("(don't visit either recharge) to **2990** (visit both at zero")
    out.append("energy). At 2990, that's:")
    out.append("")
    out.append("- 2990 tap shots, or")
    out.append("- 299 regular shots, or")
    out.append("- 59 superblasts (with 40 energy left — 4 regular shots or 40 taps).")
    out.append("")
    return "\n".join(out)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    p.add_argument("--markdown", action="store_true", default=True)
    p.parse_args()
    sys.stdout.write(md_full_report())


if __name__ == "__main__":
    main()
