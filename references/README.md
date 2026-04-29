# references/

Frozen primary-source material the project depends on: archived
walkthroughs, captured documentation, screenshots used as evidence in
research findings.

## Standing policy

**Files in this directory are committed verbatim and are not to be
modified.** They serve as evidence for research conclusions; if any
of them changes silently, the conclusions referencing them become
unverifiable. Git has no read-only flag, so the policy is enforced
by an automated check rather than filesystem permissions.

To add a new reference:

1. Drop the file in this directory (sub-directories are fine; the
   path is recorded relative to `references/`).
2. Run `sha256sum <path> >> references/MANIFEST.sha256` to record its
   hash. Sort the manifest if you like — the checker doesn't care
   about order.
3. Commit both files in the same commit. Mention provenance in the
   commit message (where it came from, when, and the Wayback Machine
   URL where applicable).

To replace a reference (e.g. correcting a corrupt download):

1. Replace the file.
2. Update its hash in `MANIFEST.sha256`.
3. Commit, with the message clearly titled `references: replace …` so
   the diff to the manifest is visible at-a-glance.

## Verification

```bash
make verify-references
```

This runs `tools/verify_references.py`, which checks three things:

- **Hash drift** — every file in the manifest hashes to its recorded
  sha256.
- **Missing files** — every path in the manifest exists on disk.
- **Extra files** — every file in `references/` (except this README
  and the manifest itself) is recorded in the manifest.

The check exits non-zero on any violation. CI / pre-merge tooling
should run it on every change.

## Manifest format

Standard `sha256sum` output:

```
<64-hex-hash>  <path-relative-to-references/>
```

Lines beginning with `#` and blank lines are ignored.
