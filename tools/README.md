# tools/

External tool dependencies used by the extraction and analysis pipeline.

Tools listed here are **not vendored** in this repo. Each `*.lock` file
pins an external repository at a specific commit. The `make tools`
target clones (or fast-forwards) each one as a **sibling directory** of
this repo, then checks out the pinned commit.

```
compartilhado/
├── another-world-archaeology/    <- this repo
└── AnotherWorld_VMTools/         <- sibling clone
```

## Change-review rule

The owner of this project is also the upstream maintainer of
`AnotherWorld_VMTools`. **Do not modify the sibling clone or propose
upstream changes without surfacing the proposal first.** If you find a
bug or believe a feature would help the research, write up the
diagnosis or proposal here in this repo (e.g. under
`docs/content/research/`) and wait for owner review before touching
the sibling repo.

## Lock file schema

```json
{
  "name":                    "Human-readable tool name",
  "url":                     "git clone URL",
  "pinned_commit":           "Full SHA-1 hash",
  "pinned_date":             "YYYY-MM-DD",
  "pinned_subject":          "Subject line of the pinned commit",
  "expected_sibling_path":   "Path relative to this repo's parent",
  "change_review_required":  true,
  "purpose":                 "Why this repo depends on the tool",
  "depends_on":              ["pip-style requirement strings"]
}
```

## Currently pinned

- [`AWVM_Tools.lock`](AWVM_Tools.lock) — bytecode disassembler/assembler.
