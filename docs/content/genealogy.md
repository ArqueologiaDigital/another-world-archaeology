# Genealogy

The goal: reconstruct a "family tree" of Another World ports — which
release inherited what from which predecessor, where new code was
introduced, and where forks diverged.

## Working hypothesis

Cross-release diffs of disassembled bytecode will reveal **blocks of
new code present in some releases but absent from older sibling
releases**. The location and nature of those blocks is the primary
genealogy signal.

Secondary signals to check as the data fills in:

- Identical-byte resources shared verbatim across releases (auto-
  detected by the extract step — see [Format coverage](#/coverage)).
- Symbol-table or string-table overlaps.
- Bug-for-bug mirroring (a workaround in release A that survives in
  release B is suggestive of B being downstream of A).

## Findings

*None yet. This page will be filled in as cross-release comparisons
become possible (currently blocked on extractors for non-DOS formats).*
