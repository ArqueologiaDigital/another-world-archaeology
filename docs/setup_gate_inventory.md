# Setup-then-overwrite gate inventory

Static scan for the AW VM gate pattern — two `setup channel=N` instructions in the same straight-line block, where the second's address overrides the first's. The first's target is then unreachable under runtime semantics even though static control-flow has an edge to it. See research/05 (beetle in the lake) for the canonical example.

First-pass detector: scans only same-block consecutive setups separated by no `break`/`ret`/`killChannel`/`bankSwitch`/`freezeChannel`/`jmp`/label/`;@if` boundary. A complete reachability oracle (#0058) needs additional control-flow analysis.

**Total gates detected: 181.**

## `cartridge_1992`

58 gates across 5 stages.

| Stage | Channel | Gated → Surviving | Source |
| --- | :---: | --- | --- |
| CAPSULE | `0x02` | `LABEL_0CCD` → `KILL_CHAN_AT_59A3` | src/levels/cartridge_1992/CAPSULE.asm:17289-17294 |
| CAPSULE | `0x14` | `LABEL_9A9E` → `LABEL_BE04` | src/levels/cartridge_1992/CAPSULE.asm:1500-1501 |
| CAPSULE | `0x14` | `LABEL_4099` → `LABEL_40B4` | src/levels/cartridge_1992/CAPSULE.asm:10095-10097 |
| CAPSULE | `0x14` | `LABEL_3FCE` → `LABEL_3FF5` | src/levels/cartridge_1992/CAPSULE.asm:10101-10103 |
| CAPSULE | `0x14` | `LABEL_BC70` → `LABEL_BC62` | src/levels/cartridge_1992/CAPSULE.asm:18296-18298 |
| CAPSULE | `0x14` | `LABEL_BE04` → `LABEL_BDF6` | src/levels/cartridge_1992/CAPSULE.asm:18306-18308 |
| CAPSULE | `0x14` | `LABEL_BFCC` → `LABEL_BFA8` | src/levels/cartridge_1992/CAPSULE.asm:18356-18358 |
| CAPSULE | `0x14` | `LABEL_C0B2` → `LABEL_C092` | src/levels/cartridge_1992/CAPSULE.asm:18366-18368 |
| CAPSULE | `0x16` | `LABEL_9A8A` → `LABEL_B74A` | src/levels/cartridge_1992/CAPSULE.asm:1502-1503 |
| CAPSULE | `0x18` | `LABEL_5C5B` → `KILL_CHAN_AT_59A3` | src/levels/cartridge_1992/CAPSULE.asm:16798-16799 |
| CAPSULE | `0x23` | `LABEL_41B7` → `LABEL_4210` | src/levels/cartridge_1992/CAPSULE.asm:10116-10118 |
| CAPSULE | `0x25` | `LABEL_41B7` → `LABEL_4210` | src/levels/cartridge_1992/CAPSULE.asm:10122-10124 |
| CAPSULE | `0x27` | `LABEL_41B7` → `LABEL_4210` | src/levels/cartridge_1992/CAPSULE.asm:10128-10130 |
| CAPSULE | `0x2E` | `KILL_CHAN_AT_59A3` → `LABEL_2A6E` | src/levels/cartridge_1992/CAPSULE.asm:17938-17939 |
| CAPSULE | `0x37` | `LABEL_3AE8` → `LABEL_3A55` | src/levels/cartridge_1992/CAPSULE.asm:17108-17113 |
| CAPSULE | `0x3C` | `LABEL_3009` → `LABEL_2FAA` | src/levels/cartridge_1992/CAPSULE.asm:17645-17654 |
| CAVES | `0x01` | `LABEL_315E` → `LABEL_3136` | src/levels/cartridge_1992/CAVES.asm:4930-4933 |
| CAVES | `0x01` | `LABEL_315E` → `KILL_CHAN_AT_7830` | src/levels/cartridge_1992/CAVES.asm:17483-17486 |
| CAVES | `0x03` | `LABEL_2256` → `LABEL_224D` | src/levels/cartridge_1992/CAVES.asm:17700-17702 |
| CAVES | `0x04` | `LABEL_CD1A` → `KILL_CHAN_AT_7830` | src/levels/cartridge_1992/CAVES.asm:17857-17862 |
| CAVES | `0x05` | `JUNK__498E` → `KILL_CHAN_AT_7830` | src/levels/cartridge_1992/CAVES.asm:16679-16681 |
| CAVES | `0x14` | `LABEL_39E3` → `LABEL_EA2E` | src/levels/cartridge_1992/CAVES.asm:1296-1298 |
| CAVES | `0x14` | `LABEL_4B26` → `LABEL_4B41` | src/levels/cartridge_1992/CAVES.asm:11108-11110 |
| CAVES | `0x14` | `LABEL_4A5B` → `LABEL_4A82` | src/levels/cartridge_1992/CAVES.asm:11114-11116 |
| CAVES | `0x14` | `LABEL_EA2E` → `LABEL_EA20` | src/levels/cartridge_1992/CAVES.asm:22768-22770 |
| CAVES | `0x14` | `LABEL_EBC2` → `LABEL_EBB4` | src/levels/cartridge_1992/CAVES.asm:22778-22780 |
| CAVES | `0x14` | `LABEL_ED90` → `LABEL_ED6C` | src/levels/cartridge_1992/CAVES.asm:22828-22830 |
| CAVES | `0x14` | `LABEL_EE76` → `LABEL_EE56` | src/levels/cartridge_1992/CAVES.asm:22838-22840 |
| CAVES | `0x15` | `LABEL_3A26` → `KILL_CHAN_AT_7830` | src/levels/cartridge_1992/CAVES.asm:1297-1299 |
| CAVES | `0x1B` | `INIT_VARS_6C_6D_71_70` → `INIT_VARS_71_6C_6D` | src/levels/cartridge_1992/CAVES.asm:17242-17244 |
| CAVES | `0x23` | `LABEL_4C44` → `LABEL_4C9D` | src/levels/cartridge_1992/CAVES.asm:11129-11131 |
| CAVES | `0x23` | `LABEL_2FA2` → `LABEL_307B` | src/levels/cartridge_1992/CAVES.asm:17193-17203 |
| CAVES | `0x24` | `LABEL_2DAB` → `LABEL_2DB9` | src/levels/cartridge_1992/CAVES.asm:17196-17205 |
| CAVES | `0x25` | `LABEL_4C44` → `LABEL_4C9D` | src/levels/cartridge_1992/CAVES.asm:11135-11137 |
| CAVES | `0x27` | `LABEL_4C44` → `LABEL_4C9D` | src/levels/cartridge_1992/CAVES.asm:11141-11143 |
| CAVES | `0x34` | `LABEL_CF7F` → `LABEL_D026` | src/levels/cartridge_1992/CAVES.asm:16938-16940 |
| CAVES | `0x3B` | `LABEL_C794` → `LABEL_C769` | src/levels/cartridge_1992/CAVES.asm:17095-17101 |
| CAVES | `0x3E` | `LABEL_CBCD` → `LABEL_CB8C` | src/levels/cartridge_1992/CAVES.asm:22636-22639 |
| LAKE | `0x09` | `BEETLE_INIT_POS_THEN_WALK_LEFT` → `KILL_CHANNEL_ROUTINE` | src/levels/cartridge_1992/LAKE.asm:1244-1245 |
| LAKE | `0x14` | `HERO_FALL_LEFT_LOOP` → `HERO_FALL_LEFT_PRELUDE` | src/levels/cartridge_1992/LAKE.asm:6813-6815 |
| LAKE | `0x14` | `HERO_FALL_RIGHT_LOOP` → `HERO_FALL_RIGHT_PRELUDE` | src/levels/cartridge_1992/LAKE.asm:6823-6825 |
| LAKE | `0x14` | `HERO_LEAP_LEFT_LOOP` → `HERO_LEAP_LEFT_PRELUDE` | src/levels/cartridge_1992/LAKE.asm:6849-6851 |
| LAKE | `0x14` | `HERO_LEAP_RIGHT_LOOP` → `HERO_LEAP_RIGHT_PRELUDE` | src/levels/cartridge_1992/LAKE.asm:6859-6861 |
| LAKE | `0x29` | `CHECK_IF_THE_BEAST_HAS_ALREADY_REACHED_LESTER` → `WAIT_UNTIL_BEAST_CLOSE` | src/levels/cartridge_1992/LAKE.asm:4748-4750 |
| LAKE | `0x2E` | `BEETLE_KICK_DETECTOR` → `WAIT_FOR_BEETLE_OFFSCREEN_THEN_KILL` | src/levels/cartridge_1992/LAKE.asm:1246-1247 |
| PRISON | `0x01` | `INIT_VARS_E7_E8` → `KILL_CHANNEL_LANDING` | src/levels/cartridge_1992/PRISON.asm:14258-14261 |
| PRISON | `0x02` | `INLINE_SET_VARE9_TO_8` → `KILL_CHANNEL_LANDING` | src/levels/cartridge_1992/PRISON.asm:14259-14262 |
| PRISON | `0x05` | `INLINE_SET_VARE7_TO_5` → `KILL_CHANNEL_LANDING` | src/levels/cartridge_1992/PRISON.asm:14176-14178 |
| PRISON | `0x14` | `LABEL_1023` → `DRAW_CIN_146_TO_147_4F_AT_8AA18039` | src/levels/cartridge_1992/PRISON.asm:6865-6867 |
| PRISON | `0x14` | `LABEL_0F58` → `DRAW_CIN_280_TO_281_2F_AT_75ED3E60` | src/levels/cartridge_1992/PRISON.asm:6871-6873 |
| PRISON | `0x14` | `LABEL_90F7` → `STEP_DRAW_CIN555_LEFT4_RIGHT1` | src/levels/cartridge_1992/PRISON.asm:14820-14822 |
| PRISON | `0x14` | `LABEL_928E` → `DRAW_CIN555_STEP_RIGHT3` | src/levels/cartridge_1992/PRISON.asm:14830-14832 |
| PRISON | `0x14` | `LABEL_9421` → `LABEL_93FD` | src/levels/cartridge_1992/PRISON.asm:14880-14882 |
| PRISON | `0x14` | `LABEL_9507` → `LABEL_94E7` | src/levels/cartridge_1992/PRISON.asm:14890-14892 |
| PRISON | `0x23` | `LABEL_113D` → `LABEL_1199` | src/levels/cartridge_1992/PRISON.asm:6885-6887 |
| PRISON | `0x25` | `LABEL_113D` → `LABEL_1199` | src/levels/cartridge_1992/PRISON.asm:6895-6897 |
| PRISON | `0x27` | `LABEL_113D` → `LABEL_1199` | src/levels/cartridge_1992/PRISON.asm:6901-6903 |
| TANK | `0x34` | `LABEL_064D` → `LABEL_0638` | src/levels/cartridge_1992/TANK.asm:821-823 |

## `chahi_amiga_1991`

53 gates across 5 stages.

| Stage | Channel | Gated → Surviving | Source |
| --- | :---: | --- | --- |
| CAPSULE | `0x01` | `LABEL_1FFB` → `LABEL_1FD3` | src/levels/chahi_amiga_1991/CAPSULE.asm:3399-3402 |
| CAPSULE | `0x14` | `LABEL_2B2F` → `LABEL_2B4A` | src/levels/chahi_amiga_1991/CAPSULE.asm:6792-6794 |
| CAPSULE | `0x14` | `LABEL_2A64` → `LABEL_2A8B` | src/levels/chahi_amiga_1991/CAPSULE.asm:6798-6800 |
| CAPSULE | `0x14` | `LABEL_9028` → `LABEL_901A` | src/levels/chahi_amiga_1991/CAPSULE.asm:13116-13118 |
| CAPSULE | `0x14` | `LABEL_9158` → `LABEL_914A` | src/levels/chahi_amiga_1991/CAPSULE.asm:13126-13128 |
| CAPSULE | `0x14` | `LABEL_92B8` → `LABEL_9294` | src/levels/chahi_amiga_1991/CAPSULE.asm:13176-13178 |
| CAPSULE | `0x14` | `LABEL_939E` → `LABEL_937E` | src/levels/chahi_amiga_1991/CAPSULE.asm:13186-13188 |
| CAPSULE | `0x23` | `LABEL_2C4D` → `LABEL_2CA0` | src/levels/chahi_amiga_1991/CAPSULE.asm:6813-6815 |
| CAPSULE | `0x25` | `LABEL_2C4D` → `LABEL_2CA0` | src/levels/chahi_amiga_1991/CAPSULE.asm:6819-6821 |
| CAPSULE | `0x27` | `LABEL_2C4D` → `LABEL_2CA0` | src/levels/chahi_amiga_1991/CAPSULE.asm:6825-6827 |
| CAPSULE | `0x2E` | `KILL_CHAN_AT_59A3` → `LABEL_17D8` | src/levels/chahi_amiga_1991/CAPSULE.asm:12564-12565 |
| CAVES | `0x01` | `LABEL_2F51` → `LABEL_2F29` | src/levels/chahi_amiga_1991/CAVES.asm:4708-4711 |
| CAVES | `0x01` | `LABEL_2F51` → `KILL_CHAN_AT_7830` | src/levels/chahi_amiga_1991/CAVES.asm:16841-16844 |
| CAVES | `0x03` | `LABEL_20CB` → `LABEL_20C2` | src/levels/chahi_amiga_1991/CAVES.asm:17006-17008 |
| CAVES | `0x04` | `LABEL_C889` → `KILL_CHAN_AT_7830` | src/levels/chahi_amiga_1991/CAVES.asm:17161-17166 |
| CAVES | `0x14` | `LABEL_37D0` → `LABEL_E41E` | src/levels/chahi_amiga_1991/CAVES.asm:1262-1264 |
| CAVES | `0x14` | `LABEL_4958` → `LABEL_4973` | src/levels/chahi_amiga_1991/CAVES.asm:10614-10616 |
| CAVES | `0x14` | `LABEL_488D` → `LABEL_48B4` | src/levels/chahi_amiga_1991/CAVES.asm:10620-10622 |
| CAVES | `0x14` | `LABEL_E41E` → `LABEL_E410` | src/levels/chahi_amiga_1991/CAVES.asm:21810-21812 |
| CAVES | `0x14` | `LABEL_E54E` → `LABEL_E540` | src/levels/chahi_amiga_1991/CAVES.asm:21820-21822 |
| CAVES | `0x14` | `LABEL_E6AE` → `LABEL_E68A` | src/levels/chahi_amiga_1991/CAVES.asm:21870-21872 |
| CAVES | `0x14` | `LABEL_E794` → `LABEL_E774` | src/levels/chahi_amiga_1991/CAVES.asm:21880-21882 |
| CAVES | `0x15` | `LABEL_3813` → `KILL_CHAN_AT_7830` | src/levels/chahi_amiga_1991/CAVES.asm:1263-1265 |
| CAVES | `0x1B` | `INIT_VARS_6C_6D_71_70` → `INIT_VARS_71_6C_6D` | src/levels/chahi_amiga_1991/CAVES.asm:16600-16602 |
| CAVES | `0x23` | `LABEL_4A76` → `LABEL_4AC9` | src/levels/chahi_amiga_1991/CAVES.asm:10635-10637 |
| CAVES | `0x23` | `LABEL_2DAC` → `LABEL_2E85` | src/levels/chahi_amiga_1991/CAVES.asm:16551-16561 |
| CAVES | `0x24` | `LABEL_2BB5` → `LABEL_2BC3` | src/levels/chahi_amiga_1991/CAVES.asm:16554-16563 |
| CAVES | `0x25` | `LABEL_4A76` → `LABEL_4AC9` | src/levels/chahi_amiga_1991/CAVES.asm:10641-10643 |
| CAVES | `0x27` | `LABEL_4A76` → `LABEL_4AC9` | src/levels/chahi_amiga_1991/CAVES.asm:10647-10649 |
| CAVES | `0x34` | `LABEL_CAB0` → `LABEL_CB57` | src/levels/chahi_amiga_1991/CAVES.asm:16306-16308 |
| CAVES | `0x3B` | `LABEL_C360` → `LABEL_C335` | src/levels/chahi_amiga_1991/CAVES.asm:16453-16459 |
| CAVES | `0x3E` | `LABEL_C742` → `LABEL_C70E` | src/levels/chahi_amiga_1991/CAVES.asm:21701-21704 |
| CODE_WHEEL | `0x3C` | `LABEL_0DA8` → `LABEL_0DB7` | src/levels/chahi_amiga_1991/CODE_WHEEL.asm:379-383 |
| LAKE | `0x14` | `HERO_FALL_LEFT_LOOP` → `HERO_FALL_LEFT_PRELUDE` | src/levels/chahi_amiga_1991/LAKE.asm:6568-6570 |
| LAKE | `0x14` | `HERO_FALL_RIGHT_LOOP` → `HERO_FALL_RIGHT_PRELUDE` | src/levels/chahi_amiga_1991/LAKE.asm:6578-6580 |
| LAKE | `0x14` | `HERO_LEAP_LEFT_LOOP` → `HERO_LEAP_LEFT_PRELUDE` | src/levels/chahi_amiga_1991/LAKE.asm:6604-6606 |
| LAKE | `0x14` | `HERO_LEAP_RIGHT_LOOP` → `HERO_LEAP_RIGHT_PRELUDE` | src/levels/chahi_amiga_1991/LAKE.asm:6614-6616 |
| LAKE | `0x2E` | `BEETLE_KICK_DETECTOR` → `WAIT_FOR_BEETLE_OFFSCREEN_THEN_KILL` | src/levels/chahi_amiga_1991/LAKE.asm:1151-1152 |
| PRISON | `0x01` | `LABEL_7D25` → `LABEL_7D31` | src/levels/chahi_amiga_1991/PRISON.asm:13031-13033 |
| PRISON | `0x01` | `LABEL_7D12` → `LABEL_7D25` | src/levels/chahi_amiga_1991/PRISON.asm:13037-13039 |
| PRISON | `0x01` | `DRAW_CIN_090_TO_104_3F_AT_8C208B32` → `LABEL_7D1E` | src/levels/chahi_amiga_1991/PRISON.asm:13043-13045 |
| PRISON | `0x01` | `INIT_VARS_E7_E8` → `KILL_CHANNEL_LANDING` | src/levels/chahi_amiga_1991/PRISON.asm:13759-13762 |
| PRISON | `0x02` | `INLINE_SET_VARE9_TO_8` → `KILL_CHANNEL_LANDING` | src/levels/chahi_amiga_1991/PRISON.asm:13760-13763 |
| PRISON | `0x05` | `INLINE_SET_VARE7_TO_5` → `KILL_CHANNEL_LANDING` | src/levels/chahi_amiga_1991/PRISON.asm:13689-13691 |
| PRISON | `0x14` | `LABEL_0FBB` → `DRAW_CIN_146_TO_147_4F_AT_8AA18039` | src/levels/chahi_amiga_1991/PRISON.asm:6561-6563 |
| PRISON | `0x14` | `LABEL_0EF0` → `DRAW_CIN_280_TO_281_2F_AT_75ED3E60` | src/levels/chahi_amiga_1991/PRISON.asm:6567-6569 |
| PRISON | `0x14` | `LABEL_8E2B` → `STEP_DRAW_CIN555_LEFT4_RIGHT1` | src/levels/chahi_amiga_1991/PRISON.asm:14138-14140 |
| PRISON | `0x14` | `LABEL_8F62` → `DRAW_CIN555_STEP_RIGHT3` | src/levels/chahi_amiga_1991/PRISON.asm:14148-14150 |
| PRISON | `0x14` | `LABEL_908D` → `LABEL_9069` | src/levels/chahi_amiga_1991/PRISON.asm:14198-14200 |
| PRISON | `0x14` | `LABEL_9173` → `LABEL_9153` | src/levels/chahi_amiga_1991/PRISON.asm:14208-14210 |
| PRISON | `0x23` | `LABEL_10D5` → `LABEL_1128` | src/levels/chahi_amiga_1991/PRISON.asm:6581-6583 |
| PRISON | `0x25` | `LABEL_10D5` → `LABEL_1128` | src/levels/chahi_amiga_1991/PRISON.asm:6591-6593 |
| PRISON | `0x27` | `LABEL_10D5` → `LABEL_1128` | src/levels/chahi_amiga_1991/PRISON.asm:6597-6599 |

## `dos_1992`

63 gates across 6 stages.

| Stage | Channel | Gated → Surviving | Source |
| --- | :---: | --- | --- |
| CAPSULE | `0x02` | `LABEL_0C0E` → `KILL_CHAN_AT_59A3` | src/levels/dos_1992/CAPSULE.asm:17310-17315 |
| CAPSULE | `0x14` | `LABEL_9A35` → `LABEL_BD20` | src/levels/dos_1992/CAPSULE.asm:1472-1473 |
| CAPSULE | `0x14` | `LABEL_40CD` → `LABEL_40E8` | src/levels/dos_1992/CAPSULE.asm:10132-10134 |
| CAPSULE | `0x14` | `LABEL_4002` → `LABEL_4029` | src/levels/dos_1992/CAPSULE.asm:10138-10140 |
| CAPSULE | `0x14` | `LABEL_BB8C` → `LABEL_BB7E` | src/levels/dos_1992/CAPSULE.asm:18286-18288 |
| CAPSULE | `0x14` | `LABEL_BD20` → `LABEL_BD12` | src/levels/dos_1992/CAPSULE.asm:18296-18298 |
| CAPSULE | `0x14` | `LABEL_BEE8` → `LABEL_BEC4` | src/levels/dos_1992/CAPSULE.asm:18346-18348 |
| CAPSULE | `0x14` | `LABEL_BFCE` → `LABEL_BFAE` | src/levels/dos_1992/CAPSULE.asm:18356-18358 |
| CAPSULE | `0x16` | `LABEL_9A21` → `LABEL_B666` | src/levels/dos_1992/CAPSULE.asm:1474-1475 |
| CAPSULE | `0x18` | `LABEL_5C58` → `KILL_CHAN_AT_59A3` | src/levels/dos_1992/CAPSULE.asm:16819-16820 |
| CAPSULE | `0x23` | `LABEL_41EB` → `LABEL_4244` | src/levels/dos_1992/CAPSULE.asm:10153-10155 |
| CAPSULE | `0x25` | `LABEL_41EB` → `LABEL_4244` | src/levels/dos_1992/CAPSULE.asm:10159-10161 |
| CAPSULE | `0x27` | `LABEL_41EB` → `LABEL_4244` | src/levels/dos_1992/CAPSULE.asm:10165-10167 |
| CAPSULE | `0x27` | `LABEL_02D2` → `LABEL_4AE8` | src/levels/dos_1992/CAPSULE.asm:16784-16789 |
| CAPSULE | `0x2E` | `KILL_CHAN_AT_59A3` → `LABEL_28F7` | src/levels/dos_1992/CAPSULE.asm:17929-17930 |
| CAPSULE | `0x37` | `LABEL_3A7F` → `LABEL_39EC` | src/levels/dos_1992/CAPSULE.asm:17130-17135 |
| CAPSULE | `0x3C` | `LABEL_2E8C` → `LABEL_2E2D` | src/levels/dos_1992/CAPSULE.asm:17637-17646 |
| CAVES | `0x01` | `LABEL_317A` → `LABEL_3152` | src/levels/dos_1992/CAVES.asm:4972-4975 |
| CAVES | `0x01` | `LABEL_317A` → `KILL_CHAN_AT_7830` | src/levels/dos_1992/CAVES.asm:17574-17577 |
| CAVES | `0x03` | `LABEL_228F` → `LABEL_2286` | src/levels/dos_1992/CAVES.asm:17788-17790 |
| CAVES | `0x04` | `LABEL_CD2F` → `KILL_CHAN_AT_7830` | src/levels/dos_1992/CAVES.asm:17943-17948 |
| CAVES | `0x05` | `JUNK__4AD1` → `KILL_CHAN_AT_7830` | src/levels/dos_1992/CAVES.asm:16789-16791 |
| CAVES | `0x14` | `LABEL_39F9` → `LABEL_E9A5` | src/levels/dos_1992/CAVES.asm:1309-1311 |
| CAVES | `0x14` | `LABEL_4C69` → `LABEL_4C84` | src/levels/dos_1992/CAVES.asm:11236-11238 |
| CAVES | `0x14` | `LABEL_4B9E` → `LABEL_4BC5` | src/levels/dos_1992/CAVES.asm:11242-11244 |
| CAVES | `0x14` | `LABEL_E9A5` → `LABEL_E997` | src/levels/dos_1992/CAVES.asm:22787-22789 |
| CAVES | `0x14` | `LABEL_EB39` → `LABEL_EB2B` | src/levels/dos_1992/CAVES.asm:22797-22799 |
| CAVES | `0x14` | `LABEL_ED07` → `LABEL_ECE3` | src/levels/dos_1992/CAVES.asm:22847-22849 |
| CAVES | `0x14` | `LABEL_EDED` → `LABEL_EDCD` | src/levels/dos_1992/CAVES.asm:22857-22859 |
| CAVES | `0x15` | `LABEL_3A3C` → `KILL_CHAN_AT_7830` | src/levels/dos_1992/CAVES.asm:1310-1312 |
| CAVES | `0x1B` | `INIT_VARS_6C_6D_71_70` → `INIT_VARS_71_6C_6D` | src/levels/dos_1992/CAVES.asm:17333-17335 |
| CAVES | `0x23` | `LABEL_4D87` → `LABEL_4DE0` | src/levels/dos_1992/CAVES.asm:11257-11259 |
| CAVES | `0x23` | `LABEL_2FCF` → `LABEL_30A8` | src/levels/dos_1992/CAVES.asm:17284-17294 |
| CAVES | `0x24` | `LABEL_2DD8` → `LABEL_2DE6` | src/levels/dos_1992/CAVES.asm:17287-17296 |
| CAVES | `0x25` | `LABEL_4D87` → `LABEL_4DE0` | src/levels/dos_1992/CAVES.asm:11263-11265 |
| CAVES | `0x27` | `LABEL_4D87` → `LABEL_4DE0` | src/levels/dos_1992/CAVES.asm:11269-11271 |
| CAVES | `0x34` | `LABEL_CF56` → `LABEL_CFFD` | src/levels/dos_1992/CAVES.asm:17039-17041 |
| CAVES | `0x3B` | `LABEL_C7B3` → `LABEL_C788` | src/levels/dos_1992/CAVES.asm:17186-17192 |
| CAVES | `0x3E` | `LABEL_CBE2` → `LABEL_CBA1` | src/levels/dos_1992/CAVES.asm:22655-22658 |
| CODE_WHEEL | `0x3C` | `LABEL_10B2` → `LABEL_10C1` | src/levels/dos_1992/CODE_WHEEL.asm:416-420 |
| LAKE | `0x09` | `BEETLE_INIT_POS_THEN_WALK_LEFT` → `KILL_CHANNEL_ROUTINE` | src/levels/dos_1992/LAKE.asm:1227-1228 |
| LAKE | `0x14` | `HERO_FALL_LEFT_LOOP` → `HERO_FALL_LEFT_PRELUDE` | src/levels/dos_1992/LAKE.asm:6759-6761 |
| LAKE | `0x14` | `HERO_FALL_RIGHT_LOOP` → `HERO_FALL_RIGHT_PRELUDE` | src/levels/dos_1992/LAKE.asm:6769-6771 |
| LAKE | `0x14` | `HERO_LEAP_LEFT_LOOP` → `HERO_LEAP_LEFT_PRELUDE` | src/levels/dos_1992/LAKE.asm:6795-6797 |
| LAKE | `0x14` | `HERO_LEAP_RIGHT_LOOP` → `HERO_LEAP_RIGHT_PRELUDE` | src/levels/dos_1992/LAKE.asm:6805-6807 |
| LAKE | `0x29` | `CHECK_IF_THE_BEAST_HAS_ALREADY_REACHED_LESTER` → `WAIT_UNTIL_BEAST_CLOSE` | src/levels/dos_1992/LAKE.asm:4717-4719 |
| LAKE | `0x2E` | `BEETLE_KICK_DETECTOR` → `WAIT_FOR_BEETLE_OFFSCREEN_THEN_KILL` | src/levels/dos_1992/LAKE.asm:1229-1230 |
| PRISON | `0x01` | `LABEL_7DF0` → `LABEL_7DFC` | src/levels/dos_1992/PRISON.asm:13399-13401 |
| PRISON | `0x01` | `LABEL_7DDD` → `LABEL_7DF0` | src/levels/dos_1992/PRISON.asm:13405-13407 |
| PRISON | `0x01` | `DRAW_CIN_090_TO_104_3F_AT_8C208B32` → `LABEL_7DE9` | src/levels/dos_1992/PRISON.asm:13411-13413 |
| PRISON | `0x01` | `INIT_VARS_E7_E8` → `KILL_CHANNEL_LANDING` | src/levels/dos_1992/PRISON.asm:14156-14159 |
| PRISON | `0x02` | `INLINE_SET_VARE9_TO_8` → `KILL_CHANNEL_LANDING` | src/levels/dos_1992/PRISON.asm:14157-14160 |
| PRISON | `0x05` | `INLINE_SET_VARE7_TO_5` → `KILL_CHANNEL_LANDING` | src/levels/dos_1992/PRISON.asm:14075-14077 |
| PRISON | `0x14` | `LABEL_0F9B` → `DRAW_CIN_146_TO_147_4F_AT_8AA18039` | src/levels/dos_1992/PRISON.asm:6791-6793 |
| PRISON | `0x14` | `LABEL_0ED0` → `DRAW_CIN_280_TO_281_2F_AT_75ED3E60` | src/levels/dos_1992/PRISON.asm:6797-6799 |
| PRISON | `0x14` | `LABEL_8F91` → `STEP_DRAW_CIN555_LEFT4_RIGHT1` | src/levels/dos_1992/PRISON.asm:14715-14717 |
| PRISON | `0x14` | `LABEL_9128` → `DRAW_CIN555_STEP_RIGHT3` | src/levels/dos_1992/PRISON.asm:14725-14727 |
| PRISON | `0x14` | `LABEL_92BB` → `LABEL_9297` | src/levels/dos_1992/PRISON.asm:14775-14777 |
| PRISON | `0x14` | `LABEL_93A1` → `LABEL_9381` | src/levels/dos_1992/PRISON.asm:14785-14787 |
| PRISON | `0x23` | `LABEL_10B5` → `LABEL_1111` | src/levels/dos_1992/PRISON.asm:6811-6813 |
| PRISON | `0x25` | `LABEL_10B5` → `LABEL_1111` | src/levels/dos_1992/PRISON.asm:6821-6823 |
| PRISON | `0x27` | `LABEL_10B5` → `LABEL_1111` | src/levels/dos_1992/PRISON.asm:6827-6829 |
| TANK | `0x34` | `LABEL_0675` → `LABEL_0660` | src/levels/dos_1992/TANK.asm:853-855 |

## `gba_2004`

7 gates across 1 stages.

| Stage | Channel | Gated → Surviving | Source |
| --- | :---: | --- | --- |
| LAKE | `0x09` | `BEETLE_INIT_POS_THEN_WALK_LEFT` → `KILL_CHANNEL_ROUTINE` | src/levels/gba_2004/LAKE.asm:1234-1235 |
| LAKE | `0x14` | `HERO_FALL_LEFT_LOOP` → `HERO_FALL_LEFT_PRELUDE` | src/levels/gba_2004/LAKE.asm:6781-6783 |
| LAKE | `0x14` | `HERO_FALL_RIGHT_LOOP` → `HERO_FALL_RIGHT_PRELUDE` | src/levels/gba_2004/LAKE.asm:6791-6793 |
| LAKE | `0x14` | `HERO_LEAP_LEFT_LOOP` → `HERO_LEAP_LEFT_PRELUDE` | src/levels/gba_2004/LAKE.asm:6817-6819 |
| LAKE | `0x14` | `HERO_LEAP_RIGHT_LOOP` → `HERO_LEAP_RIGHT_PRELUDE` | src/levels/gba_2004/LAKE.asm:6827-6829 |
| LAKE | `0x29` | `CHECK_IF_THE_BEAST_HAS_ALREADY_REACHED_LESTER` → `WAIT_UNTIL_BEAST_CLOSE` | src/levels/gba_2004/LAKE.asm:4725-4727 |
| LAKE | `0x2E` | `BEETLE_KICK_DETECTOR` → `WAIT_FOR_BEETLE_OFFSCREEN_THEN_KILL` | src/levels/gba_2004/LAKE.asm:1236-1237 |

