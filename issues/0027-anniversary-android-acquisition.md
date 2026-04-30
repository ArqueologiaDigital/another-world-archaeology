---
id: 0027
title: Acquire Anniversary Edition Android APK
status: blocked
tier: C
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [acquisition, anniversary, android]
---

# Context

Android Anniversary Edition is on Google Play. APK can be pulled
via `adb backup` (on the owner's device) or downloaded from
APKMirror (community archive). APK = ZIP containing
`assets/` + `lib/` + `classes.dex` etc.

# Acceptance criteria

- [ ] Owner extracts the APK.
- [ ] Archive the APK.
- [ ] Unpack + compare assets against PC variant.

# Log

- 2026-04-30: opened. `blocked` on owner action.
