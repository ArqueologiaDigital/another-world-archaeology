"""Windows XP `Pak01.pak` extractor — not yet implemented.

The Windows XP hi-res 1.1c port packs its resources inside
`Data/Pak01.pak`. The format has not been verified; it may be a
Valve-style PAK or a custom bundle. Investigation pending.
"""


def extract(release_meta, cache_dir, work_dir):
    raise NotImplementedError(
        "winxp-pak extractor not implemented — Pak01.pak format needs investigation"
    )
