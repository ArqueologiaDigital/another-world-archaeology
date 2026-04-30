---
id: 0041
title: Generate per-release pages in the static doc site from metadata.json
status: open
tier: D
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [infrastructure, docs]
---

# Context

`docs/content/catalog.md` is currently one big page with all 29
releases. As the project grows, individual releases need their
own pages — each can carry its own findings log, per-release
md5 manifests, and links to issues touching that release.

# Acceptance criteria

- [ ] Extend `tools/gen_docs_data.py` to emit per-slug entries.
- [ ] Add a `Release/<slug>` route to the static viewer.
- [ ] Link each catalog entry to its dedicated page.
- [ ] Each release page lists open issues filtered by tag /
      release.

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier D 13.
