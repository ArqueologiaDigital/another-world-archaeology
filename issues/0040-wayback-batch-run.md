---
id: 0040
title: Submit references/sources.csv to Wayback Save Page Now in batch
status: open
tier: D
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [infrastructure, wayback, provenance]
---

# Context

`references/sources.csv` has 144+ rows, ~half lacking a Wayback
snapshot. Wayback's Save Page Now has a Google Sheets importer
that handles batch submission. Once URLs are snapshotted, populate
the `wayback` column.

# Acceptance criteria

- [ ] Export sources.csv to a Google Sheet.
- [ ] Run the Save Page Now importer.
- [ ] Pull back snapshot URLs and populate the csv's `wayback`
      column.
- [ ] Commit updated csv.

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier D 12.
