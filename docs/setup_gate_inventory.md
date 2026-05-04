# Setup-then-overwrite gate inventory

Static scan for the AW VM gate pattern — two `setup channel=N` instructions in the same straight-line block, where the second's address overrides the first's. The first's target is then unreachable under runtime semantics even though static control-flow has an edge to it. See research/05 (beetle in the lake) for the canonical example.

First-pass detector: scans only same-block consecutive setups separated by no `break`/`ret`/`killChannel`/`bankSwitch`/`freezeChannel`/`jmp`/label/`;@if` boundary. A complete reachability oracle (#0058) needs additional control-flow analysis.

**Total gates detected: 22.**

## Category breakdown (cross-branch)

Each gate is classified by what it's gating. Killer detection is body-aware: any label whose body is a
single `killChannel` instruction counts as a killer
regardless of name.

- **silencer** — substantive routine → killer.
  The surviving address kills the channel; the gated
  routine never runs. Likely deliberate cut-content
  (research/05).
- **reschedule** — killer → substantive.
  The gated kill-self gets replaced by a real routine —
  common idiom for tearing down and starting fresh on
  the same channel.
- **swap** — substantive → substantive. Both are real
  game logic; only the second runs (the first was a
  changed mind, possibly a placeholder cinematic).

| Category | Count |
| --- | ---: |
| `silencer` | 12 |
| `reschedule` | 3 |
| `swap` | 7 |

## `cartridge_1992`

8 gates across 3 stages.

| Stage | Channel | Gated → Surviving | Category | Source |
| --- | :---: | --- | :---: | --- |
| CAPSULE | `0x14` | `LABEL_9A9E` → `LABEL_BE04` | `swap` | src/levels/cartridge_1992/CAPSULE.asm:1500-1501 |
| CAPSULE | `0x16` | `LABEL_9A8A` → `LABEL_B74A` | `swap` | src/levels/cartridge_1992/CAPSULE.asm:1502-1503 |
| CAPSULE | `0x18` | `LABEL_5C5B` → `KILL_CHAN_AT_59A3` | `silencer` | src/levels/cartridge_1992/CAPSULE.asm:16798-16799 |
| CAPSULE | `0x2E` | `KILL_CHAN_AT_59A3` → `LABEL_2A6E` | `reschedule` | src/levels/cartridge_1992/CAPSULE.asm:17938-17939 |
| CAVES | `0x14` | `LABEL_39E3` → `LABEL_EA2E` | `swap` | src/levels/cartridge_1992/CAVES.asm:1296-1298 |
| CAVES | `0x15` | `LABEL_3A26` → `KILL_CHAN_AT_7830` | `silencer` | src/levels/cartridge_1992/CAVES.asm:1297-1299 |
| LAKE | `0x09` | `BEETLE_INIT_POS_THEN_WALK_LEFT` → `KILL_CHANNEL_ROUTINE` | `silencer` | src/levels/cartridge_1992/LAKE.asm:1244-1245 |
| LAKE | `0x2E` | `BEETLE_KICK_DETECTOR` → `WAIT_FOR_BEETLE_OFFSCREEN_THEN_KILL` | `silencer` | src/levels/cartridge_1992/LAKE.asm:1246-1247 |

## `chahi_amiga_1991`

4 gates across 3 stages.

| Stage | Channel | Gated → Surviving | Category | Source |
| --- | :---: | --- | :---: | --- |
| CAPSULE | `0x2E` | `KILL_CHAN_AT_59A3` → `LABEL_17D8` | `reschedule` | src/levels/chahi_amiga_1991/CAPSULE.asm:12564-12565 |
| CAVES | `0x14` | `LABEL_37D0` → `LABEL_E41E` | `swap` | src/levels/chahi_amiga_1991/CAVES.asm:1262-1264 |
| CAVES | `0x15` | `LABEL_3813` → `KILL_CHAN_AT_7830` | `silencer` | src/levels/chahi_amiga_1991/CAVES.asm:1263-1265 |
| LAKE | `0x2E` | `BEETLE_KICK_DETECTOR` → `WAIT_FOR_BEETLE_OFFSCREEN_THEN_KILL` | `silencer` | src/levels/chahi_amiga_1991/LAKE.asm:1151-1152 |

## `dos_1992`

8 gates across 3 stages.

| Stage | Channel | Gated → Surviving | Category | Source |
| --- | :---: | --- | :---: | --- |
| CAPSULE | `0x14` | `LABEL_9A35` → `LABEL_BD20` | `swap` | src/levels/dos_1992/CAPSULE.asm:1472-1473 |
| CAPSULE | `0x16` | `LABEL_9A21` → `LABEL_B666` | `swap` | src/levels/dos_1992/CAPSULE.asm:1474-1475 |
| CAPSULE | `0x18` | `LABEL_5C58` → `KILL_CHAN_AT_59A3` | `silencer` | src/levels/dos_1992/CAPSULE.asm:16819-16820 |
| CAPSULE | `0x2E` | `KILL_CHAN_AT_59A3` → `LABEL_28F7` | `reschedule` | src/levels/dos_1992/CAPSULE.asm:17929-17930 |
| CAVES | `0x14` | `LABEL_39F9` → `LABEL_E9A5` | `swap` | src/levels/dos_1992/CAVES.asm:1309-1311 |
| CAVES | `0x15` | `LABEL_3A3C` → `KILL_CHAN_AT_7830` | `silencer` | src/levels/dos_1992/CAVES.asm:1310-1312 |
| LAKE | `0x09` | `BEETLE_INIT_POS_THEN_WALK_LEFT` → `KILL_CHANNEL_ROUTINE` | `silencer` | src/levels/dos_1992/LAKE.asm:1227-1228 |
| LAKE | `0x2E` | `BEETLE_KICK_DETECTOR` → `WAIT_FOR_BEETLE_OFFSCREEN_THEN_KILL` | `silencer` | src/levels/dos_1992/LAKE.asm:1229-1230 |

## `gba_2004`

2 gates across 1 stages.

| Stage | Channel | Gated → Surviving | Category | Source |
| --- | :---: | --- | :---: | --- |
| LAKE | `0x09` | `BEETLE_INIT_POS_THEN_WALK_LEFT` → `KILL_CHANNEL_ROUTINE` | `silencer` | src/levels/gba_2004/LAKE.asm:1234-1235 |
| LAKE | `0x2E` | `BEETLE_KICK_DETECTOR` → `WAIT_FOR_BEETLE_OFFSCREEN_THEN_KILL` | `silencer` | src/levels/gba_2004/LAKE.asm:1236-1237 |

