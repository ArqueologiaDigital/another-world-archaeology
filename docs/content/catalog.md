# Release catalog

The five releases currently tracked in `metadata.json`. The package
md5sum is the canonical identifier; the slug is the human-readable
handle used in paths and reports.

| Slug | Release | Format | Package md5 | Source |
|---|---|---|---|---|
| `dos` | MSDOS | `dos-bank` | `076117919d1dca51e486f33b8f7817e3` | classicgames.me |
| `winxp-1.1c` | WindowsXP-hires-1.1c | `winxp-pak` | `135375d23845898dd91ad5d6a6fc35fb` | anotherworld.fr |
| `amiga-retro-presskit` | Amiga retro press kit | `amiga-adf` | `5dca377e0e1506d5cf83317b1495f3e8` | thedigitalounge.com |
| `snes-eu` | SNES (Europe) | `snes-rom` | `f65e3d6efe35900c0015bcb751ee567e` | wowroms.com |
| `genesis-eu` | SEGA Genesis (Europe) | `genesis-rom` | *(not yet recorded)* | wowroms.com |

Future targets (not yet cataloged): Atari ST, Apple IIgs, 3DO,
Jaguar, GBA, iOS, Android, the 20th Anniversary HD edition, and the
Fabien Sanglard C++ rewrite.

## Provenance

Every entry in `metadata.json` carries a `download` URL,
`download_date`, and (eventually) a `wayback_url` + `wayback_date`
pair pointing to an Internet Archive snapshot. Wayback fields are
currently `null` and will be populated by an upcoming pipeline step
that archives source URLs to the Wayback Machine.
