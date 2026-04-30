---
id: 0001
title: Mac resource-fork walker for 1993 StuffIt forks
status: done
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [extractor, mac, rust]
---

# Context

The 1993 Mac port's StuffIt archive bundles three application
builds (v1.0 / v1.0.2 / v1.0.3) plus two updaters, each with a
~525 KB resource fork containing 68k engine code + Mac UI
resources. Per-resource (TYPE+ID-keyed) extraction was needed
before any cross-version analysis could happen.

# Acceptance criteria

- [x] AWVM_Tools binary `mac-rsrc-walk` parses Mac resource forks
      via the upstream `macbinary` crate.
- [x] Wired into `extractors/mac_classic.py` as a stage-2 step
      after `mac-stuffit-extract`.
- [x] End-to-end produces per-resource files named
      `<TYPE>_<ID>[_<safe_name>].bin` for each .rsrc input.

# Log

- 2026-04-30: opened, implemented, closed. AWVM_Tools commit 808a361.
  Yields 1697 per-resource blobs across 50 forks for the AW Mac
  fixture. See research finding #04.
