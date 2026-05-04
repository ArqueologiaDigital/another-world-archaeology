---
id: 0042
title: Build cross-release md5 index of all extracted resources
status: done
tier: D
created: 2026-04-30
updated: 2026-05-04
depends_on: []
blocks: []
tags: [infrastructure, genealogy, tooling]
---

# Context

Per the strict "compare ALL assets" policy, genealogy work needs a
fast lookup of "which releases share this resource md5". The Amiga
codewheel-protection finding (research/02) was found by hand;
automation would surface every such relationship.

# Acceptance criteria

- [x] Tool that aggregates every `manifest.json` across `work/`.
- [x] Index every per-resource md5 → list of (release, name).
- [x] Output a Markdown report listing all md5s shared across ≥2
      releases.
- [x] Run the report; commit at least one finding it surfaces.

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier D 14.
- 2026-05-04: done. `tools/cross_release_md5_index.py` aggregates
  per-resource md5s from work/ manifests + tmp/output scratch trees,
  emits `docs/cross-release-md5-index.md` (3 releases, 436 resources,
  162 distinct md5s, 135 shared across ≥2). Headline finding written
  up as `docs/content/research/13-cross-release-md5-index.md`:
  Amiga 1991 → DOS 1992 reused 117/144 resources verbatim and
  rebuilt exactly the per-stage triplet (PALETTE + BYTECODE +
  POLY_CINEMATIC) for all 9 stages.
