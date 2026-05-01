# 01 — How is the gun's ammo / shot quota tracked in the bytecode?

> ✅ **Resolved 2026-04-30.** Full answer at
> [Research finding 01](#/research/01-gun-ammo).

## Short version of the resolution

- Gun energy is **var `0x06`**.
- Costs: **−1** tap shot, **−10** regular shot, **−50** superblast
  (or **−100** in level 3 / Prison Escape).
- **Shield is free.**
- One recharge station total, in level 4, **clamps to 1000**.
- Per-level entry: 199 (Prison), 990 (Caves), 990 (Final).
- Mechanics are **byte-for-byte identical** across DOS / Amiga /
  Genesis-EU.

See [research/01-gun-ammo](#/research/01-gun-ammo) for full
disassembly references and bytecode snippets.

---

## Original question (verbatim)

From `initial_research_plan.txt`:

> The walkthrough mentions: "the gun doesn't have unlimited ammo"
> I also know that in some places there are charging stations for the gun.
> But it is not clear to me how the gun is handled in the code. Is there a counter? What does it count? Simple shots, shield-shots, or mega-blast shots? If there's a usage quota, how can we precisely describe it?
