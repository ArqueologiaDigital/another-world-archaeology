---
id: 0096
title: verify-resources-all: gba_usa.resources.json manifest is stale (bytecode.rom md5 + cinematic.rom extra)
status: open
tier: C
created: 2026-05-09
updated: 2026-05-09
depends_on: []
blocks: []
tags: [reconstruction, testing, verify, resources, manifest]
---

# Context

`make verify-resources-all` (in source-reconstruction) fails on
gba_usa with:

    port=gba_usa, manifest=gba_usa.resources.json
      expected resources: 4
      found  resources: 5
      MISMATCH  romset/bytecode.rom  exp=eaa9835c57a7 act=de7ffef613b7
      EXTRA     romset/cinematic.rom  (9570d2e8fc48)
      OK=3  mismatch=1  missing=0  extra=1

The romset files in `tmp/output/gba_usa/romset/` are dated 2026-05-01,
predating this work. Surfaced while regenerating the disasm tree for
#0094.

Two issues with the manifest at
`source-reconstruction/releases/gba_usa.resources.json`:

1. **bytecode.rom md5 mismatch.** Manifest expects `eaa9835c57a7…`;
   actual file is `de7ffef613b7…`. The current awvm-disasm produces
   the `de7ffef…` hash; the manifest predates whatever change moved
   it from `eaa9835…`.

2. **cinematic.rom is "extra".** Current cartridge_rom.py extractor
   writes `cinematic.rom` to the romset (md5 `9570d2e8fc48…`), but
   the manifest doesn't list it. So either the manifest is missing
   this resource (forgot to include it when generated) or the
   extractor was updated to emit cinematic.rom after the manifest
   was last regenerated.

# Acceptance criteria

- [ ] Decide canonical action: regenerate the manifest with
      `verify_resources.py --port gba_usa --bootstrap` after
      confirming the current extractor output is correct, OR fix
      the extractor / awvm-disasm to match the recorded manifest
      (only if manifest is the trusted source of truth).
- [ ] Same audit for snes_eu / genesis_europe / msdos / amiga
      manifests — they happen to match today, but if the
      bytecode.rom format changed for gba it may have changed for
      others too.
- [ ] `make verify-resources-all` (and therefore the full
      `make test-full` chain) passes clean.

# Log

- 2026-05-09: opened. Surfaced while extending
  `tools/regen_disasm.py` with cart-format support (#0094). The
  regen path itself is fine (29/29 bytecode round-trip); only the
  resource md5 audit fails because the gba_usa manifest is older
  than the current awvm-disasm cartridge_rom output.
