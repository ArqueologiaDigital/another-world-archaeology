---
id: 0028
title: Acquire Anniversary Edition iOS IPA
status: blocked
tier: C
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [acquisition, anniversary, ios]
---

# Context

iOS App Store distribution. IPA acquisition needs Apple
Configurator on macOS or a jailbroken device dump; FairPlay
encryption complicates analysis. Lower priority than PC + Android
since the engine is the same Anniversary codebase.

# Acceptance criteria

- [ ] Owner acquires the IPA.
- [ ] Decrypt FairPlay layer (or document the failure mode).
- [ ] Compare assets against PC + Android.

# Log

- 2026-04-30: opened. `blocked` on owner action + iOS tooling.
