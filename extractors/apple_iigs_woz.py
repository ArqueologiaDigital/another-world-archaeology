"""Apple IIgs WOZ flux-image extractor — stub.

The Apple IIgs port (`apple-iigs-1992`) is preserved as two .woz
flux-level disk images by 4am in the archive.org woz-a-day
collection. WOZ2 format details are confirmed by inspection:

  disk_type:       2 (3.5")
  disk_sides:      2 (double-sided)
  cleaned:         1 (canonicalised)
  creator:         "Applesauce v1.46.1"
  largest_track:   19 (in 512-byte blocks)

Extracting AW resources requires three layers of decode work that
have not yet been implemented here:

1. **WOZ2 container**: parse INFO + TMAP + TRKS chunks; recover the
   per-track raw bit stream. (~50 lines, mostly already prototyped
   in this repo's adhoc scripts.)

2. **3.5" GCR (Apple GS double-sided 800K)**: decode the bit stream
   into 524-byte sectors (512 data + 12 tag). This is the 8-and-3
   group-code encoding from Apple's IWM controller — non-trivial
   (~200 lines), distinct from the 5.25" 6-and-2 GCR used by Apple ][
   floppies.

3. **ProDOS volume walk**: traverse the ProDOS volume directory at
   block 2 and recursively read files. Block-based, well-documented.

Useful upstream references:
- Applesauce WOZ2 spec: https://applesaucefdc.com/woz/reference2/
- ProDOS technical reference (block-level filesystem)
- The `dsktools` / `cc65` toolchain implements parts of this in C

For this archaeology project the win is identifying *where* the AW
VM resources live on the IIgs disk, then extracting the relevant
data fork. The IIgs port is engine-rewritten for the 65C816
processor (vs the 68000 used by Amiga/Mac/Atari ST), and bytecode
compatibility with the SNES port is plausible (same CPU family) but
not yet verified.
"""

from __future__ import annotations


def extract(release_meta, archive_dir, work_dir):
    raise NotImplementedError(
        "apple-iigs-2mg extractor not implemented — needs WOZ2 container "
        "parser + 3.5\" GCR decoder + ProDOS volume walker. Two .woz disk "
        "images are present in the archive; see extractors/apple_iigs_woz.py "
        "for the protocol breakdown."
    )
