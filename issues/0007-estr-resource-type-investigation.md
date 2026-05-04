---
id: 0007
title: Investigate the Mac port's 192-entry Estr resource type
status: done
tier: A
created: 2026-04-30
updated: 2026-05-04
depends_on: []
blocks: []
tags: [research, mac, estr]
---

# Context

The 1993 Mac port's resource fork has exactly **192 `Estr`
resources totalling 6,114 bytes**, byte-stable across all three
build versions (v1.0, v1.0.2, v1.0.3). 192 doesn't match the
canonical 144 AW resource indices, but is suspiciously round.
Could be event/error strings, or a different indexing scheme.

# Resolution

`Estr` is a **classic Mac OS system resource type** — "Error
string" — used to map system error codes to human-readable
messages. It is **not game-specific data**.

The 192 entries are the standard `MacErrors.h` table entries
embedded into the app binary at link time. Decoding the first
~15 confirms the format: each resource is a Pascal-style string
(length byte + Mac Roman bytes) with content like:

  - `Estr_0`: "No error"
  - `Estr_1`: "Event type not designated in system event mask"
  - `Estr_2`: "Communications error (operations timeout)"
  - `Estr_3`–`Estr_8`: SCSI Manager errors
  - `Estr_31`: "Not the requested disk"
  - `Estr_33`: "ZcbFree is negative"
  - `Estr_84`: "Happens when a menu is purged"
  - `Estr_128`: "Application or user requested abort"

These are all standard Apple-defined error strings, not AW VM
content. The 192-entry count is whatever subset of MacErrors.h
the Mac toolchain decided to include when linking the binary.

# Acceptance criteria

- [x] Diff Estr_<id>.bin across the three Mac versions to confirm
      byte-stability per resource (not just per-type aggregate).
      *(Confirmed 2026-05-04: all 192 Estr files are byte-identical
      between v1.0.2 and v1.0.3 — the only two builds in
      `work/macintosh-1993/rsrc/` that contain the binary's full
      resource fork. v1.0 itself wasn't extracted as a separate
      directory; the "1.0_1.02" combo dir is the v1.0.2 update
      applied over v1.0.)*
- [x] Decode at least 10 Estr resources to determine their content
      format. *(Done — Pascal-style ASCII/Mac-Roman strings.)*
- [x] Cross-reference Estr IDs against any AW VM error/event-code
      tables we know about. *(N/A — these are Mac OS error codes,
      not AW VM data. No cross-reference applies.)*
- [x] Document the type's purpose. *(Documented in this resolution
      block; no fresh research file needed because the finding is
      that the resource type is system-Mac, not AW-genealogical.)*

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier A item 7.

- 2026-05-04: closed.
  - All 192 Estr files byte-identical between v1.0.2 and v1.0.3
    extractions (md5 diff: 192/192 match).
  - First 15 Estr files decode cleanly as Pascal strings containing
    standard Mac OS error messages ("No error", "Not the requested
    disk", SCSI Manager errors, etc.).
  - Conclusion: `Estr` is generic Apple system data, not AW VM
    content. Marking done — the resource type's purpose is now
    understood and explicitly NOT relevant to genealogy work.
