# 02 — Why does the Amiga "presskit" dump differ from other Amiga dumps?

> ✅ **Resolved 2026-04-30.** Full answer at
> [Research finding 02](#/research/02-amiga-codewheel-protection).

## Short version of the resolution

Two Amiga dumps in our local archive are **NOT the same binary**:

- `amiga-retro-presskit` (2014 redistribution, filenames
  `AnotherWorld_DiskA_nologo_noprotec.adf`)
- `amiga-archive-org` (2020 Internet Archive upload, CC0)

They share **143 of 144 resources byte-for-byte**. Only the
**level-0 BYTECODE resource** differs, in **exactly 13 bytes**
(0.4% of its 3,544-byte payload). The diff cluster lives at
bytecode offsets `0x9fc..0xa88` — exactly where the codewheel
copy-protection check lives. The presskit's filename
`_nologo_noprotec` is the smoking gun: it's a copy-protection-
bypassed variant of the same release.

This was the project's **first concrete genealogy finding**:
intra-release diffs CAN isolate down to a single feature, in a
single resource, in a single contiguous byte range — confirming
that comparative analysis at the resource level is a viable
methodology.

See [research/02-amiga-codewheel-protection](#/research/02-amiga-codewheel-protection)
for the per-resource md5 walk + disassembly diff.

---

## Original question

The user asked early in the cataloging effort why we had two
Amiga ADF sets (presskit + archive.org) and whether they were
the same release or genuinely different. The investigation
discovered the codewheel patch.
