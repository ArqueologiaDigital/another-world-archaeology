---
id: 0042
title: Build cross-release md5 index of all extracted resources
status: open
tier: D
created: 2026-04-30
updated: 2026-04-30
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

- [ ] Tool that aggregates every `manifest.json` across `work/`.
- [ ] Index every per-resource md5 → list of (release, name).
- [ ] Output a Markdown report listing all md5s shared across ≥2
      releases.
- [ ] Run the report; commit at least one finding it surfaces.

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier D 14.
