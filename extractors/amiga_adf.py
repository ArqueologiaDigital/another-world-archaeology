"""Amiga ADF disk-image extractor — not yet implemented.

The Amiga retro press kit ships two ADF floppy images
(`AnotherWorld_DiskA_nologo_noprotec.adf`,
`AnotherWorld_DiskB_nologo_noprotec.adf`). The disks themselves are
standard OFS/FFS so a generic ADF reader will yield the contained
files; the in-disk layout of Another World's banks then needs its own
parser (likely close to but not identical to the DOS bank format).
"""


def extract(release_meta, cache_dir, work_dir):
    raise NotImplementedError(
        "amiga-adf extractor not implemented — needs ADF reader + Amiga bank parser"
    )
