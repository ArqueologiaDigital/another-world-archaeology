# `;@raw=` residue categorisation

Total annotations surveyed: **366** in unified tree.

- annotations with a multiply-defined operand symbol: **363** (across 63 distinct symbols)
- annotations whose symbol has only one definition: **0**
- annotations with no resolvable symbol: **3**

## Multi-defined symbol groups (probable EQU/label collision)

Each section: a symbol name + every definition site + every annotated call site. The symbol values across definitions tell you whether the collision is genuine (different addresses/values) or coincidence (same value at multiple sites — safe to canonicalise).

### `DEDUP_CAVES_5B_003` — 58 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/DEDUP_CAVES_5B_003.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1005` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1052` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/amiga__post_COMPUTE_VAR22_AS_VAR40_MINUS_28.inc:97` — `jle [0x06], 0x00, DEDUP_CAVES_5B_003` ⇒ `;@raw=0x0A,0x05,0x06,0x00,0x72,0xCC`
- `src/levels/_unified/caves/amiga__post_COMPUTE_VAR22_AS_VAR40_MINUS_28.inc:102` — `jne [HERO_POS_LEFT_RIGHT], 0x00, DEDUP_CAVES_5B_003` ⇒ `;@raw=0x0A,0x01,0xFC,0x00,0x72,0xCC`
- `src/levels/_unified/caves/amiga__post_COMPUTE_VAR22_AS_VAR40_MINUS_28.inc:103` — `je [HERO_ACTION], 0x00, DEDUP_CAVES_5B_003` ⇒ `;@raw=0x0A,0x00,0xFA,0x00,0x72,0xCC`
- `src/levels/_unified/caves/amiga__post_COMPUTE_VAR22_AS_VAR40_MINUS_28.inc:124` — `jle [0x06], 0x00, DEDUP_CAVES_5B_003` ⇒ `;@raw=0x0A,0x05,0x06,0x00,0x72,0xCC`
- `src/levels/_unified/caves/amiga__post_COMPUTE_VAR22_AS_VAR40_MINUS_28.inc:129` — `je [HERO_ACTION], 0x00, DEDUP_CAVES_5B_003` ⇒ `;@raw=0x0A,0x00,0xFA,0x00,0x72,0xCC`
- …and 53 more

### `SHARED_RET` — 55 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/SHARED_RET.inc:1` (label)
- `src/levels/_unified/capsule/amiga__post_COPY_VAR01_TO_VAR28.inc:391` (label)
- `src/levels/_unified/capsule/cart__post_COPY_VAR01_TO_VAR28.inc:396` (label)
- `src/levels/_unified/capsule/dos__post_COPY_VAR01_TO_VAR28.inc:396` (label)
- `src/levels/_unified/code_wheel/amiga__post_COMPUTE_VAR07_TIMES_44_PLUS_20.inc:161` (label)
- `src/levels/_unified/code_wheel/dos__post_COMPUTE_VAR07_TIMES_44_PLUS_20.inc:211` (label)
- `src/levels/_unified/passcode/cart__post_INIT_VAR08_TO_150.inc:269` (label)
- `src/levels/_unified/passcode/dos__post_INIT_VAR08_TO_150.inc:452` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1459` (label)
- `src/levels/cartridge_1992/CAPSULE.asm:4923` (label)
- `src/levels/cartridge_1992/PASSCODE.asm:1103` (label)
- `src/levels/cartridge_1992/PRISON.asm:2879` (label)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:2860` (label)
- `src/levels/chahi_amiga_1991/CODE_WHEEL.asm:1376` (label)
- `src/levels/chahi_amiga_1991/PRISON.asm:2728` (label)
- `src/levels/dos_1992/CAPSULE.asm:4815` (label)
- `src/levels/dos_1992/CODE_WHEEL.asm:1679` (label)
- `src/levels/dos_1992/PASSCODE.asm:1592` (label)
- `src/levels/dos_1992/PRISON.asm:2844` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/prison/amiga__post_DRAW_CIN_169_WITH_POS_STEP_AT_B673C5FF.inc:51` — `jg [0x13], [0x30], SHARED_RET` ⇒ `;@raw=0x0A,0x82,0x13,0x30,0x52,0x8D`
- `src/levels/_unified/prison/amiga__post_DRAW_CIN_169_WITH_POS_STEP_AT_B673C5FF.inc:54` — `je [0xF8], 0x00, SHARED_RET` ⇒ `;@raw=0x0A,0x00,0xF8,0x00,0x52,0x8D`
- `src/levels/_unified/prison/amiga__post_DRAW_CIN_169_WITH_POS_STEP_AT_B673C5FF.inc:66` — `jg [0x13], [0x30], SHARED_RET` ⇒ `;@raw=0x0A,0x82,0x13,0x30,0x52,0x8D`
- `src/levels/_unified/prison/amiga__post_DRAW_CIN_169_WITH_POS_STEP_AT_B673C5FF.inc:69` — `je [0xF8], 0x00, SHARED_RET` ⇒ `;@raw=0x0A,0x00,0xF8,0x00,0x52,0x8D`
- `src/levels/_unified/prison/amiga__post_DRAW_CIN_169_WITH_POS_STEP_AT_B673C5FF.inc:75` — `jg [0x13], [0x30], SHARED_RET` ⇒ `;@raw=0x0A,0x82,0x13,0x30,0x52,0x8D`
- …and 50 more

### `KILL_CHANNEL_LANDING` — 50 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/KILL_CHANNEL_LANDING.inc:1` (label)
- `src/levels/_unified/capsule/amiga__post_BREAK_5X_THEN_INIT_VAR03_14.inc:64` (label)
- `src/levels/_unified/capsule/cart__post_DRAW_TEXT_0174_AT_26_180.inc:7` (label)
- `src/levels/_unified/capsule/dos__post_DRAW_TEXT_0174_AT_26_180.inc:7` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:230` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1950` (label)
- `src/levels/cartridge_1992/PRISON.asm:1223` (label)
- `src/levels/chahi_amiga_1991/PRISON.asm:1143` (label)
- `src/levels/dos_1992/PRISON.asm:1194` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/prison/amiga__entry.inc:2258` — `setup channel=0x3C, address=KILL_CHANNEL_LANDING` ⇒ `;@raw=0x08,0x3C,0x01,0x7F`
- `src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:207` — `setup channel=0x05, address=KILL_CHANNEL_LANDING` ⇒ `;@raw=0x08,0x05,0x01,0x7F`
- `src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:278` — `setup channel=0x01, address=KILL_CHANNEL_LANDING` ⇒ `;@raw=0x08,0x01,0x01,0x7F`
- `src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:279` — `setup channel=0x02, address=KILL_CHANNEL_LANDING` ⇒ `;@raw=0x08,0x02,0x01,0x7F`
- `src/levels/_unified/prison/amiga__post_DECREMENT_VAR08_BY_D.inc:376` — `je [0x0A], [0x0C], KILL_CHANNEL_LANDING` ⇒ `;@raw=0x0A,0x80,0x0A,0x0C,0x6A,0x43`
- …and 45 more

### `DEDUP_CAVES_5B_007` — 24 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/DEDUP_CAVES_5B_007.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1360` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1416` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1433` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1735` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1791` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1808` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/amiga__post_DEDUP_CAVES_5B_007.inc:9` — `jmp DEDUP_CAVES_5B_007` ⇒ `;@raw=0x07,0x89,0xAB`
- `src/levels/_unified/caves/amiga__post_DEDUP_CAVES_5B_009.inc:9` — `jmp DEDUP_CAVES_5B_007` ⇒ `;@raw=0x07,0x8A,0x7C`
- `src/levels/_unified/caves/amiga__post_DEDUP_CAVES_5B_020.inc:24` — `jmp DEDUP_CAVES_5B_007` ⇒ `;@raw=0x07,0x89,0x7E`
- `src/levels/_unified/caves/amiga__post_DEDUP_CAVES_5B_021.inc:24` — `jmp DEDUP_CAVES_5B_007` ⇒ `;@raw=0x07,0x8A,0x4F`
- `src/levels/_unified/caves/cart__post_DEDUP_CAVES_5B_007.inc:9` — `jmp DEDUP_CAVES_5B_007` ⇒ `;@raw=0x07,0x8C,0x80`
- …and 19 more

### `DEDUP_CAVES_6B_001` — 18 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/DEDUP_CAVES_6B_001.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1098` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1104` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/amiga__post_COPY_VAR01_TO_VAR28.inc:127` — `jmp DEDUP_CAVES_6B_001` ⇒ `;@raw=0x07,0x7D,0x49`
- `src/levels/_unified/caves/amiga__post_COPY_VAR01_TO_VAR28.inc:134` — `jmp DEDUP_CAVES_6B_001` ⇒ `;@raw=0x07,0x7D,0x49`
- `src/levels/_unified/caves/amiga__post_INLINE_COPY_VAR44_TO_VAR25.inc:41` — `jmp DEDUP_CAVES_6B_001` ⇒ `;@raw=0x07,0x75,0x87`
- `src/levels/_unified/caves/cart__post_COPY_VAR01_TO_VAR28.inc:127` — `jmp DEDUP_CAVES_6B_001` ⇒ `;@raw=0x07,0x80,0x1E`
- `src/levels/_unified/caves/cart__post_COPY_VAR01_TO_VAR28.inc:134` — `jmp DEDUP_CAVES_6B_001` ⇒ `;@raw=0x07,0x80,0x1E`
- …and 13 more

### `INIT_VARS_2F_29_12` — 12 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/INIT_VARS_2F_29_12.inc:1` (label)
- `src/levels/_unified/capsule/capsule_init_dispatch.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:842` (label)
- `src/levels/cartridge_1992/CAPSULE.asm:9199` (label)
- `src/levels/cartridge_1992/CAVES.asm:10223` (label)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:5940` (label)
- `src/levels/chahi_amiga_1991/CAVES.asm:9742` (label)
- `src/levels/dos_1992/CAPSULE.asm:9247` (label)
- `src/levels/dos_1992/CAVES.asm:10358` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/capsule/amiga__post_INIT_VARS_2F_29_12.inc:10` — `jle [0x26], 0x46, INIT_VARS_2F_29_12` ⇒ `;@raw=0x0A,0x05,0x26,0x46,0x3F,0x18`
- `src/levels/_unified/capsule/amiga__post_STEP_VAR29_DOWN10_SET_VAR2F_11.inc:100` — `jg [0x01], 0xA0, INIT_VARS_2F_29_12` ⇒ `;@raw=0x0A,0x02,0x01,0xA0,0x3E,0xBA`
- `src/levels/_unified/capsule/cart__post_INIT_VARS_2F_29.inc:29` — `jg [0x01], 0xA0, INIT_VARS_2F_29_12` ⇒ `;@raw=0x0A,0x02,0x01,0xA0,0x55,0xBC`
- `src/levels/_unified/capsule/cart__post_INIT_VARS_2F_29_12.inc:10` — `jle [0x26], 0x46, INIT_VARS_2F_29_12` ⇒ `;@raw=0x0A,0x05,0x26,0x46,0x56,0x1A`
- `src/levels/_unified/capsule/dos__post_INIT_VARS_2F_29.inc:29` — `jg [0x01], 0xA0, INIT_VARS_2F_29_12` ⇒ `;@raw=0x0A,0x02,0x01,0xA0,0x55,0xCC`
- …and 7 more

### `DEDUP_CAVES_5B_020` — 12 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/DEDUP_CAVES_5B_020.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1388` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1763` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/amiga__post_DEDUP_CAVES_5B_008.inc:24` — `jmp DEDUP_CAVES_5B_020` ⇒ `;@raw=0x07,0x89,0xFD`
- `src/levels/_unified/caves/amiga__post_SHARED_RET.inc:894` — `jmp DEDUP_CAVES_5B_020` ⇒ `;@raw=0x07,0x89,0x2C`
- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_255_031.inc:12` — `jmp DEDUP_CAVES_5B_020` ⇒ `;@raw=0x07,0x8C,0xD2`
- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_266_006.inc:178` — `jmp DEDUP_CAVES_5B_020` ⇒ `;@raw=0x07,0x8C,0x01`
- `src/levels/_unified/caves/dos__post_INLINE_DRAW_CV_255_031.inc:12` — `jmp DEDUP_CAVES_5B_020` ⇒ `;@raw=0x07,0x8D,0x5B`
- …and 7 more

### `INLINE_DRAW_CV_272_003` — 12 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/INLINE_DRAW_CV_272_003.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1263` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1274` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1638` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1649` (label)
- `src/levels/cartridge_1992/CAVES.asm:14167` (label)
- `src/levels/cartridge_1992/PRISON.asm:9949` (label)
- `src/levels/dos_1992/CAVES.asm:14277` (label)
- `src/levels/dos_1992/PRISON.asm:9873` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/cart__post_DRAW_CV275_AT_X07_Y08.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_272_003` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x89,0x4F`
- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_269_024.inc:11` — `je [0x0D], 0x00, INLINE_DRAW_CV_272_003` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x89,0x01`
- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_272_014.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_272_003` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x89,0x76`
- `src/levels/_unified/caves/dos__post_DRAW_CV275_AT_X07_Y08.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_272_003` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x89,0xD8`
- `src/levels/_unified/caves/dos__post_INLINE_DRAW_CV_269_024.inc:11` — `je [0x0D], 0x00, INLINE_DRAW_CV_272_003` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x89,0x8A`
- …and 7 more

### `INLINE_DRAW_CV_269_024` — 12 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/INLINE_DRAW_CV_269_024.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1285` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1296` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1660` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1671` (label)
- `src/levels/cartridge_1992/CAVES.asm:14150` (label)
- `src/levels/cartridge_1992/PRISON.asm:9932` (label)
- `src/levels/dos_1992/CAVES.asm:14260` (label)
- `src/levels/dos_1992/PRISON.asm:9856` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_266_005.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_269_024` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x88,0xD6`
- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_269_025.inc:11` — `je [0x0D], 0x00, INLINE_DRAW_CV_269_024` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x89,0xC8`
- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_272_015.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_269_024` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x89,0x9D`
- `src/levels/_unified/caves/dos__post_INLINE_DRAW_CV_266_005.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_269_024` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x89,0x5F`
- `src/levels/_unified/caves/dos__post_INLINE_DRAW_CV_269_025.inc:11` — `je [0x0D], 0x00, INLINE_DRAW_CV_269_024` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8A,0x51`
- …and 7 more

### `INLINE_DRAW_CV_252_018` — 8 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/INLINE_DRAW_CV_252_018.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1401` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1776` (label)
- `src/levels/cartridge_1992/CAVES.asm:14495` (label)
- `src/levels/cartridge_1992/PRISON.asm:10278` (label)
- `src/levels/dos_1992/CAVES.asm:14605` (label)
- `src/levels/dos_1992/PRISON.asm:10202` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/cart__post_DEDUP_CAVES_5B_007.inc:7` — `je [0x0D], 0x00, INLINE_DRAW_CV_252_018` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8C,0x7B`
- `src/levels/_unified/caves/cart__post_DEDUP_CAVES_5B_021.inc:6` — `je [0x0D], 0x00, INLINE_DRAW_CV_252_018` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8C,0xF6`
- `src/levels/_unified/caves/dos__post_DEDUP_CAVES_5B_007.inc:7` — `je [0x0D], 0x00, INLINE_DRAW_CV_252_018` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8D,0x04`
- `src/levels/_unified/caves/dos__post_DEDUP_CAVES_5B_021.inc:6` — `je [0x0D], 0x00, INLINE_DRAW_CV_252_018` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8D,0x7F`
- `src/levels/_unified/prison/cart__post_DEDUP_PRISON_5B_007.inc:6` — `je [0x0D], 0x00, INLINE_DRAW_CV_252_018` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x5E,0xD9`
- …and 3 more

### `INLINE_DRAW_CV_255_010` — 8 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/INLINE_DRAW_CV_255_010.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1383` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1758` (label)
- `src/levels/cartridge_1992/CAVES.asm:14511` (label)
- `src/levels/cartridge_1992/PRISON.asm:10294` (label)
- `src/levels/dos_1992/CAVES.asm:14621` (label)
- `src/levels/dos_1992/PRISON.asm:10218` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/cart__post_DEDUP_CAVES_5B_008.inc:6` — `je [0x0D], 0x00, INLINE_DRAW_CV_255_010` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8C,0xA4`
- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_255_031.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_255_010` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8C,0xCD`
- `src/levels/_unified/caves/dos__post_DEDUP_CAVES_5B_008.inc:6` — `je [0x0D], 0x00, INLINE_DRAW_CV_255_010` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8D,0x2D`
- `src/levels/_unified/caves/dos__post_INLINE_DRAW_CV_255_031.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_255_010` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8D,0x56`
- `src/levels/_unified/prison/cart__post_DEDUP_PRISON_5B_015.inc:6` — `je [0x0D], 0x00, INLINE_DRAW_CV_255_010` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x5E,0x81`
- …and 3 more

### `INLINE_DRAW_CV_243_012` — 8 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/INLINE_DRAW_CV_243_012.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1446` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1821` (label)
- `src/levels/cartridge_1992/CAVES.asm:14446` (label)
- `src/levels/cartridge_1992/PRISON.asm:10229` (label)
- `src/levels/dos_1992/CAVES.asm:14556` (label)
- `src/levels/dos_1992/PRISON.asm:10153` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/cart__post_DEDUP_CAVES_5B_010.inc:7` — `je [0x0D], 0x00, INLINE_DRAW_CV_243_012` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8D,0x79`
- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_266_006.inc:176` — `je [0x0D], 0x00, INLINE_DRAW_CV_243_012` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8B,0xFC`
- `src/levels/_unified/caves/dos__post_DEDUP_CAVES_5B_010.inc:7` — `je [0x0D], 0x00, INLINE_DRAW_CV_243_012` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8E,0x02`
- `src/levels/_unified/caves/dos__post_INLINE_DRAW_CV_266_006.inc:176` — `je [0x0D], 0x00, INLINE_DRAW_CV_243_012` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8C,0x85`
- `src/levels/_unified/prison/cart__post_DEDUP_PRISON_5B_017.inc:7` — `je [0x0D], 0x00, INLINE_DRAW_CV_243_012` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x5F,0x5C`
- …and 3 more

### `INLINE_DRAW_CV_216_027` — 8 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/INLINE_DRAW_CV_216_027.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1202` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1577` (label)
- `src/levels/cartridge_1992/CAVES.asm:13770` (label)
- `src/levels/cartridge_1992/PRISON.asm:9495` (label)
- `src/levels/dos_1992/CAVES.asm:13880` (label)
- `src/levels/dos_1992/PRISON.asm:9419` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/cart__post_DRAW_CV204_AT_X07_PLUS1_Y08.inc:47` — `je [0x0D], 0x00, INLINE_DRAW_CV_216_027` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x85,0x04`
- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_220_017.inc:11` — `je [0x0D], 0x00, INLINE_DRAW_CV_216_027` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x85,0xF6`
- `src/levels/_unified/caves/dos__post_DRAW_CV204_AT_X07_PLUS1_Y08.inc:47` — `je [0x0D], 0x00, INLINE_DRAW_CV_216_027` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x85,0x8D`
- `src/levels/_unified/caves/dos__post_INLINE_DRAW_CV_220_017.inc:11` — `je [0x0D], 0x00, INLINE_DRAW_CV_216_027` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x86,0x7F`
- `src/levels/_unified/prison/cart__post_DRAW_CV204_AT_X07_PLUS1_Y08.inc:47` — `je [0x0D], 0x00, INLINE_DRAW_CV_216_027` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x56,0x57`
- …and 3 more

### `INLINE_DRAW_CV_228_018` — 8 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/INLINE_DRAW_CV_228_018.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1180` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1555` (label)
- `src/levels/cartridge_1992/CAVES.asm:13818` (label)
- `src/levels/cartridge_1992/PRISON.asm:9543` (label)
- `src/levels/chahi_amiga_1991/CAVES.asm:13621` (label)
- `src/levels/chahi_amiga_1991/PRISON.asm:9605` (label)
- `src/levels/dos_1992/CAVES.asm:13928` (label)
- `src/levels/dos_1992/PRISON.asm:9467` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/cart__post_DRAW_CV224_AT_X07_Y08.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_228_018` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x85,0x76`
- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_228_018.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_228_018` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x85,0x9C`
- `src/levels/_unified/caves/dos__post_DRAW_CV224_AT_X07_Y08.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_228_018` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x85,0xFF`
- `src/levels/_unified/caves/dos__post_INLINE_DRAW_CV_228_018.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_228_018` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x86,0x25`
- `src/levels/_unified/prison/cart__post_DRAW_CV224_AT_X07_Y08.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_228_018` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x56,0xC9`
- …and 3 more

### `INLINE_DRAW_CV_266_005` — 8 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/INLINE_DRAW_CV_266_005.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1307` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1682` (label)
- `src/levels/cartridge_1992/CAVES.asm:14134` (label)
- `src/levels/cartridge_1992/PRISON.asm:9916` (label)
- `src/levels/dos_1992/CAVES.asm:14244` (label)
- `src/levels/dos_1992/PRISON.asm:9840` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/cart__post_DRAW_CV263_AT_X07_Y08.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_266_005` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x88,0xAF`
- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_269_026.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_266_005` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x89,0xEF`
- `src/levels/_unified/caves/dos__post_DRAW_CV263_AT_X07_Y08.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_266_005` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x89,0x38`
- `src/levels/_unified/caves/dos__post_INLINE_DRAW_CV_269_026.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_266_005` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x8A,0x78`
- `src/levels/_unified/prison/cart__post_DRAW_CV263_AT_X07_Y08.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_266_005` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x5A,0x86`
- …and 3 more

### `INLINE_DRAW_CV_220_008` — 8 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/INLINE_DRAW_CV_220_008.inc:1` (label)
- `src/levels/_unified/caves/caves_inline_setters_and_init.inc:1191` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:1566` (label)
- `src/levels/cartridge_1992/CAVES.asm:13786` (label)
- `src/levels/cartridge_1992/PRISON.asm:9511` (label)
- `src/levels/dos_1992/CAVES.asm:13896` (label)
- `src/levels/dos_1992/PRISON.asm:9435` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_216_029.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_220_008` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x85,0x2A`
- `src/levels/_unified/caves/cart__post_INLINE_DRAW_CV_228_019.inc:12` — `je [0x0D], 0x00, INLINE_DRAW_CV_220_008` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x85,0xCA`
- `src/levels/_unified/caves/dos__post_INLINE_DRAW_CV_216_029.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_220_008` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x85,0xB3`
- `src/levels/_unified/caves/dos__post_INLINE_DRAW_CV_228_019.inc:12` — `je [0x0D], 0x00, INLINE_DRAW_CV_220_008` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x86,0x53`
- `src/levels/_unified/prison/cart__post_INLINE_DRAW_CV_216_027.inc:10` — `je [0x0D], 0x00, INLINE_DRAW_CV_220_008` ⇒ `;@raw=0x0A,0x00,0x0D,0x00,0x56,0x7D`
- …and 3 more

### `GUARDED_DRAW_CIN_338_339` — 4 annotated call site(s)

**Definitions:**

- `src/levels/_unified/prison/amiga__post_DRAW_CIN_241.inc:315` (label)
- `src/levels/_unified/prison/amiga__post_DRAW_CIN_241.inc:351` (label)
- `src/levels/_unified/prison/cart__post_INLINE_DRAW_CV_216_028.inc:32` (label)
- `src/levels/_unified/prison/cart__post_INLINE_DRAW_CV_216_028.inc:68` (label)
- `src/levels/_unified/prison/dos__post_INLINE_DRAW_CV_216_028.inc:68` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/prison/amiga__post_DRAW_CIN_241.inc:506` — `call GUARDED_DRAW_CIN_338_339` ⇒ `;@raw=0x04,0x55,0xE9`
- `src/levels/_unified/prison/amiga__post_DRAW_CIN_241.inc:566` — `call GUARDED_DRAW_CIN_338_339` ⇒ `;@raw=0x04,0x55,0xE9`
- `src/levels/_unified/prison/cart__post_INLINE_DRAW_CV_216_028.inc:227` — `call GUARDED_DRAW_CIN_338_339` ⇒ `;@raw=0x04,0x57,0x99`
- `src/levels/_unified/prison/cart__post_INLINE_DRAW_CV_216_028.inc:287` — `call GUARDED_DRAW_CIN_338_339` ⇒ `;@raw=0x04,0x57,0x99`

### `SET_VAR2F_TO_000F` — 3 annotated call site(s)

**Definitions:**

- `src/levels/_unified/_helpers/SET_VAR2F_TO_000F.inc:1` (label)
- `src/levels/_unified/prison/prison_inline_setters_and_init.inc:794` (label)
- `src/levels/cartridge_1992/PRISON.asm:6002` (label)
- `src/levels/chahi_amiga_1991/PRISON.asm:5723` (label)
- `src/levels/dos_1992/PRISON.asm:5939` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/prison/amiga__post_FOLD_BODY_99B_32B55F1E.inc:115` — `jl [0x2C], 0x0A, SET_VAR2F_TO_000F` ⇒ `;@raw=0x0A,0x04,0x2C,0x0A,0x31,0x7E`
- `src/levels/_unified/prison/cart__post_INIT_VARS_2F_29_1.inc:169` — `jl [0x2C], 0x0A, SET_VAR2F_TO_000F` ⇒ `;@raw=0x0A,0x04,0x2C,0x0A,0x32,0xA3`
- `src/levels/_unified/prison/dos__post_FOLD_BODY_99B_32B55F1E.inc:119` — `jl [0x2C], 0x0A, SET_VAR2F_TO_000F` ⇒ `;@raw=0x0A,0x04,0x2C,0x0A,0x31,0xCB`

### `COMMON_VIDEO_204` — 2 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1390` (equ=0x2058)
- `src/levels/_unified/caves/amiga__entry.inc:3017` (equ=0x2058)
- `src/levels/_unified/prison/amiga__entry.inc:2115` (equ=0x2058)
- `src/levels/cartridge_1992/CAPSULE.asm:940` (equ=0x2D6E)
- `src/levels/cartridge_1992/CAVES.asm:1122` (equ=0x2D6E)
- `src/levels/cartridge_1992/PRISON.asm:931` (equ=0x2D6E)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:769` (equ=0x2058)
- `src/levels/chahi_amiga_1991/CAVES.asm:1094` (equ=0x2058)
- `src/levels/chahi_amiga_1991/PRISON.asm:917` (equ=0x2058)
- `src/levels/dos_1992/CAPSULE.asm:947` (equ=0x2D6E)
- `src/levels/dos_1992/CAVES.asm:1136` (equ=0x2D6E)
- `src/levels/dos_1992/PRISON.asm:937` (equ=0x2D6E)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV204_AT_X07_PLUS1_Y08.inc:3` — `video type=0, offset=COMMON_VIDEO_204, x=[0x07], y=[0x08], zoom=0x40` ⇒ `;@raw=0x57,0x16,0xB7,0x07,0x08`
- `src/levels/_unified/_helpers/DRAW_CV204_AT_X07_Y08.inc:2` — `video type=0, offset=COMMON_VIDEO_204, x=[0x07], y=[0x08], zoom=0x40` ⇒ `;@raw=0x57,0x16,0xB7,0x07,0x08`

### `COMMON_VIDEO_352` — 2 annotated call site(s)

**Definitions:**

- `src/levels/cartridge_1992/CAPSULE.asm:1084` (equ=0x09F6)
- `src/levels/cartridge_1992/CAVES.asm:1270` (equ=0x09F6)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:914` (equ=0x09F6)
- `src/levels/chahi_amiga_1991/CAVES.asm:1242` (equ=0x09F6)
- `src/levels/dos_1992/CAPSULE.asm:1091` (equ=0x09F6)
- `src/levels/dos_1992/CAVES.asm:1284` (equ=0x09F6)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV352_STEP_RIGHT3.inc:3` — `video type=0, offset=COMMON_VIDEO_352, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x04,0xFB,0x01,0x02`
- `src/levels/_unified/_helpers/STEP_DRAW_CV352_LEFT4_RIGHT1.inc:3` — `video type=0, offset=COMMON_VIDEO_352, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x04,0xFB,0x01,0x02`

### `COMMON_VIDEO_097` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1283` (equ=0x5420)
- `src/levels/_unified/caves/amiga__entry.inc:2910` (equ=0x5420)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:77` (equ=0x3650)
- `src/levels/_unified/prison/amiga__entry.inc:2008` (equ=0x5420)
- `src/levels/cartridge_1992/CAPSULE.asm:833` (equ=0x3650)
- `src/levels/cartridge_1992/CAVES.asm:1015` (equ=0x3650)
- `src/levels/cartridge_1992/LAKE.asm:794` (equ=0x3650)
- `src/levels/cartridge_1992/PRISON.asm:824` (equ=0x3650)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:662` (equ=0x5420)
- `src/levels/chahi_amiga_1991/CAVES.asm:987` (equ=0x5420)
- `src/levels/chahi_amiga_1991/PRISON.asm:810` (equ=0x5420)
- `src/levels/dos_1992/CAPSULE.asm:840` (equ=0x3650)
- `src/levels/dos_1992/CAVES.asm:1029` (equ=0x3650)
- `src/levels/dos_1992/LAKE.asm:794` (equ=0x3650)
- `src/levels/dos_1992/PRISON.asm:830` (equ=0x3650)
- `src/levels/gba_2004/LAKE.asm:784` (equ=0x3650)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV097_AT_X01_Y02.inc:2` — `video type=0, offset=COMMON_VIDEO_097, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1B,0x28,0x01,0x02`

### `COMMON_VIDEO_099` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1285` (equ=0x037C)
- `src/levels/_unified/caves/amiga__entry.inc:2912` (equ=0x037C)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:79` (equ=0x3674)
- `src/levels/_unified/prison/amiga__entry.inc:2010` (equ=0x037C)
- `src/levels/cartridge_1992/CAPSULE.asm:835` (equ=0x3674)
- `src/levels/cartridge_1992/CAVES.asm:1017` (equ=0x3674)
- `src/levels/cartridge_1992/LAKE.asm:796` (equ=0x3674)
- `src/levels/cartridge_1992/PRISON.asm:826` (equ=0x3674)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:664` (equ=0x037C)
- `src/levels/chahi_amiga_1991/CAVES.asm:989` (equ=0x037C)
- `src/levels/chahi_amiga_1991/PRISON.asm:812` (equ=0x037C)
- `src/levels/dos_1992/CAPSULE.asm:842` (equ=0x3674)
- `src/levels/dos_1992/CAVES.asm:1031` (equ=0x3674)
- `src/levels/dos_1992/LAKE.asm:796` (equ=0x3674)
- `src/levels/dos_1992/PRISON.asm:832` (equ=0x3674)
- `src/levels/gba_2004/LAKE.asm:786` (equ=0x3674)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV099_AT_X01_Y02.inc:2` — `video type=0, offset=COMMON_VIDEO_099, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1B,0x3A,0x01,0x02`

### `COMMON_VIDEO_101` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1287` (equ=0x0764)
- `src/levels/_unified/caves/amiga__entry.inc:2914` (equ=0x0764)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:81` (equ=0x3658)
- `src/levels/_unified/prison/amiga__entry.inc:2012` (equ=0x0764)
- `src/levels/cartridge_1992/CAPSULE.asm:837` (equ=0x3658)
- `src/levels/cartridge_1992/CAVES.asm:1019` (equ=0x3658)
- `src/levels/cartridge_1992/LAKE.asm:798` (equ=0x3658)
- `src/levels/cartridge_1992/PRISON.asm:828` (equ=0x3658)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:666` (equ=0x0764)
- `src/levels/chahi_amiga_1991/CAVES.asm:991` (equ=0x0764)
- `src/levels/chahi_amiga_1991/PRISON.asm:814` (equ=0x0764)
- `src/levels/dos_1992/CAPSULE.asm:844` (equ=0x3658)
- `src/levels/dos_1992/CAVES.asm:1033` (equ=0x3658)
- `src/levels/dos_1992/LAKE.asm:798` (equ=0x3658)
- `src/levels/dos_1992/PRISON.asm:834` (equ=0x3658)
- `src/levels/gba_2004/LAKE.asm:788` (equ=0x3658)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV101_AT_X01_Y02.inc:2` — `video type=0, offset=COMMON_VIDEO_101, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1B,0x2C,0x01,0x02`

### `COMMON_VIDEO_103` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1289` (equ=0x0790)
- `src/levels/_unified/caves/amiga__entry.inc:2916` (equ=0x0790)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:83` (equ=0x3660)
- `src/levels/_unified/prison/amiga__entry.inc:2014` (equ=0x0790)
- `src/levels/cartridge_1992/CAPSULE.asm:839` (equ=0x3660)
- `src/levels/cartridge_1992/CAVES.asm:1021` (equ=0x3660)
- `src/levels/cartridge_1992/LAKE.asm:800` (equ=0x3660)
- `src/levels/cartridge_1992/PRISON.asm:830` (equ=0x3660)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:668` (equ=0x0790)
- `src/levels/chahi_amiga_1991/CAVES.asm:993` (equ=0x0790)
- `src/levels/chahi_amiga_1991/PRISON.asm:816` (equ=0x0790)
- `src/levels/dos_1992/CAPSULE.asm:846` (equ=0x3660)
- `src/levels/dos_1992/CAVES.asm:1035` (equ=0x3660)
- `src/levels/dos_1992/LAKE.asm:800` (equ=0x3660)
- `src/levels/dos_1992/PRISON.asm:836` (equ=0x3660)
- `src/levels/gba_2004/LAKE.asm:790` (equ=0x3660)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV103_AT_X01_Y02.inc:2` — `video type=0, offset=COMMON_VIDEO_103, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1B,0x30,0x01,0x02`

### `COMMON_VIDEO_105` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1291` (equ=0x07BC)
- `src/levels/_unified/caves/amiga__entry.inc:2918` (equ=0x07BC)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:85` (equ=0x366C)
- `src/levels/_unified/prison/amiga__entry.inc:2016` (equ=0x07BC)
- `src/levels/cartridge_1992/CAPSULE.asm:841` (equ=0x366C)
- `src/levels/cartridge_1992/CAVES.asm:1023` (equ=0x366C)
- `src/levels/cartridge_1992/LAKE.asm:802` (equ=0x366C)
- `src/levels/cartridge_1992/PRISON.asm:832` (equ=0x366C)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:670` (equ=0x07BC)
- `src/levels/chahi_amiga_1991/CAVES.asm:995` (equ=0x07BC)
- `src/levels/chahi_amiga_1991/PRISON.asm:818` (equ=0x07BC)
- `src/levels/dos_1992/CAPSULE.asm:848` (equ=0x366C)
- `src/levels/dos_1992/CAVES.asm:1037` (equ=0x366C)
- `src/levels/dos_1992/LAKE.asm:802` (equ=0x366C)
- `src/levels/dos_1992/PRISON.asm:838` (equ=0x366C)
- `src/levels/gba_2004/LAKE.asm:792` (equ=0x366C)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV105_AT_X01_Y02.inc:2` — `video type=0, offset=COMMON_VIDEO_105, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1B,0x36,0x01,0x02`

### `COMMON_VIDEO_107` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1293` (equ=0x07E8)
- `src/levels/_unified/caves/amiga__entry.inc:2920` (equ=0x07E8)
- `src/levels/_unified/prison/amiga__entry.inc:2018` (equ=0x07E8)
- `src/levels/cartridge_1992/CAPSULE.asm:843` (equ=0x3630)
- `src/levels/cartridge_1992/CAVES.asm:1025` (equ=0x3630)
- `src/levels/cartridge_1992/LAKE.asm:804` (equ=0x3630)
- `src/levels/cartridge_1992/PRISON.asm:834` (equ=0x3630)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:672` (equ=0x07E8)
- `src/levels/chahi_amiga_1991/CAVES.asm:997` (equ=0x07E8)
- `src/levels/chahi_amiga_1991/PRISON.asm:820` (equ=0x07E8)
- `src/levels/dos_1992/CAPSULE.asm:850` (equ=0x3630)
- `src/levels/dos_1992/CAVES.asm:1039` (equ=0x3630)
- `src/levels/dos_1992/LAKE.asm:804` (equ=0x3630)
- `src/levels/dos_1992/PRISON.asm:840` (equ=0x3630)
- `src/levels/gba_2004/LAKE.asm:794` (equ=0x3630)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV107_AT_X01_Y02.inc:2` — `video type=0, offset=COMMON_VIDEO_107, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1B,0x18,0x01,0x02`

### `COMMON_VIDEO_109` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1295` (equ=0x0814)
- `src/levels/_unified/caves/amiga__entry.inc:2922` (equ=0x0814)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:88` (equ=0x3638)
- `src/levels/_unified/prison/amiga__entry.inc:2020` (equ=0x0814)
- `src/levels/cartridge_1992/CAPSULE.asm:845` (equ=0x3638)
- `src/levels/cartridge_1992/CAVES.asm:1027` (equ=0x3638)
- `src/levels/cartridge_1992/LAKE.asm:806` (equ=0x3638)
- `src/levels/cartridge_1992/PRISON.asm:836` (equ=0x3638)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:674` (equ=0x0814)
- `src/levels/chahi_amiga_1991/CAVES.asm:999` (equ=0x0814)
- `src/levels/chahi_amiga_1991/PRISON.asm:822` (equ=0x0814)
- `src/levels/dos_1992/CAPSULE.asm:852` (equ=0x3638)
- `src/levels/dos_1992/CAVES.asm:1041` (equ=0x3638)
- `src/levels/dos_1992/LAKE.asm:806` (equ=0x3638)
- `src/levels/dos_1992/PRISON.asm:842` (equ=0x3638)
- `src/levels/gba_2004/LAKE.asm:796` (equ=0x3638)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV109_AT_X01_Y02.inc:2` — `video type=0, offset=COMMON_VIDEO_109, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1B,0x1C,0x01,0x02`

### `COMMON_VIDEO_111` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1297` (equ=0x0874)
- `src/levels/_unified/caves/amiga__entry.inc:2924` (equ=0x0874)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:90` (equ=0x3640)
- `src/levels/_unified/prison/amiga__entry.inc:2022` (equ=0x0874)
- `src/levels/cartridge_1992/CAPSULE.asm:847` (equ=0x3640)
- `src/levels/cartridge_1992/CAVES.asm:1029` (equ=0x3640)
- `src/levels/cartridge_1992/LAKE.asm:808` (equ=0x3640)
- `src/levels/cartridge_1992/PRISON.asm:838` (equ=0x3640)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:676` (equ=0x0874)
- `src/levels/chahi_amiga_1991/CAVES.asm:1001` (equ=0x0874)
- `src/levels/chahi_amiga_1991/PRISON.asm:824` (equ=0x0874)
- `src/levels/dos_1992/CAPSULE.asm:854` (equ=0x3640)
- `src/levels/dos_1992/CAVES.asm:1043` (equ=0x3640)
- `src/levels/dos_1992/LAKE.asm:808` (equ=0x3640)
- `src/levels/dos_1992/PRISON.asm:844` (equ=0x3640)
- `src/levels/gba_2004/LAKE.asm:798` (equ=0x3640)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV111_AT_X01_Y02.inc:2` — `video type=0, offset=COMMON_VIDEO_111, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1B,0x20,0x01,0x02`

### `COMMON_VIDEO_113` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1299` (equ=0x0020)
- `src/levels/_unified/caves/amiga__entry.inc:2926` (equ=0x0020)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:92` (equ=0x3648)
- `src/levels/_unified/prison/amiga__entry.inc:2024` (equ=0x0020)
- `src/levels/cartridge_1992/CAPSULE.asm:849` (equ=0x3648)
- `src/levels/cartridge_1992/CAVES.asm:1031` (equ=0x3648)
- `src/levels/cartridge_1992/LAKE.asm:810` (equ=0x3648)
- `src/levels/cartridge_1992/PRISON.asm:840` (equ=0x3648)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:678` (equ=0x0020)
- `src/levels/chahi_amiga_1991/CAVES.asm:1003` (equ=0x0020)
- `src/levels/chahi_amiga_1991/PRISON.asm:826` (equ=0x0020)
- `src/levels/dos_1992/CAPSULE.asm:856` (equ=0x3648)
- `src/levels/dos_1992/CAVES.asm:1045` (equ=0x3648)
- `src/levels/dos_1992/LAKE.asm:810` (equ=0x3648)
- `src/levels/dos_1992/PRISON.asm:846` (equ=0x3648)
- `src/levels/gba_2004/LAKE.asm:800` (equ=0x3648)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV113_AT_X01_Y02.inc:2` — `video type=0, offset=COMMON_VIDEO_113, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1B,0x24,0x01,0x02`

### `COMMON_VIDEO_224` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1410` (equ=0x3116)
- `src/levels/_unified/caves/amiga__entry.inc:3037` (equ=0x3116)
- `src/levels/_unified/prison/amiga__entry.inc:2135` (equ=0x3116)
- `src/levels/cartridge_1992/CAPSULE.asm:960` (equ=0x2D4E)
- `src/levels/cartridge_1992/CAVES.asm:1142` (equ=0x2D4E)
- `src/levels/cartridge_1992/PRISON.asm:951` (equ=0x2D4E)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:789` (equ=0x3116)
- `src/levels/chahi_amiga_1991/CAVES.asm:1114` (equ=0x3116)
- `src/levels/chahi_amiga_1991/PRISON.asm:937` (equ=0x3116)
- `src/levels/dos_1992/CAPSULE.asm:967` (equ=0x2D4E)
- `src/levels/dos_1992/CAVES.asm:1156` (equ=0x2D4E)
- `src/levels/dos_1992/PRISON.asm:957` (equ=0x2D4E)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV224_AT_X07_Y08.inc:2` — `video type=0, offset=COMMON_VIDEO_224, x=[0x07], y=[0x08], zoom=0x40` ⇒ `;@raw=0x57,0x16,0xA7,0x07,0x08`

### `COMMON_VIDEO_246` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1432` (equ=0x426C)
- `src/levels/_unified/capsule/cart__entry.inc:1572` (equ=0x21A8)
- `src/levels/_unified/capsule/dos__entry.inc:1579` (equ=0x21A8)
- `src/levels/_unified/caves/amiga__entry.inc:3059` (equ=0x426C)
- `src/levels/_unified/caves/cart__entry.inc:3056` (equ=0x21A8)
- `src/levels/_unified/caves/dos__entry.inc:3070` (equ=0x21A8)
- `src/levels/_unified/prison/amiga__entry.inc:2157` (equ=0x426C)
- `src/levels/cartridge_1992/CAPSULE.asm:982` (equ=0x21A8)
- `src/levels/cartridge_1992/CAVES.asm:1164` (equ=0x21A8)
- `src/levels/cartridge_1992/PRISON.asm:973` (equ=0x21A8)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:811` (equ=0x426C)
- `src/levels/chahi_amiga_1991/CAVES.asm:1136` (equ=0x426C)
- `src/levels/chahi_amiga_1991/PRISON.asm:959` (equ=0x426C)
- `src/levels/dos_1992/CAPSULE.asm:989` (equ=0x21A8)
- `src/levels/dos_1992/CAVES.asm:1178` (equ=0x21A8)
- `src/levels/dos_1992/PRISON.asm:979` (equ=0x21A8)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV246_AT_X07_Y08.inc:2` — `video type=0, offset=COMMON_VIDEO_246, x=[0x07], y=[0x08], zoom=0x40` ⇒ `;@raw=0x57,0x10,0xD4,0x07,0x08`

### `COMMON_VIDEO_249` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1435` (equ=0x3A64)
- `src/levels/_unified/capsule/cart__entry.inc:1575` (equ=0x21D6)
- `src/levels/_unified/capsule/dos__entry.inc:1582` (equ=0x21D6)
- `src/levels/_unified/caves/amiga__entry.inc:3062` (equ=0x3A64)
- `src/levels/_unified/caves/cart__entry.inc:3059` (equ=0x21D6)
- `src/levels/_unified/caves/dos__entry.inc:3073` (equ=0x21D6)
- `src/levels/_unified/prison/amiga__entry.inc:2160` (equ=0x3A64)
- `src/levels/cartridge_1992/CAPSULE.asm:985` (equ=0x21D6)
- `src/levels/cartridge_1992/CAVES.asm:1167` (equ=0x21D6)
- `src/levels/cartridge_1992/PRISON.asm:976` (equ=0x21D6)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:814` (equ=0x3A64)
- `src/levels/chahi_amiga_1991/CAVES.asm:1139` (equ=0x3A64)
- `src/levels/chahi_amiga_1991/PRISON.asm:962` (equ=0x3A64)
- `src/levels/dos_1992/CAPSULE.asm:992` (equ=0x21D6)
- `src/levels/dos_1992/CAVES.asm:1181` (equ=0x21D6)
- `src/levels/dos_1992/PRISON.asm:982` (equ=0x21D6)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV249_AT_X07_Y08.inc:2` — `video type=0, offset=COMMON_VIDEO_249, x=[0x07], y=[0x08], zoom=0x40` ⇒ `;@raw=0x57,0x10,0xEB,0x07,0x08`

### `COMMON_VIDEO_259` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1445` (equ=0x34D6)
- `src/levels/_unified/capsule/cart__entry.inc:1585` (equ=0x224C)
- `src/levels/_unified/capsule/dos__entry.inc:1592` (equ=0x224C)
- `src/levels/_unified/caves/amiga__entry.inc:3072` (equ=0x34D6)
- `src/levels/_unified/caves/cart__entry.inc:3069` (equ=0x224C)
- `src/levels/_unified/caves/dos__entry.inc:3083` (equ=0x224C)
- `src/levels/_unified/prison/amiga__entry.inc:2170` (equ=0x34D6)
- `src/levels/cartridge_1992/CAPSULE.asm:995` (equ=0x224C)
- `src/levels/cartridge_1992/CAVES.asm:1177` (equ=0x224C)
- `src/levels/cartridge_1992/PRISON.asm:986` (equ=0x224C)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:824` (equ=0x34D6)
- `src/levels/chahi_amiga_1991/CAVES.asm:1149` (equ=0x34D6)
- `src/levels/chahi_amiga_1991/PRISON.asm:972` (equ=0x34D6)
- `src/levels/dos_1992/CAPSULE.asm:1002` (equ=0x224C)
- `src/levels/dos_1992/CAVES.asm:1191` (equ=0x224C)
- `src/levels/dos_1992/PRISON.asm:992` (equ=0x224C)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV259_AT_X07_Y08.inc:2` — `video type=0, offset=COMMON_VIDEO_259, x=[0x07], y=[0x08], zoom=0x40` ⇒ `;@raw=0x57,0x11,0x26,0x07,0x08`

### `COMMON_VIDEO_261` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1447` (equ=0x34DE)
- `src/levels/_unified/capsule/cart__entry.inc:1587` (equ=0x2276)
- `src/levels/_unified/capsule/dos__entry.inc:1594` (equ=0x2276)
- `src/levels/_unified/caves/amiga__entry.inc:3074` (equ=0x34DE)
- `src/levels/_unified/caves/cart__entry.inc:3071` (equ=0x2276)
- `src/levels/_unified/caves/dos__entry.inc:3085` (equ=0x2276)
- `src/levels/_unified/prison/amiga__entry.inc:2172` (equ=0x34DE)
- `src/levels/cartridge_1992/CAPSULE.asm:997` (equ=0x2276)
- `src/levels/cartridge_1992/CAVES.asm:1179` (equ=0x2276)
- `src/levels/cartridge_1992/PRISON.asm:988` (equ=0x2276)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:826` (equ=0x34DE)
- `src/levels/chahi_amiga_1991/CAVES.asm:1151` (equ=0x34DE)
- `src/levels/chahi_amiga_1991/PRISON.asm:974` (equ=0x34DE)
- `src/levels/dos_1992/CAPSULE.asm:1004` (equ=0x2276)
- `src/levels/dos_1992/CAVES.asm:1193` (equ=0x2276)
- `src/levels/dos_1992/PRISON.asm:994` (equ=0x2276)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV261_AT_X07_Y08.inc:2` — `video type=0, offset=COMMON_VIDEO_261, x=[0x07], y=[0x08], zoom=0x40` ⇒ `;@raw=0x57,0x11,0x3B,0x07,0x08`

### `COMMON_VIDEO_263` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1449` (equ=0x34E6)
- `src/levels/_unified/caves/amiga__entry.inc:3076` (equ=0x34E6)
- `src/levels/_unified/prison/amiga__entry.inc:2174` (equ=0x34E6)
- `src/levels/cartridge_1992/CAPSULE.asm:999` (equ=0x320A)
- `src/levels/cartridge_1992/CAVES.asm:1181` (equ=0x320A)
- `src/levels/cartridge_1992/PRISON.asm:990` (equ=0x320A)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:828` (equ=0x34E6)
- `src/levels/chahi_amiga_1991/CAVES.asm:1153` (equ=0x34E6)
- `src/levels/chahi_amiga_1991/PRISON.asm:976` (equ=0x34E6)
- `src/levels/dos_1992/CAPSULE.asm:1006` (equ=0x320A)
- `src/levels/dos_1992/CAVES.asm:1195` (equ=0x320A)
- `src/levels/dos_1992/PRISON.asm:996` (equ=0x320A)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV263_AT_X07_Y08.inc:2` — `video type=0, offset=COMMON_VIDEO_263, x=[0x07], y=[0x08], zoom=0x40` ⇒ `;@raw=0x57,0x19,0x05,0x07,0x08`

### `COMMON_VIDEO_061` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1249` (equ=0x33AC)
- `src/levels/_unified/caves/amiga__entry.inc:2876` (equ=0x33AC)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:44` (equ=0x037C)
- `src/levels/_unified/prison/amiga__entry.inc:1972` (equ=0x33AC)
- `src/levels/cartridge_1992/CAPSULE.asm:797` (equ=0x037C)
- `src/levels/cartridge_1992/CAVES.asm:979` (equ=0x037C)
- `src/levels/cartridge_1992/LAKE.asm:758` (equ=0x037C)
- `src/levels/cartridge_1992/PRISON.asm:788` (equ=0x037C)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:628` (equ=0x33AC)
- `src/levels/chahi_amiga_1991/CAVES.asm:953` (equ=0x33AC)
- `src/levels/chahi_amiga_1991/PRISON.asm:774` (equ=0x33AC)
- `src/levels/dos_1992/CAPSULE.asm:804` (equ=0x037C)
- `src/levels/dos_1992/CAVES.asm:993` (equ=0x037C)
- `src/levels/dos_1992/LAKE.asm:758` (equ=0x037C)
- `src/levels/dos_1992/PRISON.asm:794` (equ=0x037C)
- `src/levels/gba_2004/LAKE.asm:748` (equ=0x037C)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_061.inc:2` — `video type=0, offset=COMMON_VIDEO_061, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x01,0xBE,0x01,0x02`

### `COMMON_VIDEO_063` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1251` (equ=0x33B6)
- `src/levels/_unified/caves/amiga__entry.inc:2878` (equ=0x33B6)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:46` (equ=0x0764)
- `src/levels/_unified/prison/amiga__entry.inc:1974` (equ=0x33B6)
- `src/levels/cartridge_1992/CAPSULE.asm:799` (equ=0x0764)
- `src/levels/cartridge_1992/CAVES.asm:981` (equ=0x0764)
- `src/levels/cartridge_1992/LAKE.asm:760` (equ=0x0764)
- `src/levels/cartridge_1992/PRISON.asm:790` (equ=0x0764)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:630` (equ=0x33B6)
- `src/levels/chahi_amiga_1991/CAVES.asm:955` (equ=0x33B6)
- `src/levels/chahi_amiga_1991/PRISON.asm:776` (equ=0x33B6)
- `src/levels/dos_1992/CAPSULE.asm:806` (equ=0x0764)
- `src/levels/dos_1992/CAVES.asm:995` (equ=0x0764)
- `src/levels/dos_1992/LAKE.asm:760` (equ=0x0764)
- `src/levels/dos_1992/PRISON.asm:796` (equ=0x0764)
- `src/levels/gba_2004/LAKE.asm:750` (equ=0x0764)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_063.inc:2` — `video type=0, offset=COMMON_VIDEO_063, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x03,0xB2,0x01,0x02`

### `COMMON_VIDEO_065` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1253` (equ=0x33C0)
- `src/levels/_unified/caves/amiga__entry.inc:2880` (equ=0x33C0)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:48` (equ=0x0790)
- `src/levels/_unified/prison/amiga__entry.inc:1976` (equ=0x33C0)
- `src/levels/cartridge_1992/CAPSULE.asm:801` (equ=0x0790)
- `src/levels/cartridge_1992/CAVES.asm:983` (equ=0x0790)
- `src/levels/cartridge_1992/LAKE.asm:762` (equ=0x0790)
- `src/levels/cartridge_1992/PRISON.asm:792` (equ=0x0790)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:632` (equ=0x33C0)
- `src/levels/chahi_amiga_1991/CAVES.asm:957` (equ=0x33C0)
- `src/levels/chahi_amiga_1991/PRISON.asm:778` (equ=0x33C0)
- `src/levels/dos_1992/CAPSULE.asm:808` (equ=0x0790)
- `src/levels/dos_1992/CAVES.asm:997` (equ=0x0790)
- `src/levels/dos_1992/LAKE.asm:762` (equ=0x0790)
- `src/levels/dos_1992/PRISON.asm:798` (equ=0x0790)
- `src/levels/gba_2004/LAKE.asm:752` (equ=0x0790)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_065.inc:2` — `video type=0, offset=COMMON_VIDEO_065, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x03,0xC8,0x01,0x02`

### `COMMON_VIDEO_067` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1255` (equ=0x33CA)
- `src/levels/_unified/caves/amiga__entry.inc:2882` (equ=0x33CA)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:50` (equ=0x07BC)
- `src/levels/_unified/prison/amiga__entry.inc:1978` (equ=0x33CA)
- `src/levels/cartridge_1992/CAPSULE.asm:803` (equ=0x07BC)
- `src/levels/cartridge_1992/CAVES.asm:985` (equ=0x07BC)
- `src/levels/cartridge_1992/LAKE.asm:764` (equ=0x07BC)
- `src/levels/cartridge_1992/PRISON.asm:794` (equ=0x07BC)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:634` (equ=0x33CA)
- `src/levels/chahi_amiga_1991/CAVES.asm:959` (equ=0x33CA)
- `src/levels/chahi_amiga_1991/PRISON.asm:780` (equ=0x33CA)
- `src/levels/dos_1992/CAPSULE.asm:810` (equ=0x07BC)
- `src/levels/dos_1992/CAVES.asm:999` (equ=0x07BC)
- `src/levels/dos_1992/LAKE.asm:764` (equ=0x07BC)
- `src/levels/dos_1992/PRISON.asm:800` (equ=0x07BC)
- `src/levels/gba_2004/LAKE.asm:754` (equ=0x07BC)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_067.inc:2` — `video type=0, offset=COMMON_VIDEO_067, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x03,0xDE,0x01,0x02`

### `COMMON_VIDEO_069` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1257` (equ=0x33D4)
- `src/levels/_unified/caves/amiga__entry.inc:2884` (equ=0x33D4)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:52` (equ=0x07E8)
- `src/levels/_unified/prison/amiga__entry.inc:1980` (equ=0x33D4)
- `src/levels/cartridge_1992/CAPSULE.asm:805` (equ=0x07E8)
- `src/levels/cartridge_1992/CAVES.asm:987` (equ=0x07E8)
- `src/levels/cartridge_1992/LAKE.asm:766` (equ=0x07E8)
- `src/levels/cartridge_1992/PRISON.asm:796` (equ=0x07E8)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:636` (equ=0x33D4)
- `src/levels/chahi_amiga_1991/CAVES.asm:961` (equ=0x33D4)
- `src/levels/chahi_amiga_1991/PRISON.asm:782` (equ=0x33D4)
- `src/levels/dos_1992/CAPSULE.asm:812` (equ=0x07E8)
- `src/levels/dos_1992/CAVES.asm:1001` (equ=0x07E8)
- `src/levels/dos_1992/LAKE.asm:766` (equ=0x07E8)
- `src/levels/dos_1992/PRISON.asm:802` (equ=0x07E8)
- `src/levels/gba_2004/LAKE.asm:756` (equ=0x07E8)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_069.inc:2` — `video type=0, offset=COMMON_VIDEO_069, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x03,0xF4,0x01,0x02`

### `COMMON_VIDEO_071` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1259` (equ=0x33DE)
- `src/levels/_unified/caves/amiga__entry.inc:2886` (equ=0x33DE)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:54` (equ=0x0844)
- `src/levels/_unified/prison/amiga__entry.inc:1982` (equ=0x33DE)
- `src/levels/cartridge_1992/CAPSULE.asm:807` (equ=0x0844)
- `src/levels/cartridge_1992/CAVES.asm:989` (equ=0x0844)
- `src/levels/cartridge_1992/LAKE.asm:768` (equ=0x0844)
- `src/levels/cartridge_1992/PRISON.asm:798` (equ=0x0844)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:638` (equ=0x33DE)
- `src/levels/chahi_amiga_1991/CAVES.asm:963` (equ=0x33DE)
- `src/levels/chahi_amiga_1991/PRISON.asm:784` (equ=0x33DE)
- `src/levels/dos_1992/CAPSULE.asm:814` (equ=0x0844)
- `src/levels/dos_1992/CAVES.asm:1003` (equ=0x0844)
- `src/levels/dos_1992/LAKE.asm:768` (equ=0x0844)
- `src/levels/dos_1992/PRISON.asm:804` (equ=0x0844)
- `src/levels/gba_2004/LAKE.asm:758` (equ=0x0844)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_071.inc:2` — `video type=0, offset=COMMON_VIDEO_071, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x04,0x22,0x01,0x02`

### `COMMON_VIDEO_072` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1260` (equ=0x117E)
- `src/levels/_unified/caves/amiga__entry.inc:2887` (equ=0x117E)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:55` (equ=0x0874)
- `src/levels/_unified/prison/amiga__entry.inc:1983` (equ=0x117E)
- `src/levels/cartridge_1992/CAPSULE.asm:808` (equ=0x0874)
- `src/levels/cartridge_1992/CAVES.asm:990` (equ=0x0874)
- `src/levels/cartridge_1992/LAKE.asm:769` (equ=0x0874)
- `src/levels/cartridge_1992/PRISON.asm:799` (equ=0x0874)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:639` (equ=0x117E)
- `src/levels/chahi_amiga_1991/CAVES.asm:964` (equ=0x117E)
- `src/levels/chahi_amiga_1991/PRISON.asm:785` (equ=0x117E)
- `src/levels/dos_1992/CAPSULE.asm:815` (equ=0x0874)
- `src/levels/dos_1992/CAVES.asm:1004` (equ=0x0874)
- `src/levels/dos_1992/LAKE.asm:769` (equ=0x0874)
- `src/levels/dos_1992/PRISON.asm:805` (equ=0x0874)
- `src/levels/gba_2004/LAKE.asm:759` (equ=0x0874)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_072.inc:2` — `video type=0, offset=COMMON_VIDEO_072, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x04,0x3A,0x01,0x02`

### `COMMON_VIDEO_073` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1261` (equ=0x33E8)
- `src/levels/_unified/caves/amiga__entry.inc:2888` (equ=0x33E8)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:56` (equ=0x08A0)
- `src/levels/_unified/prison/amiga__entry.inc:1984` (equ=0x33E8)
- `src/levels/cartridge_1992/CAPSULE.asm:809` (equ=0x08A0)
- `src/levels/cartridge_1992/CAVES.asm:991` (equ=0x08A0)
- `src/levels/cartridge_1992/LAKE.asm:770` (equ=0x08A0)
- `src/levels/cartridge_1992/PRISON.asm:800` (equ=0x08A0)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:640` (equ=0x33E8)
- `src/levels/chahi_amiga_1991/CAVES.asm:965` (equ=0x33E8)
- `src/levels/chahi_amiga_1991/PRISON.asm:786` (equ=0x33E8)
- `src/levels/dos_1992/CAPSULE.asm:816` (equ=0x08A0)
- `src/levels/dos_1992/CAVES.asm:1005` (equ=0x08A0)
- `src/levels/dos_1992/LAKE.asm:770` (equ=0x08A0)
- `src/levels/dos_1992/PRISON.asm:806` (equ=0x08A0)
- `src/levels/gba_2004/LAKE.asm:760` (equ=0x08A0)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_073.inc:2` — `video type=0, offset=COMMON_VIDEO_073, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x04,0x50,0x01,0x02`

### `COMMON_VIDEO_074` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1262` (equ=0x0CBA)
- `src/levels/_unified/caves/amiga__entry.inc:2889` (equ=0x0CBA)
- `src/levels/_unified/lake/opening_bg_droplet_sprinkles.inc:1` (equ=0x0020)
- `src/levels/_unified/prison/amiga__entry.inc:1985` (equ=0x0CBA)
- `src/levels/cartridge_1992/CAPSULE.asm:810` (equ=0x0020)
- `src/levels/cartridge_1992/CAVES.asm:992` (equ=0x0020)
- `src/levels/cartridge_1992/LAKE.asm:595` (equ=0x0020)
- `src/levels/cartridge_1992/LAKE.asm:771` (equ=0x0020)
- `src/levels/cartridge_1992/PRISON.asm:801` (equ=0x0020)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:641` (equ=0x0CBA)
- `src/levels/chahi_amiga_1991/CAVES.asm:966` (equ=0x0CBA)
- `src/levels/chahi_amiga_1991/LAKE.asm:655` (equ=0x0020)
- `src/levels/chahi_amiga_1991/PRISON.asm:787` (equ=0x0CBA)
- `src/levels/dos_1992/CAPSULE.asm:817` (equ=0x0020)
- `src/levels/dos_1992/CAVES.asm:1006` (equ=0x0020)
- `src/levels/dos_1992/LAKE.asm:595` (equ=0x0020)
- `src/levels/dos_1992/LAKE.asm:771` (equ=0x0020)
- `src/levels/dos_1992/PRISON.asm:807` (equ=0x0020)
- `src/levels/gba_2004/LAKE.asm:595` (equ=0x0020)
- `src/levels/gba_2004/LAKE.asm:761` (equ=0x0020)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_074.inc:2` — `video type=0, offset=COMMON_VIDEO_074, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x00,0x10,0x01,0x02`

### `COMMON_VIDEO_075` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1263` (equ=0x0D48)
- `src/levels/_unified/caves/amiga__entry.inc:2890` (equ=0x0D48)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:57` (equ=0x00B4)
- `src/levels/_unified/prison/amiga__entry.inc:1986` (equ=0x0D48)
- `src/levels/cartridge_1992/CAPSULE.asm:811` (equ=0x00B4)
- `src/levels/cartridge_1992/CAVES.asm:993` (equ=0x00B4)
- `src/levels/cartridge_1992/LAKE.asm:772` (equ=0x00B4)
- `src/levels/cartridge_1992/PRISON.asm:802` (equ=0x00B4)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:642` (equ=0x0D48)
- `src/levels/chahi_amiga_1991/CAVES.asm:967` (equ=0x0D48)
- `src/levels/chahi_amiga_1991/PRISON.asm:788` (equ=0x0D48)
- `src/levels/dos_1992/CAPSULE.asm:818` (equ=0x00B4)
- `src/levels/dos_1992/CAVES.asm:1007` (equ=0x00B4)
- `src/levels/dos_1992/LAKE.asm:772` (equ=0x00B4)
- `src/levels/dos_1992/PRISON.asm:808` (equ=0x00B4)
- `src/levels/gba_2004/LAKE.asm:762` (equ=0x00B4)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_075.inc:2` — `video type=0, offset=COMMON_VIDEO_075, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x00,0x5A,0x01,0x02`

### `COMMON_VIDEO_076` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1264` (equ=0x0DB6)
- `src/levels/_unified/caves/amiga__entry.inc:2891` (equ=0x0DB6)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:58` (equ=0x0128)
- `src/levels/_unified/prison/amiga__entry.inc:1987` (equ=0x0DB6)
- `src/levels/cartridge_1992/CAPSULE.asm:812` (equ=0x0128)
- `src/levels/cartridge_1992/CAVES.asm:994` (equ=0x0128)
- `src/levels/cartridge_1992/LAKE.asm:773` (equ=0x0128)
- `src/levels/cartridge_1992/PRISON.asm:803` (equ=0x0128)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:643` (equ=0x0DB6)
- `src/levels/chahi_amiga_1991/CAVES.asm:968` (equ=0x0DB6)
- `src/levels/chahi_amiga_1991/PRISON.asm:789` (equ=0x0DB6)
- `src/levels/dos_1992/CAPSULE.asm:819` (equ=0x0128)
- `src/levels/dos_1992/CAVES.asm:1008` (equ=0x0128)
- `src/levels/dos_1992/LAKE.asm:773` (equ=0x0128)
- `src/levels/dos_1992/PRISON.asm:809` (equ=0x0128)
- `src/levels/gba_2004/LAKE.asm:763` (equ=0x0128)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_076.inc:2` — `video type=0, offset=COMMON_VIDEO_076, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x00,0x94,0x01,0x02`

### `COMMON_VIDEO_077` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1265` (equ=0x3366)
- `src/levels/_unified/caves/amiga__entry.inc:2892` (equ=0x3366)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:59` (equ=0x01B0)
- `src/levels/_unified/prison/amiga__entry.inc:1988` (equ=0x3366)
- `src/levels/cartridge_1992/CAPSULE.asm:813` (equ=0x01B0)
- `src/levels/cartridge_1992/CAVES.asm:995` (equ=0x01B0)
- `src/levels/cartridge_1992/LAKE.asm:774` (equ=0x01B0)
- `src/levels/cartridge_1992/PRISON.asm:804` (equ=0x01B0)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:644` (equ=0x3366)
- `src/levels/chahi_amiga_1991/CAVES.asm:969` (equ=0x3366)
- `src/levels/chahi_amiga_1991/PRISON.asm:790` (equ=0x3366)
- `src/levels/dos_1992/CAPSULE.asm:820` (equ=0x01B0)
- `src/levels/dos_1992/CAVES.asm:1009` (equ=0x01B0)
- `src/levels/dos_1992/LAKE.asm:774` (equ=0x01B0)
- `src/levels/dos_1992/PRISON.asm:810` (equ=0x01B0)
- `src/levels/gba_2004/LAKE.asm:764` (equ=0x01B0)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_077.inc:2` — `video type=0, offset=COMMON_VIDEO_077, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x00,0xD8,0x01,0x02`

### `COMMON_VIDEO_080` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1268` (equ=0x0EB6)
- `src/levels/_unified/caves/amiga__entry.inc:2895` (equ=0x0EB6)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:62` (equ=0x02AC)
- `src/levels/_unified/prison/amiga__entry.inc:1991` (equ=0x0EB6)
- `src/levels/cartridge_1992/CAPSULE.asm:816` (equ=0x02AC)
- `src/levels/cartridge_1992/CAVES.asm:998` (equ=0x02AC)
- `src/levels/cartridge_1992/LAKE.asm:777` (equ=0x02AC)
- `src/levels/cartridge_1992/PRISON.asm:807` (equ=0x02AC)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:647` (equ=0x0EB6)
- `src/levels/chahi_amiga_1991/CAVES.asm:972` (equ=0x0EB6)
- `src/levels/chahi_amiga_1991/PRISON.asm:793` (equ=0x0EB6)
- `src/levels/dos_1992/CAPSULE.asm:823` (equ=0x02AC)
- `src/levels/dos_1992/CAVES.asm:1012` (equ=0x02AC)
- `src/levels/dos_1992/LAKE.asm:777` (equ=0x02AC)
- `src/levels/dos_1992/PRISON.asm:813` (equ=0x02AC)
- `src/levels/gba_2004/LAKE.asm:767` (equ=0x02AC)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_080.inc:2` — `video type=0, offset=COMMON_VIDEO_080, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x01,0x56,0x01,0x02`

### `COMMON_VIDEO_100` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1286` (equ=0x332A)
- `src/levels/_unified/caves/amiga__entry.inc:2913` (equ=0x332A)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:80` (equ=0x1530)
- `src/levels/_unified/prison/amiga__entry.inc:2011` (equ=0x332A)
- `src/levels/cartridge_1992/CAPSULE.asm:836` (equ=0x1530)
- `src/levels/cartridge_1992/CAVES.asm:1018` (equ=0x1530)
- `src/levels/cartridge_1992/LAKE.asm:797` (equ=0x1530)
- `src/levels/cartridge_1992/PRISON.asm:827` (equ=0x1530)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:665` (equ=0x332A)
- `src/levels/chahi_amiga_1991/CAVES.asm:990` (equ=0x332A)
- `src/levels/chahi_amiga_1991/PRISON.asm:813` (equ=0x332A)
- `src/levels/dos_1992/CAPSULE.asm:843` (equ=0x1530)
- `src/levels/dos_1992/CAVES.asm:1032` (equ=0x1530)
- `src/levels/dos_1992/LAKE.asm:797` (equ=0x1530)
- `src/levels/dos_1992/PRISON.asm:833` (equ=0x1530)
- `src/levels/gba_2004/LAKE.asm:787` (equ=0x1530)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_100.inc:2` — `video type=0, offset=COMMON_VIDEO_100, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x0A,0x98,0x01,0x02`

### `COMMON_VIDEO_102` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1288` (equ=0x3332)
- `src/levels/_unified/caves/amiga__entry.inc:2915` (equ=0x3332)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:82` (equ=0x1556)
- `src/levels/_unified/prison/amiga__entry.inc:2013` (equ=0x3332)
- `src/levels/cartridge_1992/CAPSULE.asm:838` (equ=0x1556)
- `src/levels/cartridge_1992/CAVES.asm:1020` (equ=0x1556)
- `src/levels/cartridge_1992/LAKE.asm:799` (equ=0x1556)
- `src/levels/cartridge_1992/PRISON.asm:829` (equ=0x1556)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:667` (equ=0x3332)
- `src/levels/chahi_amiga_1991/CAVES.asm:992` (equ=0x3332)
- `src/levels/chahi_amiga_1991/PRISON.asm:815` (equ=0x3332)
- `src/levels/dos_1992/CAPSULE.asm:845` (equ=0x1556)
- `src/levels/dos_1992/CAVES.asm:1034` (equ=0x1556)
- `src/levels/dos_1992/LAKE.asm:799` (equ=0x1556)
- `src/levels/dos_1992/PRISON.asm:835` (equ=0x1556)
- `src/levels/gba_2004/LAKE.asm:789` (equ=0x1556)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_102.inc:2` — `video type=0, offset=COMMON_VIDEO_102, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x0A,0xAB,0x01,0x02`

### `COMMON_VIDEO_104` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1290` (equ=0x333A)
- `src/levels/_unified/caves/amiga__entry.inc:2917` (equ=0x333A)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:84` (equ=0x157C)
- `src/levels/_unified/prison/amiga__entry.inc:2015` (equ=0x333A)
- `src/levels/cartridge_1992/CAPSULE.asm:840` (equ=0x157C)
- `src/levels/cartridge_1992/CAVES.asm:1022` (equ=0x157C)
- `src/levels/cartridge_1992/LAKE.asm:801` (equ=0x157C)
- `src/levels/cartridge_1992/PRISON.asm:831` (equ=0x157C)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:669` (equ=0x333A)
- `src/levels/chahi_amiga_1991/CAVES.asm:994` (equ=0x333A)
- `src/levels/chahi_amiga_1991/PRISON.asm:817` (equ=0x333A)
- `src/levels/dos_1992/CAPSULE.asm:847` (equ=0x157C)
- `src/levels/dos_1992/CAVES.asm:1036` (equ=0x157C)
- `src/levels/dos_1992/LAKE.asm:801` (equ=0x157C)
- `src/levels/dos_1992/PRISON.asm:837` (equ=0x157C)
- `src/levels/gba_2004/LAKE.asm:791` (equ=0x157C)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_104.inc:2` — `video type=0, offset=COMMON_VIDEO_104, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x0A,0xBE,0x01,0x02`

### `COMMON_VIDEO_110` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1296` (equ=0x0844)
- `src/levels/_unified/caves/amiga__entry.inc:2923` (equ=0x0844)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:89` (equ=0x125A)
- `src/levels/_unified/prison/amiga__entry.inc:2021` (equ=0x0844)
- `src/levels/cartridge_1992/CAPSULE.asm:846` (equ=0x125A)
- `src/levels/cartridge_1992/CAVES.asm:1028` (equ=0x125A)
- `src/levels/cartridge_1992/LAKE.asm:807` (equ=0x125A)
- `src/levels/cartridge_1992/PRISON.asm:837` (equ=0x125A)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:675` (equ=0x0844)
- `src/levels/chahi_amiga_1991/CAVES.asm:1000` (equ=0x0844)
- `src/levels/chahi_amiga_1991/PRISON.asm:823` (equ=0x0844)
- `src/levels/dos_1992/CAPSULE.asm:853` (equ=0x125A)
- `src/levels/dos_1992/CAVES.asm:1042` (equ=0x125A)
- `src/levels/dos_1992/LAKE.asm:807` (equ=0x125A)
- `src/levels/dos_1992/PRISON.asm:843` (equ=0x125A)
- `src/levels/gba_2004/LAKE.asm:797` (equ=0x125A)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_110.inc:2` — `video type=0, offset=COMMON_VIDEO_110, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x09,0x2D,0x01,0x02`

### `COMMON_VIDEO_112` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1298` (equ=0x08A0)
- `src/levels/_unified/caves/amiga__entry.inc:2925` (equ=0x08A0)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:91` (equ=0x1304)
- `src/levels/_unified/prison/amiga__entry.inc:2023` (equ=0x08A0)
- `src/levels/cartridge_1992/CAPSULE.asm:848` (equ=0x1304)
- `src/levels/cartridge_1992/CAVES.asm:1030` (equ=0x1304)
- `src/levels/cartridge_1992/LAKE.asm:809` (equ=0x1304)
- `src/levels/cartridge_1992/PRISON.asm:839` (equ=0x1304)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:677` (equ=0x08A0)
- `src/levels/chahi_amiga_1991/CAVES.asm:1002` (equ=0x08A0)
- `src/levels/chahi_amiga_1991/PRISON.asm:825` (equ=0x08A0)
- `src/levels/dos_1992/CAPSULE.asm:855` (equ=0x1304)
- `src/levels/dos_1992/CAVES.asm:1044` (equ=0x1304)
- `src/levels/dos_1992/LAKE.asm:809` (equ=0x1304)
- `src/levels/dos_1992/PRISON.asm:845` (equ=0x1304)
- `src/levels/gba_2004/LAKE.asm:799` (equ=0x1304)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_112.inc:2` — `video type=0, offset=COMMON_VIDEO_112, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x09,0x82,0x01,0x02`

### `COMMON_VIDEO_114` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1300` (equ=0x00B4)
- `src/levels/_unified/caves/amiga__entry.inc:2927` (equ=0x00B4)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:93` (equ=0x13B2)
- `src/levels/_unified/prison/amiga__entry.inc:2025` (equ=0x00B4)
- `src/levels/cartridge_1992/CAPSULE.asm:850` (equ=0x13B2)
- `src/levels/cartridge_1992/CAVES.asm:1032` (equ=0x13B2)
- `src/levels/cartridge_1992/LAKE.asm:811` (equ=0x13B2)
- `src/levels/cartridge_1992/PRISON.asm:841` (equ=0x13B2)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:679` (equ=0x00B4)
- `src/levels/chahi_amiga_1991/CAVES.asm:1004` (equ=0x00B4)
- `src/levels/chahi_amiga_1991/PRISON.asm:827` (equ=0x00B4)
- `src/levels/dos_1992/CAPSULE.asm:857` (equ=0x13B2)
- `src/levels/dos_1992/CAVES.asm:1046` (equ=0x13B2)
- `src/levels/dos_1992/LAKE.asm:811` (equ=0x13B2)
- `src/levels/dos_1992/PRISON.asm:847` (equ=0x13B2)
- `src/levels/gba_2004/LAKE.asm:801` (equ=0x13B2)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_114.inc:2` — `video type=0, offset=COMMON_VIDEO_114, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x09,0xD9,0x01,0x02`

### `COMMON_VIDEO_115` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1301` (equ=0x0128)
- `src/levels/_unified/caves/amiga__entry.inc:2928` (equ=0x0128)
- `src/levels/_unified/lake/hero_fall_right_and_drawers.inc:94` (equ=0x1474)
- `src/levels/_unified/prison/amiga__entry.inc:2026` (equ=0x0128)
- `src/levels/cartridge_1992/CAPSULE.asm:851` (equ=0x1474)
- `src/levels/cartridge_1992/CAVES.asm:1033` (equ=0x1474)
- `src/levels/cartridge_1992/LAKE.asm:812` (equ=0x1474)
- `src/levels/cartridge_1992/PRISON.asm:842` (equ=0x1474)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:680` (equ=0x0128)
- `src/levels/chahi_amiga_1991/CAVES.asm:1005` (equ=0x0128)
- `src/levels/chahi_amiga_1991/PRISON.asm:828` (equ=0x0128)
- `src/levels/dos_1992/CAPSULE.asm:858` (equ=0x1474)
- `src/levels/dos_1992/CAVES.asm:1047` (equ=0x1474)
- `src/levels/dos_1992/LAKE.asm:812` (equ=0x1474)
- `src/levels/dos_1992/PRISON.asm:848` (equ=0x1474)
- `src/levels/gba_2004/LAKE.asm:802` (equ=0x1474)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_115.inc:2` — `video type=0, offset=COMMON_VIDEO_115, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x0A,0x3A,0x01,0x02`

### `COMMON_VIDEO_295` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1481` (equ=0x3648)
- `src/levels/_unified/caves/amiga__entry.inc:3108` (equ=0x3648)
- `src/levels/_unified/prison/amiga__entry.inc:2206` (equ=0x3648)
- `src/levels/cartridge_1992/CAPSULE.asm:1031` (equ=0x3542)
- `src/levels/cartridge_1992/CAVES.asm:1213` (equ=0x3542)
- `src/levels/cartridge_1992/PRISON.asm:1022` (equ=0x3542)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:860` (equ=0x3648)
- `src/levels/chahi_amiga_1991/CAVES.asm:1185` (equ=0x3648)
- `src/levels/chahi_amiga_1991/PRISON.asm:1008` (equ=0x3648)
- `src/levels/dos_1992/CAPSULE.asm:1038` (equ=0x3542)
- `src/levels/dos_1992/CAVES.asm:1227` (equ=0x3542)
- `src/levels/dos_1992/PRISON.asm:1028` (equ=0x3542)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_295.inc:2` — `video type=0, offset=COMMON_VIDEO_295, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1A,0xA1,0x01,0x02`

### `COMMON_VIDEO_296` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1482` (equ=0x13B2)
- `src/levels/_unified/caves/amiga__entry.inc:3109` (equ=0x13B2)
- `src/levels/_unified/prison/amiga__entry.inc:2207` (equ=0x13B2)
- `src/levels/cartridge_1992/CAPSULE.asm:1032` (equ=0x3558)
- `src/levels/cartridge_1992/CAVES.asm:1214` (equ=0x3558)
- `src/levels/cartridge_1992/PRISON.asm:1023` (equ=0x3558)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:861` (equ=0x13B2)
- `src/levels/chahi_amiga_1991/CAVES.asm:1186` (equ=0x13B2)
- `src/levels/chahi_amiga_1991/PRISON.asm:1009` (equ=0x13B2)
- `src/levels/dos_1992/CAPSULE.asm:1039` (equ=0x3558)
- `src/levels/dos_1992/CAVES.asm:1228` (equ=0x3558)
- `src/levels/dos_1992/PRISON.asm:1029` (equ=0x3558)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_296.inc:2` — `video type=0, offset=COMMON_VIDEO_296, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1A,0xAC,0x01,0x02`

### `COMMON_VIDEO_297` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1483` (equ=0x1474)
- `src/levels/_unified/caves/amiga__entry.inc:3110` (equ=0x1474)
- `src/levels/_unified/prison/amiga__entry.inc:2208` (equ=0x1474)
- `src/levels/cartridge_1992/CAPSULE.asm:1033` (equ=0x34FE)
- `src/levels/cartridge_1992/CAVES.asm:1215` (equ=0x34FE)
- `src/levels/cartridge_1992/PRISON.asm:1024` (equ=0x34FE)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:862` (equ=0x1474)
- `src/levels/chahi_amiga_1991/CAVES.asm:1187` (equ=0x1474)
- `src/levels/chahi_amiga_1991/PRISON.asm:1010` (equ=0x1474)
- `src/levels/dos_1992/CAPSULE.asm:1040` (equ=0x34FE)
- `src/levels/dos_1992/CAVES.asm:1229` (equ=0x34FE)
- `src/levels/dos_1992/PRISON.asm:1030` (equ=0x34FE)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_297.inc:2` — `video type=0, offset=COMMON_VIDEO_297, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1A,0x7F,0x01,0x02`

### `COMMON_VIDEO_298` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1484` (equ=0x1C78)
- `src/levels/_unified/caves/amiga__entry.inc:3111` (equ=0x1C78)
- `src/levels/cartridge_1992/CAPSULE.asm:1034` (equ=0x367C)
- `src/levels/cartridge_1992/CAVES.asm:1216` (equ=0x367C)
- `src/levels/cartridge_1992/PRISON.asm:1025` (equ=0x367C)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:863` (equ=0x1C78)
- `src/levels/chahi_amiga_1991/CAVES.asm:1188` (equ=0x1C78)
- `src/levels/dos_1992/CAPSULE.asm:1041` (equ=0x367C)
- `src/levels/dos_1992/CAVES.asm:1230` (equ=0x367C)
- `src/levels/dos_1992/PRISON.asm:1031` (equ=0x367C)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_298.inc:2` — `video type=0, offset=COMMON_VIDEO_298, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1B,0x3E,0x01,0x02`

### `COMMON_VIDEO_299` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1485` (equ=0x3B44)
- `src/levels/_unified/caves/amiga__entry.inc:3112` (equ=0x3B44)
- `src/levels/cartridge_1992/CAPSULE.asm:1035` (equ=0x352C)
- `src/levels/cartridge_1992/CAVES.asm:1217` (equ=0x352C)
- `src/levels/cartridge_1992/PRISON.asm:1026` (equ=0x352C)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:864` (equ=0x3B44)
- `src/levels/chahi_amiga_1991/CAVES.asm:1189` (equ=0x3B44)
- `src/levels/dos_1992/CAPSULE.asm:1042` (equ=0x352C)
- `src/levels/dos_1992/CAVES.asm:1231` (equ=0x352C)
- `src/levels/dos_1992/PRISON.asm:1032` (equ=0x352C)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_299.inc:2` — `video type=0, offset=COMMON_VIDEO_299, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1A,0x96,0x01,0x02`

### `COMMON_VIDEO_300` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/capsule/amiga__entry.inc:1486` (equ=0x5CA4)
- `src/levels/_unified/caves/amiga__entry.inc:3113` (equ=0x5CA4)
- `src/levels/cartridge_1992/CAPSULE.asm:1036` (equ=0x356E)
- `src/levels/cartridge_1992/CAVES.asm:1218` (equ=0x356E)
- `src/levels/cartridge_1992/PRISON.asm:1027` (equ=0x356E)
- `src/levels/chahi_amiga_1991/CAPSULE.asm:865` (equ=0x5CA4)
- `src/levels/chahi_amiga_1991/CAVES.asm:1190` (equ=0x5CA4)
- `src/levels/dos_1992/CAPSULE.asm:1043` (equ=0x356E)
- `src/levels/dos_1992/CAVES.asm:1232` (equ=0x356E)
- `src/levels/dos_1992/PRISON.asm:1033` (equ=0x356E)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_300.inc:2` — `video type=0, offset=COMMON_VIDEO_300, x=[0x01], y=[0x02], zoom=0x40` ⇒ `;@raw=0x57,0x1A,0xB7,0x01,0x02`

### `COMMON_VIDEO_355` — 1 annotated call site(s)

**Definitions:**

- `src/levels/cartridge_1992/CAPSULE.asm:1087` (equ=0x3FB8)
- `src/levels/cartridge_1992/CAVES.asm:1273` (equ=0x3FB8)
- `src/levels/dos_1992/CAPSULE.asm:1094` (equ=0x3FB8)
- `src/levels/dos_1992/CAVES.asm:1287` (equ=0x3FB8)

**Annotated call sites (first 5):**

- `src/levels/_unified/_helpers/DRAW_CV_355.inc:2` — `video type=0, offset=COMMON_VIDEO_355, x=[0x07], y=[0x08], zoom=0x40` ⇒ `;@raw=0x57,0x1F,0xDC,0x07,0x08`

### `LABEL_DD59` — 1 annotated call site(s)

**Definitions:**

- `src/levels/_unified/caves/cart__post_INCR_HACK67_BY_1.inc:24` (label)
- `src/levels/cartridge_1992/CAVES.asm:22036` (label)

**Annotated call sites (first 5):**

- `src/levels/_unified/caves/dos__entry.inc:3189` — `call LABEL_DD59` ⇒ `;@raw=0x04,0xDD,0x59`

## No-symbol residue

Annotations with no resolvable operand symbol (e.g., immediate-only instructions). These are candidates for direct `;@enc=…` patterns we haven't catalogued yet.

- `src/levels/_unified/caves/amiga__entry.inc:3181` — `call LABEL_D845` ⇒ `;@raw=0x04,0xD8,0x45`
- `src/levels/_unified/caves/cart__entry.inc:3176` — `call LABEL_DDE2` ⇒ `;@raw=0x04,0xDD,0xE2`
- `src/levels/_unified/TANK.asm.in:110` — `bankSwitch 6;  Secret Code Entry Screen` ⇒ `;@raw=0x19,0x3E,0x86`

