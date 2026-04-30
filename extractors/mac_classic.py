"""Macintosh classic (StuffIt .sit) extractor — stub.

The 1993 Macintosh release (`macintosh-1993`) is preserved as a
StuffIt archive (`out_of_this_world.sit`, 3,739,614 bytes) sourced
from Macintosh Garden. It bundles three game versions (1.0, 1.2,
1.3) plus updaters as a single .sit blob.

Inside the .sit are MacBinary or AppleDouble files preserving the
classic Mac resource fork — the AW VM resources and engine code
live in the resource fork of the application binary, NOT in the
data fork (this is the inverse of every other AW release format
we've seen).

Extraction blockers as of 2026-04-30:

- **StuffIt format**: proprietary; partial open-source decoders
  exist (libunarchiver / The Unarchiver / `unar` CLI) but neither
  the system `unar` package nor a Python binding (`libarchive`,
  `unar`) is installed in this environment. Adding either would
  require root access we don't have.

- **Resource-fork extraction**: once the .sit is unpacked, the
  resulting MacBinary files need to be parsed to access the
  resource fork. The `rforks` Python package handles this; not
  installed.

- **AW resource layout in 68k Mac binary**: unknown. The Mac port
  is Motorola 68k like the Amiga and Atari ST releases, but the
  resource format inside the resource fork has not been reverse-
  engineered. A first-pass investigation would compare against the
  Atari ST bank format (extractors/atari_st_pasti.py) — the engine
  code is likely the same generation.

Useful upstream references:
- The Unarchiver source: https://github.com/MacPaw/XADMaster
- StuffIt 5.x format (the .sit version we have is StuffIt 5,
  per the `file(1)` output)
- MacBinary III spec
"""

from __future__ import annotations


def extract(release_meta, archive_dir, work_dir):
    raise NotImplementedError(
        "mac-classic extractor not implemented — needs StuffIt .sit "
        "decompressor + MacBinary parser + 68k Mac resource-fork reader. "
        "out_of_this_world.sit is in the archive; see "
        "extractors/mac_classic.py for the protocol breakdown."
    )
