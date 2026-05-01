# 03 — How can we get the files for the other 21 releases?

> ✅ **Resolved 2026-04-30.** Full answer at
> [Research finding 03](#/research/03-tier1-acquisition-sweep).

## Short version of the resolution

When the question was asked, the catalog tracked 29 documented
release variants but only 8 were locally archived. The investigation:

1. Categorized the 21 missing releases into three acquisition tiers
   (publicly redistributable / commercial digital / physical-only)
   in [acquisition_plan.md](#/acquisition_plan).
2. Executed Tier 1 (publicly redistributable downloads —
   classic-platform romdumps + fan ports).

**Outcome**: coverage went from **8/29 → 14/29 archived**. 12 of
14 archived fixtures now extract end-to-end via
`python3 extract.py --slug X`; 2 are registered as informative
stubs awaiting protocol work.

New fixtures fetched (6): Apple IIgs, Macintosh 1993, Nintendo DS
2011 (alekmaul), Symbian (anotherworld-generic), GBA (Foxy 2004),
3DO 1993.

Additional registered stubs: Apple II demake (Vince Weaver
2019). Plus Atari ST 1991 (Pasti `.stx` floppy images), Genesis-EU
1993 (cartridge ROM), and SNES-EU 1992 (cartridge ROM) had
already been archived.

See [research/03-tier1-acquisition-sweep](#/research/03-tier1-acquisition-sweep)
for the per-fixture provenance + checksum table.

The remaining 15 releases are tracked individually as Tier B/C
issues in the [issue tracker](#/issues).

---

## Original question (verbatim)

> how can we get the files for the other 21 releases?
