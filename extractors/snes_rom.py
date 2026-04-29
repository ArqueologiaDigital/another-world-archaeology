"""SNES cartridge ROM extractor — not yet implemented.

The European SNES release is a bare cartridge ROM. There is no
standard layout for resources within the ROM — the bank/offset table
needs to be located by reverse engineering before any extraction is
possible.
"""


def extract(release_meta, cache_dir, work_dir):
    raise NotImplementedError(
        "snes-rom extractor not implemented — ROM layout needs reverse engineering"
    )
