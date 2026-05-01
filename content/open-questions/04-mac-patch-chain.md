# 04 — What changed across the 1993 Mac port's three patches (v1.0 → v1.0.2 → v1.0.3)?

> ✅ **Resolved 2026-04-30.** Full answer at
> [Research finding 04](#/research/04-mac-port-patch-chain).

## Short version of the resolution

The 1993 Macintosh release ships in a single StuffIt archive
bundling three close-versioned application builds (v1.0, v1.0.2,
v1.0.3) plus two updaters — a uniquely dense genealogy dataset.

After implementing the two-stage Mac extraction pipeline
(`mac-stuffit-extract` → `mac-rsrc-walk`), per-segment md5 of
the seven `CODE` segments across the three builds revealed two
distinct patches:

- **v1.0 → v1.0.2** = focused 3-segment fix. CODE 1, 4, 6
  byte-identical between v1.0 and v1.0.2; only CODE 2, 3, 5
  changed (and CODE 0, the segment-loader jump table, regenerates).
- **v1.0.2 → v1.0.3** = structural reorganisation. Every
  CODE-segment hash changed, but the v1.0/v1.0.2 hash
  `cdf752c16d3b…` reappears as v1.0.3's CODE 5 (renamed
  `Histories _ Docs`) with a new v1.0.3 CODE 4 named
  `MacTraps2_ANSI`. Almost certainly a Symantec C runtime
  upgrade that shifted all later segments by one.

The `OOTW` custom 4cc resource even carries a human-readable
copyright string that changes per version: v1.0 = `©1992
MacPlay.`, v1.0.2 = `©1992-3 MacPlay and Delphine Software.`,
v1.0.3 reverts to `©1992 MacPlay.` (the v1.0.3 string is more
likely the *correct* one, with v1.0.2 being a brief mistake).

See [research/04-mac-port-patch-chain](#/research/04-mac-port-patch-chain)
for the full per-segment table.

---

## Original question

Derived from the user's request to "try the Mac StuffIt route"
during the Tier 1 acquisition sweep. Once extraction worked, the
multi-version archive was discovered to bundle three full builds
plus two updaters — far richer genealogy material than expected,
warranting its own dedicated finding.
