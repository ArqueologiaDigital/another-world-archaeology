# Forward plan

The forward plan is now maintained as the [issue tracker](#) under
`issues/` in the repo, generated and validated by
[`tools/issues.py`](#).

> **Use the tracker, not this page.** Open `issues/README.md` for
> the current status board (auto-generated, kept in sync). The
> per-issue files at `issues/<NNNN>-<slug>.md` hold the
> Context / Acceptance criteria / Log for each item.

## Why this redirect exists

This page used to be a hand-maintained ranked list — convenient
narrative, but easy to drift out of sync with reality. The issue
tracker replaces it because:

- **One source of truth.** Each item lives in exactly one file;
  status changes are atomic git commits.
- **Stable IDs.** `#0042` is forever; cross-references from
  research findings, commit messages, and other docs don't
  break when items move around.
- **Schema validation.** `tools/issues.py validate` catches
  broken references and missing fields before a commit lands.
- **Status semantics.** `open` / `in-progress` / `blocked` /
  `done` / `wontfix` is enforced; the index reports counts per
  tier and per status.

See [`issues/SCHEMA.md`](#) for the schema and policies.

## Where things moved

The tier-A / tier-B / tier-C / tier-D structure is preserved in
the issue tracker via the `tier:` frontmatter field. The
auto-generated index groups open work by tier, so it reads the
same way.

A few items that lived in this document but never had explicit
tracking now have proper issue numbers:

- The 9 "side findings flagged for parallel slugs" from
  [`catalog.md`](#/catalog) → issues `#0016`–`#0024`.
- "Releases we haven't found yet" → issues `#0036`–`#0039`.
- The 11 anniversary console acquisitions → issues
  `#0025`–`#0035`.
- "Open lines of inquiry" from [`genealogy.md`](#/genealogy) →
  matched against existing issue IDs (each open question now
  links to its tracking issue).

## Adding new work

Don't add to this page. Run:

```
python3 tools/issues.py new --title "Concise imperative title" \
                            --tier A \
                            --tags "extractor, mac, research"
```

Then fill in the body's Context / Acceptance criteria / Log
sections, run `tools/issues.py index` to refresh
`issues/README.md`, and commit.

## Changelog

- **2026-04-30** — page rewritten as a redirect. The tier-ranked
  content moved into the issue tracker as 42 individual issues
  (40 open, 2 closed). See `issues/README.md` for the new home.
