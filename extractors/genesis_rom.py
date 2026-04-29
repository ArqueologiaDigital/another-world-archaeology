"""SEGA Genesis cartridge ROM extractor — not yet implemented.

The European Genesis release is a bare cartridge ROM with a different
memory map from SNES. As with SNES, the bank/offset table needs to be
located by reverse engineering before any extraction is possible.
"""


def extract(release_meta, cache_dir, work_dir):
    raise NotImplementedError(
        "genesis-rom extractor not implemented — ROM layout needs reverse engineering"
    )
