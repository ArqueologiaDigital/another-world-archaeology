---
id: 0078
title: match_arms.py was abstracting CINEMATIC operands, causing false matches
status: done
tier: D
created: 2026-05-03
updated: 2026-05-03
tags: [tooling, rename, matcher]
closes_pr: b51ae35
---

# Context

`tools/match_arms.py` is used to propagate semantic-rename results
from one arm (e.g. cart) to another (e.g. dos, amiga) by abstracted
symbolic body comparison. The abstraction step replaces label-like
identifiers in instruction operands with a placeholder so that two
routines whose only difference is the per-arm hex address of branch
targets are recognized as equivalent.

The original implementation abstracted **every** ALL_CAPS_NAMES match
(except a tiny allow-list of var aliases). This was too aggressive:
it also replaced operand fields that encode actual byte values via
`;@raw=`, e.g. `CINEMATIC_086` and `CINEMATIC_087` would both become
`_LABEL_`. Two routines that differ only in CIN index — e.g.
`DRAW_CIN_086_087_SEQ` and `DRAW_CIN_075_076_SEQ` — were therefore
falsely conflated.

This surfaced in ENDING round 3: the matcher reported amiga
`LABEL_046F` as matching both routines, which would have applied the
wrong name had we not noticed.

# Acceptance criteria

- [x] Only LABEL_<HEX> and JUNK__<HEX> are abstracted.
- [x] Named operands (CINEMATIC_*, COMMON_VIDEO_*, named routines)
      preserved verbatim — they encode bytes that legitimately differ.
- [x] Existing matches still applied for stages already cross-renamed.

# Log

- 2026-05-03: opened, fixed, and closed in commit b51ae35.
