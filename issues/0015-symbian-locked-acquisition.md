---
id: 0015
title: Acquire the locked Symbian variant matching md5 fe4742b67415eb16ef340548573538b8
status: open
tier: C
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [acquisition, symbian]
---

# Context

The locked Symbian variant has its md5 published in AWVM_Tools'
`symbian2romset.py` comments
(`fe4742b67415eb16ef340548573538b8`), but no URL is recorded — we
need to find a source. The locked variant is what AWVM_Tools'
`symbian_demo` pipeline targets directly; the generic variant we
already have (#0011) needs adaptation.

# Acceptance criteria

- [ ] Locate a download URL for the file matching md5
      fe4742b67415eb16ef340548573538b8.
- [ ] Archive into `another-world-archive/symbian-locked-anotherworld/`.
- [ ] Verify with `python3 extract.py --slug symbian-locked-anotherworld`.

# Log

- 2026-04-30: opened. Note metadata recorded for years but URL
  hunt has been deferred.
