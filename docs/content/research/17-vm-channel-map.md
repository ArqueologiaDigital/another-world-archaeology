# 17 — VM thread-channel map (per stage)

Each AW VM `setup channel=NN, address=ROUTINE` opcode starts a thread on channel `NN` (one of 64 — `0x00..0x3F`) running `ROUTINE`. Channels are the engine's concurrency primitive: actor animation, frame blit, music timing, cinematic sequencing, and HUD drawing each get their own channel.

This is a STATIC scan: every `setup` opcode in the unified source is collected and grouped by stage. A channel listed with multiple routines means the bytecode REASSIGNS that channel during execution — the channel hosts a sequence of features as the level progresses.

Total `setup` opcodes scanned: **4082**.

## Channel-usage frequency (across all stages)

Channels listed with their total `setup` count across every stage. Channel `0x3C` is canonically the blit / pause-quantum loop; `0x00`-`0x0F` typically host actor and HUD threads; `0x3D`-`0x3F` are often reserved.

| channel | total setups |
| ---: | ---: |
| `0x14` | 466 |
| `0x3C` | 349 |
| `0x01` | 199 |
| `0x15` | 184 |
| `0x23` | 157 |
| `0x16` | 145 |
| `0x3B` | 135 |
| `0x02` | 133 |
| `0x36` | 124 |
| `0x25` | 120 |
| `0x04` | 119 |
| `0x37` | 117 |
| `0x27` | 116 |
| `0x34` | 100 |
| `0x05` | 99 |
| `0x03` | 93 |
| `0x39` | 83 |
| `0x3F` | 78 |
| `0x35` | 66 |
| `0x38` | 65 |
| `0x00` | 62 |
| `0x22` | 61 |
| `0x07` | 58 |
| `0x17` | 52 |
| `0x2C` | 48 |
| `0x06` | 45 |
| `0x28` | 44 |
| `0x24` | 43 |
| `0x0A` | 40 |
| `0x1A` | 37 |
| `0x3E` | 34 |
| `0x2D` | 33 |
| `0x0F` | 28 |
| `0x09` | 28 |
| `0x26` | 26 |
| `0x2A` | 26 |
| `0x31` | 25 |
| `0x2B` | 25 |
| `0x08` | 25 |
| `0x0B` | 25 |
| `0x11` | 25 |
| `0x3A` | 24 |
| `0x10` | 23 |
| `0x1B` | 22 |
| `0x0C` | 22 |
| `0x33` | 21 |
| `0x32` | 20 |
| `0x18` | 18 |
| `0x2F` | 18 |
| `0x29` | 18 |
| `0x0E` | 18 |
| `0x13` | 15 |
| `0x21` | 15 |
| `0x0D` | 14 |
| `0x2E` | 13 |
| `0x30` | 13 |
| `0x19` | 13 |
| `0x1C` | 13 |
| `0x1E` | 13 |
| `0x12` | 12 |
| `0x1D` | 9 |
| `0x20` | 6 |
| `0x1F` | 4 |

## INTRO

| channel | branch | routine | source |
| ---: | --- | --- | --- |
| `0x01` | shared | `CH_01_INIT_VAR_04_06` | src/levels/_unified/intro/intro_late_pages_fill.inc:172 |
| `0x01` | shared | `DRAW_CIN_190_LOOP` | src/levels/_unified/intro/intro_music_marks_and_city.inc:51 |
| `0x01` | shared | `DRAW_CIN_426_427_TWICE` | src/levels/_unified/intro/intro_music_marks_and_city.inc:212 (+1 more) |
| `0x01` | shared | `DRAW_CIN_431_LOOP` | src/levels/_unified/intro/intro_music_marks_and_city.inc:109 |
| `0x01` | shared | `FILL_FF_8_AND_DRAW_CIN_517_518` | src/levels/_unified/intro/intro_scene_late_phase.inc:87 |
| `0x01` | shared | `FILL_FF_PAGE_LOOP` | src/levels/_unified/intro/intro_particle_channels.inc:102 (+1 more) |
| `0x01` | shared | `INTRO_FILL_AND_DRAW_413_414` | src/levels/_unified/intro/intro_lake_transition.inc:84 |
| `0x01` | shared | `INTRO_FILL_AND_DRAW_CIN_103` | src/levels/_unified/intro/intro_dna_animation.inc:244 |
| `0x01` | shared | `INTRO_FILL_AND_DRAW_CIN_429_430` | src/levels/_unified/intro/intro_music_marks_and_city.inc:148 |
| `0x01` | shared | `INTRO_SCENE_INIT_PARTICLES` | src/levels/_unified/intro/intro_entry_and_dispatchers.inc:44 (+1 more) |
| `0x01` | shared | `INTRO_SET_PAL_7_FILL_PAGE0_5` | src/levels/_unified/intro/intro_scene_final.inc:433 |
| `0x01` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_lake_transition.inc:515 (+3 more) |
| `0x02` | shared | `CH_02_INIT_VARS_01_02_03` | src/levels/_unified/intro/intro_scene_final.inc:434 |
| `0x02` | shared | `COPY_BG_PAGE_AND_DISPLAY_TEXT_23` | src/levels/_unified/intro/intro_music_marks_and_city.inc:32 |
| `0x02` | shared | `INIT_PAGE0_PAUSE2_FILL1` | src/levels/_unified/intro/intro_lake_transition.inc:308 |
| `0x02` | shared | `INIT_VAR_04_PAL_E_VAR_01` | src/levels/_unified/intro/intro_lake_transition.inc:410 |
| `0x02` | shared | `INTRO_FILL_AND_DRAW_CIN_385` | src/levels/_unified/intro/intro_music_marks_and_city.inc:426 |
| `0x02` | shared | `INTRO_FILL_PAGE0_DRAW_CIN_118` | src/levels/_unified/intro/intro_lake_transition.inc:516 |
| `0x02` | shared | `INTRO_PAUSE_3_AND_DRAW_CIN_138` | src/levels/_unified/intro/intro_song_init_and_decor.inc:74 |
| `0x02` | shared | `INTRO_PAUSE_3_PLAY_SONG_INIT` | src/levels/_unified/intro/intro_scene_late_phase.inc:88 |
| `0x02` | shared | `INTRO_PLAY_BG_AUDIO_LOOP` | src/levels/_unified/intro/intro_entry_and_dispatchers.inc:48 |
| `0x02` | shared | `INTRO_PLAY_FX_AND_PALETTE_4_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:245 |
| `0x02` | shared | `INTRO_TRANSITION_TO_LAKE_SCENE` | src/levels/_unified/intro/intro_first_scene_init.inc:46 |
| `0x02` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_lake_transition.inc:482 |
| `0x02` | shared | `SETUP_CITY_SEQ_CHANNELS` | src/levels/_unified/intro/intro_lake_transition.inc:85 |
| `0x02` | shared | `SETUP_INTRO_CITY_CHANNELS` | src/levels/_unified/intro/intro_music_marks_and_city.inc:149 |
| `0x02` | shared | `SETUP_INTRO_PARTICLE_CHANNELS` | src/levels/_unified/intro/intro_music_marks_and_city.inc:511 |
| `0x03` | shared | `CH_03_INIT_VAR_01_02_FFF6` | src/levels/_unified/intro/intro_song_init_and_decor.inc:21 |
| `0x03` | shared | `CH_03_INIT_VAR_03_04` | src/levels/_unified/intro/intro_lake_transition.inc:73 |
| `0x03` | shared | `DRAW_CINEMATIC_005_LOOP` | src/levels/_unified/intro/intro_entry_and_dispatchers.inc:49 |
| `0x03` | shared | `DRAW_CINEMATIC_053_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:246 |
| `0x03` | shared | `DRAW_CIN_112_AT_143_94_LOOP` | src/levels/_unified/intro/intro_scene_final.inc:435 |
| `0x03` | shared | `DRAW_CIN_120_LOOP_VAR03` | src/levels/_unified/intro/intro_lake_transition.inc:517 |
| `0x03` | shared | `DRAW_CIN_128_521_ZOOM_VAR04` | src/levels/_unified/intro/intro_lake_transition.inc:494 |
| `0x03` | shared | `DRAW_CIN_468_509_ZOOM_VAR04` | src/levels/_unified/intro/intro_late_pages_fill.inc:173 |
| `0x03` | shared | `DRAW_CIN_505_LOOP_VAR_02` | src/levels/_unified/intro/intro_lake_transition.inc:309 |
| `0x03` | shared | `DRAW_CITY_SEQ_432_433` | src/levels/_unified/intro/intro_music_marks_and_city.inc:50 |
| `0x03` | shared | `INIT_VAR_02_AND_BREAK_LOOP` | src/levels/_unified/intro/intro_music_marks_and_city.inc:436 |
| `0x03` | shared | `INTRO_TRANSITION_TO_LAKE_SETUP` | src/levels/_unified/intro/intro_particle_channels.inc:62 |
| `0x03` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_lake_transition.inc:244 (+6 more) |
| `0x04` | shared | `CH_04_INIT_VAR_04_05` | src/levels/_unified/intro/intro_song_init_and_decor.inc:22 |
| `0x04` | shared | `CH_04_INIT_VAR_05` | src/levels/_unified/intro/intro_lake_transition.inc:74 |
| `0x04` | shared | `INTRO_DRAW_CIN_528_AT_96_131` | src/levels/_unified/intro/intro_scene_late_phase.inc:26 |
| `0x04` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_lake_transition.inc:87 (+7 more) |
| `0x04` | shared | `SET_PALETTE_17_INIT_VAR_14` | src/levels/_unified/intro/intro_particle_channels.inc:313 |
| `0x04` | shared | `SET_PALETTE_18` | src/levels/_unified/intro/intro_particle_channels.inc:221 |
| `0x05` | shared | `CH_05_INIT_VARS_06_07_08` | src/levels/_unified/intro/intro_scene_late_phase.inc:45 |
| `0x05` | shared | `CH_05_INIT_VAR_06_07` | src/levels/_unified/intro/intro_song_init_and_decor.inc:23 |
| `0x05` | shared | `CH_05_INIT_VAR_07_08` | src/levels/_unified/intro/intro_lake_transition.inc:75 |
| `0x05` | shared | `DISPLAY_TEXT_21` | src/levels/_unified/intro/intro_music_marks_and_city.inc:249 |
| `0x05` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_lake_transition.inc:88 (+5 more) |
| `0x06` | shared | `CH_06_DRAW_CIN_457_PARTICLES` | src/levels/_unified/intro/intro_song_init_and_decor.inc:24 |
| `0x06` | shared | `DRAW_CIN_450_451_SEQ` | src/levels/_unified/intro/intro_lake_transition.inc:59 |
| `0x06` | shared | `DRAW_CITY_SEQ_439_440` | src/levels/_unified/intro/intro_music_marks_and_city.inc:48 |
| `0x06` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_lake_transition.inc:92 (+5 more) |
| `0x06` | shared | `SCENE_TRANSITION_NEXT_PHASE` | src/levels/_unified/intro/intro_first_scene_init.inc:23 |
| `0x07` | shared | `CH_07_INIT_VAR_08_09` | src/levels/_unified/intro/intro_song_init_and_decor.inc:25 |
| `0x07` | shared | `DRAW_CIN_382_TWICE_AT_DIFF_Y` | src/levels/_unified/intro/intro_music_marks_and_city.inc:349 (+1 more) |
| `0x07` | shared | `DRAW_CITY_SEQ_435_436` | src/levels/_unified/intro/intro_music_marks_and_city.inc:49 |
| `0x07` | shared | `INIT_VAR_03_AND_LOOP` | src/levels/_unified/intro/intro_music_marks_and_city.inc:321 |
| `0x07` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_music_marks_and_city.inc:76 (+3 more) |
| `0x08` | shared | `DELETE_CHANNELS_0A_TO_1F` | src/levels/_unified/intro/intro_first_scene_init.inc:43 |
| `0x08` | shared | `DRAW_CIN_128_521_ZOOM_VAR04` | src/levels/_unified/intro/intro_scene_late_phase.inc:43 |
| `0x08` | shared | `INIT_VARS_10_11_AND_SELECT_PAGE0` | src/levels/_unified/intro/intro_song_init_and_decor.inc:28 |
| `0x08` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_scene_late_phase.inc:67 (+1 more) |
| `0x08` | shared | `SETUP_INTRO_DNA_CHANNELS` | src/levels/_unified/intro/intro_scene_transitions.inc:56 |
| `0x09` | shared | `DRAW_CINEMATICS_166_TO_171` | src/levels/_unified/intro/intro_scene_transitions.inc:19 (+4 more) |
| `0x09` | shared | `DRAW_CIN_126_127_AT_VAR01_02` | src/levels/_unified/intro/intro_scene_late_phase.inc:44 |
| `0x09` | shared | `DRAW_CIN_170_171_AT_VAR10_VAR11` | src/levels/_unified/intro/intro_song_init_and_decor.inc:29 |
| `0x09` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_scene_late_phase.inc:86 (+1 more) |
| `0x0A` | shared | `CH_0A_INIT_VAR_02` | src/levels/_unified/intro/intro_particle_channels.inc:74 |
| `0x0A` | shared | `DNA_VAR_05_HOLD_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:44 |
| `0x0A` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_lake_transition.inc:89 (+3 more) |
| `0x0A` | shared | `SELECT_PAGE0_AND_DISPATCH_BLIT` | src/levels/_unified/intro/intro_lake_transition.inc:76 |
| `0x0A` | shared | `SHOW_PAGE_0_LOOP_INTRO` | src/levels/_unified/intro/intro_music_marks_and_city.inc:213 (+1 more) |
| `0x0B` | shared | `CH_0B_INIT_VAR_03` | src/levels/_unified/intro/intro_particle_channels.inc:75 |
| `0x0B` | shared | `DRAW_CIN_442_443_444_DESC_Y` | src/levels/_unified/intro/intro_lake_transition.inc:77 |
| `0x0B` | shared | `DRAW_CITY_SEQ_419_420` | src/levels/_unified/intro/intro_music_marks_and_city.inc:257 |
| `0x0B` | shared | `DRAW_DNA_ANIMATION_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:45 |
| `0x0B` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_lake_transition.inc:90 (+1 more) |
| `0x0B` | shared | `PLAY_FX_2C_AND_DRAW_CIN_000` | src/levels/_unified/intro/intro_particle_channels.inc:314 |
| `0x0C` | shared | `CH_0C_INIT_VAR_04` | src/levels/_unified/intro/intro_particle_channels.inc:76 |
| `0x0C` | shared | `DISPLAY_TEXT_0A_0B_PLAY_FX` | src/levels/_unified/intro/intro_music_marks_and_city.inc:248 |
| `0x0C` | shared | `DNA_VAR_05_DRIFT_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:49 |
| `0x0C` | shared | `DRAW_INTRO_DECOR_340` | src/levels/_unified/intro/intro_particle_channels.inc:315 |
| `0x0C` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_particle_channels.inc:370 |
| `0x0D` | shared | `CH_0D_INIT_VAR_05` | src/levels/_unified/intro/intro_particle_channels.inc:77 |
| `0x0D` | shared | `DRAW_DNA_ANIMATION_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:50 |
| `0x0D` | shared | `DRAW_INTRO_DECOR_337` | src/levels/_unified/intro/intro_particle_channels.inc:316 |
| `0x0D` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_particle_channels.inc:371 |
| `0x0E` | shared | `CH_0E_INIT_VAR_06` | src/levels/_unified/intro/intro_particle_channels.inc:78 |
| `0x0E` | shared | `DNA_VAR_05_DRIFT_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:54 |
| `0x0E` | shared | `DRAW_INTRO_DECOR_333` | src/levels/_unified/intro/intro_particle_channels.inc:317 |
| `0x0E` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_lake_transition.inc:91 (+1 more) |
| `0x0E` | shared | `SELECT_PAGE_FF_LOOP` | src/levels/_unified/intro/intro_lake_transition.inc:78 |
| `0x0F` | shared | `CH_0F_INIT_PARTICLE_POS` | src/levels/_unified/intro/intro_particle_channels.inc:79 |
| `0x0F` | shared | `DRAW_DNA_ANIMATION_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:55 |
| `0x0F` | shared | `DRAW_INTRO_DECOR_331` | src/levels/_unified/intro/intro_particle_channels.inc:318 |
| `0x0F` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_particle_channels.inc:385 |
| `0x10` | shared | `CH_10_DRAW_CIN_353_PARTICLE` | src/levels/_unified/intro/intro_particle_channels.inc:80 |
| `0x10` | shared | `DNA_VAR_05_DRIFT_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:59 |
| `0x10` | shared | `DRAW_INTRO_DECOR_329` | src/levels/_unified/intro/intro_particle_channels.inc:319 |
| `0x10` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_music_marks_and_city.inc:424 (+2 more) |
| `0x10` | shared | `SHOW_PAGE_FF_LOOP_INTRO` | src/levels/_unified/intro/intro_music_marks_and_city.inc:214 (+1 more) |
| `0x11` | shared | `CH_11_INIT_PARTICLE_POS_2` | src/levels/_unified/intro/intro_particle_channels.inc:81 |
| `0x11` | shared | `DRAW_CIN_453_454_SEQ` | src/levels/_unified/intro/intro_song_init_and_decor.inc:36 (+2 more) |
| `0x11` | shared | `DRAW_DNA_ANIMATION_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:60 |
| `0x11` | shared | `DRAW_INTRO_DECOR_318` | src/levels/_unified/intro/intro_particle_channels.inc:320 |
| `0x11` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_particle_channels.inc:384 (+1 more) |
| `0x12` | shared | `CH_12_INIT_PARTICLE_POS_3` | src/levels/_unified/intro/intro_particle_channels.inc:82 |
| `0x12` | shared | `DNA_VAR_05_DRIFT_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:64 |
| `0x12` | shared | `INIT_VAR_0D_THEN_LOOP` | src/levels/_unified/intro/intro_particle_channels.inc:321 (+1 more) |
| `0x13` | shared | `DRAW_DNA_ANIMATION_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:65 |
| `0x14` | shared | `DNA_VAR_05_DRIFT_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:69 |
| `0x14` | shared | `DRAW_INTRO_DECOR_305` | src/levels/_unified/intro/intro_particle_channels.inc:322 |
| `0x14` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_particle_channels.inc:366 |
| `0x15` | shared | `DRAW_DNA_ANIMATION_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:70 |
| `0x15` | shared | `DRAW_INTRO_DECOR_301` | src/levels/_unified/intro/intro_particle_channels.inc:323 |
| `0x15` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/intro/intro_particle_channels.inc:367 |
| `0x16` | shared | `DNA_VAR_05_DRIFT_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:74 |
| `0x17` | shared | `DRAW_DNA_ANIMATION_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:75 |
| `0x18` | shared | `DNA_VAR_05_DRIFT_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:79 |
| `0x19` | shared | `DRAW_DNA_ANIMATION_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:80 |
| `0x1A` | shared | `DNA_VAR_05_DRIFT_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:84 |
| `0x1B` | shared | `DRAW_DNA_ANIMATION_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:85 |
| `0x1C` | shared | `DNA_VAR_05_DRIFT_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:89 |
| `0x1D` | shared | `DRAW_DNA_ANIMATION_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:90 |
| `0x1E` | shared | `DNA_VAR_05_DRIFT_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:94 |
| `0x1F` | shared | `DRAW_DNA_ANIMATION_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:95 |
| `0x3C` | shared | `BLIT_AND_COPY_PAGE_FF_LOOP` | src/levels/_unified/intro/intro_dna_animation.inc:186 (+51 more) |
| `0x3C` | shared | `BLIT_AND_DISPATCH_HERO_ACTION` | src/levels/_unified/intro/intro_entry_and_dispatchers.inc:4 (+1 more) |
| `0x3C` | shared | `BLIT_AND_DISPATCH_VAR3` | src/levels/_unified/intro/intro_dna_animation.inc:177 (+2 more) |
| `0x3C` | shared | `BLIT_DISPATCH_HERO_ACTION_ALT` | src/levels/_unified/intro/intro_lake_transition.inc:256 (+3 more) |

## LAKE

| channel | branch | routine | source |
| ---: | --- | --- | --- |
| `0x00` | shared | `DISPLAY_TEXT_01FA_AND_FADE_TO_PAL_2` | src/levels/_unified/lake/scene_transition_and_decor.inc:102 |
| `0x00` | amiga | `DISPLAY_TEXT_01FA_AND_FADE_TO_PAL_2` | src/levels/_unified/lake/scene_transition_and_decor.inc:111 |
| `0x00` | dos | `DISPLAY_TEXT_01FA_AND_FADE_TO_PAL_2` | src/levels/_unified/lake/scene_transition_and_decor.inc:105 |
| `0x00` | shared | `ENTRY_POINT_OF_LAKE_LEVEL` | src/levels/_unified/lake/lake_entry_and_init.inc:163 |
| `0x00` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/lester_drift_and_swing.inc:256 |
| `0x00` | shared | `LAKE_LEVEL_INIT` | src/levels/_unified/lake/beast_kills_lester_and_respawn.inc:151 |
| `0x01` | shared | `DRAW_INSIDE_ALIEN_POOL_SCENARIO` | src/levels/_unified/lake/pool_underwater_cinematic.inc:93 |
| `0x01` | shared | `DROPLET_DRIP_LOOP_RANDOM_X` | src/levels/_unified/lake/screen_to_the_right_setups.inc:151 |
| `0x01` | shared | `DROPLET_FALL_AND_IMPACT_LOOP` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:29 |
| `0x01` | shared | `INIT_HERO_AT_POOL_EXIT` | src/levels/_unified/lake/random_init_and_music_setup.inc:75 |
| `0x01` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/channel_cleanup_helpers.inc:2 |
| `0x02` | shared | `SCATTER_8DOT_LOOP_LEFT` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:57 |
| `0x03` | shared | `A_CALM_ALIEN_POOL_BEFORE_LESTERS_ARRIVAL` | src/levels/_unified/lake/lake_entry_and_init.inc:76 |
| `0x03` | shared | `SCATTER_8DOT_LOOP_RIGHT` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:58 |
| `0x04` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/channel_cleanup_helpers.inc:3 (+3 more) |
| `0x04` | shared | `LESTER_DRIFT_RIGHT_SEQ` | src/levels/_unified/lake/lester_drift_and_swing.inc:214 |
| `0x04` | shared | `LOOP_DRAW_CINEMATIC_VINE_SCREEN_BG_DECOR_AT_CENTER` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:22 |
| `0x04` | shared | `LOOP_DRAW_LAKE_096_DECOR_AT_72_171` | src/levels/_unified/lake/lake_decorations_096_099.inc:15 (+1 more) |
| `0x04` | shared | `LOOP_DRAW_LAKE_097_DECOR_AT_71_171` | src/levels/_unified/lake/lake_decorations_096_099.inc:17 (+2 more) |
| `0x04` | shared | `LOOP_DRAW_LAKE_098_DECOR_AT_70_172` | src/levels/_unified/lake/lake_decorations_096_099.inc:19 (+2 more) |
| `0x04` | shared | `LOOP_DRAW_LAKE_099_DECOR_AT_69_172` | src/levels/_unified/lake/lake_decorations_096_099.inc:23 |
| `0x04` | shared | `UPDATE_POSITION_OF_FIRST_WAVY_GLARE` | src/levels/_unified/lake/pool_underwater_cinematic.inc:101 |
| `0x05` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/lester_drift_and_swing.inc:203 |
| `0x05` | shared | `PLAYBACK_CINEMATIC_TENTACLE_RETREAT_F0_TO_513` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:59 |
| `0x05` | shared | `SCHEDULE_LAKE_DECORATIONS_096_TO_099` | src/levels/_unified/lake/lester_drift_and_swing.inc:152 |
| `0x05` | shared | `UPDATE_POSITION_OF_SECOND_WAVY_GLARE` | src/levels/_unified/lake/pool_underwater_cinematic.inc:102 |
| `0x06` | shared | `LESTER_GRABS_A_VINE_AND_SWINGS` | src/levels/_unified/lake/hero_lake_edge_and_init.inc:43 |
| `0x07` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/channel_cleanup_helpers.inc:13 (+3 more) |
| `0x07` | shared | `LOOP_DRAW_LAKE_093_AT_CENTER` | src/levels/_unified/lake/lester_drift_and_swing.inc:204 |
| `0x07` | shared | `POOL_WATER_WAVY_GLARE_ANIMATION` | src/levels/_unified/lake/pool_underwater_cinematic.inc:103 (+2 more) |
| `0x07` | amiga | `POOL_WATER_WAVY_GLARE_ANIMATION` | src/levels/_unified/lake/pool_underwater_cinematic.inc:137 |
| `0x07` | dos | `POOL_WATER_WAVY_GLARE_ANIMATION` | src/levels/_unified/lake/pool_underwater_cinematic.inc:140 |
| `0x07` | shared | `THE_BEAST_APPEARS_FOR_THE_FIRST_TIME_IN_THE_BACKGROUND` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:54 |
| `0x07` | shared | `THE_BEAST_WANDERS_ON_THE_FIRST_SCREEN_TO_THE_RIGHT` | src/levels/_unified/lake/screen_to_the_right_setups.inc:25 |
| `0x07` | shared | `THE_BEAST_WANDERS_ON_THE_SECOND_SCREEN_TO_THE_RIGHT` | src/levels/_unified/lake/screen_to_the_right_setups.inc:109 |
| `0x08` | shared | `SNEAKY_TENTACLE_FROM_THE_POOL` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:60 |
| `0x09` | shared | `BEETLE_ANIM_DRIFT_RIGHT` | src/levels/_unified/lake/beetle_walking_and_kick_detector.inc:99 |
| `0x09` | shared | `BEETLE_ANIM_HOVER_BOBBING_LOOP` | src/levels/_unified/lake/beetle.inc:210 (+1 more) |
| `0x09` | shared | `BEETLE_ANIM_HOVER_VERTICAL_LOOP` | src/levels/_unified/lake/beetle.inc:191 (+2 more) |
| `0x09` | shared | `BEETLE_ANIM_LIFT_AND_FLY` | src/levels/_unified/lake/beetle_walking_and_kick_detector.inc:90 |
| `0x09` | shared | `BEETLE_INIT_POS_THEN_WALK_LEFT` | src/levels/_unified/lake/random_init_and_music_setup.inc:77 |
| `0x09` | shared | `BEETLE_WALKING_LEFT` | src/levels/_unified/lake/beetle_walking_and_kick_detector.inc:109 |
| `0x09` | shared | `BEETLE_WALKING_RIGHT` | src/levels/_unified/lake/beetle_walking_and_kick_detector.inc:105 |
| `0x09` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/beetle_walking_and_kick_detector.inc:77 (+1 more) |
| `0x09` | dos | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/random_init_and_music_setup.inc:82 |
| `0x0A` | shared | `INIT_GETTING_OUT_OF_POOL_ANIMATION` | src/levels/_unified/lake/getting_out_of_pool_animation.inc:250 |
| `0x0A` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/pool_underwater_cinematic.inc:112 |
| `0x0A` | shared | `POOL_SURFACE_WAVES_ANIMATION` | src/levels/_unified/lake/pool_underwater_cinematic.inc:104 (+1 more) |
| `0x0A` | shared | `SCENE_TRANSITION_TO_GETTING_OUT_OF_POOL` | src/levels/_unified/lake/screen_edge_loops.inc:161 |
| `0x0B` | shared | `LAB_CONSOLE_SINKING_ANIMATION` | src/levels/_unified/lake/pool_underwater_cinematic.inc:126 |
| `0x0B` | shared | `MULTIPLEX_ANIM_RING1_SLOT_0` | src/levels/_unified/lake/screen_to_the_right_setups.inc:28 |
| `0x0B` | shared | `MULTIPLEX_ANIM_RING2_SLOT_0` | src/levels/_unified/lake/screen_to_the_right_setups.inc:112 |
| `0x0B` | shared | `MULTIPLEX_ANIM_RING3_SLOT_0` | src/levels/_unified/lake/scene_transition_and_decor.inc:29 |
| `0x0C` | shared | `BEAST_AI_DISPATCH_BY_X_AND_VAR_0D` | src/levels/_unified/lake/screen_to_the_right_setups.inc:29 (+1 more) |
| `0x0C` | shared | `DRAW_LAKE_051_SEQ_FROM_WORKING_POS` | src/levels/_unified/lake/scene_transition_and_decor.inc:30 |
| `0x0C` | shared | `SINKING_AT_CONSOLE` | src/levels/_unified/lake/pool_underwater_cinematic.inc:130 |
| `0x0C` | shared | `SWIMMING_UP_LEGS_ANIMATION` | src/levels/_unified/lake/pool_underwater_cinematic.inc:546 |
| `0x0D` | shared | `DECOR_F7_BLINK_3X_LOOP` | src/levels/_unified/lake/scene_transition_and_decor.inc:31 |
| `0x0D` | shared | `MULTIPLEX_ANIM_RING1_SLOT_1` | src/levels/_unified/lake/screen_to_the_right_setups.inc:30 |
| `0x0D` | shared | `MULTIPLEX_ANIM_RING2_SLOT_1` | src/levels/_unified/lake/screen_to_the_right_setups.inc:114 |
| `0x0D` | shared | `SWIMMING_UP_TORSO_ANIMATION` | src/levels/_unified/lake/pool_underwater_cinematic.inc:547 |
| `0x0E` | shared | `BEAST_AI_DISPATCH_BY_X_AND_VAR_0D` | src/levels/_unified/lake/screen_to_the_right_setups.inc:31 (+1 more) |
| `0x0E` | shared | `MULTIPLEX_ANIM_RING3_SLOT_1` | src/levels/_unified/lake/scene_transition_and_decor.inc:32 |
| `0x0E` | shared | `UPDATE_POSITION_OF_BUBBLES` | src/levels/_unified/lake/pool_underwater_cinematic.inc:127 |
| `0x0F` | shared | `BUBBLES_A_ANIMATION` | src/levels/_unified/lake/pool_underwater_cinematic.inc:128 |
| `0x0F` | shared | `DRAW_LAKE_051_SEQ_FROM_WORKING_POS` | src/levels/_unified/lake/scene_transition_and_decor.inc:33 |
| `0x0F` | shared | `MULTIPLEX_ANIM_RING1_SLOT_2` | src/levels/_unified/lake/screen_to_the_right_setups.inc:32 |
| `0x0F` | shared | `MULTIPLEX_ANIM_RING2_SLOT_2` | src/levels/_unified/lake/screen_to_the_right_setups.inc:116 |
| `0x10` | shared | `BEAST_AI_DISPATCH_BY_X_AND_VAR_0D` | src/levels/_unified/lake/screen_to_the_right_setups.inc:33 (+1 more) |
| `0x10` | shared | `BUBBLES_B_ANIMATION` | src/levels/_unified/lake/pool_underwater_cinematic.inc:129 |
| `0x10` | shared | `DECOR_F7_BLINK_3X_LOOP` | src/levels/_unified/lake/scene_transition_and_decor.inc:34 |
| `0x11` | shared | `MULTIPLEX_ANIM_RING1_SLOT_3` | src/levels/_unified/lake/screen_to_the_right_setups.inc:34 |
| `0x11` | shared | `MULTIPLEX_ANIM_RING3_SLOT_2` | src/levels/_unified/lake/scene_transition_and_decor.inc:35 |
| `0x11` | shared | `MULTIPLEX_RING4_SAVE_LOOP` | src/levels/_unified/lake/screen_to_the_right_setups.inc:118 |
| `0x12` | shared | `BEAST_AI_DISPATCH_BY_X_AND_VAR_0D` | src/levels/_unified/lake/screen_to_the_right_setups.inc:35 (+1 more) |
| `0x13` | shared | `MULTIPLEX_RING3_SAVE_LOOP` | src/levels/_unified/lake/screen_to_the_right_setups.inc:36 |
| `0x13` | shared | `MULTIPLEX_RING5_SAVE_LOOP` | src/levels/_unified/lake/screen_to_the_right_setups.inc:120 |
| `0x14` | shared | `DRAW_LAKE_051_SEQ_FROM_WORKING_POS` | src/levels/_unified/lake/scene_transition_and_decor.inc:36 |
| `0x14` | shared | `ENTITY_DROP_THEN_F15_LOOP` | src/levels/_unified/lake/lake_intro_setup.inc:37 |
| `0x14` | shared | `GETTING_OUT_OF_THE_POOL__ANIMATION_PART_4` | src/levels/_unified/lake/random_init_and_music_setup.inc:76 |
| `0x14` | shared | `HERO_CROUCH_LEFT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:87 |
| `0x14` | shared | `HERO_CROUCH_RIGHT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:81 |
| `0x14` | shared | `HERO_FALL_LEFT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:59 |
| `0x14` | shared | `HERO_FALL_LEFT_PRELUDE` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:61 |
| `0x14` | shared | `HERO_FALL_RIGHT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:69 |
| `0x14` | shared | `HERO_FALL_RIGHT_PRELUDE` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:71 |
| `0x14` | shared | `HERO_JUMP_RISE_PARABOLA` | src/levels/_unified/lake/hero_physics_jump.inc:52 |
| `0x14` | shared | `HERO_KICK_LEFT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:125 |
| `0x14` | shared | `HERO_KICK_RIGHT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:117 |
| `0x14` | shared | `HERO_LEAP_LEFT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:95 |
| `0x14` | shared | `HERO_LEAP_LEFT_PRELUDE` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:97 |
| `0x14` | shared | `HERO_LEAP_RIGHT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:105 |
| `0x14` | shared | `HERO_LEAP_RIGHT_PRELUDE` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:107 |
| `0x14` | shared | `HERO_RUN_LEFT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:9 |
| `0x14` | dos | `HERO_RUN_LEFT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:34 |
| `0x14` | shared | `HERO_RUN_RIGHT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:15 |
| `0x14` | dos | `HERO_RUN_RIGHT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:40 |
| `0x14` | shared | `HERO_STAND_LEFT_LOOP` | src/levels/_unified/lake/hero_lake_edge_and_init.inc:51 |
| `0x14` | shared | `HERO_WALK_LEFT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:21 |
| `0x14` | dos | `HERO_WALK_LEFT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:46 |
| `0x14` | shared | `HERO_WALK_RIGHT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:26 |
| `0x14` | dos | `HERO_WALK_RIGHT_LOOP` | src/levels/_unified/lake/hero_ai_dispatch_airborne.inc:51 |
| `0x14` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/hero_physics_jump.inc:43 (+1 more) |
| `0x14` | shared | `LESTER_AT_POOL_LOOP` | src/levels/_unified/lake/lake_intro_setup.inc:125 |
| `0x14` | amiga | `MAYBE_RESUME_WALK_RIGHT_IF_GROUNDED` | src/levels/_unified/lake/lester_drift_and_swing.inc:294 |
| `0x14` | cart | `RESUME_R_AFTER_VINE_LAND` | src/levels/_unified/lake/lester_drift_and_swing.inc:290 (+1 more) |
| `0x15` | shared | `DECOR_AT_327_164_BLINK_LOOP` | src/levels/_unified/lake/lester_at_pool_animations.inc:44 |
| `0x15` | shared | `DECOR_F9_THEN_F10_LOOP` | src/levels/_unified/lake/scene_transition_and_decor.inc:37 |
| `0x15` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/hero_leap_right_kicks_crouch_pool.inc:374 (+5 more) |
| `0x15` | dos | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/hero_leap_right_kicks_crouch_pool.inc:607 |
| `0x15` | shared | `LOOP_DRAW_DECOR_215_AT_327_164` | src/levels/_unified/lake/lake_intro_setup.inc:126 |
| `0x15` | shared | `POST_RUN_LEFT_DECEL_LOOP` | src/levels/_unified/lake/hero_dispatch_and_leap_left.inc:47 |
| `0x15` | amiga | `WAIT_RUN_LEFT_THEN_DECEL` | src/levels/_unified/lake/hero_dispatch_and_leap_left.inc:49 |
| `0x15` | shared | `WAIT_RUN_RIGHT_THEN_DECEL` | src/levels/_unified/lake/hero_leap_right_kicks_crouch_pool.inc:122 |
| `0x16` | shared | `HERO_AI_DISPATCH` | src/levels/_unified/lake/getting_out_of_pool_animation.inc:249 |
| `0x16` | shared | `HERO_PHYSICS_TICK` | src/levels/_unified/lake/pool_underwater_cinematic.inc:548 |
| `0x16` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/lake_intro_setup.inc:39 (+2 more) |
| `0x16` | shared | `LAKE_PALETTE_FADE_IN` | src/levels/_unified/lake/lester_at_pool_animations.inc:90 |
| `0x16` | shared | `LESTER_FALLING_PLAY_AND_ANIM` | src/levels/_unified/lake/scene_transition_and_decor.inc:38 |
| `0x16` | shared | `LOOP_DRAW_LAKE_037_AT_305_155` | src/levels/_unified/lake/lester_at_pool_animations.inc:45 |
| `0x17` | shared | `DECOR_AT_305_155_F14_F9_BG` | src/levels/_unified/lake/lake_intro_setup.inc:36 |
| `0x17` | shared | `GETTING_OUT_POOL_PART_3_RPT` | src/levels/_unified/lake/getting_out_of_pool_animation.inc:262 |
| `0x17` | shared | `MAIN_TENTACLE_INSIDE_POOL_ANIMATION` | src/levels/_unified/lake/pool_underwater_cinematic.inc:198 |
| `0x18` | shared | `SETUP_TENTACLE_ANIMATIONS` | src/levels/_unified/lake/pool_underwater_cinematic.inc:508 |
| `0x24` | shared | `AMBIENT_CH24_DELAY_F1` | src/levels/_unified/lake/opening_bg_droplet_sprinkles.inc:45 |
| `0x24` | shared | `AMBIENT_LOOP_CH24` | src/levels/_unified/lake/beast_surprises_lester.inc:162 (+1 more) |
| `0x25` | shared | `AMBIENT_CH25_RESTART` | src/levels/_unified/lake/opening_bg_droplet_sprinkles.inc:46 |
| `0x25` | shared | `AMBIENT_LOOP_CH25` | src/levels/_unified/lake/beast_surprises_lester.inc:163 (+1 more) |
| `0x28` | shared | `BEAST_AI_SPAWN_FAR_LEFT` | src/levels/_unified/lake/lester_drift_and_swing.inc:305 |
| `0x28` | shared | `BEAST_AI_SPAWN_FAR_RIGHT` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:26 |
| `0x28` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/scene_transition_and_decor.inc:48 |
| `0x28` | shared | `THE_BEAST_KILLS_LESTER` | src/levels/_unified/lake/beast_distance_check_and_spawns.inc:35 |
| `0x28` | shared | `WAIT_BEAST_TRIGGER_THEN_INIT` | src/levels/_unified/lake/screen_to_the_right_setups.inc:148 |
| `0x29` | shared | `CHECK_IF_THE_BEAST_HAS_ALREADY_REACHED_LESTER` | src/levels/_unified/lake/beast_approach_decel.inc:183 (+1 more) |
| `0x29` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/beast_approach_decel.inc:81 (+2 more) |
| `0x29` | dos | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/beast_approach_decel.inc:84 |
| `0x29` | shared | `THE_BEAST_IS_KILLED_BY_A_LASER_SHOT` | src/levels/_unified/lake/scene_transition_and_decor.inc:49 |
| `0x29` | shared | `WAIT_UNTIL_BEAST_CLOSE` | src/levels/_unified/lake/beast_approach_decel.inc:185 (+1 more) |
| `0x2B` | shared | `LESTER_FRAME_LOOP` | src/levels/_unified/lake/slug_attack_cinematic.inc:220 |
| `0x2C` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/slug_attack_cinematic.inc:217 |
| `0x2C` | shared | `SLUG_ATTACK_LEG_LOOP` | src/levels/_unified/lake/slug_attack_cinematic.inc:166 |
| `0x2D` | shared | `BEAST_FLASH_LOOP` | src/levels/_unified/lake/beast_surprise_scene.inc:37 |
| `0x2D` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/beast_surprise_scene.inc:2 |
| `0x2D` | shared | `TRIGGER_SCENE_RESUME` | src/levels/_unified/lake/slug_anim_and_flip.inc:197 (+1 more) |
| `0x2E` | shared | `BEETLE_ANIM_FLY_AWAY_INIT_COUNTER` | src/levels/_unified/lake/beetle.inc:94 (+1 more) |
| `0x2E` | shared | `BEETLE_KICK_DETECTOR` | src/levels/_unified/lake/random_init_and_music_setup.inc:84 |
| `0x2E` | shared | `WAIT_FOR_BEETLE_OFFSCREEN_THEN_KILL` | src/levels/_unified/lake/random_init_and_music_setup.inc:85 |
| `0x2F` | shared | `INC_VAR_6E_PER_TICK_LOOP` | src/levels/_unified/lake/random_init_and_music_setup.inc:86 |
| `0x30` | shared | `WAIT_FOR_TIMER_AND_HACK_67_THEN_SETUP_31` | src/levels/_unified/lake/random_init_and_music_setup.inc:87 |
| `0x31` | shared | `PICK_RANDOM_X_FOR_DROPLET_AND_PLAY_DROP_SOUND` | src/levels/_unified/lake/video_pages_and_timer.inc:65 |
| `0x33` | shared | `SCATTER_3DOTS_INIT_RIGHT` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:61 |
| `0x34` | shared | `DRAW_3_SCATTER_DOTS_CYCLE` | src/levels/_unified/lake/scatter_3dots_classify_regions.inc:13 |
| `0x34` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/scatter_3dots_classify_regions.inc:28 (+1 more) |
| `0x34` | shared | `OTHER_TENTACLES_INSIDE_POOL_ANIMATION` | src/levels/_unified/lake/pool_underwater_cinematic.inc:199 |
| `0x35` | shared | `SCATTER_3DOT_BURST_LEFT` | src/levels/_unified/lake/screen_to_the_right_setups.inc:37 |
| `0x35` | shared | `SCATTER_DOTS_BURST_RIGHT_SEQ` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:63 |
| `0x36` | shared | `DRAW_8_SCATTER_DOTS_CYCLE` | src/levels/_unified/lake/screen_to_the_right_setups.inc:38 |
| `0x36` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/scatter_dots_burst_right_drift.inc:16 (+3 more) |
| `0x36` | shared | `PARTICLE_BURST_CYCLE_LOOP` | src/levels/_unified/lake/scatter_dots_burst_right_drift.inc:10 (+1 more) |
| `0x36` | shared | `SCATTER_3DOT_BURST_RIGHT` | src/levels/_unified/lake/screen_to_the_right_setups.inc:121 |
| `0x37` | shared | `DRAW_8_SCATTER_DOTS_CYCLE` | src/levels/_unified/lake/screen_to_the_right_setups.inc:122 |
| `0x37` | shared | `PARTICLE_BURST_7X_ENTRY` | src/levels/_unified/lake/screen_to_the_right_setups.inc:40 (+1 more) |
| `0x37` | shared | `SCATTER_8DOT_F3_BLINK_LOOP` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:65 |
| `0x38` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/channel_cleanup_helpers.inc:4 (+1 more) |
| `0x38` | shared | `LOOP_DRAW_LAKE_018_AT_CENTER` | src/levels/_unified/lake/screen_to_the_right_setups.inc:123 |
| `0x38` | shared | `LOOP_DRAW_VINE_FG` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:20 |
| `0x38` | shared | `PARTICLE_BURST_7X_LOOP` | src/levels/_unified/lake/screen_to_the_right_setups.inc:44 |
| `0x38` | shared | `REED_PLANT_ANIMATION` | src/levels/_unified/lake/vine_and_outside_pool_screens.inc:66 |
| `0x3B` | shared | `GOO_DRIPPING_FROM_SLUGS_CLAW_ANIMATION` | src/levels/_unified/lake/slug_attack_cinematic.inc:120 |
| `0x3C` | shared | `BLIT_FROM_PAGE_0_LOOP` | src/levels/_unified/lake/beast_approach_decel.inc:210 (+15 more) |
| `0x3C` | amiga | `BLIT_FROM_PAGE_0_LOOP` | src/levels/_unified/lake/lake_entry_and_init.inc:63 |
| `0x3C` | dos | `BLIT_FROM_PAGE_0_LOOP` | src/levels/_unified/lake/beast_approach_decel.inc:213 (+12 more) |
| `0x3C` | shared | `BLIT_FROM_PAGE_3_LOOP` | src/levels/_unified/lake/pool_underwater_cinematic.inc:85 |
| `0x3C` | shared | `BLIT_FROM_PAGE_40_LOOP` | src/levels/_unified/lake/lake_entry_and_init.inc:61 |
| `0x3C` | shared | `CLEAR_FRAMEBUFFER_TO_COLOR_4_LOOP` | src/levels/_unified/lake/slug_attack_cinematic.inc:93 (+1 more) |
| `0x3C` | shared | `KILL_CHANNEL_ROUTINE` | src/levels/_unified/lake/lake_entry_and_init.inc:111 |
| `0x3C` | shared | `LOOP_BLIT_AND_CLEAR_FF` | src/levels/_unified/lake/beast_kills_lester_and_respawn.inc:86 |
| `0x3C` | shared | `RENDER_FRAME_DISPATCH` | src/levels/_unified/lake/beast_drift_and_screen_shift.inc:40 (+2 more) |
| `0x3F` | shared | `OUTSIDE_POOL_SCREEN` | src/levels/_unified/lake/lester_drift_and_swing.inc:253 |
| `0x3F` | shared | `START_LAKE_BG_MUSIC_AND_DELETE_CH_0_2` | src/levels/_unified/lake/random_init_and_music_setup.inc:61 |

## PRISON

| channel | branch | routine | source |
| ---: | --- | --- | --- |
| `0x00` | cart | `LABEL_0000` | src/levels/_unified/prison/cart__entry.inc:2346 |
| `0x00` | amiga | `LABEL_0000` | src/levels/_unified/prison/amiga__post_DELAY_4_QUANTUMS.inc:35 |
| `0x00` | dos | `LABEL_0000` | src/levels/_unified/prison/dos__post_DELAY_4_QUANTUMS.inc:46 |
| `0x00` | amiga | `LABEL_00C1` | src/levels/_unified/prison/amiga__post_DELAY_4_QUANTUMS.inc:13 |
| `0x00` | dos | `LABEL_00DD` | src/levels/_unified/prison/dos__post_DELAY_4_QUANTUMS.inc:16 |
| `0x00` | cart | `LABEL_0161` | src/levels/_unified/prison/cart__entry.inc:2308 |
| `0x00` | amiga | `LABEL_0180` | src/levels/_unified/prison/amiga__post_INLINE_KILL_039.inc:300 |
| `0x00` | dos | `LABEL_01A2` | src/levels/_unified/prison/dos__post_INLINE_KILL_039.inc:253 |
| `0x00` | cart | `LABEL_0210` | src/levels/_unified/prison/cart__post_INLINE_KILL_039.inc:257 |
| `0x00` | dos | `LABEL_1CB0` | src/levels/_unified/prison/dos__entry.inc:2230 (+1 more) |
| `0x00` | amiga | `LABEL_1CB8` | src/levels/_unified/prison/amiga__entry.inc:2245 (+1 more) |
| `0x00` | cart | `LABEL_1D52` | src/levels/_unified/prison/cart__entry.inc:2264 (+1 more) |
| `0x00` | amiga | `LABEL_7F0E` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:100 (+3 more) |
| `0x00` | dos | `LABEL_7FE0` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:100 (+3 more) |
| `0x00` | cart | `LABEL_810F` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:101 (+3 more) |
| `0x01` | cart | `COPY_PAGE0_TO_FF_KILL_CHANNEL` | src/levels/_unified/prison/cart__post_ADD_VAR43_VAR47_BY_20.inc:23 |
| `0x01` | amiga | `COPY_PAGE0_TO_FF_KILL_CHANNEL` | src/levels/_unified/prison/amiga__post_ADD_VAR43_VAR47_BY_20.inc:23 |
| `0x01` | dos | `COPY_PAGE0_TO_FF_KILL_CHANNEL` | src/levels/_unified/prison/dos__post_ADD_VAR43_VAR47_BY_20.inc:23 |
| `0x01` | amiga | `DRAW_CIN_090_TO_104_3F_AT_8C208B32` | src/levels/_unified/prison/amiga__post_SCROLL_UP_16_VAR14_VAR18_AND_SCROLL_Y.inc:103 |
| `0x01` | dos | `DRAW_CIN_090_TO_104_3F_AT_8C208B32` | src/levels/_unified/prison/dos__post_RESET_HERO_POS_UP_DOWN.inc:91 |
| `0x01` | amiga | `DRAW_CIN_319_TO_319_4F_AT_9E666694` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:48 |
| `0x01` | dos | `DRAW_CIN_319_TO_319_4F_AT_9E666694` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:48 |
| `0x01` | amiga | `DRAW_CIN_683_TO_685_3F_AT_1EB7324B` | src/levels/_unified/prison/amiga__post_FOLD_BODY_338B_C0D45EFA.inc:47 |
| `0x01` | dos | `DRAW_CIN_683_TO_685_3F_AT_1EB7324B` | src/levels/_unified/prison/dos__post_FOLD_BODY_338B_C0D45EFA.inc:47 |
| `0x01` | cart | `FILL_PFF_PLAY_SFX_0061_AT_C0D45EFA` | src/levels/_unified/prison/cart__entry.inc:2254 |
| `0x01` | amiga | `FILL_PFF_PLAY_SFX_0061_AT_C0D45EFA` | src/levels/_unified/prison/amiga__entry.inc:2236 |
| `0x01` | dos | `FILL_PFF_PLAY_SFX_0061_AT_C0D45EFA` | src/levels/_unified/prison/dos__entry.inc:2221 |
| `0x01` | cart | `INIT_VARS_E7_E8` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:288 |
| `0x01` | amiga | `INIT_VARS_E7_E8` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:275 |
| `0x01` | dos | `INIT_VARS_E7_E8` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:286 |
| `0x01` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:291 (+1 more) |
| `0x01` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:278 (+1 more) |
| `0x01` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:289 (+1 more) |
| `0x01` | cart | `LABEL_0B17` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:48 |
| `0x01` | dos | `LABEL_0C2F` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:24 |
| `0x01` | amiga | `LABEL_0C4F` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:24 |
| `0x01` | cart | `LABEL_0CB7` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:24 |
| `0x01` | dos | `LABEL_1D4F` | src/levels/_unified/prison/dos__post_FOLD_BODY_144B_C55279EA.inc:26 |
| `0x01` | amiga | `LABEL_1D57` | src/levels/_unified/prison/amiga__post_FOLD_BODY_144B_C55279EA.inc:26 |
| `0x01` | cart | `LABEL_1DF1` | src/levels/_unified/prison/cart__post_FOLD_BODY_144B_C55279EA.inc:26 |
| `0x01` | cart | `LABEL_4DE8` | src/levels/_unified/prison/cart__post_FOLD_BODY_338B_C0D45EFA.inc:47 |
| `0x01` | amiga | `LABEL_7D12` | src/levels/_unified/prison/amiga__post_SCROLL_UP_16_VAR14_VAR18_AND_SCROLL_Y.inc:97 |
| `0x01` | amiga | `LABEL_7D1E` | src/levels/_unified/prison/amiga__post_SCROLL_UP_16_VAR14_VAR18_AND_SCROLL_Y.inc:105 (+1 more) |
| `0x01` | amiga | `LABEL_7D25` | src/levels/_unified/prison/amiga__post_SCROLL_UP_16_VAR14_VAR18_AND_SCROLL_Y.inc:91 (+1 more) |
| `0x01` | amiga | `LABEL_7D31` | src/levels/_unified/prison/amiga__post_SCROLL_UP_16_VAR14_VAR18_AND_SCROLL_Y.inc:93 |
| `0x01` | dos | `LABEL_7DDD` | src/levels/_unified/prison/dos__post_RESET_HERO_POS_UP_DOWN.inc:85 |
| `0x01` | dos | `LABEL_7DE9` | src/levels/_unified/prison/dos__post_RESET_HERO_POS_UP_DOWN.inc:93 (+1 more) |
| `0x01` | dos | `LABEL_7DF0` | src/levels/_unified/prison/dos__post_RESET_HERO_POS_UP_DOWN.inc:79 (+1 more) |
| `0x01` | dos | `LABEL_7DFC` | src/levels/_unified/prison/dos__post_RESET_HERO_POS_UP_DOWN.inc:81 |
| `0x01` | cart | `LABEL_7EEE` | src/levels/_unified/prison/cart__post_RESET_HERO_POS_UP_DOWN.inc:99 |
| `0x01` | cart | `LABEL_7F0C` | src/levels/_unified/prison/cart__post_RESET_HERO_POS_UP_DOWN.inc:91 |
| `0x01` | cart | `LABEL_7F18` | src/levels/_unified/prison/cart__post_RESET_HERO_POS_UP_DOWN.inc:102 (+1 more) |
| `0x01` | cart | `LABEL_7F1F` | src/levels/_unified/prison/cart__post_RESET_HERO_POS_UP_DOWN.inc:83 (+1 more) |
| `0x01` | cart | `LABEL_7F2B` | src/levels/_unified/prison/cart__post_RESET_HERO_POS_UP_DOWN.inc:87 |
| `0x01` | cart | `SETUP_VARS_01_B0_02_B6_06_C7_28_FROM_01` | src/levels/_unified/prison/cart__post_ACCUMULATE_HASH_VAR37_38_X3.inc:63 |
| `0x01` | dos | `SETUP_VARS_01_B0_02_B6_06_C7_28_FROM_01` | src/levels/_unified/prison/dos__post_ACCUMULATE_HASH_VAR37_38_X3.inc:63 |
| `0x01` | cart | `SET_PAL_07_FILL_TWO_PAGES_86243111` | src/levels/_unified/prison/cart__post_FOLD_BODY_104B_22B91458.inc:310 |
| `0x01` | amiga | `SET_PAL_07_FILL_TWO_PAGES_86243111` | src/levels/_unified/prison/amiga__post_DRAW_CIN_683_TO_685_3F_AT_1EB7324B.inc:63 |
| `0x01` | dos | `SET_PAL_07_FILL_TWO_PAGES_86243111` | src/levels/_unified/prison/dos__post_DRAW_CIN_683_TO_685_3F_AT_1EB7324B.inc:64 |
| `0x02` | cart | `INIT_VARS_16_17` | src/levels/_unified/prison/cart__post_FOLD_BODY_338B_C0D45EFA.inc:48 |
| `0x02` | amiga | `INIT_VARS_16_17` | src/levels/_unified/prison/amiga__post_FOLD_BODY_338B_C0D45EFA.inc:48 |
| `0x02` | dos | `INIT_VARS_16_17` | src/levels/_unified/prison/dos__post_FOLD_BODY_338B_C0D45EFA.inc:48 |
| `0x02` | cart | `INLINE_SET_VARE9_TO_8` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:289 |
| `0x02` | amiga | `INLINE_SET_VARE9_TO_8` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:276 |
| `0x02` | dos | `INLINE_SET_VARE9_TO_8` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:287 |
| `0x02` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:292 (+1 more) |
| `0x02` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:279 (+1 more) |
| `0x02` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:290 (+1 more) |
| `0x02` | dos | `LABEL_0C08` | src/levels/_unified/prison/dos__post_SET_VAR13_TO_FFFF.inc:21 |
| `0x02` | amiga | `LABEL_0C28` | src/levels/_unified/prison/amiga__post_SET_VAR13_TO_FFFF.inc:21 |
| `0x02` | cart | `LABEL_0C90` | src/levels/_unified/prison/cart__post_SET_VAR13_TO_FFFF.inc:21 |
| `0x02` | dos | `LABEL_0CA3` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:25 |
| `0x02` | amiga | `LABEL_0CC3` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:25 |
| `0x02` | cart | `LABEL_0D2B` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:25 |
| `0x02` | dos | `LABEL_0DEC` | src/levels/_unified/prison/dos__post_INIT_VARS_15_19_18_14_PLUS4.inc:42 |
| `0x02` | amiga | `LABEL_0E0C` | src/levels/_unified/prison/amiga__post_INIT_VARS_15_19_18_14_PLUS4.inc:42 |
| `0x02` | cart | `LABEL_0E74` | src/levels/_unified/prison/cart__post_INIT_VARS_15_19_18_14_PLUS4.inc:50 |
| `0x02` | dos | `LABEL_1D58` | src/levels/_unified/prison/dos__post_FOLD_BODY_144B_C55279EA.inc:27 |
| `0x02` | amiga | `LABEL_1D60` | src/levels/_unified/prison/amiga__post_FOLD_BODY_144B_C55279EA.inc:27 |
| `0x02` | cart | `LABEL_1DFA` | src/levels/_unified/prison/cart__post_FOLD_BODY_144B_C55279EA.inc:27 |
| `0x02` | amiga | `LABEL_4EDA` | src/levels/_unified/prison/amiga__entry.inc:2237 |
| `0x02` | amiga | `LABEL_4F23` | src/levels/_unified/prison/amiga__post_DRAW_CIN_683_TO_685_3F_AT_1EB7324B.inc:64 |
| `0x02` | dos | `LABEL_4F83` | src/levels/_unified/prison/dos__entry.inc:2222 |
| `0x02` | dos | `LABEL_4FCC` | src/levels/_unified/prison/dos__post_DRAW_CIN_683_TO_685_3F_AT_1EB7324B.inc:65 |
| `0x02` | cart | `LABEL_5083` | src/levels/_unified/prison/cart__entry.inc:2255 |
| `0x02` | cart | `LABEL_50CC` | src/levels/_unified/prison/cart__post_FOLD_BODY_104B_22B91458.inc:311 |
| `0x03` | amiga | `DRAW_CIN_318_TO_318_2F_AT_93A8CE70` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:26 |
| `0x03` | dos | `DRAW_CIN_318_TO_318_2F_AT_93A8CE70` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:26 |
| `0x03` | cart | `INLINE_SET_VARE6_TO_50` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:204 |
| `0x03` | amiga | `INLINE_SET_VARE6_TO_50` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:203 |
| `0x03` | dos | `INLINE_SET_VARE6_TO_50` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:203 |
| `0x03` | cart | `LABEL_0B3A` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:26 |
| `0x03` | dos | `LABEL_0E1A` | src/levels/_unified/prison/dos__post_INIT_VARS_15_19_18_14_PLUS4.inc:43 |
| `0x03` | amiga | `LABEL_0E3A` | src/levels/_unified/prison/amiga__post_INIT_VARS_15_19_18_14_PLUS4.inc:43 |
| `0x03` | cart | `LABEL_0EA2` | src/levels/_unified/prison/cart__post_INIT_VARS_15_19_18_14_PLUS4.inc:51 |
| `0x03` | dos | `LABEL_1E2B` | src/levels/_unified/prison/dos__post_FOLD_BODY_144B_C55279EA.inc:28 |
| `0x03` | amiga | `LABEL_1E33` | src/levels/_unified/prison/amiga__post_FOLD_BODY_144B_C55279EA.inc:28 |
| `0x03` | cart | `LABEL_1ECD` | src/levels/_unified/prison/cart__post_FOLD_BODY_144B_C55279EA.inc:28 |
| `0x03` | amiga | `LABEL_4D31` | src/levels/_unified/prison/amiga__post_FOLD_BODY_338B_C0D45EFA.inc:49 |
| `0x03` | dos | `LABEL_4DDA` | src/levels/_unified/prison/dos__post_FOLD_BODY_338B_C0D45EFA.inc:49 |
| `0x03` | cart | `LABEL_4EDA` | src/levels/_unified/prison/cart__post_FOLD_BODY_338B_C0D45EFA.inc:49 |
| `0x04` | dos | `LABEL_09E4` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:27 |
| `0x04` | amiga | `LABEL_0A04` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:27 |
| `0x04` | cart | `LABEL_0A6C` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:27 |
| `0x04` | dos | `LABEL_0B88` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:204 |
| `0x04` | amiga | `LABEL_0BA8` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:204 |
| `0x04` | cart | `LABEL_0C10` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:205 |
| `0x04` | dos | `LABEL_1D58` | src/levels/_unified/prison/dos__post_FOLD_BODY_144B_C55279EA.inc:29 |
| `0x04` | amiga | `LABEL_1D60` | src/levels/_unified/prison/amiga__post_FOLD_BODY_144B_C55279EA.inc:29 |
| `0x04` | cart | `LABEL_1DFA` | src/levels/_unified/prison/cart__post_FOLD_BODY_144B_C55279EA.inc:29 |
| `0x05` | cart | `INLINE_SET_VARE7_TO_5` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:206 |
| `0x05` | amiga | `INLINE_SET_VARE7_TO_5` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:205 |
| `0x05` | dos | `INLINE_SET_VARE7_TO_5` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:205 |
| `0x05` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:208 |
| `0x05` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:207 |
| `0x05` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:207 |
| `0x05` | dos | `LABEL_09F1` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:28 |
| `0x05` | amiga | `LABEL_0A11` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:28 |
| `0x05` | cart | `LABEL_0A79` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:28 |
| `0x05` | dos | `LABEL_1D01` | src/levels/_unified/prison/dos__post_FOLD_BODY_144B_C55279EA.inc:30 |
| `0x05` | amiga | `LABEL_1D09` | src/levels/_unified/prison/amiga__post_FOLD_BODY_144B_C55279EA.inc:30 |
| `0x05` | cart | `LABEL_1DA3` | src/levels/_unified/prison/cart__post_FOLD_BODY_144B_C55279EA.inc:30 |
| `0x08` | amiga | `DRAW_CIN_624_TO_628_5F_AT_499AFE0A` | src/levels/_unified/prison/amiga__post_FILL_AND_DRAW_CIN_24_28.inc:86 |
| `0x08` | dos | `DRAW_CIN_624_TO_628_5F_AT_499AFE0A` | src/levels/_unified/prison/dos__post_FILL_AND_DRAW_CIN_24_28.inc:86 |
| `0x08` | amiga | `DRAW_CIN_628_TO_625_4F_AT_2F47D6D0` | src/levels/_unified/prison/amiga__post_FILL_AND_DRAW_CIN_24_28.inc:44 |
| `0x08` | dos | `DRAW_CIN_628_TO_625_4F_AT_2F47D6D0` | src/levels/_unified/prison/dos__post_FILL_AND_DRAW_CIN_24_28.inc:44 |
| `0x08` | cart | `INLINE_SET_VARF1_TO_64` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR29_TO_6.inc:32 |
| `0x08` | amiga | `INLINE_SET_VARF1_TO_64` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR29_TO_6.inc:32 |
| `0x08` | dos | `INLINE_SET_VARF1_TO_64` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR29_TO_6.inc:32 |
| `0x08` | cart | `LABEL_4D83` | src/levels/_unified/prison/cart__post_FOLD_BODY_104B_22B91458.inc:179 |
| `0x08` | cart | `LABEL_4D9C` | src/levels/_unified/prison/cart__post_FOLD_BODY_104B_22B91458.inc:137 |
| `0x0A` | dos | `JUNK__7E74` | src/levels/_unified/prison/dos__post_DECREMENT_VAR10_BY_1.inc:199 |
| `0x0A` | cart | `JUNK__7FA3` | src/levels/_unified/prison/cart__post_DECREMENT_VAR10_BY_1.inc:201 |
| `0x0A` | dos | `LABEL_0567` | src/levels/_unified/prison/dos__entry.inc:2212 |
| `0x0A` | cart | `LABEL_05EF` | src/levels/_unified/prison/cart__entry.inc:2240 |
| `0x10` | dos | `LABEL_12D8` | src/levels/_unified/prison/dos__post_INIT_VARS_A1_A4_A7_AA_PLUS4.inc:24 |
| `0x10` | amiga | `LABEL_12E0` | src/levels/_unified/prison/amiga__post_INIT_VARS_A1_A4_A7_AA_PLUS4.inc:24 |
| `0x10` | cart | `LABEL_136A` | src/levels/_unified/prison/cart__post_INIT_VARS_A1_A4_A7_AA_PLUS4.inc:24 |
| `0x11` | amiga | `DRAW_CIN_569_TO_572_6F_AT_F8680E45` | src/levels/_unified/prison/amiga__post_DECREMENT_VAR29_BY_1.inc:54 (+1 more) |
| `0x11` | dos | `DRAW_CIN_569_TO_572_6F_AT_F8680E45` | src/levels/_unified/prison/dos__post_DECREMENT_VAR29_BY_1.inc:54 (+1 more) |
| `0x11` | amiga | `DRAW_CIN_570_574_BLOCK` | src/levels/_unified/prison/amiga__post_DRAW_CIN_576_578_BLOCK.inc:198 |
| `0x11` | dos | `DRAW_CIN_570_574_BLOCK` | src/levels/_unified/prison/dos__post_DRAW_CIN_576_578_BLOCK.inc:198 |
| `0x11` | cart | `DRAW_CIN_570_574_BLOCK__CART__POST_FOLD_BODY_144B_C55279EA` | src/levels/_unified/prison/cart__post_FOLD_BODY_144B_C55279EA.inc:503 |
| `0x11` | cart | `LABEL_1FA0` | src/levels/_unified/prison/cart__post_DECREMENT_VAR29_BY_1.inc:54 (+1 more) |
| `0x12` | cart | `DRAW_CIN_576_578_BLOCK` | src/levels/_unified/prison/cart__post_STEP_VAR1A_DOWN5_VAR1B_UP2.inc:331 |
| `0x12` | amiga | `DRAW_CIN_576_578_BLOCK` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:54 |
| `0x12` | dos | `DRAW_CIN_576_578_BLOCK` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:54 |
| `0x14` | amiga | `BANK4_AFTER_CIN_414` | src/levels/_unified/prison/amiga__post_INLINE_SET_VARE9_TO_8.inc:134 |
| `0x14` | dos | `BANK4_AFTER_CIN_414` | src/levels/_unified/prison/dos__post_INLINE_SET_VARE9_TO_8.inc:134 |
| `0x14` | cart | `DRAW_CIN555_STEP_RIGHT3` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_1.inc:6 |
| `0x14` | amiga | `DRAW_CIN555_STEP_RIGHT3` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_1.inc:6 |
| `0x14` | dos | `DRAW_CIN555_STEP_RIGHT3` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_1.inc:6 |
| `0x14` | amiga | `DRAW_CIN_146_TO_147_4F_AT_8AA18039` | src/levels/_unified/prison/amiga__post_PLAY_SFX_005C_CH01.inc:13 |
| `0x14` | dos | `DRAW_CIN_146_TO_147_4F_AT_8AA18039` | src/levels/_unified/prison/dos__post_PLAY_SFX_005C_CH01.inc:13 |
| `0x14` | amiga | `DRAW_CIN_280_TO_281_2F_AT_75ED3E60` | src/levels/_unified/prison/amiga__post_PLAY_SFX_005C_CH01.inc:19 |
| `0x14` | dos | `DRAW_CIN_280_TO_281_2F_AT_75ED3E60` | src/levels/_unified/prison/dos__post_PLAY_SFX_005C_CH01.inc:19 |
| `0x14` | amiga | `DRAW_CIN_422_WITH_POS_STEP_AT_C7A1BFCB` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:84 |
| `0x14` | dos | `DRAW_CIN_422_WITH_POS_STEP_AT_C7A1BFCB` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:85 |
| `0x14` | cart | `INIT_VARS_15_19_18_14_PLUS4` | src/levels/_unified/prison/cart__entry.inc:2262 (+1 more) |
| `0x14` | amiga | `INIT_VARS_15_19_18_14_PLUS4` | src/levels/_unified/prison/amiga__entry.inc:2243 (+1 more) |
| `0x14` | dos | `INIT_VARS_15_19_18_14_PLUS4` | src/levels/_unified/prison/dos__entry.inc:2228 (+1 more) |
| `0x14` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR03_TO_7.inc:14 |
| `0x14` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR03_TO_7.inc:14 |
| `0x14` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR03_TO_7.inc:14 |
| `0x14` | dos | `LABEL_0481` | src/levels/_unified/prison/dos__post_DRAW_CIN_406_408_BLOCK.inc:10 |
| `0x14` | amiga | `LABEL_04BB` | src/levels/_unified/prison/amiga__post_DRAW_CIN_406_408_BLOCK.inc:10 |
| `0x14` | cart | `LABEL_0501` | src/levels/_unified/prison/cart__post_INLINE_SET_VARF1_TO_64.inc:37 |
| `0x14` | cart | `LABEL_055F` | src/levels/_unified/prison/cart__post_INLINE_SET_VARE9_TO_8.inc:134 |
| `0x14` | cart | `LABEL_0607` | src/levels/_unified/prison/cart__post_STEP_VAR1A_DOWN5_VAR1B_UP2.inc:362 |
| `0x14` | dos | `LABEL_0ED0` | src/levels/_unified/prison/dos__post_PLAY_SFX_005C_CH01.inc:17 |
| `0x14` | amiga | `LABEL_0EF0` | src/levels/_unified/prison/amiga__post_PLAY_SFX_005C_CH01.inc:17 |
| `0x14` | cart | `LABEL_0F58` | src/levels/_unified/prison/cart__post_PLAY_SFX_005C_CH01.inc:18 |
| `0x14` | cart | `LABEL_0F7F` | src/levels/_unified/prison/cart__post_PLAY_SFX_005C_CH01.inc:20 |
| `0x14` | dos | `LABEL_0F9B` | src/levels/_unified/prison/dos__post_PLAY_SFX_005C_CH01.inc:11 |
| `0x14` | amiga | `LABEL_0FBB` | src/levels/_unified/prison/amiga__post_PLAY_SFX_005C_CH01.inc:11 |
| `0x14` | cart | `LABEL_1023` | src/levels/_unified/prison/cart__post_PLAY_SFX_005C_CH01.inc:12 |
| `0x14` | cart | `LABEL_103E` | src/levels/_unified/prison/cart__post_PLAY_SFX_005C_CH01.inc:14 |
| `0x14` | amiga | `LABEL_75D8` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:40 |
| `0x14` | dos | `LABEL_7685` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:40 |
| `0x14` | cart | `LABEL_7788` | src/levels/_unified/prison/cart__post_STEP_VAR1A_DOWN5_VAR1B_UP2.inc:316 |
| `0x14` | amiga | `LABEL_7DEF` | src/levels/_unified/prison/amiga__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:13 |
| `0x14` | amiga | `LABEL_7E12` | src/levels/_unified/prison/amiga__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:8 |
| `0x14` | dos | `LABEL_7EBA` | src/levels/_unified/prison/dos__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:16 |
| `0x14` | dos | `LABEL_7EDD` | src/levels/_unified/prison/dos__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:11 |
| `0x14` | cart | `LABEL_7FE9` | src/levels/_unified/prison/cart__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:16 |
| `0x14` | cart | `LABEL_800C` | src/levels/_unified/prison/cart__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:11 |
| `0x14` | amiga | `LABEL_8E2B` | src/levels/_unified/prison/amiga__post_SET_VAR04_TO_0008.inc:9 |
| `0x14` | amiga | `LABEL_8F00` | src/levels/_unified/prison/amiga__post_ADD_VAR43_VAR47_BY_20.inc:15 (+1 more) |
| `0x14` | amiga | `LABEL_8F62` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_1.inc:4 |
| `0x14` | dos | `LABEL_8F91` | src/levels/_unified/prison/dos__post_SET_VAR04_TO_0008.inc:32 |
| `0x14` | amiga | `LABEL_9069` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_2.inc:46 |
| `0x14` | amiga | `LABEL_908D` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_2.inc:44 |
| `0x14` | dos | `LABEL_90C6` | src/levels/_unified/prison/dos__post_ADD_VAR43_VAR47_BY_20.inc:15 (+1 more) |
| `0x14` | cart | `LABEL_90F7` | src/levels/_unified/prison/cart__entry.inc:2237 (+1 more) |
| `0x14` | dos | `LABEL_9128` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_1.inc:4 |
| `0x14` | amiga | `LABEL_9153` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_5.inc:6 |
| `0x14` | amiga | `LABEL_9173` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_5.inc:4 |
| `0x14` | amiga | `LABEL_9200` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_2.inc:39 |
| `0x14` | cart | `LABEL_922C` | src/levels/_unified/prison/cart__post_ADD_VAR43_VAR47_BY_20.inc:15 (+1 more) |
| `0x14` | cart | `LABEL_928E` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_1.inc:4 |
| `0x14` | dos | `LABEL_9297` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_2.inc:46 |
| `0x14` | amiga | `LABEL_92A2` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_6.inc:20 |
| `0x14` | dos | `LABEL_92BB` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_2.inc:44 |
| `0x14` | amiga | `LABEL_92EB` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_2.inc:24 |
| `0x14` | dos | `LABEL_9381` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_5.inc:6 |
| `0x14` | dos | `LABEL_93A1` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_5.inc:4 |
| `0x14` | amiga | `LABEL_93F4` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_2.inc:12 |
| `0x14` | cart | `LABEL_93FD` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_2.inc:46 |
| `0x14` | cart | `LABEL_9421` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_2.inc:44 |
| `0x14` | dos | `LABEL_942E` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_2.inc:39 |
| `0x14` | dos | `LABEL_94D0` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_6.inc:20 |
| `0x14` | cart | `LABEL_94E7` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_5.inc:6 |
| `0x14` | amiga | `LABEL_94FD` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_2.inc:34 |
| `0x14` | cart | `LABEL_9507` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_5.inc:4 |
| `0x14` | dos | `LABEL_9519` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_2.inc:24 (+1 more) |
| `0x14` | cart | `LABEL_9594` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_2.inc:39 |
| `0x14` | amiga | `LABEL_9598` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_6.inc:7 |
| `0x14` | dos | `LABEL_9599` | src/levels/_unified/prison/dos__post_SET_VAR04_TO_0008.inc:8 |
| `0x14` | amiga | `LABEL_95E1` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_6.inc:25 |
| `0x14` | amiga | `LABEL_962A` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_6.inc:12 |
| `0x14` | cart | `LABEL_9636` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_6.inc:20 |
| `0x14` | dos | `LABEL_9638` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_2.inc:12 (+1 more) |
| `0x14` | cart | `LABEL_967F` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_2.inc:24 (+1 more) |
| `0x14` | dos | `LABEL_96B8` | src/levels/_unified/prison/dos__post_SET_VAR04_TO_0008.inc:14 |
| `0x14` | cart | `LABEL_9716` | src/levels/_unified/prison/cart__post_SET_VAR04_TO_0008.inc:8 |
| `0x14` | dos | `LABEL_9757` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_2.inc:34 |
| `0x14` | amiga | `LABEL_978A` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_2.inc:18 |
| `0x14` | cart | `LABEL_97A4` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_2.inc:12 (+1 more) |
| `0x14` | dos | `LABEL_97F2` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_6.inc:7 |
| `0x14` | cart | `LABEL_983B` | src/levels/_unified/prison/cart__post_SET_VAR04_TO_0008.inc:14 |
| `0x14` | dos | `LABEL_983B` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_6.inc:25 |
| `0x14` | amiga | `LABEL_9865` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR63_TO_2.inc:6 |
| `0x14` | dos | `LABEL_9884` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_6.inc:12 |
| `0x14` | cart | `LABEL_98C9` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_2.inc:34 |
| `0x14` | cart | `LABEL_9964` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_6.inc:7 |
| `0x14` | cart | `LABEL_99AD` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_6.inc:25 |
| `0x14` | dos | `LABEL_99E4` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_2.inc:18 |
| `0x14` | cart | `LABEL_99F6` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_6.inc:12 |
| `0x14` | dos | `LABEL_9ABF` | src/levels/_unified/prison/dos__post_INLINE_SET_VAR63_TO_2.inc:6 |
| `0x14` | cart | `LABEL_9B62` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_2.inc:18 |
| `0x14` | cart | `LABEL_9C49` | src/levels/_unified/prison/cart__post_INLINE_SET_VAR63_TO_2.inc:6 |
| `0x14` | cart | `STEP_DRAW_CIN555_LEFT4_RIGHT1` | src/levels/_unified/prison/cart__post_SET_VAR04_TO_0008.inc:34 |
| `0x14` | amiga | `STEP_DRAW_CIN555_LEFT4_RIGHT1` | src/levels/_unified/prison/amiga__post_SET_VAR04_TO_0008.inc:11 |
| `0x14` | dos | `STEP_DRAW_CIN555_LEFT4_RIGHT1` | src/levels/_unified/prison/dos__post_SET_VAR04_TO_0008.inc:34 |
| `0x15` | amiga | `DRAW_CIN_284_BLOCK_95B` | src/levels/_unified/prison/amiga__post_DRAW_CIN_280_TO_281_2F_AT_75ED3E60.inc:5 |
| `0x15` | dos | `DRAW_CIN_284_BLOCK_95B` | src/levels/_unified/prison/dos__post_DRAW_CIN_280_TO_281_2F_AT_75ED3E60.inc:5 |
| `0x15` | cart | `DRAW_CIN_284_BLOCK_95B__CART__POST_INLINE_KILL_040` | src/levels/_unified/prison/cart__post_INLINE_KILL_040.inc:178 |
| `0x15` | cart | `DRAW_CIN_694_695_PROGRESSIVE` | src/levels/_unified/prison/cart__post_FOLD_BODY_144B_C55279EA.inc:1230 |
| `0x15` | dos | `DRAW_CIN_694_695_PROGRESSIVE` | src/levels/_unified/prison/dos__post_DRAW_CIN_576_578_BLOCK.inc:925 |
| `0x15` | cart | `INLINE_SET_VAR03_TO_7` | src/levels/_unified/prison/cart__post_INLINE_KILL_039.inc:353 |
| `0x15` | amiga | `INLINE_SET_VAR03_TO_7` | src/levels/_unified/prison/amiga__post_DRAW_CIN_422_WITH_POS_STEP_AT_C7A1BFCB.inc:27 |
| `0x15` | dos | `INLINE_SET_VAR03_TO_7` | src/levels/_unified/prison/dos__post_DRAW_CIN_422_WITH_POS_STEP_AT_C7A1BFCB.inc:27 |
| `0x15` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__post_INLINE_BREAK_035.inc:78 (+4 more) |
| `0x15` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/amiga__post_INLINE_BREAK_035.inc:76 (+1 more) |
| `0x15` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/dos__post_INLINE_BREAK_035.inc:78 (+3 more) |
| `0x15` | amiga | `LABEL_6A25` | src/levels/_unified/prison/amiga__post_INLINE_KILL_041.inc:19 (+1 more) |
| `0x15` | dos | `LABEL_6AD2` | src/levels/_unified/prison/dos__post_INLINE_KILL_041.inc:19 (+1 more) |
| `0x15` | cart | `LABEL_6BD5` | src/levels/_unified/prison/cart__post_INLINE_KILL_041.inc:19 (+1 more) |
| `0x15` | amiga | `LABEL_777F` | src/levels/_unified/prison/amiga__entry.inc:2244 (+1 more) |
| `0x15` | dos | `LABEL_7830` | src/levels/_unified/prison/dos__entry.inc:2229 (+1 more) |
| `0x15` | cart | `LABEL_7939` | src/levels/_unified/prison/cart__entry.inc:2263 (+1 more) |
| `0x15` | amiga | `LABEL_903C` | src/levels/_unified/prison/amiga__post_DRAW_CIN555_STEP_RIGHT3.inc:112 |
| `0x15` | amiga | `LABEL_9126` | src/levels/_unified/prison/amiga__post_DRAW_CIN555_STEP_RIGHT3.inc:200 |
| `0x15` | dos | `LABEL_926A` | src/levels/_unified/prison/dos__post_DRAW_CIN555_STEP_RIGHT3.inc:152 |
| `0x15` | dos | `LABEL_9354` | src/levels/_unified/prison/dos__post_DRAW_CIN555_STEP_RIGHT3.inc:240 |
| `0x15` | cart | `LABEL_93D0` | src/levels/_unified/prison/cart__post_DRAW_CIN555_STEP_RIGHT3.inc:152 |
| `0x15` | cart | `LABEL_94BA` | src/levels/_unified/prison/cart__post_DRAW_CIN555_STEP_RIGHT3.inc:240 |
| `0x15` | cart | `SETUP_VARS_01_B0_02_B6_06_C7_28_FROM_01` | src/levels/_unified/prison/cart__entry.inc:2235 (+1 more) |
| `0x15` | amiga | `SETUP_VARS_01_B0_02_B6_06_C7_28_FROM_01` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:78 |
| `0x15` | dos | `SETUP_VARS_01_B0_02_B6_06_C7_28_FROM_01` | src/levels/_unified/prison/dos__entry.inc:2210 (+1 more) |
| `0x16` | dos | `LABEL_0D28` | src/levels/_unified/prison/dos__post_DRAW_CIN_406_408_BLOCK.inc:11 |
| `0x16` | amiga | `LABEL_0D48` | src/levels/_unified/prison/amiga__post_DRAW_CIN_406_408_BLOCK.inc:11 |
| `0x16` | cart | `LABEL_0DB0` | src/levels/_unified/prison/cart__post_INLINE_SET_VARF1_TO_64.inc:38 |
| `0x16` | amiga | `LABEL_8944` | src/levels/_unified/prison/amiga__post_INLINE_SET_VAR03_TO_7.inc:45 |
| `0x16` | dos | `LABEL_8A67` | src/levels/_unified/prison/dos__entry.inc:2211 (+1 more) |
| `0x16` | cart | `LABEL_8BC5` | src/levels/_unified/prison/cart__entry.inc:2239 (+1 more) |
| `0x17` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__post_INIT_VARS_15_19_18_14_PLUS4.inc:135 |
| `0x17` | amiga | `LABEL_444D` | src/levels/_unified/prison/amiga__post_DRAW_CIN555_STEP_RIGHT3.inc:298 (+1 more) |
| `0x17` | amiga | `LABEL_449B` | src/levels/_unified/prison/amiga__post_INLINE_BREAK_035.inc:247 (+1 more) |
| `0x17` | dos | `LABEL_44AF` | src/levels/_unified/prison/dos__post_DRAW_CIN555_STEP_RIGHT3.inc:338 (+1 more) |
| `0x17` | dos | `LABEL_450B` | src/levels/_unified/prison/dos__post_INLINE_BREAK_035.inc:259 (+1 more) |
| `0x17` | cart | `LABEL_45A9` | src/levels/_unified/prison/cart__post_DRAW_CIN555_STEP_RIGHT3.inc:338 (+1 more) |
| `0x17` | cart | `LABEL_4605` | src/levels/_unified/prison/cart__post_INLINE_BREAK_035.inc:263 (+1 more) |
| `0x18` | amiga | `LABEL_41E3` | src/levels/_unified/prison/amiga__post_INIT_VARS_A1_A4_A7_AA_PLUS4.inc:26 |
| `0x18` | dos | `LABEL_4245` | src/levels/_unified/prison/dos__post_INIT_VARS_A1_A4_A7_AA_PLUS4.inc:26 |
| `0x18` | cart | `LABEL_433F` | src/levels/_unified/prison/cart__post_INIT_VARS_A1_A4_A7_AA_PLUS4.inc:26 |
| `0x1A` | amiga | `LABEL_7DCB` | src/levels/_unified/prison/amiga__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:24 |
| `0x1A` | amiga | `LABEL_7DDD` | src/levels/_unified/prison/amiga__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:10 |
| `0x1A` | dos | `LABEL_7E96` | src/levels/_unified/prison/dos__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:24 |
| `0x1A` | dos | `LABEL_7EA8` | src/levels/_unified/prison/dos__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:10 |
| `0x1A` | cart | `LABEL_7FC5` | src/levels/_unified/prison/cart__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:24 |
| `0x1A` | cart | `LABEL_7FD7` | src/levels/_unified/prison/cart__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:10 |
| `0x21` | dos | `LABEL_141E` | src/levels/_unified/prison/dos__post_FILL_AND_DRAW_CIN_24_28.inc:75 |
| `0x21` | amiga | `LABEL_1426` | src/levels/_unified/prison/amiga__post_FILL_AND_DRAW_CIN_24_28.inc:75 |
| `0x21` | cart | `LABEL_14B0` | src/levels/_unified/prison/cart__post_FOLD_BODY_104B_22B91458.inc:168 |
| `0x22` | amiga | `DRAW_CIN_229_TO_632_2F_AT_1C4A817A` | src/levels/_unified/prison/amiga__post_FILL_AND_DRAW_CIN_24_28.inc:31 |
| `0x22` | dos | `DRAW_CIN_229_TO_632_2F_AT_1C4A817A` | src/levels/_unified/prison/dos__post_FILL_AND_DRAW_CIN_24_28.inc:31 |
| `0x22` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__post_FOLD_BODY_104B_22B91458.inc:133 |
| `0x22` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/amiga__post_FILL_AND_DRAW_CIN_24_28.inc:40 |
| `0x22` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/dos__post_FILL_AND_DRAW_CIN_24_28.inc:40 |
| `0x22` | dos | `LABEL_141E` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:86 |
| `0x22` | amiga | `LABEL_1426` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:85 |
| `0x22` | cart | `LABEL_14B0` | src/levels/_unified/prison/cart__post_STEP_VAR1A_DOWN5_VAR1B_UP2.inc:363 |
| `0x22` | dos | `LABEL_1BBC` | src/levels/_unified/prison/dos__post_FILL_AND_DRAW_CIN_24_28.inc:76 |
| `0x22` | amiga | `LABEL_1BC4` | src/levels/_unified/prison/amiga__post_FILL_AND_DRAW_CIN_24_28.inc:76 |
| `0x22` | cart | `LABEL_1C5E` | src/levels/_unified/prison/cart__post_FOLD_BODY_104B_22B91458.inc:169 |
| `0x22` | amiga | `LABEL_4C18` | src/levels/_unified/prison/amiga__entry.inc:2241 (+1 more) |
| `0x22` | dos | `LABEL_4CB9` | src/levels/_unified/prison/dos__entry.inc:2226 (+1 more) |
| `0x22` | cart | `LABEL_4DB9` | src/levels/_unified/prison/cart__entry.inc:2260 (+1 more) |
| `0x22` | cart | `LABEL_4DCF` | src/levels/_unified/prison/cart__post_FOLD_BODY_104B_22B91458.inc:124 |
| `0x23` | cart | `DRAW_CIN_406_408_BLOCK` | src/levels/_unified/prison/cart__entry.inc:2244 |
| `0x23` | cart | `INLINE_SET_VAR29_TO_28` | src/levels/_unified/prison/cart__post_INLINE_SET_VARE9_TO_8.inc:127 |
| `0x23` | amiga | `INLINE_SET_VAR29_TO_28` | src/levels/_unified/prison/amiga__post_INLINE_SET_VARE9_TO_8.inc:127 |
| `0x23` | dos | `INLINE_SET_VAR29_TO_28` | src/levels/_unified/prison/dos__post_INLINE_SET_VARE9_TO_8.inc:127 |
| `0x23` | cart | `INLINE_SUB_VAR08_INIT_VAR29` | src/levels/_unified/prison/cart__post_STEP_VAR1A_DOWN5_VAR1B_UP2.inc:364 |
| `0x23` | amiga | `INLINE_SUB_VAR08_INIT_VAR29` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:86 |
| `0x23` | dos | `INLINE_SUB_VAR08_INIT_VAR29` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:87 |
| `0x23` | dos | `LABEL_10B5` | src/levels/_unified/prison/dos__post_PLAY_SFX_005C_CH01.inc:31 |
| `0x23` | amiga | `LABEL_10D5` | src/levels/_unified/prison/amiga__post_PLAY_SFX_005C_CH01.inc:31 |
| `0x23` | dos | `LABEL_1111` | src/levels/_unified/prison/dos__post_PLAY_SFX_005C_CH01.inc:33 |
| `0x23` | amiga | `LABEL_1128` | src/levels/_unified/prison/amiga__post_PLAY_SFX_005C_CH01.inc:33 |
| `0x23` | cart | `LABEL_113D` | src/levels/_unified/prison/cart__post_PLAY_SFX_005C_CH01.inc:32 |
| `0x23` | cart | `LABEL_1199` | src/levels/_unified/prison/cart__post_PLAY_SFX_005C_CH01.inc:34 |
| `0x23` | dos | `LABEL_1846` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:53 |
| `0x23` | amiga | `LABEL_184E` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:53 |
| `0x23` | cart | `LABEL_18DE` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:53 |
| `0x23` | dos | `LABEL_1F98` | src/levels/_unified/prison/dos__post_DECREMENT_VAR29_BY_1.inc:23 |
| `0x23` | amiga | `LABEL_1FA0` | src/levels/_unified/prison/amiga__post_DECREMENT_VAR29_BY_1.inc:23 |
| `0x23` | dos | `LABEL_1FC4` | src/levels/_unified/prison/dos__post_DECREMENT_VAR29_BY_1.inc:16 |
| `0x23` | amiga | `LABEL_1FCC` | src/levels/_unified/prison/amiga__post_DECREMENT_VAR29_BY_1.inc:16 |
| `0x23` | dos | `LABEL_1FF0` | src/levels/_unified/prison/dos__post_DECREMENT_VAR29_BY_1.inc:2 |
| `0x23` | amiga | `LABEL_1FF8` | src/levels/_unified/prison/amiga__post_DECREMENT_VAR29_BY_1.inc:2 |
| `0x23` | dos | `LABEL_2038` | src/levels/_unified/prison/dos__post_DECREMENT_VAR29_BY_1.inc:38 |
| `0x23` | cart | `LABEL_203A` | src/levels/_unified/prison/cart__post_DECREMENT_VAR29_BY_1.inc:23 |
| `0x23` | amiga | `LABEL_2040` | src/levels/_unified/prison/amiga__post_DECREMENT_VAR29_BY_1.inc:38 |
| `0x23` | cart | `LABEL_2066` | src/levels/_unified/prison/cart__post_DECREMENT_VAR29_BY_1.inc:16 |
| `0x23` | cart | `LABEL_2092` | src/levels/_unified/prison/cart__post_DECREMENT_VAR29_BY_1.inc:2 |
| `0x23` | cart | `LABEL_20DA` | src/levels/_unified/prison/cart__post_DECREMENT_VAR29_BY_1.inc:38 |
| `0x23` | dos | `LABEL_2150` | src/levels/_unified/prison/dos__post_DECREMENT_VAR29_BY_1.inc:59 |
| `0x23` | amiga | `LABEL_2158` | src/levels/_unified/prison/amiga__post_DECREMENT_VAR29_BY_1.inc:59 |
| `0x23` | dos | `LABEL_21A5` | src/levels/_unified/prison/dos__post_DECREMENT_VAR29_BY_1.inc:44 |
| `0x23` | amiga | `LABEL_21AD` | src/levels/_unified/prison/amiga__post_DECREMENT_VAR29_BY_1.inc:44 |
| `0x23` | dos | `LABEL_21C4` | src/levels/_unified/prison/dos__post_DECREMENT_VAR29_BY_1.inc:27 |
| `0x23` | amiga | `LABEL_21CC` | src/levels/_unified/prison/amiga__post_DECREMENT_VAR29_BY_1.inc:27 |
| `0x23` | cart | `LABEL_21F2` | src/levels/_unified/prison/cart__post_DECREMENT_VAR29_BY_1.inc:59 |
| `0x23` | dos | `LABEL_2204` | src/levels/_unified/prison/dos__post_DECREMENT_VAR29_BY_1.inc:32 |
| `0x23` | amiga | `LABEL_220C` | src/levels/_unified/prison/amiga__post_DECREMENT_VAR29_BY_1.inc:32 |
| `0x23` | cart | `LABEL_2247` | src/levels/_unified/prison/cart__post_DECREMENT_VAR29_BY_1.inc:44 |
| `0x23` | cart | `LABEL_2266` | src/levels/_unified/prison/cart__post_DECREMENT_VAR29_BY_1.inc:27 |
| `0x23` | cart | `LABEL_22A6` | src/levels/_unified/prison/cart__post_DECREMENT_VAR29_BY_1.inc:32 |
| `0x23` | amiga | `LABEL_4AC9` | src/levels/_unified/prison/amiga__entry.inc:2242 (+1 more) |
| `0x23` | dos | `LABEL_4B6A` | src/levels/_unified/prison/dos__entry.inc:2227 (+1 more) |
| `0x23` | cart | `LABEL_4C64` | src/levels/_unified/prison/cart__entry.inc:2261 (+1 more) |
| `0x24` | dos | `LABEL_1441` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:88 (+1 more) |
| `0x24` | amiga | `LABEL_1449` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:87 (+1 more) |
| `0x24` | cart | `LABEL_14D3` | src/levels/_unified/prison/cart__post_FOLD_BODY_104B_22B91458.inc:170 (+1 more) |
| `0x25` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__post_INLINE_SET_VARE9_TO_8.inc:133 |
| `0x25` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/amiga__post_INLINE_SET_VARE9_TO_8.inc:133 |
| `0x25` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/dos__post_INLINE_SET_VARE9_TO_8.inc:133 |
| `0x25` | dos | `LABEL_10B5` | src/levels/_unified/prison/dos__post_PLAY_SFX_005C_CH01.inc:41 |
| `0x25` | amiga | `LABEL_10D5` | src/levels/_unified/prison/amiga__post_PLAY_SFX_005C_CH01.inc:41 |
| `0x25` | dos | `LABEL_1111` | src/levels/_unified/prison/dos__post_PLAY_SFX_005C_CH01.inc:43 |
| `0x25` | amiga | `LABEL_1128` | src/levels/_unified/prison/amiga__post_PLAY_SFX_005C_CH01.inc:43 |
| `0x25` | cart | `LABEL_113D` | src/levels/_unified/prison/cart__post_PLAY_SFX_005C_CH01.inc:42 |
| `0x25` | cart | `LABEL_1199` | src/levels/_unified/prison/cart__post_PLAY_SFX_005C_CH01.inc:44 |
| `0x25` | amiga | `LABEL_2563` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:137 |
| `0x25` | dos | `LABEL_2597` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:137 (+1 more) |
| `0x25` | amiga | `LABEL_25A5` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:88 |
| `0x25` | dos | `LABEL_25D9` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:89 |
| `0x25` | cart | `LABEL_2639` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:138 (+1 more) |
| `0x25` | cart | `LABEL_267B` | src/levels/_unified/prison/cart__post_STEP_VAR1A_DOWN5_VAR1B_UP2.inc:366 |
| `0x26` | dos | `LABEL_147C` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:90 |
| `0x26` | amiga | `LABEL_1484` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:89 |
| `0x26` | cart | `LABEL_150E` | src/levels/_unified/prison/cart__post_STEP_VAR1A_DOWN5_VAR1B_UP2.inc:367 |
| `0x27` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__post_STEP_VAR1A_DOWN5_VAR1B_UP2.inc:368 |
| `0x27` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:90 |
| `0x27` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:91 |
| `0x27` | dos | `LABEL_10B5` | src/levels/_unified/prison/dos__post_PLAY_SFX_005C_CH01.inc:47 |
| `0x27` | amiga | `LABEL_10D5` | src/levels/_unified/prison/amiga__post_PLAY_SFX_005C_CH01.inc:47 |
| `0x27` | dos | `LABEL_1111` | src/levels/_unified/prison/dos__post_PLAY_SFX_005C_CH01.inc:49 |
| `0x27` | amiga | `LABEL_1128` | src/levels/_unified/prison/amiga__post_PLAY_SFX_005C_CH01.inc:49 |
| `0x27` | cart | `LABEL_113D` | src/levels/_unified/prison/cart__post_PLAY_SFX_005C_CH01.inc:48 |
| `0x27` | cart | `LABEL_1199` | src/levels/_unified/prison/cart__post_PLAY_SFX_005C_CH01.inc:50 |
| `0x27` | dos | `LABEL_1616` | src/levels/_unified/prison/dos__post_INLINE_SET_VARE9_TO_8.inc:123 |
| `0x27` | amiga | `LABEL_161E` | src/levels/_unified/prison/amiga__post_INLINE_SET_VARE9_TO_8.inc:123 |
| `0x27` | cart | `LABEL_16B4` | src/levels/_unified/prison/cart__post_INLINE_SET_VARE9_TO_8.inc:123 |
| `0x27` | amiga | `LABEL_25A5` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:155 (+1 more) |
| `0x27` | dos | `LABEL_25D9` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:155 (+1 more) |
| `0x27` | cart | `LABEL_267B` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:156 (+1 more) |
| `0x28` | dos | `LABEL_14B7` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:92 |
| `0x28` | amiga | `LABEL_14BF` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:91 |
| `0x28` | cart | `LABEL_1549` | src/levels/_unified/prison/cart__post_STEP_VAR1A_DOWN5_VAR1B_UP2.inc:369 |
| `0x29` | amiga | `LABEL_2B14` | src/levels/_unified/prison/amiga__post_COPY_PAGE0_TO_FF_KILL_CHANNEL.inc:144 |
| `0x29` | dos | `LABEL_2B52` | src/levels/_unified/prison/dos__post_COPY_PAGE0_TO_FF_KILL_CHANNEL.inc:148 |
| `0x29` | cart | `LABEL_2BF4` | src/levels/_unified/prison/cart__post_COPY_PAGE0_TO_FF_KILL_CHANNEL.inc:152 |
| `0x2A` | amiga | `LABEL_2BFA` | src/levels/_unified/prison/amiga__post_FOLD_BODY_58B_A2D4469A.inc:90 |
| `0x2A` | dos | `LABEL_2C38` | src/levels/_unified/prison/dos__post_FOLD_BODY_58B_A2D4469A.inc:96 |
| `0x2A` | amiga | `LABEL_2C83` | src/levels/_unified/prison/amiga__post_FOLD_BODY_58B_A2D4469A.inc:128 |
| `0x2A` | dos | `LABEL_2CC1` | src/levels/_unified/prison/dos__post_FOLD_BODY_58B_A2D4469A.inc:134 |
| `0x2A` | cart | `LABEL_2CDA` | src/levels/_unified/prison/cart__post_FOLD_BODY_58B_A2D4469A.inc:96 |
| `0x2A` | cart | `LABEL_2D63` | src/levels/_unified/prison/cart__post_FOLD_BODY_58B_A2D4469A.inc:134 |
| `0x2B` | amiga | `LABEL_2C67` | src/levels/_unified/prison/amiga__post_FOLD_BODY_58B_A2D4469A.inc:187 |
| `0x2B` | dos | `LABEL_2CA5` | src/levels/_unified/prison/dos__post_FOLD_BODY_58B_A2D4469A.inc:193 |
| `0x2B` | cart | `LABEL_2D47` | src/levels/_unified/prison/cart__post_FOLD_BODY_58B_A2D4469A.inc:193 |
| `0x2F` | amiga | `LABEL_3807` | src/levels/_unified/prison/amiga__post_INIT_VARS_A1_A4_A7_AA_PLUS4.inc:27 |
| `0x2F` | dos | `LABEL_3869` | src/levels/_unified/prison/dos__post_INIT_VARS_A1_A4_A7_AA_PLUS4.inc:27 |
| `0x2F` | cart | `LABEL_395D` | src/levels/_unified/prison/cart__post_INIT_VARS_A1_A4_A7_AA_PLUS4.inc:27 |
| `0x30` | amiga | `LABEL_34C5` | src/levels/_unified/prison/amiga__post_INLINE_SUB_VAR22_BY_23.inc:117 |
| `0x30` | dos | `LABEL_3527` | src/levels/_unified/prison/dos__post_INLINE_SUB_VAR22_BY_23.inc:117 |
| `0x30` | cart | `LABEL_3609` | src/levels/_unified/prison/cart__post_INLINE_SUB_VAR22_BY_23.inc:117 |
| `0x31` | amiga | `LABEL_3322` | src/levels/_unified/prison/amiga__post_INLINE_SUB_VAR22_BY_23.inc:126 |
| `0x31` | dos | `LABEL_3384` | src/levels/_unified/prison/dos__post_INLINE_SUB_VAR22_BY_23.inc:126 |
| `0x31` | cart | `LABEL_3466` | src/levels/_unified/prison/cart__post_INLINE_SUB_VAR22_BY_23.inc:126 |
| `0x31` | amiga | `LABEL_34CE` | src/levels/_unified/prison/amiga__post_INLINE_SUB_VAR22_BY_23.inc:118 |
| `0x31` | dos | `LABEL_3530` | src/levels/_unified/prison/dos__post_INLINE_SUB_VAR22_BY_23.inc:118 |
| `0x31` | cart | `LABEL_3612` | src/levels/_unified/prison/cart__post_INLINE_SUB_VAR22_BY_23.inc:118 |
| `0x32` | amiga | `LABEL_3322` | src/levels/_unified/prison/amiga__post_INLINE_SUB_VAR22_BY_23.inc:134 |
| `0x32` | dos | `LABEL_3384` | src/levels/_unified/prison/dos__post_INLINE_SUB_VAR22_BY_23.inc:134 |
| `0x32` | cart | `LABEL_3466` | src/levels/_unified/prison/cart__post_INLINE_SUB_VAR22_BY_23.inc:134 |
| `0x32` | amiga | `LABEL_34CE` | src/levels/_unified/prison/amiga__post_INLINE_SUB_VAR22_BY_23.inc:119 |
| `0x32` | dos | `LABEL_3530` | src/levels/_unified/prison/dos__post_INLINE_SUB_VAR22_BY_23.inc:119 |
| `0x32` | cart | `LABEL_3612` | src/levels/_unified/prison/cart__post_INLINE_SUB_VAR22_BY_23.inc:119 |
| `0x33` | amiga | `LABEL_3322` | src/levels/_unified/prison/amiga__post_INLINE_SUB_VAR22_BY_23.inc:142 |
| `0x33` | dos | `LABEL_3384` | src/levels/_unified/prison/dos__post_INLINE_SUB_VAR22_BY_23.inc:142 |
| `0x33` | cart | `LABEL_3466` | src/levels/_unified/prison/cart__post_INLINE_SUB_VAR22_BY_23.inc:142 |
| `0x34` | cart | `HANG_DRAW_CIN_275` | src/levels/_unified/prison/cart__post_COPY_PAGE0_TO_FF_KILL_CHANNEL.inc:155 (+1 more) |
| `0x34` | amiga | `HANG_DRAW_CIN_275` | src/levels/_unified/prison/amiga__post_COPY_PAGE0_TO_FF_KILL_CHANNEL.inc:147 (+1 more) |
| `0x34` | dos | `HANG_DRAW_CIN_275` | src/levels/_unified/prison/dos__post_COPY_PAGE0_TO_FF_KILL_CHANNEL.inc:151 (+1 more) |
| `0x34` | amiga | `HANG_DRAW_CIN_549` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:76 |
| `0x34` | dos | `HANG_DRAW_CIN_549` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:76 |
| `0x34` | cart | `HANG_DRAW_CIN_549__CART__POST_STEP_VAR1A_DOWN5_VAR1B_UP2` | src/levels/_unified/prison/cart__post_STEP_VAR1A_DOWN5_VAR1B_UP2.inc:353 |
| `0x34` | dos | `LABEL_0DC2` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:79 |
| `0x34` | amiga | `LABEL_0DE2` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:79 |
| `0x34` | cart | `LABEL_0E4A` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:79 |
| `0x34` | amiga | `LABEL_7EC8` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:101 (+3 more) |
| `0x34` | dos | `LABEL_7F9A` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:101 (+3 more) |
| `0x34` | cart | `LABEL_80C9` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:102 (+3 more) |
| `0x35` | amiga | `DRAW_CIN_540_543_WITH_SFX_57` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:77 |
| `0x35` | dos | `DRAW_CIN_540_543_WITH_SFX_57` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:77 |
| `0x35` | cart | `DRAW_CIN_540_543_WITH_SFX_57__CART__POST_STEP_VAR1A_DOWN5_VAR1B_UP2` | src/levels/_unified/prison/cart__post_STEP_VAR1A_DOWN5_VAR1B_UP2.inc:354 |
| `0x35` | amiga | `LABEL_018D` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:301 |
| `0x35` | dos | `LABEL_01AF` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:312 |
| `0x35` | cart | `LABEL_021D` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:314 |
| `0x35` | dos | `LABEL_0DEC` | src/levels/_unified/prison/dos__post_INIT_VARS_15_19_18_14_PLUS4.inc:49 |
| `0x35` | amiga | `LABEL_0E0C` | src/levels/_unified/prison/amiga__post_INIT_VARS_15_19_18_14_PLUS4.inc:49 |
| `0x35` | cart | `LABEL_0E74` | src/levels/_unified/prison/cart__post_INIT_VARS_15_19_18_14_PLUS4.inc:57 |
| `0x35` | amiga | `LABEL_22F4` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:80 |
| `0x35` | dos | `LABEL_2328` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:80 |
| `0x35` | cart | `LABEL_23CA` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:80 |
| `0x35` | amiga | `LABEL_8320` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:102 |
| `0x35` | dos | `LABEL_83FF` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:102 |
| `0x35` | cart | `LABEL_854D` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:103 |
| `0x36` | dos | `LABEL_0E1A` | src/levels/_unified/prison/dos__post_INIT_VARS_15_19_18_14_PLUS4.inc:50 |
| `0x36` | amiga | `LABEL_0E3A` | src/levels/_unified/prison/amiga__post_INIT_VARS_15_19_18_14_PLUS4.inc:50 |
| `0x36` | cart | `LABEL_0EA2` | src/levels/_unified/prison/cart__post_INIT_VARS_15_19_18_14_PLUS4.inc:58 |
| `0x37` | dos | `LABEL_0E48` | src/levels/_unified/prison/dos__post_INIT_VARS_15_19_18_14_PLUS4.inc:51 |
| `0x37` | amiga | `LABEL_0E68` | src/levels/_unified/prison/amiga__post_INIT_VARS_15_19_18_14_PLUS4.inc:51 |
| `0x37` | cart | `LABEL_0ED0` | src/levels/_unified/prison/cart__post_INIT_VARS_15_19_18_14_PLUS4.inc:59 |
| `0x38` | amiga | `DRAW_CIN_149_TO_150_2F_AT_F63AB95D` | src/levels/_unified/prison/amiga__post_DRAW_CIN_092.inc:34 |
| `0x38` | dos | `DRAW_CIN_149_TO_150_2F_AT_F63AB95D` | src/levels/_unified/prison/dos__post_DRAW_CIN_092.inc:34 |
| `0x38` | amiga | `DRAW_CIN_154_TO_156_3F_AT_A74B7DB1` | src/levels/_unified/prison/amiga__post_DRAW_CIN_092.inc:26 |
| `0x38` | dos | `DRAW_CIN_154_TO_156_3F_AT_A74B7DB1` | src/levels/_unified/prison/dos__post_DRAW_CIN_092.inc:26 |
| `0x38` | dos | `LABEL_0875` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:29 |
| `0x38` | amiga | `LABEL_0895` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:29 |
| `0x38` | cart | `LABEL_08FD` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:29 |
| `0x38` | cart | `LABEL_0F04` | src/levels/_unified/prison/cart__post_DEDUP_PRISON_4B_034.inc:55 |
| `0x38` | cart | `LABEL_0F34` | src/levels/_unified/prison/cart__post_DEDUP_PRISON_4B_034.inc:63 |
| `0x39` | amiga | `DRAW_CIN_132_TO_133_2F_AT_BB9185F0` | src/levels/_unified/prison/amiga__post_DRAW_CIN_092.inc:38 |
| `0x39` | dos | `DRAW_CIN_132_TO_133_2F_AT_BB9185F0` | src/levels/_unified/prison/dos__post_DRAW_CIN_092.inc:38 |
| `0x39` | amiga | `DRAW_CIN_151_TO_153_3F_AT_40D20636` | src/levels/_unified/prison/amiga__post_DRAW_CIN_092.inc:30 |
| `0x39` | dos | `DRAW_CIN_151_TO_153_3F_AT_40D20636` | src/levels/_unified/prison/dos__post_DRAW_CIN_092.inc:30 |
| `0x39` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__post_ACCUMULATE_HASH_VAR37_38_X3.inc:110 |
| `0x39` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/amiga__post_ACCUMULATE_HASH_VAR37_38_X3.inc:100 |
| `0x39` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/dos__post_ACCUMULATE_HASH_VAR37_38_X3.inc:110 |
| `0x39` | dos | `LABEL_0896` | src/levels/_unified/prison/dos__post_ACCUMULATE_HASH_VAR37_38_X3.inc:71 |
| `0x39` | amiga | `LABEL_08B6` | src/levels/_unified/prison/amiga__post_ACCUMULATE_HASH_VAR37_38_X3.inc:61 |
| `0x39` | dos | `LABEL_08CF` | src/levels/_unified/prison/dos__post_ACCUMULATE_HASH_VAR37_38_X3.inc:104 |
| `0x39` | amiga | `LABEL_08EF` | src/levels/_unified/prison/amiga__post_ACCUMULATE_HASH_VAR37_38_X3.inc:94 |
| `0x39` | cart | `LABEL_091E` | src/levels/_unified/prison/cart__post_ACCUMULATE_HASH_VAR37_38_X3.inc:71 |
| `0x39` | cart | `LABEL_0957` | src/levels/_unified/prison/cart__post_ACCUMULATE_HASH_VAR37_38_X3.inc:104 |
| `0x39` | cart | `LABEL_0F1C` | src/levels/_unified/prison/cart__post_DEDUP_PRISON_4B_034.inc:59 |
| `0x39` | cart | `LABEL_0F46` | src/levels/_unified/prison/cart__post_DEDUP_PRISON_4B_034.inc:67 |
| `0x3A` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__post_STEP_VAR1A_DOWN5_VAR1B_UP2.inc:370 |
| `0x3A` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:92 |
| `0x3A` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:93 |
| `0x3A` | dos | `LABEL_0503` | src/levels/_unified/prison/dos__post_INLINE_KILL_039.inc:231 |
| `0x3A` | amiga | `LABEL_053D` | src/levels/_unified/prison/amiga__post_INLINE_KILL_039.inc:278 |
| `0x3A` | cart | `LABEL_0583` | src/levels/_unified/prison/cart__post_INLINE_KILL_039.inc:235 |
| `0x3A` | dos | `LABEL_0D38` | src/levels/_unified/prison/dos__post_INIT_VARS_2F_29.inc:9 |
| `0x3A` | amiga | `LABEL_0D58` | src/levels/_unified/prison/amiga__post_INIT_VARS_2F_29.inc:9 |
| `0x3A` | cart | `LABEL_0DC0` | src/levels/_unified/prison/cart__post_INIT_VARS_2F_29.inc:9 |
| `0x3B` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__post_INIT_VARS_A1_A4_A7_AA_PLUS4.inc:4 (+1 more) |
| `0x3B` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/amiga__post_INIT_VARS_A1_A4_A7_AA_PLUS4.inc:4 (+1 more) |
| `0x3B` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/dos__post_INIT_VARS_A1_A4_A7_AA_PLUS4.inc:4 (+1 more) |
| `0x3B` | dos | `LABEL_0CC7` | src/levels/_unified/prison/dos__post_COPY_PAGE3_TO_PAGE0.inc:238 |
| `0x3B` | amiga | `LABEL_0CE7` | src/levels/_unified/prison/amiga__post_COPY_PAGE3_TO_PAGE0.inc:238 |
| `0x3B` | cart | `LABEL_0D4F` | src/levels/_unified/prison/cart__post_COPY_PAGE3_TO_PAGE0.inc:239 |
| `0x3B` | amiga | `LABEL_7F92` | src/levels/_unified/prison/amiga__post_COPY_PAGE0_TO_FF_KILL_CHANNEL.inc:132 |
| `0x3B` | dos | `LABEL_8064` | src/levels/_unified/prison/dos__post_COPY_PAGE0_TO_FF_KILL_CHANNEL.inc:136 |
| `0x3B` | cart | `LABEL_8193` | src/levels/_unified/prison/cart__post_COPY_PAGE0_TO_FF_KILL_CHANNEL.inc:140 |
| `0x3C` | cart | `BLIT_PAGE_00_TO_FF_AND_BREAK` | src/levels/_unified/prison/cart__entry.inc:2191 (+12 more) |
| `0x3C` | dos | `BLIT_PAGE_00_TO_FF_AND_BREAK` | src/levels/_unified/prison/dos__entry.inc:2196 (+12 more) |
| `0x3C` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/cart__entry.inc:2279 |
| `0x3C` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/amiga__entry.inc:2258 |
| `0x3C` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/prison/dos__entry.inc:2243 |
| `0x3C` | dos | `LABEL_0467` | src/levels/_unified/prison/dos__post_INLINE_KILL_039.inc:14 (+1 more) |
| `0x3C` | amiga | `LABEL_04A1` | src/levels/_unified/prison/amiga__post_INLINE_KILL_039.inc:14 (+1 more) |
| `0x3C` | cart | `LABEL_04E7` | src/levels/_unified/prison/cart__post_INLINE_KILL_039.inc:14 (+1 more) |
| `0x3C` | dos | `LABEL_0665` | src/levels/_unified/prison/dos__post_ACCUMULATE_HASH_VAR37_38_X3.inc:52 (+1 more) |
| `0x3C` | dos | `LABEL_0689` | src/levels/_unified/prison/dos__post_BANK4_AFTER_CIN_414.inc:3 (+1 more) |
| `0x3C` | amiga | `LABEL_069F` | src/levels/_unified/prison/amiga__entry.inc:2215 (+5 more) |
| `0x3C` | dos | `LABEL_069F` | src/levels/_unified/prison/dos__post_INIT_VARS_E7_E8.inc:13 |
| `0x3C` | amiga | `LABEL_06AD` | src/levels/_unified/prison/amiga__post_BANK4_AFTER_CIN_414.inc:3 (+1 more) |
| `0x3C` | amiga | `LABEL_06C3` | src/levels/_unified/prison/amiga__post_INIT_VARS_E7_E8.inc:13 |
| `0x3C` | cart | `LABEL_06ED` | src/levels/_unified/prison/cart__post_ACCUMULATE_HASH_VAR37_38_X3.inc:52 (+1 more) |
| `0x3C` | cart | `LABEL_0711` | src/levels/_unified/prison/cart__post_INIT_VARS_15_19_18_14_PLUS4.inc:132 (+1 more) |
| `0x3C` | cart | `LABEL_0727` | src/levels/_unified/prison/cart__post_INIT_VARS_E7_E8.inc:13 |
| `0x3C` | amiga | `LABEL_88F6` | src/levels/_unified/prison/amiga__post_FOLD_BODY_338B_C0D45EFA.inc:30 |
| `0x3C` | dos | `LABEL_8A19` | src/levels/_unified/prison/dos__post_FOLD_BODY_338B_C0D45EFA.inc:30 |
| `0x3C` | cart | `LABEL_8B77` | src/levels/_unified/prison/cart__post_FOLD_BODY_338B_C0D45EFA.inc:30 |
| `0x3F` | amiga | `DELAY_4_QUANTUMS` | src/levels/_unified/prison/amiga__post_DRAW_CIN_576_578_BLOCK.inc:877 (+1 more) |
| `0x3F` | dos | `DELAY_4_QUANTUMS` | src/levels/_unified/prison/dos__post_DRAW_CIN_576_578_BLOCK.inc:960 (+1 more) |
| `0x3F` | cart | `LABEL_0116` | src/levels/_unified/prison/cart__post_FOLD_BODY_144B_C55279EA.inc:1265 (+1 more) |
| `0x3F` | dos | `LABEL_0861` | src/levels/_unified/prison/dos__post_ACCUMULATE_HASH_VAR37_38_X3.inc:56 |
| `0x3F` | cart | `LABEL_08E9` | src/levels/_unified/prison/cart__post_ACCUMULATE_HASH_VAR37_38_X3.inc:56 |
| `0x3F` | amiga | `LABEL_871B` | src/levels/_unified/prison/amiga__post_DRAW_CIN_037.inc:93 |
| `0x3F` | dos | `LABEL_8824` | src/levels/_unified/prison/dos__post_DRAW_CIN_037.inc:94 |
| `0x3F` | cart | `LABEL_897B` | src/levels/_unified/prison/cart__entry.inc:2245 (+1 more) |

## CAVES

| channel | branch | routine | source |
| ---: | --- | --- | --- |
| `0x00` | cart | `LABEL_0000` | src/levels/_unified/caves/cart__post_KILL_CHANNEL_LANDING.inc:76 (+1 more) |
| `0x00` | amiga | `LABEL_0000` | src/levels/_unified/caves/amiga__post_KILL_CHANNEL_LANDING.inc:55 |
| `0x00` | dos | `LABEL_0000` | src/levels/_unified/caves/dos__post_KILL_CHANNEL_LANDING.inc:58 |
| `0x00` | amiga | `LABEL_0162` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:33 |
| `0x00` | dos | `LABEL_016F` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:51 |
| `0x00` | amiga | `LABEL_018F` | src/levels/_unified/caves/amiga__post_KILL_CHANNEL_LANDING.inc:28 |
| `0x00` | dos | `LABEL_01A8` | src/levels/_unified/caves/dos__post_KILL_CHANNEL_LANDING.inc:30 |
| `0x00` | cart | `LABEL_01FC` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:53 |
| `0x00` | cart | `LABEL_0247` | src/levels/_unified/caves/cart__post_KILL_CHANNEL_LANDING.inc:37 |
| `0x00` | amiga | `LABEL_12CF` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAREF_TO_5.inc:198 |
| `0x00` | cart | `LABEL_142A` | src/levels/_unified/caves/cart__post_INLINE_SET_VAREF_TO_5.inc:203 |
| `0x00` | dos | `LABEL_148F` | src/levels/_unified/caves/dos__post_INLINE_SET_VAREF_TO_5.inc:199 |
| `0x01` | cart | `DRAW_CIN_437_439_BLOCK` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:360 |
| `0x01` | amiga | `DRAW_CIN_437_439_BLOCK` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:324 |
| `0x01` | dos | `DRAW_CIN_437_439_BLOCK` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:342 |
| `0x01` | cart | `INIT_VARS_E6_E7` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:258 (+1 more) |
| `0x01` | amiga | `INIT_VARS_E6_E7` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:232 (+1 more) |
| `0x01` | dos | `INIT_VARS_E6_E7` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:250 (+1 more) |
| `0x01` | cart | `INLINE_SET_VAR68_TO_32` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR6A_TO_2F.inc:66 |
| `0x01` | amiga | `INLINE_SET_VAR68_TO_32` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR6A_TO_2F.inc:68 |
| `0x01` | dos | `INLINE_SET_VAR68_TO_32` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR6A_TO_2F.inc:66 |
| `0x01` | cart | `INLINE_SET_VARE6_TO_32` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1243 |
| `0x01` | amiga | `INLINE_SET_VARE6_TO_32` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1152 |
| `0x01` | dos | `INLINE_SET_VARE6_TO_32` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1219 |
| `0x01` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:834 |
| `0x01` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:797 |
| `0x01` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:815 |
| `0x01` | amiga | `LABEL_0411` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_3.inc:107 |
| `0x01` | dos | `LABEL_042A` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_3.inc:107 |
| `0x01` | cart | `LABEL_0492` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1547 |
| `0x01` | amiga | `LABEL_0512` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1441 |
| `0x01` | dos | `LABEL_052B` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1508 |
| `0x01` | cart | `LABEL_0F0C` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6D_71_70.inc:178 |
| `0x01` | amiga | `LABEL_0F5F` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6D_71_70.inc:178 |
| `0x01` | dos | `LABEL_0F80` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6D_71_70.inc:178 |
| `0x01` | amiga | `LABEL_2026` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:966 |
| `0x01` | cart | `LABEL_21B1` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1055 |
| `0x01` | dos | `LABEL_21EA` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1033 |
| `0x01` | amiga | `LABEL_2F29` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_68_69_6B.inc:366 (+3 more) |
| `0x01` | amiga | `LABEL_2F51` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_68_69_6B.inc:363 (+1 more) |
| `0x01` | amiga | `LABEL_2F73` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:748 |
| `0x01` | cart | `LABEL_3136` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_68_69_6B.inc:376 (+3 more) |
| `0x01` | dos | `LABEL_3152` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_68_69_6B.inc:376 (+3 more) |
| `0x01` | cart | `LABEL_315E` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_68_69_6B.inc:373 (+1 more) |
| `0x01` | dos | `LABEL_317A` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_68_69_6B.inc:373 (+1 more) |
| `0x01` | cart | `LABEL_3180` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:785 |
| `0x01` | dos | `LABEL_319C` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:766 |
| `0x01` | amiga | `LABEL_32A8` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:68 (+1 more) |
| `0x01` | cart | `LABEL_34B5` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:89 (+1 more) |
| `0x01` | dos | `LABEL_34D1` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:86 (+1 more) |
| `0x02` | cart | `INIT_VAR08_FROM_VARE9_VAR09_TO_4` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:90 (+1 more) |
| `0x02` | amiga | `INIT_VAR08_FROM_VARE9_VAR09_TO_4` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:69 (+1 more) |
| `0x02` | dos | `INIT_VAR08_FROM_VARE9_VAR09_TO_4` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:87 (+1 more) |
| `0x02` | cart | `INIT_VARS_E6_E7_1` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:870 |
| `0x02` | dos | `INIT_VARS_E6_E7_1` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:851 |
| `0x02` | cart | `INIT_VARS_E6_E7_2` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:828 |
| `0x02` | amiga | `INIT_VARS_E6_E7_2` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:791 |
| `0x02` | dos | `INIT_VARS_E6_E7_2` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:809 |
| `0x02` | cart | `INIT_VARS_E6_E7_E8_E8_PLUS3` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1417 |
| `0x02` | amiga | `INIT_VARS_E6_E7_E8_E8_PLUS3` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1311 |
| `0x02` | dos | `INIT_VARS_E6_E7_E8_E8_PLUS3` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1378 |
| `0x02` | cart | `INIT_VARS_EE_EF` | src/levels/_unified/caves/cart__post_INLINE_SET_VAREF_TO_5.inc:37 |
| `0x02` | amiga | `INIT_VARS_EE_EF` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAREF_TO_5.inc:34 |
| `0x02` | dos | `INIT_VARS_EE_EF` | src/levels/_unified/caves/dos__post_INLINE_SET_VAREF_TO_5.inc:35 |
| `0x02` | cart | `INLINE_SET_VAR6A_TO_2F` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR6A_TO_2F.inc:67 |
| `0x02` | amiga | `INLINE_SET_VAR6A_TO_2F` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR6A_TO_2F.inc:69 |
| `0x02` | dos | `INLINE_SET_VAR6A_TO_2F` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR6A_TO_2F.inc:67 |
| `0x02` | amiga | `INLINE_SET_VARE6_TO_3` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1460 |
| `0x02` | dos | `INLINE_SET_VARE6_TO_3` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1527 |
| `0x02` | cart | `INLINE_SET_VARE8_TO_2F` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1244 |
| `0x02` | amiga | `INLINE_SET_VARE8_TO_2F` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1153 |
| `0x02` | dos | `INLINE_SET_VARE8_TO_2F` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1220 |
| `0x02` | cart | `INLINE_SET_VARE8_TO_8` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:259 (+1 more) |
| `0x02` | amiga | `INLINE_SET_VARE8_TO_8` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:233 (+1 more) |
| `0x02` | dos | `INLINE_SET_VARE8_TO_8` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:251 (+1 more) |
| `0x02` | cart | `INLINE_SET_VAREF_TO_5` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:357 |
| `0x02` | amiga | `INLINE_SET_VAREF_TO_5` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:321 |
| `0x02` | dos | `INLINE_SET_VAREF_TO_5` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:339 |
| `0x02` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INIT_VARS_0E_29.inc:288 (+1 more) |
| `0x02` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INIT_VARS_0E_29.inc:287 (+1 more) |
| `0x02` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INIT_VARS_0E_29.inc:287 (+1 more) |
| `0x02` | cart | `LABEL_0492` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1566 |
| `0x02` | cart | `LABEL_0633` | src/levels/_unified/caves/cart__post_COPY_VARF8_TO_VAR00.inc:98 |
| `0x02` | cart | `LABEL_0644` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1410 |
| `0x02` | amiga | `LABEL_0692` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_3.inc:142 |
| `0x02` | amiga | `LABEL_06A3` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1304 |
| `0x02` | dos | `LABEL_06B3` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_3.inc:142 |
| `0x02` | dos | `LABEL_06C4` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1371 |
| `0x02` | amiga | `LABEL_C6E2` | src/levels/_unified/caves/amiga__post_SET_VAR22_TO_00B8.inc:503 (+1 more) |
| `0x02` | cart | `LABEL_CB60` | src/levels/_unified/caves/cart__post_SET_VAR22_TO_00B8.inc:529 (+1 more) |
| `0x02` | dos | `LABEL_CB75` | src/levels/_unified/caves/dos__post_SET_VAR22_TO_00B8.inc:528 (+1 more) |
| `0x03` | amiga | `HANG_DRAW_CIN_330` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_68_69_6B.inc:62 (+1 more) |
| `0x03` | amiga | `HANG_DRAW_CIN_331` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:959 |
| `0x03` | cart | `HANG_DRAW_CIN_351` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_68_69_6B.inc:62 (+1 more) |
| `0x03` | dos | `HANG_DRAW_CIN_351` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_68_69_6B.inc:62 (+1 more) |
| `0x03` | cart | `HANG_DRAW_CIN_352` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1048 |
| `0x03` | dos | `HANG_DRAW_CIN_352` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1026 |
| `0x03` | cart | `INIT_VARS_E6_E9_E8` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:57 |
| `0x03` | dos | `INIT_VARS_E6_E9_E8` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:55 |
| `0x03` | cart | `INIT_VARS_EA_EB` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:260 (+1 more) |
| `0x03` | amiga | `INIT_VARS_EA_EB` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:234 (+1 more) |
| `0x03` | dos | `INIT_VARS_EA_EB` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:252 (+1 more) |
| `0x03` | cart | `JUNK__498E` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:25 |
| `0x03` | dos | `JUNK__4AD1` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:25 |
| `0x03` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_68_69_6B.inc:7 |
| `0x03` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_68_69_6B.inc:7 |
| `0x03` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_68_69_6B.inc:7 |
| `0x03` | cart | `LABEL_06E4` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1418 |
| `0x03` | amiga | `LABEL_073D` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1312 |
| `0x03` | dos | `LABEL_075E` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1379 |
| `0x03` | amiga | `LABEL_115E` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:37 |
| `0x03` | amiga | `LABEL_20D4` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:992 |
| `0x03` | cart | `LABEL_225F` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1081 |
| `0x03` | dos | `LABEL_2298` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1059 |
| `0x04` | amiga | `HANG_DRAW_CIN_253` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:70 (+1 more) |
| `0x04` | cart | `HANG_DRAW_CIN_270` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:91 (+1 more) |
| `0x04` | dos | `HANG_DRAW_CIN_271` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:88 (+1 more) |
| `0x04` | amiga | `HANG_DRAW_CIN_351` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1114 |
| `0x04` | cart | `HANG_DRAW_CIN_371` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1205 |
| `0x04` | dos | `HANG_DRAW_CIN_372` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1181 |
| `0x04` | cart | `INIT_VARS_EB_47` | src/levels/_unified/caves/cart__post_SET_VAR13_TO_FFFF.inc:98 |
| `0x04` | amiga | `INIT_VARS_EB_47` | src/levels/_unified/caves/amiga__post_SET_VAR13_TO_FFFF.inc:101 |
| `0x04` | dos | `INIT_VARS_EB_47` | src/levels/_unified/caves/dos__post_SET_VAR13_TO_FFFF.inc:98 |
| `0x04` | cart | `JUNK__498E` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:26 |
| `0x04` | dos | `JUNK__4AD1` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:26 |
| `0x04` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1210 |
| `0x04` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1119 |
| `0x04` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1186 |
| `0x04` | amiga | `LABEL_203D` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:965 |
| `0x04` | cart | `LABEL_21C8` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1054 |
| `0x04` | dos | `LABEL_2201` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1032 |
| `0x04` | amiga | `LABEL_3102` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:235 |
| `0x04` | amiga | `LABEL_3184` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:930 |
| `0x04` | cart | `LABEL_330F` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:261 |
| `0x04` | dos | `LABEL_332B` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:253 |
| `0x04` | cart | `LABEL_3391` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1018 |
| `0x04` | dos | `LABEL_33AD` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:997 |
| `0x04` | amiga | `LABEL_CBD3` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:274 |
| `0x04` | dos | `LABEL_D079` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:292 |
| `0x04` | cart | `LABEL_D0A2` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:309 |
| `0x05` | amiga | `INCR_VARE6_PLAY_FX55_2X_CH0_CH2__AMIGA__POST_PLAY_FX_6B_THEN_KILL_CHANNEL` | src/levels/_unified/caves/amiga__post_PLAY_FX_6B_THEN_KILL_CHANNEL.inc:38 |
| `0x05` | dos | `INCR_VARE6_PLAY_FX55_2X_CH0_CH2__DOS__POST_PLAY_FX_6B_THEN_KILL_CHANNEL` | src/levels/_unified/caves/dos__post_PLAY_FX_6B_THEN_KILL_CHANNEL.inc:38 |
| `0x05` | cart | `INIT_VARS_E6_EA` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1206 |
| `0x05` | amiga | `INIT_VARS_E6_EA` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1115 |
| `0x05` | dos | `INIT_VARS_E6_EA` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1182 |
| `0x05` | amiga | `INLINE_SET_VAR6B_TO_1` | src/levels/_unified/caves/amiga__entry.inc:3192 |
| `0x05` | dos | `INLINE_SET_VAR6B_TO_1` | src/levels/_unified/caves/dos__entry.inc:3200 |
| `0x05` | cart | `JUNK__498E` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:27 |
| `0x05` | dos | `JUNK__4AD1` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:27 |
| `0x05` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:29 |
| `0x05` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:29 |
| `0x05` | cart | `LABEL_07A4` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1178 |
| `0x05` | amiga | `LABEL_07FD` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1088 |
| `0x05` | dos | `LABEL_081E` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1155 |
| `0x05` | cart | `LABEL_10A3` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:92 |
| `0x05` | amiga | `LABEL_10ED` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:71 |
| `0x05` | dos | `LABEL_110E` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:89 |
| `0x05` | amiga | `LABEL_11F9` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:38 |
| `0x05` | cart | `LABEL_139C` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:58 |
| `0x05` | dos | `LABEL_1401` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:56 |
| `0x05` | amiga | `LABEL_307F` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:236 |
| `0x05` | amiga | `LABEL_30BD` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:931 |
| `0x05` | cart | `LABEL_328C` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:262 |
| `0x05` | dos | `LABEL_32A8` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:254 |
| `0x05` | cart | `LABEL_32CA` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1019 |
| `0x05` | dos | `LABEL_32E6` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:998 |
| `0x05` | amiga | `LABEL_3535` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR6B_TO_1.inc:6 |
| `0x05` | cart | `LABEL_3742` | src/levels/_unified/caves/cart__post_INLINE_SET_VARE8_TO_2F.inc:60 |
| `0x05` | dos | `LABEL_375E` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR6B_TO_1.inc:6 |
| `0x05` | cart | `LABEL_3778` | src/levels/_unified/caves/cart__entry.inc:3234 |
| `0x05` | amiga | `LABEL_C90A` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1126 (+1 more) |
| `0x05` | cart | `LABEL_CD7E` | src/levels/_unified/caves/cart__post_PLAY_FX_6B_THEN_KILL_CHANNEL.inc:38 |
| `0x05` | cart | `LABEL_CDA9` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1217 (+1 more) |
| `0x05` | dos | `LABEL_CDB0` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1193 (+1 more) |
| `0x06` | cart | `INIT_VARS_EB_EC_ED` | src/levels/_unified/caves/cart__post_INLINE_SET_VARE8_TO_2F.inc:30 |
| `0x06` | amiga | `INIT_VARS_EB_EC_ED` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE8_TO_2F.inc:30 |
| `0x06` | dos | `INIT_VARS_EB_EC_ED` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE8_TO_2F.inc:30 |
| `0x06` | cart | `LABEL_0492` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1565 |
| `0x06` | amiga | `LABEL_0507` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1459 |
| `0x06` | dos | `LABEL_0520` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1526 |
| `0x06` | cart | `LABEL_10A3` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:93 |
| `0x06` | amiga | `LABEL_10ED` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:72 |
| `0x06` | dos | `LABEL_110E` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:90 |
| `0x06` | amiga | `LABEL_30DC` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:932 |
| `0x06` | amiga | `LABEL_3128` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:237 |
| `0x06` | cart | `LABEL_32E9` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1020 |
| `0x06` | dos | `LABEL_3305` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:999 |
| `0x06` | cart | `LABEL_3335` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:263 |
| `0x06` | dos | `LABEL_3351` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:255 |
| `0x06` | amiga | `LABEL_C894` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1116 |
| `0x06` | cart | `LABEL_CD25` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1207 |
| `0x06` | dos | `LABEL_CD3A` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1183 |
| `0x07` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1218 (+1 more) |
| `0x07` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1127 (+1 more) |
| `0x07` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1194 (+1 more) |
| `0x07` | cart | `LABEL_10A3` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:94 |
| `0x07` | amiga | `LABEL_10ED` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:73 |
| `0x07` | dos | `LABEL_110E` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:91 |
| `0x07` | amiga | `LABEL_309E` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:238 (+1 more) |
| `0x07` | cart | `LABEL_32AB` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:264 (+1 more) |
| `0x07` | dos | `LABEL_32C7` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:256 (+1 more) |
| `0x07` | amiga | `LABEL_3491` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR6B_TO_1.inc:13 |
| `0x07` | cart | `LABEL_369E` | src/levels/_unified/caves/cart__post_INLINE_SET_VARE8_TO_2F.inc:67 |
| `0x07` | dos | `LABEL_36BA` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR6B_TO_1.inc:13 |
| `0x07` | amiga | `LABEL_C307` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:36 |
| `0x07` | cart | `LABEL_C73B` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:56 |
| `0x07` | dos | `LABEL_C75A` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:54 |
| `0x07` | amiga | `LABEL_C7F6` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1117 |
| `0x07` | cart | `LABEL_CC87` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1208 |
| `0x07` | dos | `LABEL_CC9C` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1184 |
| `0x08` | amiga | `INLINE_SET_VAR6B_TO_1` | src/levels/_unified/caves/amiga__post_SET_VAR22_TO_00B8.inc:7 |
| `0x08` | dos | `INLINE_SET_VAR6B_TO_1` | src/levels/_unified/caves/dos__post_SET_VAR22_TO_00B8.inc:7 |
| `0x08` | cart | `LABEL_10A3` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:95 |
| `0x08` | amiga | `LABEL_10ED` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:74 |
| `0x08` | dos | `LABEL_110E` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:92 |
| `0x08` | cart | `LABEL_3778` | src/levels/_unified/caves/cart__post_SET_VAR22_TO_00B8.inc:7 |
| `0x0F` | amiga | `LABEL_DD5E` | src/levels/_unified/caves/amiga__post_DEDUP_CAVES_5B_036.inc:143 |
| `0x0F` | dos | `LABEL_E2AE` | src/levels/_unified/caves/dos__post_DEDUP_CAVES_5B_036.inc:151 |
| `0x0F` | cart | `LABEL_E337` | src/levels/_unified/caves/cart__post_DEDUP_CAVES_5B_036.inc:151 |
| `0x10` | amiga | `LABEL_4C8D` | src/levels/_unified/caves/amiga__post_DELETE_GAME_AND_FX_CHANNELS.inc:36 |
| `0x10` | cart | `LABEL_4E77` | src/levels/_unified/caves/cart__post_DELETE_GAME_AND_FX_CHANNELS.inc:37 |
| `0x10` | dos | `LABEL_4FB0` | src/levels/_unified/caves/dos__post_DELETE_GAME_AND_FX_CHANNELS.inc:37 |
| `0x13` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR01_TO_E.inc:12 |
| `0x13` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR01_TO_E.inc:12 |
| `0x13` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR01_TO_E.inc:12 |
| `0x13` | amiga | `LABEL_1AA9` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR6A_TO_2F.inc:49 |
| `0x13` | cart | `LABEL_1C26` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR6A_TO_2F.inc:45 |
| `0x13` | dos | `LABEL_1C67` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR6A_TO_2F.inc:45 |
| `0x14` | cart | `DRAW_CV352_STEP_RIGHT3` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_1.inc:6 |
| `0x14` | amiga | `DRAW_CV352_STEP_RIGHT3` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_1.inc:6 |
| `0x14` | dos | `DRAW_CV352_STEP_RIGHT3` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_1.inc:6 |
| `0x14` | cart | `INLINE_SET_VAR01_TO_E` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR6A_TO_2F.inc:87 |
| `0x14` | amiga | `INLINE_SET_VAR01_TO_E` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR6A_TO_2F.inc:88 |
| `0x14` | dos | `INLINE_SET_VAR01_TO_E` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR6A_TO_2F.inc:86 |
| `0x14` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_E9_E8.inc:307 |
| `0x14` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_E7_2.inc:228 |
| `0x14` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_E9_E8.inc:302 |
| `0x14` | cart | `LABEL_0720` | src/levels/_unified/caves/cart__post_INIT_VARS_EA_EB.inc:50 |
| `0x14` | cart | `LABEL_076F` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_E8_E8_PLUS3.inc:182 |
| `0x14` | amiga | `LABEL_0779` | src/levels/_unified/caves/amiga__post_INIT_VARS_EA_EB.inc:50 |
| `0x14` | dos | `LABEL_079A` | src/levels/_unified/caves/dos__post_INIT_VARS_EA_EB.inc:50 |
| `0x14` | amiga | `LABEL_07C8` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_E7_E8_E8_PLUS3.inc:181 |
| `0x14` | dos | `LABEL_07E9` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_E8_E8_PLUS3.inc:181 |
| `0x14` | cart | `LABEL_1217` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_E9_E8.inc:187 |
| `0x14` | dos | `LABEL_1282` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_E9_E8.inc:186 |
| `0x14` | amiga | `LABEL_14A1` | src/levels/_unified/caves/amiga__post_INIT_VARS_0E_29.inc:74 |
| `0x14` | cart | `LABEL_1606` | src/levels/_unified/caves/cart__post_INIT_VARS_0E_29.inc:74 |
| `0x14` | dos | `LABEL_1661` | src/levels/_unified/caves/dos__post_INIT_VARS_0E_29.inc:74 |
| `0x14` | amiga | `LABEL_17B3` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAREF_TO_5.inc:85 |
| `0x14` | cart | `LABEL_1926` | src/levels/_unified/caves/cart__post_INLINE_SET_VAREF_TO_5.inc:90 |
| `0x14` | dos | `LABEL_1973` | src/levels/_unified/caves/dos__post_INLINE_SET_VAREF_TO_5.inc:86 |
| `0x14` | amiga | `LABEL_1A65` | src/levels/_unified/caves/amiga__post_SET_VAR22_TO_0085.inc:10 |
| `0x14` | cart | `LABEL_1BEE` | src/levels/_unified/caves/cart__post_SET_VAR22_TO_0085.inc:11 |
| `0x14` | dos | `LABEL_1C2F` | src/levels/_unified/caves/dos__post_SET_VAR22_TO_0085.inc:11 |
| `0x14` | amiga | `LABEL_2349` | src/levels/_unified/caves/amiga__post_INIT_VAR08_FROM_VARE9_VAR09_TO_4.inc:100 |
| `0x14` | amiga | `LABEL_237F` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_68_69_6B.inc:105 |
| `0x14` | cart | `LABEL_24D4` | src/levels/_unified/caves/cart__post_INIT_VAR08_FROM_VARE9_VAR09_TO_4.inc:100 |
| `0x14` | cart | `LABEL_250A` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_68_69_6B.inc:105 |
| `0x14` | dos | `LABEL_250D` | src/levels/_unified/caves/dos__post_INIT_VAR08_FROM_VARE9_VAR09_TO_4.inc:100 |
| `0x14` | dos | `LABEL_2543` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_68_69_6B.inc:105 |
| `0x14` | amiga | `LABEL_29A7` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR7C_TO_0001_040.inc:49 |
| `0x14` | cart | `LABEL_2B75` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR7C_TO_0001_040.inc:61 |
| `0x14` | dos | `LABEL_2BA8` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR7C_TO_0001_040.inc:61 |
| `0x14` | amiga | `LABEL_37D0` | src/levels/_unified/caves/amiga__entry.inc:3184 |
| `0x14` | cart | `LABEL_39E3` | src/levels/_unified/caves/cart__entry.inc:3179 |
| `0x14` | dos | `LABEL_39F9` | src/levels/_unified/caves/dos__entry.inc:3192 |
| `0x14` | amiga | `LABEL_488D` | src/levels/_unified/caves/amiga__post_PLAY_SFX_005C_CH00.inc:18 |
| `0x14` | amiga | `LABEL_48B4` | src/levels/_unified/caves/amiga__post_PLAY_SFX_005C_CH00.inc:20 |
| `0x14` | amiga | `LABEL_4958` | src/levels/_unified/caves/amiga__post_PLAY_SFX_005C_CH00.inc:12 |
| `0x14` | amiga | `LABEL_4973` | src/levels/_unified/caves/amiga__post_PLAY_SFX_005C_CH00.inc:14 |
| `0x14` | cart | `LABEL_4A5B` | src/levels/_unified/caves/cart__post_PLAY_SFX_005C_CH00.inc:19 |
| `0x14` | cart | `LABEL_4A82` | src/levels/_unified/caves/cart__post_PLAY_SFX_005C_CH00.inc:21 |
| `0x14` | cart | `LABEL_4B26` | src/levels/_unified/caves/cart__post_PLAY_SFX_005C_CH00.inc:13 |
| `0x14` | cart | `LABEL_4B41` | src/levels/_unified/caves/cart__post_PLAY_SFX_005C_CH00.inc:15 |
| `0x14` | dos | `LABEL_4B9E` | src/levels/_unified/caves/dos__post_PLAY_SFX_005C_CH00.inc:18 |
| `0x14` | dos | `LABEL_4BC5` | src/levels/_unified/caves/dos__post_PLAY_SFX_005C_CH00.inc:20 |
| `0x14` | dos | `LABEL_4C69` | src/levels/_unified/caves/dos__post_PLAY_SFX_005C_CH00.inc:12 |
| `0x14` | dos | `LABEL_4C84` | src/levels/_unified/caves/dos__post_PLAY_SFX_005C_CH00.inc:14 |
| `0x14` | amiga | `LABEL_7782` | src/levels/_unified/caves/amiga__post_COPY_VAR40_TO_VAR22.inc:41 (+1 more) |
| `0x14` | amiga | `LABEL_7847` | src/levels/_unified/caves/amiga__post_ADD_VAR11_TO_VAR34.inc:44 (+2 more) |
| `0x14` | amiga | `LABEL_794A` | src/levels/_unified/caves/amiga__post_COPY_VAR40_TO_VAR22.inc:60 |
| `0x14` | cart | `LABEL_7A43` | src/levels/_unified/caves/cart__post_COPY_VAR40_TO_VAR22.inc:41 (+1 more) |
| `0x14` | dos | `LABEL_7ADA` | src/levels/_unified/caves/dos__post_COPY_VAR40_TO_VAR22.inc:41 (+1 more) |
| `0x14` | cart | `LABEL_7B1C` | src/levels/_unified/caves/cart__post_ADD_VAR11_TO_VAR34.inc:46 (+2 more) |
| `0x14` | dos | `LABEL_7BA5` | src/levels/_unified/caves/dos__post_ADD_VAR11_TO_VAR34.inc:44 (+2 more) |
| `0x14` | cart | `LABEL_7C1F` | src/levels/_unified/caves/cart__post_COPY_VAR40_TO_VAR22.inc:60 |
| `0x14` | dos | `LABEL_7CA8` | src/levels/_unified/caves/dos__post_COPY_VAR40_TO_VAR22.inc:60 |
| `0x14` | amiga | `LABEL_9E1E` | src/levels/_unified/caves/amiga__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:15 |
| `0x14` | amiga | `LABEL_9E41` | src/levels/_unified/caves/amiga__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:9 |
| `0x14` | cart | `LABEL_A0F3` | src/levels/_unified/caves/cart__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:18 |
| `0x14` | cart | `LABEL_A116` | src/levels/_unified/caves/cart__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:12 |
| `0x14` | dos | `LABEL_A17C` | src/levels/_unified/caves/dos__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:18 |
| `0x14` | dos | `LABEL_A19F` | src/levels/_unified/caves/dos__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:12 |
| `0x14` | amiga | `LABEL_DBA5` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_68_69_6B.inc:400 |
| `0x14` | dos | `LABEL_E0DB` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_68_69_6B.inc:410 |
| `0x14` | cart | `LABEL_E164` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_68_69_6B.inc:410 |
| `0x14` | amiga | `LABEL_E2C9` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:39 |
| `0x14` | amiga | `LABEL_E41E` | src/levels/_unified/caves/amiga__entry.inc:3186 (+5 more) |
| `0x14` | amiga | `LABEL_E54E` | src/levels/_unified/caves/amiga__post_INIT_VARS_0E_29.inc:87 (+5 more) |
| `0x14` | amiga | `LABEL_E68A` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_2.inc:46 |
| `0x14` | amiga | `LABEL_E6AE` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_2.inc:44 |
| `0x14` | amiga | `LABEL_E774` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_5.inc:6 |
| `0x14` | amiga | `LABEL_E794` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_5.inc:4 |
| `0x14` | dos | `LABEL_E850` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:57 |
| `0x14` | amiga | `LABEL_E85D` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_2.inc:39 |
| `0x14` | cart | `LABEL_E8D9` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:59 |
| `0x14` | amiga | `LABEL_E901` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_2.inc:24 |
| `0x14` | dos | `LABEL_E9A5` | src/levels/_unified/caves/dos__entry.inc:3194 (+5 more) |
| `0x14` | amiga | `LABEL_E9BC` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_6.inc:19 |
| `0x14` | cart | `LABEL_EA2E` | src/levels/_unified/caves/cart__entry.inc:3181 (+5 more) |
| `0x14` | amiga | `LABEL_EA63` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_2.inc:12 |
| `0x14` | amiga | `LABEL_EB1E` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_6.inc:6 |
| `0x14` | dos | `LABEL_EB39` | src/levels/_unified/caves/dos__post_INIT_VARS_0E_29.inc:87 (+5 more) |
| `0x14` | cart | `LABEL_EBC2` | src/levels/_unified/caves/cart__post_INIT_VARS_0E_29.inc:87 (+4 more) |
| `0x14` | amiga | `LABEL_EBD9` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_2.inc:34 |
| `0x14` | amiga | `LABEL_EC7C` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_6.inc:24 |
| `0x14` | amiga | `LABEL_EC94` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_6.inc:11 |
| `0x14` | dos | `LABEL_ECE3` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_2.inc:46 |
| `0x14` | dos | `LABEL_ED07` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_2.inc:44 |
| `0x14` | amiga | `LABEL_ED35` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_2.inc:18 |
| `0x14` | cart | `LABEL_ED6C` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_2.inc:46 |
| `0x14` | cart | `LABEL_ED90` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_2.inc:44 |
| `0x14` | dos | `LABEL_EDCD` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_5.inc:6 |
| `0x14` | dos | `LABEL_EDED` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_5.inc:4 |
| `0x14` | amiga | `LABEL_EE06` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR63_TO_2.inc:6 |
| `0x14` | cart | `LABEL_EE56` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_5.inc:6 |
| `0x14` | cart | `LABEL_EE76` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_5.inc:4 |
| `0x14` | dos | `LABEL_EEB6` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_2.inc:39 |
| `0x14` | cart | `LABEL_EF3F` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_2.inc:39 |
| `0x14` | dos | `LABEL_EF5A` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_2.inc:24 (+1 more) |
| `0x14` | cart | `LABEL_EFE3` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_2.inc:24 (+1 more) |
| `0x14` | dos | `LABEL_F021` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_6.inc:19 (+1 more) |
| `0x14` | cart | `LABEL_F0AA` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_6.inc:19 (+1 more) |
| `0x14` | dos | `LABEL_F0CE` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_2.inc:12 (+1 more) |
| `0x14` | cart | `LABEL_F157` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_2.inc:12 (+1 more) |
| `0x14` | dos | `LABEL_F195` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_6.inc:6 (+1 more) |
| `0x14` | cart | `LABEL_F21E` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_6.inc:6 (+1 more) |
| `0x14` | dos | `LABEL_F256` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_2.inc:34 |
| `0x14` | cart | `LABEL_F2DF` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_2.inc:34 |
| `0x14` | dos | `LABEL_F2F9` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_6.inc:24 |
| `0x14` | dos | `LABEL_F311` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_6.inc:11 |
| `0x14` | cart | `LABEL_F382` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_6.inc:24 |
| `0x14` | cart | `LABEL_F39A` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_6.inc:11 |
| `0x14` | dos | `LABEL_F3B2` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_2.inc:18 |
| `0x14` | cart | `LABEL_F43B` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_2.inc:18 |
| `0x14` | dos | `LABEL_F483` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR63_TO_2.inc:6 |
| `0x14` | cart | `LABEL_F50C` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR63_TO_2.inc:6 |
| `0x14` | cart | `STEP_DRAW_CV352_LEFT4_RIGHT1` | src/levels/_unified/caves/cart__post_SET_VAR18_TO_0122.inc:169 |
| `0x14` | amiga | `STEP_DRAW_CV352_LEFT4_RIGHT1` | src/levels/_unified/caves/amiga__post_SET_VAR18_TO_0122.inc:146 |
| `0x14` | dos | `STEP_DRAW_CV352_LEFT4_RIGHT1` | src/levels/_unified/caves/dos__post_SET_VAR18_TO_0122.inc:169 |
| `0x15` | amiga | `DRAW_CIN_110_BLOCK__AMIGA__POST_INCREMENT_VAR07_BY_4` | src/levels/_unified/caves/amiga__post_INCREMENT_VAR07_BY_4.inc:201 |
| `0x15` | cart | `DRAW_CIN_110_BLOCK__CART__POST_INCREMENT_VAR07_BY_4` | src/levels/_unified/caves/cart__post_INCREMENT_VAR07_BY_4.inc:231 |
| `0x15` | dos | `DRAW_CIN_110_BLOCK__DOS__POST_INCREMENT_VAR07_BY_4` | src/levels/_unified/caves/dos__post_INCREMENT_VAR07_BY_4.inc:231 |
| `0x15` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__entry.inc:3182 (+7 more) |
| `0x15` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__entry.inc:3187 (+7 more) |
| `0x15` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__entry.inc:3195 (+7 more) |
| `0x15` | cart | `LABEL_12A9` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_E9_E8.inc:188 |
| `0x15` | dos | `LABEL_130E` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_E9_E8.inc:187 |
| `0x15` | amiga | `LABEL_23FC` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_68_69_6B.inc:106 |
| `0x15` | cart | `LABEL_2587` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_68_69_6B.inc:106 |
| `0x15` | dos | `LABEL_25C0` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_68_69_6B.inc:106 |
| `0x15` | amiga | `LABEL_2643` | src/levels/_unified/caves/amiga__post_SET_VAR22_TO_00B8.inc:576 (+1 more) |
| `0x15` | cart | `LABEL_27CE` | src/levels/_unified/caves/cart__post_SET_VAR22_TO_00B8.inc:607 (+1 more) |
| `0x15` | dos | `LABEL_2807` | src/levels/_unified/caves/dos__post_SET_VAR22_TO_00B8.inc:605 (+1 more) |
| `0x15` | amiga | `LABEL_3813` | src/levels/_unified/caves/amiga__entry.inc:3185 |
| `0x15` | amiga | `LABEL_3863` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:120 |
| `0x15` | amiga | `LABEL_3916` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:84 |
| `0x15` | amiga | `LABEL_394F` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:126 |
| `0x15` | amiga | `LABEL_3980` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:90 |
| `0x15` | amiga | `LABEL_39BA` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:108 |
| `0x15` | amiga | `LABEL_39EB` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:132 |
| `0x15` | cart | `LABEL_3A26` | src/levels/_unified/caves/cart__entry.inc:3180 |
| `0x15` | dos | `LABEL_3A3C` | src/levels/_unified/caves/dos__entry.inc:3193 |
| `0x15` | amiga | `LABEL_3A58` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:96 |
| `0x15` | cart | `LABEL_3A76` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:125 |
| `0x15` | dos | `LABEL_3A8C` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:125 |
| `0x15` | amiga | `LABEL_3A91` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:138 |
| `0x15` | amiga | `LABEL_3AFE` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:114 |
| `0x15` | cart | `LABEL_3B29` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:89 |
| `0x15` | amiga | `LABEL_3B2F` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:102 |
| `0x15` | dos | `LABEL_3B3F` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:89 |
| `0x15` | cart | `LABEL_3B62` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:131 |
| `0x15` | dos | `LABEL_3B78` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:131 |
| `0x15` | cart | `LABEL_3B93` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:95 |
| `0x15` | dos | `LABEL_3BA9` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:95 |
| `0x15` | cart | `LABEL_3BCD` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:113 |
| `0x15` | dos | `LABEL_3BE3` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:113 |
| `0x15` | cart | `LABEL_3BFE` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:137 |
| `0x15` | dos | `LABEL_3C14` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:137 |
| `0x15` | cart | `LABEL_3C6B` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:101 |
| `0x15` | dos | `LABEL_3C81` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:101 |
| `0x15` | cart | `LABEL_3CA4` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:143 |
| `0x15` | dos | `LABEL_3CBA` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:143 |
| `0x15` | cart | `LABEL_3D11` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:119 |
| `0x15` | dos | `LABEL_3D27` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:119 |
| `0x15` | cart | `LABEL_3D42` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:107 |
| `0x15` | dos | `LABEL_3D58` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:107 |
| `0x15` | amiga | `LABEL_969B` | src/levels/_unified/caves/amiga__post_DECREMENT_VAR08_BY_D.inc:372 (+1 more) |
| `0x15` | cart | `LABEL_9970` | src/levels/_unified/caves/cart__post_DECREMENT_VAR08_BY_D.inc:389 (+1 more) |
| `0x15` | dos | `LABEL_99F9` | src/levels/_unified/caves/dos__post_DECREMENT_VAR08_BY_D.inc:389 (+1 more) |
| `0x15` | amiga | `LABEL_E65D` | src/levels/_unified/caves/amiga__post_DRAW_CV352_STEP_RIGHT3.inc:126 |
| `0x15` | amiga | `LABEL_E747` | src/levels/_unified/caves/amiga__post_DRAW_CV352_STEP_RIGHT3.inc:214 |
| `0x15` | dos | `LABEL_ECB6` | src/levels/_unified/caves/dos__post_DRAW_CV352_STEP_RIGHT3.inc:169 |
| `0x15` | cart | `LABEL_ED3F` | src/levels/_unified/caves/cart__post_DRAW_CV352_STEP_RIGHT3.inc:169 |
| `0x15` | dos | `LABEL_EDA0` | src/levels/_unified/caves/dos__post_DRAW_CV352_STEP_RIGHT3.inc:257 |
| `0x15` | cart | `LABEL_EE29` | src/levels/_unified/caves/cart__post_DRAW_CV352_STEP_RIGHT3.inc:257 |
| `0x16` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:91 (+10 more) |
| `0x16` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:86 (+10 more) |
| `0x16` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:91 (+10 more) |
| `0x16` | amiga | `LABEL_23B2` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_68_69_6B.inc:192 |
| `0x16` | cart | `LABEL_253D` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_68_69_6B.inc:192 |
| `0x16` | cart | `LABEL_2557` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_68_69_6B.inc:199 |
| `0x16` | dos | `LABEL_2576` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_68_69_6B.inc:192 |
| `0x16` | dos | `LABEL_2590` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_68_69_6B.inc:199 |
| `0x16` | amiga | `LABEL_3813` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:79 (+2 more) |
| `0x16` | cart | `LABEL_3A26` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:84 (+2 more) |
| `0x16` | dos | `LABEL_3A3C` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:84 (+2 more) |
| `0x16` | amiga | `LABEL_3BA3` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:191 (+1 more) |
| `0x16` | amiga | `LABEL_3C0E` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:157 (+1 more) |
| `0x16` | amiga | `LABEL_3CD9` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6B.inc:209 (+2 more) |
| `0x16` | cart | `LABEL_3DB6` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:196 (+1 more) |
| `0x16` | dos | `LABEL_3DCC` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:196 (+1 more) |
| `0x16` | cart | `LABEL_3E21` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:162 (+1 more) |
| `0x16` | dos | `LABEL_3E37` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:162 (+1 more) |
| `0x16` | cart | `LABEL_3EEC` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6B.inc:214 (+2 more) |
| `0x16` | dos | `LABEL_3F02` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6B.inc:214 (+2 more) |
| `0x16` | amiga | `LABEL_DF3B` | src/levels/_unified/caves/amiga__entry.inc:3188 (+10 more) |
| `0x16` | cart | `SETUP_CHAN_14_BY_VAR63` | src/levels/_unified/caves/cart__entry.inc:3183 (+9 more) |
| `0x16` | dos | `SETUP_CHAN_14_BY_VAR63` | src/levels/_unified/caves/dos__entry.inc:3196 (+10 more) |
| `0x17` | amiga | `LABEL_71A7` | src/levels/_unified/caves/amiga__post_DRAW_CV352_STEP_RIGHT3.inc:323 (+1 more) |
| `0x17` | amiga | `LABEL_71FB` | src/levels/_unified/caves/amiga__post_INLINE_BREAK_041.inc:278 (+1 more) |
| `0x17` | cart | `LABEL_7400` | src/levels/_unified/caves/cart__post_DRAW_CV352_STEP_RIGHT3.inc:366 (+1 more) |
| `0x17` | cart | `LABEL_7462` | src/levels/_unified/caves/cart__post_INLINE_BREAK_041.inc:288 (+1 more) |
| `0x17` | dos | `LABEL_74C1` | src/levels/_unified/caves/dos__post_DRAW_CV352_STEP_RIGHT3.inc:366 (+1 more) |
| `0x17` | dos | `LABEL_7523` | src/levels/_unified/caves/dos__post_INLINE_BREAK_041.inc:288 (+1 more) |
| `0x18` | amiga | `LABEL_6EC3` | src/levels/_unified/caves/amiga__post_DELETE_GAME_AND_FX_CHANNELS.inc:39 |
| `0x18` | cart | `LABEL_710A` | src/levels/_unified/caves/cart__post_DELETE_GAME_AND_FX_CHANNELS.inc:40 |
| `0x18` | dos | `LABEL_71DD` | src/levels/_unified/caves/dos__post_DELETE_GAME_AND_FX_CHANNELS.inc:40 |
| `0x19` | cart | `LABEL_082C` | src/levels/_unified/caves/cart__post_INIT_VARS_EA_EB.inc:51 |
| `0x19` | amiga | `LABEL_0885` | src/levels/_unified/caves/amiga__post_INIT_VARS_EA_EB.inc:51 |
| `0x19` | dos | `LABEL_08A6` | src/levels/_unified/caves/dos__post_INIT_VARS_EA_EB.inc:51 |
| `0x1A` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_DELETE_GAME_AND_FX_CHANNELS.inc:39 |
| `0x1A` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_DELETE_GAME_AND_FX_CHANNELS.inc:38 |
| `0x1A` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_DELETE_GAME_AND_FX_CHANNELS.inc:39 |
| `0x1A` | amiga | `LABEL_9DFA` | src/levels/_unified/caves/amiga__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:24 |
| `0x1A` | amiga | `LABEL_9E0C` | src/levels/_unified/caves/amiga__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:10 |
| `0x1A` | cart | `LABEL_A0CF` | src/levels/_unified/caves/cart__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:24 |
| `0x1A` | cart | `LABEL_A0E1` | src/levels/_unified/caves/cart__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:10 |
| `0x1A` | dos | `LABEL_A158` | src/levels/_unified/caves/dos__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:24 |
| `0x1A` | dos | `LABEL_A16A` | src/levels/_unified/caves/dos__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:10 |
| `0x1B` | cart | `INIT_VARS_6C_6D_71_70` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:590 |
| `0x1B` | amiga | `INIT_VARS_6C_6D_71_70` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:553 |
| `0x1B` | dos | `INIT_VARS_6C_6D_71_70` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:571 |
| `0x1B` | cart | `INIT_VARS_71_6C_6D` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:592 |
| `0x1B` | amiga | `INIT_VARS_71_6C_6D` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:555 |
| `0x1B` | dos | `INIT_VARS_71_6C_6D` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:573 |
| `0x1B` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:535 |
| `0x1B` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:498 |
| `0x1B` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:516 |
| `0x1C` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:534 |
| `0x1C` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:497 |
| `0x1C` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:515 |
| `0x1C` | cart | `LABEL_08FA` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:550 (+1 more) |
| `0x1C` | amiga | `LABEL_0953` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:513 (+1 more) |
| `0x1C` | dos | `LABEL_0974` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:531 (+1 more) |
| `0x21` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1008 (+1 more) |
| `0x21` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:920 (+1 more) |
| `0x21` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:987 (+1 more) |
| `0x21` | amiga | `LABEL_20FC` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:962 |
| `0x21` | cart | `LABEL_2287` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1051 |
| `0x21` | dos | `LABEL_22C0` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1029 |
| `0x22` | cart | `INLINE_SET_VAR73_TO_6` | src/levels/_unified/caves/cart__post_SET_VAR13_TO_FFFF.inc:39 |
| `0x22` | amiga | `INLINE_SET_VAR73_TO_6` | src/levels/_unified/caves/amiga__post_SET_VAR13_TO_FFFF.inc:39 |
| `0x22` | dos | `INLINE_SET_VAR73_TO_6` | src/levels/_unified/caves/dos__post_SET_VAR13_TO_FFFF.inc:39 |
| `0x22` | amiga | `LABEL_284D` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:638 (+2 more) |
| `0x22` | cart | `LABEL_2A1B` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:675 (+4 more) |
| `0x22` | dos | `LABEL_2A4E` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:656 (+4 more) |
| `0x22` | amiga | `LABEL_2BA7` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:503 (+1 more) |
| `0x22` | cart | `LABEL_2D9D` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:540 (+1 more) |
| `0x22` | dos | `LABEL_2DCA` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:521 (+1 more) |
| `0x22` | amiga | `LABEL_4DEA` | src/levels/_unified/caves/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:42 (+1 more) |
| `0x22` | cart | `LABEL_4FD4` | src/levels/_unified/caves/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:43 (+1 more) |
| `0x22` | dos | `LABEL_510D` | src/levels/_unified/caves/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:43 (+1 more) |
| `0x23` | cart | `GAME_LOOP_HERO_CV128_VAR2F` | src/levels/_unified/caves/cart__post_SETUP_67_4B_VARS_B0_3_01_50_AF_58_B1.inc:67 |
| `0x23` | amiga | `GAME_LOOP_HERO_DISPATCH_LAST` | src/levels/_unified/caves/amiga__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:56 |
| `0x23` | dos | `GAME_LOOP_HERO_DISPATCH_LAST` | src/levels/_unified/caves/dos__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:56 |
| `0x23` | cart | `HANG_DRAW_CIN_734_VAR09_GUARD` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:676 (+4 more) |
| `0x23` | dos | `HANG_DRAW_CIN_743_VAR09_GUARD` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:657 (+4 more) |
| `0x23` | cart | `INIT_VARS_29_07_08` | src/levels/_unified/caves/cart__post_SETUP_67_4B_VARS_B0_3_01_50_AF_58_B1.inc:194 |
| `0x23` | amiga | `INIT_VARS_29_07_08` | src/levels/_unified/caves/amiga__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:183 |
| `0x23` | dos | `INIT_VARS_29_07_08` | src/levels/_unified/caves/dos__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:183 |
| `0x23` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:44 (+3 more) |
| `0x23` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:43 (+3 more) |
| `0x23` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:44 (+3 more) |
| `0x23` | cart | `LABEL_0492` | src/levels/_unified/caves/cart__post_SETUP_67_4B_VARS_B0_3_01_50_AF_58_B1.inc:203 |
| `0x23` | amiga | `LABEL_04A3` | src/levels/_unified/caves/amiga__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:194 |
| `0x23` | dos | `LABEL_04BC` | src/levels/_unified/caves/dos__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:194 |
| `0x23` | amiga | `LABEL_2DAC` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:504 (+1 more) |
| `0x23` | amiga | `LABEL_2E58` | src/levels/_unified/caves/amiga__post_INIT_VARS_6D_71_70.inc:228 |
| `0x23` | amiga | `LABEL_2E85` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:514 |
| `0x23` | amiga | `LABEL_2F9B` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:639 (+2 more) |
| `0x23` | cart | `LABEL_2FA2` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:541 (+1 more) |
| `0x23` | dos | `LABEL_2FCF` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:522 (+1 more) |
| `0x23` | cart | `LABEL_304E` | src/levels/_unified/caves/cart__post_INIT_VARS_6D_71_70.inc:228 |
| `0x23` | cart | `LABEL_307B` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:551 |
| `0x23` | dos | `LABEL_307B` | src/levels/_unified/caves/dos__post_INIT_VARS_6D_71_70.inc:228 |
| `0x23` | dos | `LABEL_30A8` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:532 |
| `0x23` | amiga | `LABEL_4A76` | src/levels/_unified/caves/amiga__post_PLAY_SFX_005C_CH00.inc:33 |
| `0x23` | amiga | `LABEL_4AC9` | src/levels/_unified/caves/amiga__post_PLAY_SFX_005C_CH00.inc:35 |
| `0x23` | cart | `LABEL_4C44` | src/levels/_unified/caves/cart__post_PLAY_SFX_005C_CH00.inc:34 |
| `0x23` | cart | `LABEL_4C9D` | src/levels/_unified/caves/cart__post_PLAY_SFX_005C_CH00.inc:36 |
| `0x23` | dos | `LABEL_4D87` | src/levels/_unified/caves/dos__post_PLAY_SFX_005C_CH00.inc:33 |
| `0x23` | dos | `LABEL_4DE0` | src/levels/_unified/caves/dos__post_PLAY_SFX_005C_CH00.inc:35 |
| `0x24` | amiga | `LABEL_2872` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:642 (+1 more) |
| `0x24` | cart | `LABEL_2A40` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:679 (+3 more) |
| `0x24` | dos | `LABEL_2A73` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:660 (+3 more) |
| `0x24` | amiga | `LABEL_2BB5` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:507 |
| `0x24` | amiga | `LABEL_2BC3` | src/levels/_unified/caves/amiga__post_INIT_VARS_6D_71_70.inc:229 (+1 more) |
| `0x24` | cart | `LABEL_2DAB` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:544 |
| `0x24` | cart | `LABEL_2DB9` | src/levels/_unified/caves/cart__post_INIT_VARS_6D_71_70.inc:229 (+1 more) |
| `0x24` | dos | `LABEL_2DD8` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:525 |
| `0x24` | dos | `LABEL_2DE6` | src/levels/_unified/caves/dos__post_INIT_VARS_6D_71_70.inc:229 (+1 more) |
| `0x24` | amiga | `LABEL_4E0A` | src/levels/_unified/caves/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:44 (+1 more) |
| `0x24` | cart | `LABEL_4FF4` | src/levels/_unified/caves/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:45 (+1 more) |
| `0x24` | dos | `LABEL_512D` | src/levels/_unified/caves/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:45 (+1 more) |
| `0x25` | cart | `GAME_LOOP_HERO_CV128_VAR2F` | src/levels/_unified/caves/cart__post_SETUP_67_4B_VARS_B0_3_01_50_AF_58_B1.inc:78 (+4 more) |
| `0x25` | amiga | `GAME_LOOP_HERO_DISPATCH_LAST` | src/levels/_unified/caves/amiga__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:67 (+4 more) |
| `0x25` | dos | `GAME_LOOP_HERO_DISPATCH_LAST` | src/levels/_unified/caves/dos__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:67 (+4 more) |
| `0x25` | cart | `HANG_DRAW_CIN_734_VAR09_GUARD` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:680 (+3 more) |
| `0x25` | dos | `HANG_DRAW_CIN_743_VAR09_GUARD` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:661 (+3 more) |
| `0x25` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:46 (+2 more) |
| `0x25` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:45 (+1 more) |
| `0x25` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:46 (+1 more) |
| `0x25` | amiga | `LABEL_2E0C` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:508 |
| `0x25` | amiga | `LABEL_2F9B` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:643 (+1 more) |
| `0x25` | cart | `LABEL_3002` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:545 |
| `0x25` | dos | `LABEL_302F` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:526 |
| `0x25` | amiga | `LABEL_4A76` | src/levels/_unified/caves/amiga__post_PLAY_SFX_005C_CH00.inc:39 |
| `0x25` | amiga | `LABEL_4AC9` | src/levels/_unified/caves/amiga__post_PLAY_SFX_005C_CH00.inc:41 |
| `0x25` | cart | `LABEL_4C44` | src/levels/_unified/caves/cart__post_PLAY_SFX_005C_CH00.inc:40 |
| `0x25` | cart | `LABEL_4C9D` | src/levels/_unified/caves/cart__post_PLAY_SFX_005C_CH00.inc:42 |
| `0x25` | dos | `LABEL_4D87` | src/levels/_unified/caves/dos__post_PLAY_SFX_005C_CH00.inc:39 |
| `0x25` | dos | `LABEL_4DE0` | src/levels/_unified/caves/dos__post_PLAY_SFX_005C_CH00.inc:41 |
| `0x26` | amiga | `LABEL_2880` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:646 (+1 more) |
| `0x26` | cart | `LABEL_2A4E` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:683 (+2 more) |
| `0x26` | dos | `LABEL_2A81` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:664 (+2 more) |
| `0x26` | amiga | `LABEL_4E45` | src/levels/_unified/caves/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:46 (+1 more) |
| `0x26` | cart | `LABEL_502F` | src/levels/_unified/caves/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:47 (+1 more) |
| `0x26` | dos | `LABEL_5168` | src/levels/_unified/caves/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:47 (+1 more) |
| `0x27` | cart | `GAME_LOOP_HERO_CV128_VAR2F` | src/levels/_unified/caves/cart__post_SETUP_67_4B_VARS_B0_3_01_50_AF_58_B1.inc:89 (+4 more) |
| `0x27` | amiga | `GAME_LOOP_HERO_DISPATCH_LAST` | src/levels/_unified/caves/amiga__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:78 (+4 more) |
| `0x27` | dos | `GAME_LOOP_HERO_DISPATCH_LAST` | src/levels/_unified/caves/dos__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:78 (+4 more) |
| `0x27` | cart | `HANG_DRAW_CIN_734_VAR09_GUARD` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:684 (+2 more) |
| `0x27` | dos | `HANG_DRAW_CIN_743_VAR09_GUARD` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:665 (+2 more) |
| `0x27` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:48 (+1 more) |
| `0x27` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:47 (+1 more) |
| `0x27` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:48 (+1 more) |
| `0x27` | amiga | `LABEL_14DE` | src/levels/_unified/caves/amiga__post_INIT_VARS_0E_29.inc:85 |
| `0x27` | amiga | `LABEL_14FE` | src/levels/_unified/caves/amiga__post_INIT_VARS_0E_29.inc:75 |
| `0x27` | amiga | `LABEL_15DD` | src/levels/_unified/caves/amiga__post_INIT_VARS_0E_29.inc:207 |
| `0x27` | cart | `LABEL_1649` | src/levels/_unified/caves/cart__post_INIT_VARS_0E_29.inc:85 |
| `0x27` | cart | `LABEL_1669` | src/levels/_unified/caves/cart__post_INIT_VARS_0E_29.inc:75 |
| `0x27` | dos | `LABEL_169E` | src/levels/_unified/caves/dos__post_INIT_VARS_0E_29.inc:85 |
| `0x27` | dos | `LABEL_16BE` | src/levels/_unified/caves/dos__post_INIT_VARS_0E_29.inc:75 |
| `0x27` | cart | `LABEL_1748` | src/levels/_unified/caves/cart__post_INIT_VARS_0E_29.inc:208 |
| `0x27` | dos | `LABEL_179D` | src/levels/_unified/caves/dos__post_INIT_VARS_0E_29.inc:207 |
| `0x27` | amiga | `LABEL_2F9B` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:647 (+1 more) |
| `0x27` | amiga | `LABEL_4A76` | src/levels/_unified/caves/amiga__post_PLAY_SFX_005C_CH00.inc:45 |
| `0x27` | amiga | `LABEL_4AC9` | src/levels/_unified/caves/amiga__post_PLAY_SFX_005C_CH00.inc:47 |
| `0x27` | cart | `LABEL_4C44` | src/levels/_unified/caves/cart__post_PLAY_SFX_005C_CH00.inc:46 |
| `0x27` | cart | `LABEL_4C9D` | src/levels/_unified/caves/cart__post_PLAY_SFX_005C_CH00.inc:48 |
| `0x27` | dos | `LABEL_4D87` | src/levels/_unified/caves/dos__post_PLAY_SFX_005C_CH00.inc:45 |
| `0x27` | dos | `LABEL_4DE0` | src/levels/_unified/caves/dos__post_PLAY_SFX_005C_CH00.inc:47 |
| `0x27` | amiga | `LABEL_534D` | src/levels/_unified/caves/amiga__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:45 |
| `0x27` | cart | `LABEL_5573` | src/levels/_unified/caves/cart__post_SETUP_67_4B_VARS_B0_3_01_50_AF_58_B1.inc:56 |
| `0x27` | dos | `LABEL_5670` | src/levels/_unified/caves/dos__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:45 |
| `0x28` | cart | `INLINE_SET_VAR74_TO_6` | src/levels/_unified/caves/cart__post_SET_VAR13_TO_FFFF.inc:17 (+1 more) |
| `0x28` | amiga | `INLINE_SET_VAR74_TO_6` | src/levels/_unified/caves/amiga__post_SET_VAR13_TO_FFFF.inc:17 (+1 more) |
| `0x28` | dos | `INLINE_SET_VAR74_TO_6` | src/levels/_unified/caves/dos__post_SET_VAR13_TO_FFFF.inc:17 (+1 more) |
| `0x28` | amiga | `LABEL_2BE0` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:651 (+1 more) |
| `0x28` | cart | `LABEL_2DD6` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:688 (+1 more) |
| `0x28` | dos | `LABEL_2E03` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:669 (+1 more) |
| `0x28` | amiga | `LABEL_4E80` | src/levels/_unified/caves/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:48 (+1 more) |
| `0x28` | cart | `LABEL_506A` | src/levels/_unified/caves/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:49 (+1 more) |
| `0x28` | dos | `LABEL_51A3` | src/levels/_unified/caves/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:49 (+1 more) |
| `0x29` | amiga | `LABEL_2DAC` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:652 (+1 more) |
| `0x29` | cart | `LABEL_2FA2` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:689 (+1 more) |
| `0x29` | dos | `LABEL_2FCF` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:670 (+1 more) |
| `0x2A` | cart | `INLINE_SET_VAR75_TO_6` | src/levels/_unified/caves/cart__post_SET_VAR13_TO_FFFF.inc:24 (+1 more) |
| `0x2A` | amiga | `INLINE_SET_VAR75_TO_6` | src/levels/_unified/caves/amiga__post_SET_VAR13_TO_FFFF.inc:24 (+1 more) |
| `0x2A` | dos | `INLINE_SET_VAR75_TO_6` | src/levels/_unified/caves/dos__post_SET_VAR13_TO_FFFF.inc:24 (+1 more) |
| `0x2A` | amiga | `LABEL_2BEE` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:656 (+1 more) |
| `0x2A` | cart | `LABEL_2DE4` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:693 (+1 more) |
| `0x2A` | dos | `LABEL_2E11` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:674 (+1 more) |
| `0x2B` | amiga | `HANG_DRAW_CIN_625` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:560 |
| `0x2B` | cart | `HANG_DRAW_CIN_637` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:597 |
| `0x2B` | dos | `HANG_DRAW_CIN_646` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:578 |
| `0x2B` | cart | `INLINE_SET_VAR76_TO_0001_037` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_EB.inc:94 (+1 more) |
| `0x2B` | amiga | `INLINE_SET_VAR76_TO_0001_037` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR7F_TO_6.inc:11 (+1 more) |
| `0x2B` | dos | `INLINE_SET_VAR76_TO_0001_037` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_EB.inc:94 (+1 more) |
| `0x2B` | cart | `INLINE_SET_VAR76_TO_0001_038` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_EB.inc:113 |
| `0x2B` | amiga | `INLINE_SET_VAR76_TO_0001_038` | src/levels/_unified/caves/amiga__post_SCROLL_BLIT_P83_TO_PFF_OFFSET_00C8.inc:136 |
| `0x2B` | dos | `INLINE_SET_VAR76_TO_0001_038` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_EB.inc:113 |
| `0x2B` | amiga | `LABEL_2DAC` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:657 (+1 more) |
| `0x2B` | cart | `LABEL_2FA2` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:694 (+1 more) |
| `0x2B` | dos | `LABEL_2FCF` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:675 (+1 more) |
| `0x2C` | amiga | `HANG_DRAW_CIN_624` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:563 |
| `0x2C` | cart | `HANG_DRAW_CIN_636` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:600 |
| `0x2C` | dos | `HANG_DRAW_CIN_645` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:581 |
| `0x2C` | cart | `INLINE_SET_VAR76_TO_6` | src/levels/_unified/caves/cart__post_SET_VAR13_TO_FFFF.inc:31 (+1 more) |
| `0x2C` | amiga | `INLINE_SET_VAR76_TO_6` | src/levels/_unified/caves/amiga__post_SET_VAR13_TO_FFFF.inc:31 (+1 more) |
| `0x2C` | dos | `INLINE_SET_VAR76_TO_6` | src/levels/_unified/caves/dos__post_SET_VAR13_TO_FFFF.inc:31 (+1 more) |
| `0x2C` | cart | `INLINE_SET_VAR79_TO_1` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_EB.inc:80 (+2 more) |
| `0x2C` | amiga | `INLINE_SET_VAR79_TO_1` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR7F_TO_6.inc:7 (+2 more) |
| `0x2C` | dos | `INLINE_SET_VAR79_TO_1` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_EB.inc:80 (+2 more) |
| `0x2C` | amiga | `LABEL_2BFC` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:661 (+1 more) |
| `0x2C` | cart | `LABEL_2DF2` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:698 (+1 more) |
| `0x2C` | dos | `LABEL_2E1F` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:679 (+1 more) |
| `0x2D` | amiga | `HANG_DRAW_CIN_708` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:566 |
| `0x2D` | cart | `HANG_DRAW_CIN_720` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:603 |
| `0x2D` | dos | `HANG_DRAW_CIN_729` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:584 |
| `0x2D` | cart | `INLINE_SET_VAR7C_TO_0001_039` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_EB.inc:87 (+1 more) |
| `0x2D` | amiga | `INLINE_SET_VAR7C_TO_0001_039` | src/levels/_unified/caves/amiga__post_SCROLL_BLIT_P83_TO_PFF_OFFSET_00C8.inc:110 (+1 more) |
| `0x2D` | dos | `INLINE_SET_VAR7C_TO_0001_039` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_EB.inc:87 (+1 more) |
| `0x2D` | cart | `INLINE_SET_VAR7C_TO_0001_040` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR7F_TO_6.inc:15 (+1 more) |
| `0x2D` | amiga | `INLINE_SET_VAR7C_TO_0001_040` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR7F_TO_6.inc:15 (+1 more) |
| `0x2D` | dos | `INLINE_SET_VAR7C_TO_0001_040` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR7F_TO_6.inc:15 (+1 more) |
| `0x2D` | amiga | `LABEL_2DAC` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:662 (+1 more) |
| `0x2D` | cart | `LABEL_2FA2` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:699 (+1 more) |
| `0x2D` | dos | `LABEL_2FCF` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:680 (+1 more) |
| `0x2E` | amiga | `LABEL_19A2` | src/levels/_unified/caves/amiga__post_DELETE_GAME_AND_FX_CHANNELS.inc:40 |
| `0x2E` | cart | `LABEL_1B25` | src/levels/_unified/caves/cart__post_DELETE_GAME_AND_FX_CHANNELS.inc:41 |
| `0x2E` | dos | `LABEL_1B66` | src/levels/_unified/caves/dos__post_DELETE_GAME_AND_FX_CHANNELS.inc:41 |
| `0x2F` | amiga | `LABEL_6345` | src/levels/_unified/caves/amiga__post_DELETE_GAME_AND_FX_CHANNELS.inc:41 |
| `0x2F` | cart | `LABEL_658F` | src/levels/_unified/caves/cart__post_DELETE_GAME_AND_FX_CHANNELS.inc:42 |
| `0x2F` | dos | `LABEL_6668` | src/levels/_unified/caves/dos__post_DELETE_GAME_AND_FX_CHANNELS.inc:42 |
| `0x30` | amiga | `LABEL_5FF1` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR22_BY_23.inc:121 |
| `0x30` | cart | `LABEL_6229` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR22_BY_23.inc:121 |
| `0x30` | dos | `LABEL_6314` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR22_BY_23.inc:121 |
| `0x31` | amiga | `LABEL_5E36` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR22_BY_23.inc:130 |
| `0x31` | amiga | `LABEL_5FFA` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR22_BY_23.inc:122 |
| `0x31` | cart | `LABEL_606E` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR22_BY_23.inc:130 |
| `0x31` | dos | `LABEL_6159` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR22_BY_23.inc:130 |
| `0x31` | cart | `LABEL_6232` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR22_BY_23.inc:122 |
| `0x31` | dos | `LABEL_631D` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR22_BY_23.inc:122 |
| `0x32` | amiga | `LABEL_5E36` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR22_BY_23.inc:138 |
| `0x32` | amiga | `LABEL_5FFA` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR22_BY_23.inc:123 |
| `0x32` | cart | `LABEL_606E` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR22_BY_23.inc:138 |
| `0x32` | dos | `LABEL_6159` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR22_BY_23.inc:138 |
| `0x32` | cart | `LABEL_6232` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR22_BY_23.inc:123 |
| `0x32` | dos | `LABEL_631D` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR22_BY_23.inc:123 |
| `0x33` | amiga | `LABEL_5E36` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR22_BY_23.inc:146 |
| `0x33` | cart | `LABEL_606E` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR22_BY_23.inc:146 |
| `0x33` | dos | `LABEL_6159` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR22_BY_23.inc:146 |
| `0x33` | amiga | `LABEL_70AF` | src/levels/_unified/caves/amiga__post_FOLD_BODY_58B_A2D4469A.inc:234 (+1 more) |
| `0x33` | cart | `LABEL_72F6` | src/levels/_unified/caves/cart__post_FOLD_BODY_58B_A2D4469A.inc:246 (+1 more) |
| `0x33` | dos | `LABEL_73C9` | src/levels/_unified/caves/dos__post_FOLD_BODY_58B_A2D4469A.inc:245 (+1 more) |
| `0x34` | cart | `HANG_DRAW_CIN_012` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:170 |
| `0x34` | amiga | `HANG_DRAW_CIN_012` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:147 |
| `0x34` | dos | `HANG_DRAW_CIN_012` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:165 |
| `0x34` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_EB.inc:86 |
| `0x34` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_SCROLL_BLIT_P83_TO_PFF_OFFSET_00C8.inc:109 |
| `0x34` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_EB.inc:86 |
| `0x34` | amiga | `LABEL_1450` | src/levels/_unified/caves/amiga__post_INIT_VARS_0E_29.inc:28 |
| `0x34` | amiga | `LABEL_1480` | src/levels/_unified/caves/amiga__post_INIT_VARS_0E_29.inc:58 |
| `0x34` | cart | `LABEL_15B5` | src/levels/_unified/caves/cart__post_INIT_VARS_0E_29.inc:28 |
| `0x34` | cart | `LABEL_15E5` | src/levels/_unified/caves/cart__post_INIT_VARS_0E_29.inc:58 |
| `0x34` | amiga | `LABEL_15E8` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_E7_2.inc:229 |
| `0x34` | dos | `LABEL_1610` | src/levels/_unified/caves/dos__post_INIT_VARS_0E_29.inc:28 |
| `0x34` | dos | `LABEL_1640` | src/levels/_unified/caves/dos__post_INIT_VARS_0E_29.inc:58 |
| `0x34` | cart | `LABEL_1753` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_E9_E8.inc:308 |
| `0x34` | dos | `LABEL_17A8` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_E9_E8.inc:303 |
| `0x34` | amiga | `LABEL_3E5D` | src/levels/_unified/caves/amiga__post_SCROLL_BLIT_P83_TO_PFF_OFFSET_00C8.inc:96 (+1 more) |
| `0x34` | cart | `LABEL_4089` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_EB.inc:73 (+1 more) |
| `0x34` | dos | `LABEL_409F` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_EB.inc:73 (+1 more) |
| `0x34` | amiga | `LABEL_70E3` | src/levels/_unified/caves/amiga__post_FOLD_BODY_58B_A2D4469A.inc:224 (+1 more) |
| `0x34` | cart | `LABEL_732D` | src/levels/_unified/caves/cart__post_FOLD_BODY_58B_A2D4469A.inc:236 (+1 more) |
| `0x34` | dos | `LABEL_73FD` | src/levels/_unified/caves/dos__post_FOLD_BODY_58B_A2D4469A.inc:235 (+1 more) |
| `0x34` | amiga | `LABEL_CAB0` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:259 |
| `0x34` | amiga | `LABEL_CB57` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:261 (+1 more) |
| `0x34` | dos | `LABEL_CF56` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:277 |
| `0x34` | cart | `LABEL_CF7F` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:286 |
| `0x34` | dos | `LABEL_CFFD` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:279 (+1 more) |
| `0x34` | cart | `LABEL_D026` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:288 (+1 more) |
| `0x35` | cart | `DRAW_CIN_424_426_VERTICAL` | src/levels/_unified/caves/cart__post_SET_VAR13_TO_FFFF.inc:71 |
| `0x35` | amiga | `DRAW_CIN_424_426_VERTICAL` | src/levels/_unified/caves/amiga__post_SET_VAR13_TO_FFFF.inc:71 |
| `0x35` | dos | `DRAW_CIN_424_426_VERTICAL` | src/levels/_unified/caves/dos__post_SET_VAR13_TO_FFFF.inc:71 |
| `0x35` | cart | `HANG_DRAW_CIN_186` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_E9_E8.inc:309 |
| `0x35` | amiga | `HANG_DRAW_CIN_186` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_E7_2.inc:230 |
| `0x35` | dos | `HANG_DRAW_CIN_186` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_E9_E8.inc:304 |
| `0x35` | cart | `INLINE_SET_VAR7F_TO_6` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:650 |
| `0x35` | amiga | `INLINE_SET_VAR7F_TO_6` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:613 |
| `0x35` | dos | `INLINE_SET_VAR7F_TO_6` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:631 |
| `0x35` | amiga | `LABEL_18A6` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:342 |
| `0x35` | amiga | `LABEL_1983` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1440 |
| `0x35` | cart | `LABEL_1A29` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:379 |
| `0x35` | dos | `LABEL_1A6A` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:360 |
| `0x35` | cart | `LABEL_1B06` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1546 |
| `0x35` | dos | `LABEL_1B47` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1507 |
| `0x35` | amiga | `LABEL_3E79` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:567 |
| `0x35` | cart | `LABEL_4168` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:604 |
| `0x35` | dos | `LABEL_417E` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:585 |
| `0x36` | cart | `LABEL_0627` | src/levels/_unified/caves/cart__post_COPY_VARF8_TO_VAR00.inc:167 |
| `0x36` | amiga | `LABEL_0686` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_3.inc:211 |
| `0x36` | dos | `LABEL_06A7` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_3.inc:211 |
| `0x36` | amiga | `LABEL_1C4B` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_1E.inc:5 (+4 more) |
| `0x36` | amiga | `LABEL_1C6F` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_1E.inc:35 (+1 more) |
| `0x36` | cart | `LABEL_1DD4` | src/levels/_unified/caves/cart__post_INLINE_SET_VARE6_TO_1E.inc:6 (+4 more) |
| `0x36` | cart | `LABEL_1DF8` | src/levels/_unified/caves/cart__post_INLINE_SET_VARE6_TO_1E.inc:36 (+1 more) |
| `0x36` | dos | `LABEL_1E0F` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_1E.inc:5 (+4 more) |
| `0x36` | dos | `LABEL_1E33` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_1E.inc:35 (+1 more) |
| `0x36` | amiga | `LABEL_1E39` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_1E.inc:72 |
| `0x36` | cart | `LABEL_1FC4` | src/levels/_unified/caves/cart__post_INLINE_SET_VARE6_TO_1E.inc:73 |
| `0x36` | dos | `LABEL_1FFD` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_1E.inc:72 |
| `0x36` | amiga | `LABEL_27B9` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_EA.inc:307 |
| `0x36` | cart | `LABEL_2955` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_EA.inc:333 |
| `0x36` | dos | `LABEL_298E` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_EA.inc:307 |
| `0x36` | amiga | `LABEL_324A` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:76 (+1 more) |
| `0x36` | cart | `LABEL_3457` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:97 (+1 more) |
| `0x36` | dos | `LABEL_3473` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:94 (+1 more) |
| `0x36` | amiga | `LABEL_4847` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:318 (+1 more) |
| `0x36` | cart | `LABEL_4A15` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:354 (+1 more) |
| `0x36` | dos | `LABEL_4B58` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:336 (+1 more) |
| `0x36` | amiga | `LABEL_C5ED` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:364 |
| `0x36` | cart | `LABEL_CA62` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:401 |
| `0x36` | dos | `LABEL_CA7D` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:382 |
| `0x37` | amiga | `HANG_DRAW_CIN_269` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_EA.inc:318 |
| `0x37` | cart | `HANG_DRAW_CIN_287__CART__POST_INIT_VARS_E6_EA` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_EA.inc:344 |
| `0x37` | dos | `HANG_DRAW_CIN_288__DOS__POST_INIT_VARS_E6_EA` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_EA.inc:318 |
| `0x37` | cart | `INIT_VARS_E6_E7_EB` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:901 |
| `0x37` | dos | `INIT_VARS_E6_E7_EB` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:882 |
| `0x37` | cart | `INLINE_SET_VARE6_TO_1E` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:175 |
| `0x37` | amiga | `INLINE_SET_VARE6_TO_1E` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:152 |
| `0x37` | dos | `INLINE_SET_VARE6_TO_1E` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:170 |
| `0x37` | amiga | `LABEL_1A8C` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:418 (+2 more) |
| `0x37` | cart | `LABEL_1C15` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:455 (+2 more) |
| `0x37` | dos | `LABEL_1C56` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:436 (+2 more) |
| `0x37` | amiga | `LABEL_4726` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1305 |
| `0x37` | cart | `LABEL_48F4` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1411 |
| `0x37` | dos | `LABEL_4A37` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1372 |
| `0x37` | amiga | `LABEL_C5CF` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:405 |
| `0x37` | cart | `LABEL_CA44` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:442 |
| `0x37` | dos | `LABEL_CA5F` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:423 |
| `0x37` | cart | `SET_VARE6_TO_64_KILL_CHANNEL` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:204 |
| `0x37` | amiga | `SET_VARE6_TO_64_KILL_CHANNEL` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:179 |
| `0x37` | dos | `SET_VARE6_TO_64_KILL_CHANNEL` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:197 |
| `0x38` | amiga | `LABEL_0507` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_3.inc:27 |
| `0x38` | dos | `LABEL_0520` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_3.inc:27 |
| `0x38` | amiga | `LABEL_1881` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:317 |
| `0x38` | cart | `LABEL_1A04` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:353 |
| `0x38` | dos | `LABEL_1A45` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:335 |
| `0x38` | amiga | `LABEL_1D69` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_1E.inc:26 |
| `0x38` | cart | `LABEL_1EF4` | src/levels/_unified/caves/cart__post_INLINE_SET_VARE6_TO_1E.inc:27 |
| `0x38` | dos | `LABEL_1F2D` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_1E.inc:26 |
| `0x38` | amiga | `LABEL_1F82` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_1E.inc:78 |
| `0x38` | cart | `LABEL_210D` | src/levels/_unified/caves/cart__post_INLINE_SET_VARE6_TO_1E.inc:79 |
| `0x38` | dos | `LABEL_2146` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_1E.inc:78 |
| `0x38` | amiga | `LABEL_234D` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:519 |
| `0x38` | cart | `LABEL_24D8` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:556 |
| `0x38` | dos | `LABEL_2511` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:537 |
| `0x38` | amiga | `LABEL_26EE` | src/levels/_unified/caves/amiga__post_SET_VAR22_TO_00B8.inc:577 (+1 more) |
| `0x38` | cart | `LABEL_2879` | src/levels/_unified/caves/cart__post_SET_VAR22_TO_00B8.inc:608 (+1 more) |
| `0x38` | dos | `LABEL_28B2` | src/levels/_unified/caves/dos__post_SET_VAR22_TO_00B8.inc:606 (+1 more) |
| `0x39` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INLINE_SET_VARE6_TO_1E.inc:81 |
| `0x39` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_1E.inc:80 |
| `0x39` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_1E.inc:80 (+1 more) |
| `0x39` | amiga | `LABEL_1C4B` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_1E.inc:39 (+1 more) |
| `0x39` | amiga | `LABEL_1C6F` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_1E.inc:20 (+1 more) |
| `0x39` | cart | `LABEL_1DD4` | src/levels/_unified/caves/cart__post_INLINE_SET_VARE6_TO_1E.inc:40 (+1 more) |
| `0x39` | cart | `LABEL_1DF8` | src/levels/_unified/caves/cart__post_INLINE_SET_VARE6_TO_1E.inc:21 (+1 more) |
| `0x39` | dos | `LABEL_1E0F` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_1E.inc:39 (+1 more) |
| `0x39` | dos | `LABEL_1E33` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_1E.inc:20 (+1 more) |
| `0x39` | amiga | `LABEL_276B` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:520 |
| `0x39` | amiga | `LABEL_278C` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:435 (+1 more) |
| `0x39` | amiga | `LABEL_279B` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:796 |
| `0x39` | cart | `LABEL_28F6` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:557 |
| `0x39` | cart | `LABEL_2928` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:472 (+1 more) |
| `0x39` | dos | `LABEL_292F` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:538 |
| `0x39` | cart | `LABEL_2937` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:833 |
| `0x39` | dos | `LABEL_2961` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:453 (+1 more) |
| `0x39` | dos | `LABEL_2970` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:814 |
| `0x39` | amiga | `LABEL_46F3` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_E7_E8_E8_PLUS3.inc:14 (+1 more) |
| `0x39` | dos | `LABEL_47D3` | src/levels/_unified/caves/dos__post_SETUP_67_A7_VARS_B0_2_02_5D_01_7F_BE_3.inc:238 |
| `0x39` | cart | `LABEL_48C1` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_E8_E8_PLUS3.inc:15 (+1 more) |
| `0x39` | dos | `LABEL_4A04` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_E8_E8_PLUS3.inc:14 (+1 more) |
| `0x3A` | amiga | `LABEL_1EDE` | src/levels/_unified/caves/amiga__post_INLINE_SET_VARE6_TO_1E.inc:85 |
| `0x3A` | cart | `LABEL_2069` | src/levels/_unified/caves/cart__post_INLINE_SET_VARE6_TO_1E.inc:86 |
| `0x3A` | dos | `LABEL_20A2` | src/levels/_unified/caves/dos__post_INLINE_SET_VARE6_TO_1E.inc:85 |
| `0x3A` | amiga | `LABEL_4726` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_E7_E8_E8_PLUS3.inc:15 (+1 more) |
| `0x3A` | cart | `LABEL_48F4` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_E7_E8_E8_PLUS3.inc:16 (+1 more) |
| `0x3A` | dos | `LABEL_4A37` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_E7_E8_E8_PLUS3.inc:15 (+1 more) |
| `0x3B` | amiga | `HANG_DRAW_CIN_300` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:967 |
| `0x3B` | dos | `HANG_DRAW_CIN_321` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1034 |
| `0x3B` | amiga | `HANG_DRAW_CIN_374` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:180 |
| `0x3B` | cart | `HANG_DRAW_CIN_394` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:205 |
| `0x3B` | dos | `HANG_DRAW_CIN_395` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:198 |
| `0x3B` | amiga | `HANG_DRAW_CIN_412` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:291 |
| `0x3B` | cart | `HANG_DRAW_CIN_433` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:327 |
| `0x3B` | dos | `HANG_DRAW_CIN_433` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:309 |
| `0x3B` | amiga | `HANG_DRAW_CIN_637` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:749 |
| `0x3B` | cart | `HANG_DRAW_CIN_648` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:786 |
| `0x3B` | dos | `HANG_DRAW_CIN_658` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:767 |
| `0x3B` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_DELETE_GAME_AND_FX_CHANNELS.inc:43 (+2 more) |
| `0x3B` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_DELETE_GAME_AND_FX_CHANNELS.inc:42 (+2 more) |
| `0x3B` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_DELETE_GAME_AND_FX_CHANNELS.inc:43 (+2 more) |
| `0x3B` | cart | `LABEL_0492` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1567 |
| `0x3B` | amiga | `LABEL_04DF` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1461 |
| `0x3B` | dos | `LABEL_04F8` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1528 |
| `0x3B` | amiga | `LABEL_783B` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:85 |
| `0x3B` | cart | `LABEL_7B10` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:106 |
| `0x3B` | dos | `LABEL_7B96` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:103 |
| `0x3B` | amiga | `LABEL_C31D` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1151 |
| `0x3B` | amiga | `LABEL_C335` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:412 |
| `0x3B` | amiga | `LABEL_C360` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:406 |
| `0x3B` | amiga | `LABEL_C391` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:362 |
| `0x3B` | amiga | `LABEL_C3C1` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:210 |
| `0x3B` | amiga | `LABEL_C3F4` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:386 |
| `0x3B` | amiga | `LABEL_C433` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:800 |
| `0x3B` | amiga | `LABEL_C497` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:771 |
| `0x3B` | amiga | `LABEL_C4D5` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:592 |
| `0x3B` | amiga | `LABEL_C51F` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:521 |
| `0x3B` | amiga | `LABEL_C560` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:576 |
| `0x3B` | amiga | `LABEL_C5BA` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:877 |
| `0x3B` | amiga | `LABEL_C726` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:630 |
| `0x3B` | amiga | `LABEL_C732` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:680 |
| `0x3B` | cart | `LABEL_C751` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1242 |
| `0x3B` | cart | `LABEL_C769` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:449 |
| `0x3B` | dos | `LABEL_C770` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1218 |
| `0x3B` | dos | `LABEL_C788` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:430 |
| `0x3B` | cart | `LABEL_C794` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:443 |
| `0x3B` | dos | `LABEL_C7B3` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:424 |
| `0x3B` | cart | `LABEL_C7C5` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:399 |
| `0x3B` | dos | `LABEL_C7E4` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:380 |
| `0x3B` | cart | `LABEL_C7F5` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:236 |
| `0x3B` | dos | `LABEL_C814` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:228 |
| `0x3B` | cart | `LABEL_C82C` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:423 |
| `0x3B` | dos | `LABEL_C847` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:404 |
| `0x3B` | cart | `LABEL_C86B` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:841 |
| `0x3B` | dos | `LABEL_C886` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:822 |
| `0x3B` | cart | `LABEL_C8ED` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:808 |
| `0x3B` | dos | `LABEL_C908` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:789 |
| `0x3B` | cart | `LABEL_C94A` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:629 |
| `0x3B` | dos | `LABEL_C965` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:610 |
| `0x3B` | cart | `LABEL_C994` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:558 |
| `0x3B` | dos | `LABEL_C9AF` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:539 |
| `0x3B` | cart | `LABEL_C9D5` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:613 |
| `0x3B` | dos | `LABEL_C9F0` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:594 |
| `0x3B` | cart | `LABEL_CA2F` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:962 |
| `0x3B` | dos | `LABEL_CA4A` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:941 |
| `0x3B` | cart | `LABEL_CBB1` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:667 |
| `0x3B` | cart | `LABEL_CBBD` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:717 |
| `0x3B` | dos | `LABEL_CBC6` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:648 |
| `0x3B` | dos | `LABEL_CBD2` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:698 |
| `0x3B` | amiga | `LABEL_CC68` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:995 |
| `0x3B` | amiga | `LABEL_CC79` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1026 |
| `0x3B` | amiga | `LABEL_CC9B` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:896 |
| `0x3B` | amiga | `LABEL_CCA8` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:853 |
| `0x3B` | amiga | `LABEL_CCCF` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:319 |
| `0x3B` | amiga | `LABEL_CCE5` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:344 |
| `0x3B` | amiga | `LABEL_CCF7` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1220 |
| `0x3B` | amiga | `LABEL_CD05` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1237 |
| `0x3B` | amiga | `LABEL_CD25` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:275 |
| `0x3B` | amiga | `LABEL_CD3C` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1130 |
| `0x3B` | dos | `LABEL_D114` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1062 |
| `0x3B` | dos | `LABEL_D125` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1093 |
| `0x3B` | cart | `LABEL_D13D` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1084 |
| `0x3B` | dos | `LABEL_D147` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:961 |
| `0x3B` | dos | `LABEL_D154` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:917 |
| `0x3B` | cart | `LABEL_D15E` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1115 |
| `0x3B` | dos | `LABEL_D17B` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:337 |
| `0x3B` | cart | `LABEL_D180` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:982 |
| `0x3B` | dos | `LABEL_D191` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:362 |
| `0x3B` | cart | `LABEL_D197` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:938 |
| `0x3B` | dos | `LABEL_D1A3` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1287 |
| `0x3B` | dos | `LABEL_D1B1` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1304 |
| `0x3B` | cart | `LABEL_D1B5` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1056 |
| `0x3B` | cart | `LABEL_D1CA` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:355 |
| `0x3B` | dos | `LABEL_D1D1` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:293 |
| `0x3B` | dos | `LABEL_D1E8` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1197 |
| `0x3B` | cart | `LABEL_D216` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:381 |
| `0x3B` | cart | `LABEL_D228` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1321 |
| `0x3B` | cart | `LABEL_D236` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1341 |
| `0x3B` | cart | `LABEL_D256` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:310 |
| `0x3B` | cart | `LABEL_D26D` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1221 |
| `0x3C` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__entry.inc:3265 |
| `0x3C` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__entry.inc:3219 |
| `0x3C` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__entry.inc:3230 |
| `0x3C` | amiga | `LABEL_3D25` | src/levels/_unified/caves/amiga__entry.inc:3171 (+3 more) |
| `0x3C` | amiga | `LABEL_3D3B` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR6A_TO_2F.inc:66 (+3 more) |
| `0x3C` | amiga | `LABEL_3D49` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR7C_TO_0001_040.inc:33 (+4 more) |
| `0x3C` | amiga | `LABEL_3D52` | src/levels/_unified/caves/amiga__post_ADD_VAR11_TO_VAR34.inc:95 (+1 more) |
| `0x3C` | amiga | `LABEL_3D5B` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR7F_TO_6.inc:32 (+3 more) |
| `0x3C` | amiga | `LABEL_3D61` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR7F_TO_6.inc:37 (+1 more) |
| `0x3C` | amiga | `LABEL_3D6B` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6D_71_70.inc:247 |
| `0x3C` | amiga | `LABEL_3D88` | src/levels/_unified/caves/amiga__post_INIT_VARS_E6_EA.inc:301 |
| `0x3C` | amiga | `LABEL_3DC8` | src/levels/_unified/caves/amiga__post_SET_VAR22_TO_00B8.inc:8 |
| `0x3C` | amiga | `LABEL_3DE6` | src/levels/_unified/caves/amiga__post_INIT_VARS_EB_EC_ED.inc:54 |
| `0x3C` | amiga | `LABEL_3E04` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR7C_TO_0001_040.inc:47 |
| `0x3C` | amiga | `LABEL_3E21` | src/levels/_unified/caves/amiga__post_SET_VAR13_TO_FFFF.inc:87 |
| `0x3C` | cart | `LABEL_3F46` | src/levels/_unified/caves/cart__entry.inc:3165 (+4 more) |
| `0x3C` | dos | `LABEL_3F5C` | src/levels/_unified/caves/dos__entry.inc:3179 (+4 more) |
| `0x3C` | cart | `LABEL_3F67` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR6A_TO_2F.inc:64 (+3 more) |
| `0x3C` | cart | `LABEL_3F75` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR7C_TO_0001_040.inc:45 (+4 more) |
| `0x3C` | dos | `LABEL_3F7D` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR6A_TO_2F.inc:64 (+3 more) |
| `0x3C` | cart | `LABEL_3F7E` | src/levels/_unified/caves/cart__post_ADD_VAR11_TO_VAR34.inc:97 (+1 more) |
| `0x3C` | cart | `LABEL_3F87` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR7F_TO_6.inc:32 (+3 more) |
| `0x3C` | dos | `LABEL_3F8B` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR7C_TO_0001_040.inc:45 (+4 more) |
| `0x3C` | cart | `LABEL_3F8D` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR7F_TO_6.inc:37 (+1 more) |
| `0x3C` | dos | `LABEL_3F94` | src/levels/_unified/caves/dos__post_ADD_VAR11_TO_VAR34.inc:95 (+1 more) |
| `0x3C` | cart | `LABEL_3F97` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6D_71_70.inc:252 |
| `0x3C` | dos | `LABEL_3F9D` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR7F_TO_6.inc:32 (+3 more) |
| `0x3C` | dos | `LABEL_3FA3` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR7F_TO_6.inc:37 (+1 more) |
| `0x3C` | dos | `LABEL_3FAD` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6D_71_70.inc:247 |
| `0x3C` | cart | `LABEL_3FB4` | src/levels/_unified/caves/cart__post_INIT_VARS_E6_EA.inc:327 |
| `0x3C` | dos | `LABEL_3FCA` | src/levels/_unified/caves/dos__post_INIT_VARS_E6_EA.inc:301 |
| `0x3C` | cart | `LABEL_3FF4` | src/levels/_unified/caves/cart__post_SET_VAR22_TO_00B8.inc:8 |
| `0x3C` | dos | `LABEL_400A` | src/levels/_unified/caves/dos__post_SET_VAR22_TO_00B8.inc:8 |
| `0x3C` | cart | `LABEL_4012` | src/levels/_unified/caves/cart__post_INIT_VARS_EB_EC_ED.inc:67 |
| `0x3C` | dos | `LABEL_4028` | src/levels/_unified/caves/dos__post_INIT_VARS_EB_EC_ED.inc:66 |
| `0x3C` | cart | `LABEL_4030` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR7C_TO_0001_040.inc:59 |
| `0x3C` | dos | `LABEL_4046` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR7C_TO_0001_040.inc:59 |
| `0x3C` | cart | `LABEL_404D` | src/levels/_unified/caves/cart__post_SET_VAR13_TO_FFFF.inc:87 |
| `0x3C` | dos | `LABEL_4063` | src/levels/_unified/caves/dos__post_SET_VAR13_TO_FFFF.inc:87 |
| `0x3C` | amiga | `LABEL_D82A` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:40 |
| `0x3C` | amiga | `LABEL_D839` | src/levels/_unified/caves/amiga__post_INIT_VARS_6C_6D_71_70.inc:179 |
| `0x3C` | dos | `LABEL_DD3E` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:58 |
| `0x3C` | dos | `LABEL_DD4D` | src/levels/_unified/caves/dos__post_INIT_VARS_6C_6D_71_70.inc:179 |
| `0x3C` | cart | `LABEL_DDC7` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:60 |
| `0x3C` | cart | `LABEL_DDD6` | src/levels/_unified/caves/cart__post_INIT_VARS_6C_6D_71_70.inc:179 |
| `0x3E` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:169 (+4 more) |
| `0x3E` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:146 (+3 more) |
| `0x3E` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:164 (+4 more) |
| `0x3E` | amiga | `LABEL_C70E` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:1176 (+2 more) |
| `0x3E` | amiga | `LABEL_C742` | src/levels/_unified/caves/amiga__post_SET_VAR18_TO_0122.inc:35 |
| `0x3E` | cart | `LABEL_CB8C` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:1269 (+2 more) |
| `0x3E` | dos | `LABEL_CBA1` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:1243 (+2 more) |
| `0x3E` | cart | `LABEL_CBCD` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:838 (+1 more) |
| `0x3E` | dos | `LABEL_CBE2` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:819 (+1 more) |
| `0x3E` | amiga | `LABEL_CBF2` | src/levels/_unified/caves/amiga__post_INLINE_SUB_VAR50_BY_14.inc:834 |
| `0x3E` | dos | `LABEL_D098` | src/levels/_unified/caves/dos__post_INLINE_SUB_VAR50_BY_14.inc:898 |
| `0x3E` | cart | `LABEL_D0C1` | src/levels/_unified/caves/cart__post_INLINE_SUB_VAR50_BY_14.inc:918 |
| `0x3F` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/cart__post_INLINE_SET_VAR6A_TO_2F.inc:44 |
| `0x3F` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/amiga__post_INLINE_SET_VAR6A_TO_2F.inc:48 |
| `0x3F` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/caves/dos__post_INLINE_SET_VAR6A_TO_2F.inc:44 |
| `0x3F` | amiga | `LABEL_016F` | src/levels/_unified/caves/amiga__post_ADD_VAR11_TO_VAR34.inc:109 (+7 more) |
| `0x3F` | dos | `LABEL_0184` | src/levels/_unified/caves/dos__post_ADD_VAR11_TO_VAR34.inc:109 (+8 more) |
| `0x3F` | cart | `LABEL_0211` | src/levels/_unified/caves/cart__post_ADD_VAR11_TO_VAR34.inc:112 (+8 more) |
| `0x3F` | amiga | `LABEL_D7A5` | src/levels/_unified/caves/amiga__entry.inc:3190 |
| `0x3F` | dos | `LABEL_DC99` | src/levels/_unified/caves/dos__entry.inc:3198 |
| `0x3F` | cart | `LABEL_DD1F` | src/levels/_unified/caves/cart__entry.inc:3185 |

## CODE_WHEEL

| channel | branch | routine | source |
| ---: | --- | --- | --- |
| `0x0A` | amiga | `LABEL_0AF3` | src/levels/_unified/code_wheel/amiga__post_SUM_HASH_VARS_TO_VAR_37.inc:156 |
| `0x0A` | dos | `LABEL_0D70` | src/levels/_unified/code_wheel/dos__post_SUM_HASH_VARS_TO_VAR_37.inc:185 |
| `0x0E` | amiga | `LABEL_0AE2` | src/levels/_unified/code_wheel/amiga__post_MARK_VAR67_AND_KILL.inc:10 |
| `0x0E` | dos | `LABEL_0D62` | src/levels/_unified/code_wheel/dos__post_MARK_VAR67_AND_KILL.inc:12 |
| `0x14` | amiga | `ENTRY_CALL_INIT_4A` | src/levels/_unified/code_wheel/amiga__entry.inc:120 |
| `0x14` | dos | `ENTRY_CALL_INIT_4A` | src/levels/_unified/code_wheel/dos__entry.inc:147 |
| `0x1E` | dos | `BLITTER_LOOP_WITH_VAR1B_2B` | src/levels/_unified/code_wheel/dos__post_MARK_VAR67_AND_KILL.inc:13 |
| `0x1E` | amiga | `LABEL_0AFB` | src/levels/_unified/code_wheel/amiga__post_PAL_FADE_UP_9_TO_F.inc:77 (+1 more) |
| `0x1E` | amiga | `LABEL_0D99` | src/levels/_unified/code_wheel/amiga__post_MARK_VAR67_AND_KILL.inc:11 |
| `0x1E` | dos | `ZERO_VAR31_LOOP` | src/levels/_unified/code_wheel/dos__post_PAL_FADE_UP_9_TO_F.inc:77 (+1 more) |
| `0x2C` | amiga | `PAL_FADE_4_TO_18_AND_BACK` | src/levels/_unified/code_wheel/amiga__post_INIT_PROGRESS_HASH_VARS.inc:31 |
| `0x2C` | dos | `PAL_FADE_4_TO_18_AND_BACK` | src/levels/_unified/code_wheel/dos__post_INIT_PROGRESS_HASH_VARS.inc:32 |
| `0x2C` | amiga | `PAL_FADE_DOWN_17_TO_11` | src/levels/_unified/code_wheel/amiga__post_INIT_PROGRESS_HASH_VARS.inc:43 |
| `0x2C` | dos | `PAL_FADE_DOWN_17_TO_11` | src/levels/_unified/code_wheel/dos__post_INIT_PROGRESS_HASH_VARS.inc:45 |
| `0x2C` | amiga | `PAL_FADE_DOWN_1A_TO_4` | src/levels/_unified/code_wheel/amiga__post_INIT_PROGRESS_HASH_VARS.inc:25 |
| `0x2C` | dos | `PAL_FADE_DOWN_1A_TO_4` | src/levels/_unified/code_wheel/dos__post_INIT_PROGRESS_HASH_VARS.inc:25 |
| `0x2C` | amiga | `PAL_FADE_DOWN_E_TO_8` | src/levels/_unified/code_wheel/amiga__post_LOAD_RESOURCE_13.inc:3 |
| `0x2C` | dos | `PAL_FADE_DOWN_E_TO_8` | src/levels/_unified/code_wheel/dos__post_LOAD_RESOURCE_13.inc:3 |
| `0x2C` | amiga | `PAL_FADE_UP_9_TO_F` | src/levels/_unified/code_wheel/amiga__post_LOAD_RESOURCE_13.inc:9 |
| `0x2C` | dos | `PAL_FADE_UP_9_TO_F` | src/levels/_unified/code_wheel/dos__post_LOAD_RESOURCE_13.inc:10 |
| `0x32` | amiga | `MARK_VAR67_AND_KILL` | src/levels/_unified/code_wheel/amiga__post_SUM_HASH_VARS_TO_VAR_37.inc:176 |
| `0x32` | dos | `MARK_VAR67_AND_KILL` | src/levels/_unified/code_wheel/dos__post_SUM_HASH_VARS_TO_VAR_37.inc:205 |
| `0x3C` | dos | `BLITTER_LOOP_WITH_VAR1B_2B` | src/levels/_unified/code_wheel/dos__entry.inc:144 |
| `0x3C` | amiga | `LABEL_0D99` | src/levels/_unified/code_wheel/amiga__entry.inc:117 |
| `0x3C` | amiga | `LABEL_0DA8` | src/levels/_unified/code_wheel/amiga__post_PAL_FADE_UP_9_TO_F.inc:76 |
| `0x3C` | amiga | `LABEL_0DB7` | src/levels/_unified/code_wheel/amiga__post_PAL_FADE_UP_9_TO_F.inc:80 |
| `0x3C` | dos | `LABEL_10B2` | src/levels/_unified/code_wheel/dos__post_PAL_FADE_UP_9_TO_F.inc:76 |
| `0x3C` | dos | `LABEL_10C1` | src/levels/_unified/code_wheel/dos__post_PAL_FADE_UP_9_TO_F.inc:80 |
| `0x3F` | amiga | `LABEL_0ACC` | src/levels/_unified/code_wheel/amiga__post_SUM_HASH_VARS_TO_VAR_37.inc:177 |
| `0x3F` | dos | `LABEL_0D46` | src/levels/_unified/code_wheel/dos__post_SUM_HASH_VARS_TO_VAR_37.inc:206 |

## TANK

| channel | branch | routine | source |
| ---: | --- | --- | --- |
| `0x00` | cart | `INIT_VARS_A_B_PAL_1` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:38 |
| `0x00` | amiga | `INIT_VARS_A_B_PAL_1` | src/levels/_unified/tank/amiga__entry.inc:459 (+1 more) |
| `0x00` | dos | `INIT_VARS_A_B_PAL_1` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:36 |
| `0x00` | cart | `LABEL_0004` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:211 |
| `0x00` | dos | `LABEL_0004` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:202 |
| `0x00` | cart | `LABEL_07F6` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:180 |
| `0x00` | dos | `LABEL_0818` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:179 |
| `0x00` | cart | `LABEL_1C05` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:44 |
| `0x00` | dos | `LABEL_1CDC` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:42 |
| `0x01` | amiga | `LABEL_001B` | src/levels/_unified/tank/amiga__post_SUM_HASH_VARS_TO_VAR_64.inc:36 |
| `0x01` | dos | `LABEL_001F` | src/levels/_unified/tank/dos__post_INIT_TANK_DRIVE_VARS.inc:14 |
| `0x01` | cart | `LABEL_0026` | src/levels/_unified/tank/cart__post_INIT_TANK_DRIVE_VARS.inc:12 |
| `0x01` | amiga | `LABEL_083D` | src/levels/_unified/tank/amiga__post_INIT_VARS_50_NEG40_51_32.inc:255 |
| `0x01` | cart | `LABEL_0C43` | src/levels/_unified/tank/cart__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:21 |
| `0x01` | dos | `LABEL_0C44` | src/levels/_unified/tank/dos__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:21 |
| `0x01` | cart | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:23 (+2 more) |
| `0x01` | dos | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:23 (+2 more) |
| `0x01` | amiga | `RESET_PAGES_AND_SETUP_CH_0A__AMIGA__POST_SETUP_TANK_HERO_VARS_PLAY_4SFX` | src/levels/_unified/tank/amiga__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:400 |
| `0x02` | cart | `DRAW_CIN_224_MULTI_FRAME` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:16 (+1 more) |
| `0x02` | amiga | `LABEL_16D4` | src/levels/_unified/tank/amiga__entry.inc:439 (+1 more) |
| `0x02` | dos | `LABEL_1BDA` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:14 (+1 more) |
| `0x02` | cart | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:143 |
| `0x02` | dos | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:143 |
| `0x04` | amiga | `LABEL_10E1` | src/levels/_unified/tank/amiga__entry.inc:440 |
| `0x04` | cart | `LABEL_14F7` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:17 |
| `0x04` | dos | `LABEL_15E3` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:15 |
| `0x06` | cart | `LABEL_0C7B` | src/levels/_unified/tank/cart__post_COPY_VAR62_TO_VAR5F.inc:235 |
| `0x06` | dos | `LABEL_0C7C` | src/levels/_unified/tank/dos__post_COPY_VAR62_TO_VAR5F.inc:235 |
| `0x09` | amiga | `LABEL_021C` | src/levels/_unified/tank/amiga__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:193 |
| `0x09` | dos | `LABEL_022E` | src/levels/_unified/tank/dos__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:193 |
| `0x09` | cart | `LABEL_0258` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:281 |
| `0x09` | amiga | `LABEL_0955` | src/levels/_unified/tank/amiga__entry.inc:433 |
| `0x09` | dos | `LABEL_0E2F` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:8 |
| `0x09` | cart | `LABEL_0E32` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:10 |
| `0x0A` | cart | `DRAW_CIN_260_AT_3_POSITIONS` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:261 |
| `0x0A` | amiga | `HANG_DRAW_CIN_173` | src/levels/_unified/tank/amiga__post_COPY_VAR62_TO_VAR5F.inc:302 |
| `0x0A` | dos | `HANG_DRAW_CIN_225__DOS__POST_COPY_VAR62_TO_VAR5F` | src/levels/_unified/tank/dos__post_COPY_VAR62_TO_VAR5F.inc:405 |
| `0x0A` | amiga | `LABEL_0101` | src/levels/_unified/tank/amiga__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:14 |
| `0x0A` | dos | `LABEL_0113` | src/levels/_unified/tank/dos__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:14 |
| `0x0A` | amiga | `LABEL_0114` | src/levels/_unified/tank/amiga__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:173 |
| `0x0A` | dos | `LABEL_0126` | src/levels/_unified/tank/dos__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:173 |
| `0x0A` | cart | `LABEL_013D` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:101 |
| `0x0A` | amiga | `LABEL_141E` | src/levels/_unified/tank/amiga__entry.inc:441 |
| `0x0A` | cart | `LABEL_1838` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:18 |
| `0x0A` | dos | `LABEL_1924` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:16 |
| `0x0B` | cart | `DRAW_CIN_260_AT_3_POSITIONS` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:282 |
| `0x0B` | amiga | `LABEL_0114` | src/levels/_unified/tank/amiga__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:194 |
| `0x0B` | dos | `LABEL_0126` | src/levels/_unified/tank/dos__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:194 |
| `0x0B` | cart | `WAIT_VAR3E_DEC_AND_RANDOMIZE` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:19 |
| `0x0B` | amiga | `WAIT_VAR3E_DEC_AND_RANDOMIZE` | src/levels/_unified/tank/amiga__entry.inc:442 |
| `0x0B` | dos | `WAIT_VAR3E_DEC_AND_RANDOMIZE` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:17 |
| `0x0E` | cart | `WAIT_VAR4E_PLAY_8C_DRAW_CIN_201` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:20 |
| `0x0E` | amiga | `WAIT_VAR4E_PLAY_8C_DRAW_CIN_201` | src/levels/_unified/tank/amiga__entry.inc:443 |
| `0x0E` | dos | `WAIT_VAR4E_PLAY_8C_DRAW_CIN_201` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:18 |
| `0x0F` | cart | `INIT_VARS_48_49_4A` | src/levels/_unified/tank/cart__post_COPY_VAR62_TO_VAR5F.inc:579 |
| `0x0F` | amiga | `INIT_VARS_48_49_4A` | src/levels/_unified/tank/amiga__post_COPY_VAR62_TO_VAR5F.inc:557 |
| `0x0F` | dos | `INIT_VARS_48_49_4A` | src/levels/_unified/tank/dos__post_COPY_VAR62_TO_VAR5F.inc:661 |
| `0x14` | amiga | `LABEL_03ED` | src/levels/_unified/tank/amiga__entry.inc:430 |
| `0x14` | dos | `LABEL_03FF` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:5 |
| `0x14` | cart | `LABEL_042F` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:6 |
| `0x14` | amiga | `LABEL_14A1` | src/levels/_unified/tank/amiga__post_INIT_VARS_50_NEG40_51_32.inc:273 |
| `0x14` | cart | `LABEL_18BB` | src/levels/_unified/tank/cart__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:42 |
| `0x14` | dos | `LABEL_19A7` | src/levels/_unified/tank/dos__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:42 |
| `0x15` | amiga | `LABEL_166F` | src/levels/_unified/tank/amiga__post_INIT_VARS_50_NEG40_51_32.inc:274 |
| `0x15` | cart | `LABEL_1A89` | src/levels/_unified/tank/cart__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:43 |
| `0x15` | dos | `LABEL_1B75` | src/levels/_unified/tank/dos__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:43 |
| `0x16` | amiga | `LABEL_14B8` | src/levels/_unified/tank/amiga__post_INIT_VARS_50_NEG40_51_32.inc:275 |
| `0x16` | cart | `LABEL_18D2` | src/levels/_unified/tank/cart__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:44 |
| `0x16` | dos | `LABEL_19BE` | src/levels/_unified/tank/dos__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:44 |
| `0x17` | cart | `ALTERNATE_VAR06_VAR04_TIMING` | src/levels/_unified/tank/cart__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:45 |
| `0x17` | amiga | `ALTERNATE_VAR06_VAR04_TIMING` | src/levels/_unified/tank/amiga__post_INIT_VARS_50_NEG40_51_32.inc:276 |
| `0x17` | dos | `ALTERNATE_VAR06_VAR04_TIMING` | src/levels/_unified/tank/dos__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:45 |
| `0x18` | amiga | `LABEL_14E4` | src/levels/_unified/tank/amiga__post_INIT_VARS_50_NEG40_51_32.inc:277 |
| `0x18` | cart | `LABEL_18FE` | src/levels/_unified/tank/cart__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:46 |
| `0x18` | dos | `LABEL_19EA` | src/levels/_unified/tank/dos__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:46 |
| `0x19` | cart | `ANIMATE_VAR06_VAR04_REVERSE` | src/levels/_unified/tank/cart__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:47 |
| `0x19` | amiga | `LABEL_15D4` | src/levels/_unified/tank/amiga__post_INIT_VARS_50_NEG40_51_32.inc:278 |
| `0x19` | dos | `LABEL_1ADA` | src/levels/_unified/tank/dos__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:47 |
| `0x1A` | amiga | `LABEL_1510` | src/levels/_unified/tank/amiga__post_INIT_VARS_50_NEG40_51_32.inc:279 |
| `0x1A` | cart | `LABEL_192A` | src/levels/_unified/tank/cart__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:48 |
| `0x1A` | dos | `LABEL_1A16` | src/levels/_unified/tank/dos__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:48 |
| `0x1C` | amiga | `INIT_VARS_52_17C_53_75_54_40_55_8` | src/levels/_unified/tank/amiga__entry.inc:444 |
| `0x1C` | cart | `LABEL_1282` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:21 |
| `0x1C` | dos | `LABEL_136E` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:19 |
| `0x1F` | amiga | `LABEL_0BE9` | src/levels/_unified/tank/amiga__entry.inc:445 |
| `0x1F` | cart | `LABEL_0FDB` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:22 |
| `0x1F` | dos | `LABEL_10C7` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:20 |
| `0x20` | amiga | `HANG_DRAW_CIN_035` | src/levels/_unified/tank/amiga__entry.inc:466 |
| `0x20` | dos | `HANG_DRAW_CIN_037` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:43 |
| `0x20` | cart | `HANG_DRAW_CIN_223` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:45 |
| `0x20` | amiga | `LABEL_0B7F` | src/levels/_unified/tank/amiga__entry.inc:446 |
| `0x20` | cart | `LABEL_0F71` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:23 |
| `0x20` | dos | `LABEL_105D` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:21 |
| `0x21` | amiga | `LABEL_0D41` | src/levels/_unified/tank/amiga__entry.inc:447 |
| `0x21` | cart | `LABEL_1133` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:24 |
| `0x21` | dos | `LABEL_121F` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:22 |
| `0x22` | cart | `WAIT_VAR56_PLAY_8E_DRAW_CIN_020` | src/levels/_unified/tank/cart__post_COPY_VAR62_TO_VAR5F.inc:493 (+1 more) |
| `0x22` | amiga | `WAIT_VAR56_PLAY_8E_DRAW_CIN_020` | src/levels/_unified/tank/amiga__entry.inc:448 (+1 more) |
| `0x22` | dos | `WAIT_VAR56_PLAY_8E_DRAW_CIN_020` | src/levels/_unified/tank/dos__post_COPY_VAR62_TO_VAR5F.inc:575 (+1 more) |
| `0x23` | cart | `INIT_VAR1_NEG50_PLAY_8B_TWICE` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:26 |
| `0x23` | dos | `INIT_VAR1_NEG50_PLAY_8B_TWICE` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:24 |
| `0x23` | cart | `LABEL_00DD` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:47 |
| `0x23` | amiga | `LABEL_137C` | src/levels/_unified/tank/amiga__entry.inc:449 |
| `0x23` | amiga | `SETUP_TANK_HERO_VARS_PLAY_4SFX` | src/levels/_unified/tank/amiga__entry.inc:468 |
| `0x23` | dos | `SETUP_TANK_HERO_VARS_PLAY_4SFX` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:45 |
| `0x24` | amiga | `LABEL_12A9` | src/levels/_unified/tank/amiga__entry.inc:450 |
| `0x24` | cart | `LABEL_16BF` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:27 |
| `0x24` | dos | `LABEL_17AB` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:25 |
| `0x25` | amiga | `LABEL_0F1F` | src/levels/_unified/tank/amiga__entry.inc:451 |
| `0x25` | cart | `LABEL_1335` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:28 |
| `0x25` | dos | `LABEL_1421` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:26 |
| `0x26` | amiga | `LABEL_0A44` | src/levels/_unified/tank/amiga__post_COPY_VAR62_TO_VAR5F.inc:543 |
| `0x26` | cart | `LABEL_0E32` | src/levels/_unified/tank/cart__post_COPY_VAR62_TO_VAR5F.inc:565 |
| `0x26` | dos | `LABEL_0F1E` | src/levels/_unified/tank/dos__post_COPY_VAR62_TO_VAR5F.inc:647 |
| `0x28` | amiga | `HANG_DRAW_CIN_034` | src/levels/_unified/tank/amiga__entry.inc:467 |
| `0x28` | dos | `HANG_DRAW_CIN_036` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:44 |
| `0x28` | cart | `HANG_DRAW_CIN_222__CART__POST_INLINE_SET_VAR6D_TO_0` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:46 |
| `0x28` | amiga | `LABEL_050E` | src/levels/_unified/tank/amiga__entry.inc:452 |
| `0x28` | cart | `LABEL_085A` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:29 |
| `0x28` | dos | `LABEL_0866` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:27 |
| `0x2A` | cart | `INLINE_SET_VAR6B_TO_50` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:30 |
| `0x2A` | dos | `INLINE_SET_VAR6B_TO_50` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:28 |
| `0x2F` | cart | `LABEL_071B` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:31 |
| `0x2F` | dos | `LABEL_0743` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:29 |
| `0x2F` | cart | `LABEL_075A` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:19 |
| `0x2F` | dos | `LABEL_0782` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:19 |
| `0x2F` | cart | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:258 (+1 more) |
| `0x30` | cart | `WAIT_VAR45_PLAY_8C_DRAW_CIN_011` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:32 |
| `0x30` | amiga | `WAIT_VAR45_PLAY_8C_DRAW_CIN_011` | src/levels/_unified/tank/amiga__entry.inc:453 |
| `0x30` | dos | `WAIT_VAR45_PLAY_8C_DRAW_CIN_011` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:30 |
| `0x31` | cart | `WAIT_VAR46_PLAY_8E_DRAW_CIN_056` | src/levels/_unified/tank/cart__post_COPY_VAR62_TO_VAR5F.inc:492 (+1 more) |
| `0x31` | amiga | `WAIT_VAR46_PLAY_8E_DRAW_CIN_056` | src/levels/_unified/tank/amiga__entry.inc:454 (+1 more) |
| `0x31` | dos | `WAIT_VAR46_PLAY_8E_DRAW_CIN_056` | src/levels/_unified/tank/dos__post_COPY_VAR62_TO_VAR5F.inc:574 (+1 more) |
| `0x34` | cart | `LABEL_04F8` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6B_TO_50.inc:11 |
| `0x34` | dos | `LABEL_0520` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6B_TO_50.inc:11 |
| `0x34` | cart | `LABEL_05F6` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6B_TO_50.inc:52 |
| `0x34` | dos | `LABEL_061E` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6B_TO_50.inc:52 |
| `0x34` | cart | `LABEL_0638` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6B_TO_50.inc:41 |
| `0x34` | cart | `LABEL_064D` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6B_TO_50.inc:39 |
| `0x34` | dos | `LABEL_0660` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6B_TO_50.inc:41 |
| `0x34` | dos | `LABEL_0675` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6B_TO_50.inc:39 |
| `0x34` | cart | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:2 (+1 more) |
| `0x34` | dos | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:2 (+1 more) |
| `0x35` | cart | `INLINE_SET_VAR66_TO_32` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:34 |
| `0x35` | amiga | `INLINE_SET_VAR66_TO_32` | src/levels/_unified/tank/amiga__entry.inc:455 |
| `0x35` | dos | `INLINE_SET_VAR66_TO_32` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR6D_TO_0.inc:32 |
| `0x35` | cart | `LABEL_066A` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:112 |
| `0x35` | dos | `LABEL_0692` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:112 |
| `0x35` | cart | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:223 |
| `0x35` | dos | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:214 |
| `0x35` | amiga | `RESET_PAGES_AND_SETUP_CH_0A__AMIGA__POST_SETUP_TANK_HERO_VARS_PLAY_4SFX` | src/levels/_unified/tank/amiga__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:399 |
| `0x37` | dos | `HANG_DRAW_CIN_119` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:111 |
| `0x37` | cart | `HANG_DRAW_CIN_143` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:111 |
| `0x37` | amiga | `LABEL_0328` | src/levels/_unified/tank/amiga__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:227 |
| `0x37` | dos | `LABEL_033A` | src/levels/_unified/tank/dos__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:227 |
| `0x37` | cart | `LABEL_036A` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:315 |
| `0x37` | cart | `LABEL_043E` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:299 |
| `0x37` | amiga | `LABEL_0454` | src/levels/_unified/tank/amiga__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:211 |
| `0x37` | dos | `LABEL_0466` | src/levels/_unified/tank/dos__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:211 |
| `0x37` | amiga | `LABEL_0E21` | src/levels/_unified/tank/amiga__entry.inc:456 (+1 more) |
| `0x37` | amiga | `LABEL_0E34` | src/levels/_unified/tank/amiga__post_COPY_VAR62_TO_VAR5F.inc:351 |
| `0x37` | cart | `LABEL_1237` | src/levels/_unified/tank/cart__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:72 (+1 more) |
| `0x37` | dos | `LABEL_1323` | src/levels/_unified/tank/dos__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:72 (+1 more) |
| `0x37` | dos | `LABEL_1336` | src/levels/_unified/tank/dos__post_COPY_VAR62_TO_VAR5F.inc:454 |
| `0x37` | cart | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:306 |
| `0x37` | dos | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/dos__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:218 |
| `0x37` | amiga | `RESET_PAGES_AND_SETUP_CH_0A__AMIGA__POST_SETUP_TANK_HERO_VARS_PLAY_4SFX` | src/levels/_unified/tank/amiga__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:218 |
| `0x38` | amiga | `LABEL_0C53` | src/levels/_unified/tank/amiga__post_INLINE_SET_VAR66_TO_32.inc:76 |
| `0x38` | cart | `LABEL_1045` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR66_TO_32.inc:76 |
| `0x38` | dos | `LABEL_1131` | src/levels/_unified/tank/dos__post_INLINE_SET_VAR66_TO_32.inc:76 |
| `0x39` | dos | `HANG_DRAW_CIN_029` | src/levels/_unified/tank/dos__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:20 |
| `0x39` | cart | `HANG_DRAW_CIN_089` | src/levels/_unified/tank/cart__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:20 |
| `0x39` | amiga | `HANG_DRAW_CIN_123` | src/levels/_unified/tank/amiga__post_INIT_VARS_50_NEG40_51_32.inc:254 |
| `0x39` | cart | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:21 (+1 more) |
| `0x39` | dos | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:21 (+1 more) |
| `0x3B` | amiga | `HANG_DRAW_CIN_222__AMIGA__POST_SETUP_TANK_HERO_VARS_PLAY_4SFX` | src/levels/_unified/tank/amiga__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:183 (+1 more) |
| `0x3B` | cart | `HANG_DRAW_CIN_259` | src/levels/_unified/tank/cart__post_INLINE_SET_VAR6D_TO_0.inc:271 (+1 more) |
| `0x3B` | dos | `HANG_DRAW_CIN_274` | src/levels/_unified/tank/dos__post_SETUP_TANK_HERO_VARS_PLAY_4SFX.inc:183 (+2 more) |
| `0x3B` | cart | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:22 (+1 more) |
| `0x3B` | dos | `RESET_PAGES_AND_SETUP_CH_0A` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:22 (+1 more) |
| `0x3B` | cart | `WAIT_LOOP_VAR_5C` | src/levels/_unified/tank/cart__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:22 |
| `0x3B` | amiga | `WAIT_LOOP_VAR_5C` | src/levels/_unified/tank/amiga__post_INIT_VARS_50_NEG40_51_32.inc:256 |
| `0x3B` | dos | `WAIT_LOOP_VAR_5C` | src/levels/_unified/tank/dos__post_INIT_VAR1_NEG50_PLAY_8B_TWICE.inc:22 |
| `0x3C` | cart | `BLITTER_LOOP_COPY_PAGE_03` | src/levels/_unified/tank/cart__post_INIT_TANK_DRIVE_VARS.inc:13 (+2 more) |
| `0x3C` | amiga | `BLITTER_LOOP_COPY_PAGE_03` | src/levels/_unified/tank/amiga__entry.inc:438 (+2 more) |
| `0x3C` | dos | `BLITTER_LOOP_COPY_PAGE_03` | src/levels/_unified/tank/dos__post_INIT_TANK_DRIVE_VARS.inc:15 (+2 more) |
| `0x3C` | cart | `HANG_BLITTING_PAGE_FF` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:189 (+3 more) |
| `0x3C` | amiga | `HANG_BLITTING_PAGE_FF` | src/levels/_unified/tank/amiga__entry.inc:429 (+2 more) |
| `0x3C` | dos | `HANG_BLITTING_PAGE_FF` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:187 (+4 more) |
| `0x3C` | cart | `PALETTE_FLASH_1F_TO_01` | src/levels/_unified/tank/cart__post_COPY_VAR62_TO_VAR5F.inc:441 (+3 more) |
| `0x3C` | amiga | `PALETTE_FLASH_1F_TO_01` | src/levels/_unified/tank/amiga__post_COPY_VAR62_TO_VAR5F.inc:419 |
| `0x3C` | dos | `PALETTE_FLASH_1F_TO_01` | src/levels/_unified/tank/dos__post_COPY_VAR62_TO_VAR5F.inc:523 (+3 more) |
| `0x3F` | cart | `LABEL_07DD` | src/levels/_unified/tank/cart__post_INCR_VAR_6C_BY_10_3X.inc:171 |
| `0x3F` | dos | `LABEL_07FF` | src/levels/_unified/tank/dos__post_INCR_VAR_6C_BY_10_3X.inc:170 |

## PASSCODE

| channel | branch | routine | source |
| ---: | --- | --- | --- |
| `0x14` | amiga | `SETUP_PASSCODE_SCREEN__AMIGA__ENTRY` | src/levels/_unified/passcode/amiga__entry.inc:122 |
| `0x14` | cart | `SETUP_PASSCODE_SCREEN__CART__ENTRY` | src/levels/_unified/passcode/cart__entry.inc:71 |
| `0x14` | dos | `SETUP_PASSCODE_SCREEN__DOS__ENTRY` | src/levels/_unified/passcode/dos__entry.inc:125 |
| `0x3C` | amiga | `AMIGA_PASSCODE_BANK_INIT` | src/levels/_unified/passcode/amiga__entry.inc:254 |
| `0x3C` | cart | `BLITTER_LOOP_COPY_PAGE_00` | src/levels/_unified/passcode/cart__entry.inc:65 |
| `0x3C` | amiga | `BLITTER_LOOP_COPY_PAGE_00` | src/levels/_unified/passcode/amiga__entry.inc:116 |
| `0x3C` | dos | `BLITTER_LOOP_COPY_PAGE_00` | src/levels/_unified/passcode/dos__entry.inc:118 |
| `0x3C` | cart | `JUNK__001E` | src/levels/_unified/passcode/cart__entry.inc:223 |
| `0x3C` | dos | `KILL_CHAN_AT_0021` | src/levels/_unified/passcode/dos__entry.inc:274 |

## CAPSULE

| channel | branch | routine | source |
| ---: | --- | --- | --- |
| `0x00` | cart | `LABEL_0000` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR03_TO_14.inc:53 |
| `0x00` | amiga | `LABEL_0000` | src/levels/_unified/capsule/amiga__post_BREAK_5X_THEN_INIT_VAR03_14.inc:35 |
| `0x00` | dos | `LABEL_0000` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR03_TO_14.inc:39 |
| `0x00` | amiga | `LABEL_0349` | src/levels/_unified/capsule/amiga__post_BREAK_5X_THEN_INIT_VAR03_14.inc:12 |
| `0x00` | dos | `LABEL_13D6` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR03_TO_14.inc:9 |
| `0x00` | cart | `LABEL_14C7` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR03_TO_14.inc:10 |
| `0x01` | cart | `INLINE_SET_VARE6_TO_F` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:464 (+2 more) |
| `0x01` | dos | `INLINE_SET_VARE6_TO_F` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:458 (+2 more) |
| `0x01` | cart | `INLINE_SET_VARED_TO_6` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:120 |
| `0x01` | amiga | `INLINE_SET_VARED_TO_6` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:56 |
| `0x01` | dos | `INLINE_SET_VARED_TO_6` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:113 |
| `0x01` | amiga | `LABEL_05C5` | src/levels/_unified/capsule/amiga__post_BREAK_5X_THEN_INIT_VAR03_14.inc:167 |
| `0x01` | amiga | `LABEL_0636` | src/levels/_unified/capsule/amiga__post_BREAK_5X_THEN_INIT_VAR03_14.inc:188 |
| `0x01` | dos | `LABEL_07A6` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:785 |
| `0x01` | cart | `LABEL_085C` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:801 |
| `0x01` | dos | `LABEL_1599` | src/levels/_unified/capsule/dos__post_DRAW_TEXT_0174_AT_26_180.inc:89 |
| `0x01` | dos | `LABEL_15E4` | src/levels/_unified/capsule/dos__post_DRAW_TEXT_0174_AT_26_180.inc:110 |
| `0x01` | cart | `LABEL_16A7` | src/levels/_unified/capsule/cart__post_DRAW_TEXT_0174_AT_26_180.inc:89 |
| `0x01` | cart | `LABEL_16F2` | src/levels/_unified/capsule/cart__post_DRAW_TEXT_0174_AT_26_180.inc:110 |
| `0x01` | amiga | `LABEL_1FD3` | src/levels/_unified/capsule/amiga__post_SET_VARB3_TO_0000.inc:447 |
| `0x01` | amiga | `LABEL_1FFB` | src/levels/_unified/capsule/amiga__post_SET_VARB3_TO_0000.inc:444 |
| `0x01` | dos | `LABEL_289B` | src/levels/_unified/capsule/dos__post_INIT_VARS_29_2F.inc:4 (+1 more) |
| `0x01` | dos | `LABEL_28C1` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:710 |
| `0x01` | cart | `LABEL_2A12` | src/levels/_unified/capsule/cart__post_INIT_VARS_29_2F.inc:4 (+1 more) |
| `0x01` | amiga | `LABEL_2A16` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARE8_TO_F.inc:94 (+2 more) |
| `0x01` | cart | `LABEL_2A38` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:723 |
| `0x01` | dos | `LABEL_2F13` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:933 |
| `0x01` | cart | `LABEL_3090` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:969 |
| `0x01` | cart | `LABEL_3BCA` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_14.inc:17 |
| `0x01` | dos | `LABEL_3C02` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_14.inc:17 |
| `0x01` | cart | `LABEL_3F38` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:153 (+6 more) |
| `0x01` | dos | `LABEL_3F6C` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:146 (+6 more) |
| `0x01` | cart | `LABEL_3F86` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:233 (+2 more) |
| `0x01` | dos | `LABEL_3FBA` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:230 (+2 more) |
| `0x01` | dos | `LABEL_9BCA` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:666 |
| `0x01` | cart | `LABEL_9C3B` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:679 |
| `0x02` | cart | `INLINE_SET_VARE6_TO_14` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:997 |
| `0x02` | dos | `INLINE_SET_VARE6_TO_14` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:961 |
| `0x02` | cart | `INLINE_SET_VARE6_TO_4` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:152 (+1 more) |
| `0x02` | amiga | `INLINE_SET_VARE6_TO_4` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:88 |
| `0x02` | dos | `INLINE_SET_VARE6_TO_4` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:145 (+1 more) |
| `0x02` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:592 (+2 more) |
| `0x02` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_SET_VAR13_TO_FFFF.inc:82 |
| `0x02` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:585 (+2 more) |
| `0x02` | dos | `LABEL_0683` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:934 |
| `0x02` | cart | `LABEL_0739` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:970 |
| `0x02` | dos | `LABEL_0C0E` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:563 (+1 more) |
| `0x02` | cart | `LABEL_0CCD` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:569 (+1 more) |
| `0x02` | amiga | `LABEL_0D0E` | src/levels/_unified/capsule/amiga__post_SET_VAR01_TO_6E_KILL_CHANNEL.inc:73 |
| `0x02` | amiga | `LABEL_0E13` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:41 |
| `0x02` | dos | `LABEL_1CBC` | src/levels/_unified/capsule/dos__post_SET_VAR01_TO_6E_KILL_CHANNEL.inc:73 |
| `0x02` | dos | `LABEL_1DC1` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:41 |
| `0x02` | cart | `LABEL_1DD0` | src/levels/_unified/capsule/cart__post_SET_VAR01_TO_6E_KILL_CHANNEL.inc:74 |
| `0x02` | cart | `LABEL_1ED5` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:41 |
| `0x03` | cart | `INIT_VARS_E6_E7` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:992 |
| `0x03` | dos | `INIT_VARS_E6_E7` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:956 |
| `0x03` | cart | `INLINE_SET_VARE8_TO_F` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:121 |
| `0x03` | amiga | `INLINE_SET_VARE8_TO_F` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:57 |
| `0x03` | dos | `INLINE_SET_VARE8_TO_F` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:114 |
| `0x03` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAREC_TO_AF.inc:31 |
| `0x03` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAREC_TO_AF.inc:31 |
| `0x03` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAREC_TO_AF.inc:31 |
| `0x03` | dos | `LABEL_0429` | src/levels/_unified/capsule/dos__post_INIT_VARS_E6_07_08.inc:26 |
| `0x03` | cart | `LABEL_0496` | src/levels/_unified/capsule/cart__post_INIT_VARS_E6_07_08.inc:26 |
| `0x03` | dos | `LABEL_04D8` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:621 (+1 more) |
| `0x03` | cart | `LABEL_0586` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:628 (+1 more) |
| `0x03` | dos | `LABEL_0C7B` | src/levels/_unified/capsule/dos__post_INIT_VARS_03_01.inc:325 |
| `0x03` | cart | `LABEL_0D3A` | src/levels/_unified/capsule/cart__post_INIT_VARS_03_01.inc:320 (+1 more) |
| `0x03` | amiga | `LABEL_0E3D` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:47 |
| `0x03` | dos | `LABEL_1DEB` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:47 |
| `0x03` | cart | `LABEL_1EFF` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:47 |
| `0x03` | cart | `LABEL_3D38` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:463 (+2 more) |
| `0x03` | dos | `LABEL_3D70` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:457 (+2 more) |
| `0x03` | cart | `PLAY_FX_30_CH2_LOUD_SET_VARED_5` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:999 |
| `0x03` | dos | `PLAY_FX_30_CH2_LOUD_SET_VARED_5` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:963 |
| `0x04` | dos | `HANG_DRAW_CIN_287` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:332 (+1 more) |
| `0x04` | cart | `HANG_DRAW_CIN_288` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:338 (+1 more) |
| `0x04` | dos | `HANG_DRAW_CIN_518` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:404 |
| `0x04` | cart | `HANG_DRAW_CIN_521` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:410 |
| `0x04` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INIT_VAR6F_TO_A_PAUSE_3.inc:114 (+3 more) |
| `0x04` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INIT_VAR6F_TO_A_PAUSE_3.inc:114 (+3 more) |
| `0x04` | amiga | `LABEL_068B` | src/levels/_unified/capsule/amiga__post_BREAK_5X_THEN_INIT_VAR03_14.inc:265 |
| `0x04` | dos | `LABEL_0A97` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:957 |
| `0x04` | amiga | `LABEL_0AC4` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:306 (+3 more) |
| `0x04` | cart | `LABEL_0B4D` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:993 |
| `0x04` | amiga | `LABEL_0DED` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_5.inc:15 |
| `0x04` | dos | `LABEL_0FAA` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:663 |
| `0x04` | cart | `LABEL_1087` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:673 |
| `0x04` | amiga | `LABEL_12E0` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:58 |
| `0x04` | dos | `LABEL_1639` | src/levels/_unified/capsule/dos__post_DRAW_TEXT_0174_AT_26_180.inc:172 |
| `0x04` | cart | `LABEL_1747` | src/levels/_unified/capsule/cart__post_DRAW_TEXT_0174_AT_26_180.inc:172 |
| `0x04` | dos | `LABEL_1A72` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:465 (+3 more) |
| `0x04` | cart | `LABEL_1B80` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:471 (+3 more) |
| `0x04` | dos | `LABEL_1D9B` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_5.inc:15 |
| `0x04` | cart | `LABEL_1EAF` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_5.inc:15 |
| `0x04` | dos | `LABEL_2467` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:115 |
| `0x04` | cart | `LABEL_25BB` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:122 |
| `0x04` | amiga | `LABEL_28EF` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:260 |
| `0x04` | cart | `LABEL_3E09` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_F.inc:245 |
| `0x04` | dos | `LABEL_3E3D` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_F.inc:244 |
| `0x04` | amiga | `LABEL_81EF` | src/levels/_unified/capsule/amiga__post_SET_VAR13_TO_FFFF.inc:93 |
| `0x04` | dos | `LABEL_B178` | src/levels/_unified/capsule/dos__post_SET_VAR13_TO_FFFF.inc:94 |
| `0x04` | cart | `LABEL_B259` | src/levels/_unified/capsule/cart__post_SET_VAR13_TO_FFFF.inc:94 |
| `0x04` | cart | `PLAY_FX_30_CH2_VOL_C_SET_VARED_A` | src/levels/_unified/capsule/cart__post_INIT_VARS_63_01_02_03.inc:53 |
| `0x04` | dos | `PLAY_FX_30_CH2_VOL_C_SET_VARED_A` | src/levels/_unified/capsule/dos__post_INIT_VARS_63_01_02_03.inc:53 |
| `0x04` | cart | `PLAY_FX_52_CH3_SET_VARED_A` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:1000 |
| `0x04` | dos | `PLAY_FX_52_CH3_SET_VARED_A` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:964 |
| `0x05` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_F.inc:238 |
| `0x05` | dos | `LABEL_050D` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:379 |
| `0x05` | cart | `LABEL_05BB` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:385 |
| `0x05` | amiga | `LABEL_0771` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAREC_TO_AF.inc:6 (+2 more) |
| `0x05` | amiga | `LABEL_1301` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARE8_TO_F.inc:37 |
| `0x05` | dos | `LABEL_171F` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAREC_TO_AF.inc:6 (+2 more) |
| `0x05` | cart | `LABEL_182D` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAREC_TO_AF.inc:6 (+2 more) |
| `0x05` | dos | `LABEL_2488` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE8_TO_F.inc:37 |
| `0x05` | cart | `LABEL_25DC` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:216 (+1 more) |
| `0x05` | amiga | `LABEL_2856` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_5.inc:16 |
| `0x05` | cart | `LABEL_3D17` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_5.inc:16 |
| `0x05` | dos | `LABEL_3D4F` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_5.inc:16 |
| `0x05` | amiga | `LABEL_8353` | src/levels/_unified/capsule/amiga__post_SET_VAR13_TO_FFFF.inc:100 |
| `0x05` | dos | `LABEL_B178` | src/levels/_unified/capsule/dos__post_SET_VAR13_TO_FFFF.inc:101 |
| `0x05` | cart | `LABEL_B259` | src/levels/_unified/capsule/cart__post_SET_VAR13_TO_FFFF.inc:101 |
| `0x05` | cart | `PLAY_FX_56_CH3_SET_VAREE_F` | src/levels/_unified/capsule/cart__post_INIT_VARS_63_01_02_03.inc:54 |
| `0x05` | dos | `PLAY_FX_56_CH3_SET_VAREE_F` | src/levels/_unified/capsule/dos__post_INIT_VARS_63_01_02_03.inc:54 |
| `0x06` | dos | `LABEL_053B` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:380 |
| `0x06` | cart | `LABEL_05E9` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:386 |
| `0x06` | amiga | `LABEL_078F` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAREC_TO_AF.inc:10 (+1 more) |
| `0x06` | amiga | `LABEL_0EB3` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_5.inc:102 |
| `0x06` | dos | `LABEL_173D` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAREC_TO_AF.inc:10 (+1 more) |
| `0x06` | cart | `LABEL_184B` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAREC_TO_AF.inc:10 (+1 more) |
| `0x06` | dos | `LABEL_1E7E` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_5.inc:102 |
| `0x06` | cart | `LABEL_1F92` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_5.inc:102 |
| `0x06` | cart | `TWEEN_VARE8_DOWN_8_STEPS` | src/levels/_unified/capsule/cart__post_SET_VAR01_TO_6E_KILL_CHANNEL.inc:49 |
| `0x06` | amiga | `TWEEN_VARE8_DOWN_8_STEPS` | src/levels/_unified/capsule/amiga__post_SET_VAR01_TO_6E_KILL_CHANNEL.inc:48 |
| `0x06` | dos | `TWEEN_VARE8_DOWN_8_STEPS` | src/levels/_unified/capsule/dos__post_SET_VAR01_TO_6E_KILL_CHANNEL.inc:48 |
| `0x07` | cart | `INLINE_SET_VAREC_TO_AF` | src/levels/_unified/capsule/cart__post_DRAW_TEXT_0174_AT_26_180.inc:219 |
| `0x07` | amiga | `INLINE_SET_VAREC_TO_AF` | src/levels/_unified/capsule/amiga__post_BREAK_5X_THEN_INIT_VAR03_14.inc:312 |
| `0x07` | dos | `INLINE_SET_VAREC_TO_AF` | src/levels/_unified/capsule/dos__post_DRAW_TEXT_0174_AT_26_180.inc:219 |
| `0x07` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_DRAW_TEXT_0174_AT_26_180.inc:183 (+1 more) |
| `0x07` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_BREAK_5X_THEN_INIT_VAR03_14.inc:276 (+1 more) |
| `0x07` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_DRAW_TEXT_0174_AT_26_180.inc:183 (+1 more) |
| `0x07` | amiga | `LABEL_130E` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:108 |
| `0x07` | dos | `LABEL_2500` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:165 |
| `0x07` | cart | `LABEL_2671` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:175 |
| `0x08` | cart | `INCREMENT_VAR31` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:1038 |
| `0x08` | amiga | `INCREMENT_VAR31` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:186 |
| `0x08` | dos | `INCREMENT_VAR31` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:1001 |
| `0x0F` | amiga | `HANG_DRAW_CIN_083` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARE8_TO_F.inc:157 |
| `0x0F` | dos | `HANG_DRAW_CIN_429` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE8_TO_F.inc:197 |
| `0x0F` | cart | `HANG_DRAW_CIN_433__CART__POST_INLINE_SET_VARE8_TO_F` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE8_TO_F.inc:205 |
| `0x0F` | cart | `INIT_VAR6F_TO_A_PAUSE_3` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:438 |
| `0x0F` | dos | `INIT_VAR6F_TO_A_PAUSE_3` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:545 |
| `0x0F` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:150 (+1 more) |
| `0x0F` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:86 |
| `0x0F` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:143 (+1 more) |
| `0x0F` | amiga | `LABEL_8988` | src/levels/_unified/capsule/amiga__post_SET_VAR04_TO_0024.inc:185 |
| `0x10` | amiga | `LABEL_2E58` | src/levels/_unified/capsule/amiga__post_INIT_VARS_A1_A4_A7.inc:32 |
| `0x10` | cart | `LABEL_43FA` | src/levels/_unified/capsule/cart__post_INIT_VARS_A1_A4_A7.inc:43 |
| `0x10` | dos | `LABEL_441E` | src/levels/_unified/capsule/dos__post_INIT_VARS_A1_A4_A7.inc:43 |
| `0x13` | cart | `RAMP_VAR1_PLUS_C_9_5_3_BREAKS` | src/levels/_unified/capsule/cart__post_INIT_VARS_03_01.inc:437 |
| `0x13` | amiga | `RAMP_VAR1_PLUS_C_9_5_3_BREAKS` | src/levels/_unified/capsule/amiga__entry.inc:1643 |
| `0x13` | dos | `RAMP_VAR1_PLUS_C_9_5_3_BREAKS` | src/levels/_unified/capsule/dos__post_INIT_VARS_03_01.inc:440 |
| `0x14` | cart | `DRAW_CV352_STEP_RIGHT3` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_1.inc:6 |
| `0x14` | amiga | `DRAW_CV352_STEP_RIGHT3` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_1.inc:6 |
| `0x14` | dos | `DRAW_CV352_STEP_RIGHT3` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_1.inc:6 |
| `0x14` | cart | `INIT_VARS_03_01` | src/levels/_unified/capsule/cart__post_INIT_VARS_E6_E7.inc:251 |
| `0x14` | dos | `INIT_VARS_03_01` | src/levels/_unified/capsule/dos__post_INIT_VARS_E6_E7.inc:242 |
| `0x14` | cart | `INIT_VARS_03_01_02` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR29_TO_8.inc:113 |
| `0x14` | dos | `INIT_VARS_03_01_02` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR29_TO_8.inc:113 |
| `0x14` | cart | `INIT_VARS_63_01_02_03` | src/levels/_unified/capsule/cart__post_INIT_VARS_0E_29.inc:179 |
| `0x14` | dos | `INIT_VARS_63_01_02_03` | src/levels/_unified/capsule/dos__post_INIT_VARS_0E_29.inc:154 |
| `0x14` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR29_TO_8.inc:95 (+1 more) |
| `0x14` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__entry.inc:1553 (+1 more) |
| `0x14` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR29_TO_8.inc:95 (+1 more) |
| `0x14` | amiga | `LABEL_08D9` | src/levels/_unified/capsule/amiga__post_INIT_VARS_07_08_29.inc:23 |
| `0x14` | amiga | `LABEL_13B1` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:24 |
| `0x14` | dos | `LABEL_1887` | src/levels/_unified/capsule/dos__post_INIT_VARS_07_08_29.inc:23 |
| `0x14` | cart | `LABEL_1995` | src/levels/_unified/capsule/cart__post_INIT_VARS_07_08_29.inc:23 |
| `0x14` | dos | `LABEL_25A7` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:24 |
| `0x14` | cart | `LABEL_2718` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:24 |
| `0x14` | dos | `LABEL_2804` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE8_TO_F.inc:368 |
| `0x14` | cart | `LABEL_297B` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE8_TO_F.inc:377 |
| `0x14` | amiga | `LABEL_2A64` | src/levels/_unified/capsule/amiga__post_PLAY_SFX_005C_CH00.inc:17 |
| `0x14` | amiga | `LABEL_2A8B` | src/levels/_unified/capsule/amiga__post_PLAY_SFX_005C_CH00.inc:19 |
| `0x14` | amiga | `LABEL_2B2F` | src/levels/_unified/capsule/amiga__post_PLAY_SFX_005C_CH00.inc:11 |
| `0x14` | amiga | `LABEL_2B4A` | src/levels/_unified/capsule/amiga__post_PLAY_SFX_005C_CH00.inc:13 |
| `0x14` | dos | `LABEL_393D` | src/levels/_unified/capsule/dos__post_INIT_VAR6F_TO_A_PAUSE_3.inc:67 |
| `0x14` | cart | `LABEL_39A6` | src/levels/_unified/capsule/cart__post_INIT_VAR6F_TO_A_PAUSE_3.inc:67 |
| `0x14` | cart | `LABEL_3FCE` | src/levels/_unified/capsule/cart__post_PLAY_SFX_005C_CH00.inc:18 |
| `0x14` | cart | `LABEL_3FF5` | src/levels/_unified/capsule/cart__post_PLAY_SFX_005C_CH00.inc:20 |
| `0x14` | dos | `LABEL_4002` | src/levels/_unified/capsule/dos__post_PLAY_SFX_005C_CH00.inc:17 |
| `0x14` | dos | `LABEL_4029` | src/levels/_unified/capsule/dos__post_PLAY_SFX_005C_CH00.inc:19 |
| `0x14` | cart | `LABEL_4099` | src/levels/_unified/capsule/cart__post_PLAY_SFX_005C_CH00.inc:12 |
| `0x14` | cart | `LABEL_40B4` | src/levels/_unified/capsule/cart__post_PLAY_SFX_005C_CH00.inc:14 |
| `0x14` | dos | `LABEL_40CD` | src/levels/_unified/capsule/dos__post_PLAY_SFX_005C_CH00.inc:11 |
| `0x14` | dos | `LABEL_40E8` | src/levels/_unified/capsule/dos__post_PLAY_SFX_005C_CH00.inc:13 |
| `0x14` | amiga | `LABEL_5913` | src/levels/_unified/capsule/amiga__post_COPY_VAR40_TO_VAR22.inc:41 |
| `0x14` | amiga | `LABEL_59BA` | src/levels/_unified/capsule/amiga__post_ADD_VAR11_TO_VAR34.inc:44 (+2 more) |
| `0x14` | amiga | `LABEL_5AA2` | src/levels/_unified/capsule/amiga__post_COPY_VAR40_TO_VAR22.inc:60 |
| `0x14` | dos | `LABEL_70E2` | src/levels/_unified/capsule/dos__post_COPY_VAR40_TO_VAR22.inc:58 (+1 more) |
| `0x14` | cart | `LABEL_713A` | src/levels/_unified/capsule/cart__post_COPY_VAR40_TO_VAR22.inc:58 (+1 more) |
| `0x14` | dos | `LABEL_7187` | src/levels/_unified/capsule/dos__post_ADD_VAR11_TO_VAR34.inc:44 (+2 more) |
| `0x14` | cart | `LABEL_71F0` | src/levels/_unified/capsule/cart__post_ADD_VAR11_TO_VAR34.inc:44 (+2 more) |
| `0x14` | dos | `LABEL_728A` | src/levels/_unified/capsule/dos__post_COPY_VAR40_TO_VAR22.inc:77 |
| `0x14` | cart | `LABEL_72F3` | src/levels/_unified/capsule/cart__post_COPY_VAR40_TO_VAR22.inc:77 |
| `0x14` | amiga | `LABEL_7E32` | src/levels/_unified/capsule/amiga__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:14 |
| `0x14` | amiga | `LABEL_7E4F` | src/levels/_unified/capsule/amiga__post_RESET_HERO_ACTION_KEEP_POS_4LSB.inc:8 |
| `0x14` | amiga | `LABEL_87CF` | src/levels/_unified/capsule/amiga__post_SET_VARB3_TO_0000.inc:481 |
| `0x14` | amiga | `LABEL_9028` | src/levels/_unified/capsule/amiga__post_SET_VAR04_TO_0024.inc:268 (+1 more) |
| `0x14` | amiga | `LABEL_9158` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_1.inc:4 (+1 more) |
| `0x14` | amiga | `LABEL_9294` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_2.inc:46 |
| `0x14` | amiga | `LABEL_92B8` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_2.inc:44 |
| `0x14` | amiga | `LABEL_937E` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_5.inc:6 |
| `0x14` | amiga | `LABEL_939E` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_5.inc:4 |
| `0x14` | amiga | `LABEL_9453` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_2.inc:39 |
| `0x14` | amiga | `LABEL_94F9` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_2.inc:24 |
| `0x14` | amiga | `LABEL_95B4` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_6.inc:19 |
| `0x14` | amiga | `LABEL_965B` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_2.inc:12 (+1 more) |
| `0x14` | amiga | `LABEL_9716` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_6.inc:6 |
| `0x14` | dos | `LABEL_9783` | src/levels/_unified/capsule/dos__post_INLINE_ADD_VAR50_BY_C.inc:13 |
| `0x14` | amiga | `LABEL_97BD` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_2.inc:34 |
| `0x14` | cart | `LABEL_97EC` | src/levels/_unified/capsule/cart__post_INLINE_ADD_VAR50_BY_C.inc:14 |
| `0x14` | dos | `LABEL_9821` | src/levels/_unified/capsule/dos__post_INLINE_ADD_VAR50_BY_C.inc:6 |
| `0x14` | amiga | `LABEL_9862` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_6.inc:24 |
| `0x14` | amiga | `LABEL_9877` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_6.inc:11 |
| `0x14` | cart | `LABEL_988A` | src/levels/_unified/capsule/cart__post_INLINE_ADD_VAR50_BY_C.inc:7 |
| `0x14` | amiga | `LABEL_991B` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_2.inc:18 |
| `0x14` | amiga | `LABEL_99BB` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR63_TO_2.inc:6 |
| `0x14` | dos | `LABEL_9A35` | src/levels/_unified/capsule/dos__post_INIT_VARS_E6_07_08.inc:22 |
| `0x14` | cart | `LABEL_9A9E` | src/levels/_unified/capsule/cart__post_INIT_VARS_E6_07_08.inc:22 |
| `0x14` | dos | `LABEL_BB8C` | src/levels/_unified/capsule/dos__entry.inc:1697 (+1 more) |
| `0x14` | cart | `LABEL_BC70` | src/levels/_unified/capsule/cart__entry.inc:1690 (+1 more) |
| `0x14` | dos | `LABEL_BD20` | src/levels/_unified/capsule/dos__post_INIT_VARS_E6_07_08.inc:23 (+1 more) |
| `0x14` | cart | `LABEL_BE04` | src/levels/_unified/capsule/cart__post_INIT_VARS_E6_07_08.inc:23 (+1 more) |
| `0x14` | dos | `LABEL_BEC4` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_2.inc:46 |
| `0x14` | dos | `LABEL_BEE8` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_2.inc:44 |
| `0x14` | cart | `LABEL_BFA8` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_2.inc:46 |
| `0x14` | dos | `LABEL_BFAE` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_5.inc:6 |
| `0x14` | cart | `LABEL_BFCC` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_2.inc:44 |
| `0x14` | dos | `LABEL_BFCE` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_5.inc:4 |
| `0x14` | dos | `LABEL_C083` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_2.inc:39 |
| `0x14` | cart | `LABEL_C092` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_5.inc:6 |
| `0x14` | cart | `LABEL_C0B2` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_5.inc:4 |
| `0x14` | dos | `LABEL_C129` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_2.inc:24 (+1 more) |
| `0x14` | cart | `LABEL_C167` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_2.inc:39 |
| `0x14` | dos | `LABEL_C1F0` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_6.inc:19 (+1 more) |
| `0x14` | cart | `LABEL_C20D` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_2.inc:24 (+1 more) |
| `0x14` | dos | `LABEL_C29D` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_2.inc:12 (+2 more) |
| `0x14` | cart | `LABEL_C2D4` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_6.inc:19 (+1 more) |
| `0x14` | dos | `LABEL_C364` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_6.inc:6 (+1 more) |
| `0x14` | cart | `LABEL_C381` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_2.inc:12 (+2 more) |
| `0x14` | dos | `LABEL_C411` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_2.inc:34 |
| `0x14` | cart | `LABEL_C448` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_6.inc:6 (+1 more) |
| `0x14` | dos | `LABEL_C4B6` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_6.inc:24 |
| `0x14` | dos | `LABEL_C4CB` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_6.inc:11 |
| `0x14` | cart | `LABEL_C4F5` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_2.inc:34 |
| `0x14` | dos | `LABEL_C56F` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_2.inc:18 |
| `0x14` | cart | `LABEL_C59A` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_6.inc:24 |
| `0x14` | cart | `LABEL_C5AF` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_6.inc:11 |
| `0x14` | dos | `LABEL_C60F` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR63_TO_2.inc:6 |
| `0x14` | cart | `LABEL_C653` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_2.inc:18 |
| `0x14` | cart | `LABEL_C6F3` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR63_TO_2.inc:6 |
| `0x14` | cart | `PLAY_3SFX_PAL_3_PAUSE_4` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR29_TO_4.inc:125 |
| `0x14` | amiga | `PLAY_3SFX_PAL_3_PAUSE_4` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR29_TO_4.inc:125 |
| `0x14` | dos | `PLAY_3SFX_PAL_3_PAUSE_4` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR29_TO_4.inc:125 |
| `0x14` | cart | `SET_VAR01_TO_6E_KILL_CHANNEL` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:513 |
| `0x14` | amiga | `SET_VAR01_TO_6E_KILL_CHANNEL` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:178 |
| `0x14` | dos | `SET_VAR01_TO_6E_KILL_CHANNEL` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:507 |
| `0x14` | cart | `STEP_DRAW_CV352_LEFT4_RIGHT1` | src/levels/_unified/capsule/cart__post_SET_VAR04_TO_0024.inc:34 |
| `0x14` | amiga | `STEP_DRAW_CV352_LEFT4_RIGHT1` | src/levels/_unified/capsule/amiga__post_SET_VAR04_TO_0024.inc:343 |
| `0x14` | dos | `STEP_DRAW_CV352_LEFT4_RIGHT1` | src/levels/_unified/capsule/dos__post_SET_VAR04_TO_0024.inc:34 |
| `0x15` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__entry.inc:1691 (+7 more) |
| `0x15` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__entry.inc:1554 (+7 more) |
| `0x15` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__entry.inc:1698 (+6 more) |
| `0x15` | amiga | `LABEL_2AC6` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:431 |
| `0x15` | cart | `LABEL_4030` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_F.inc:441 |
| `0x15` | dos | `LABEL_4064` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_F.inc:440 |
| `0x15` | dos | `LABEL_6051` | src/levels/_unified/capsule/dos__post_SPLIT_VAR09_BITS_INTO_VAR0D.inc:802 |
| `0x15` | cart | `LABEL_605A` | src/levels/_unified/capsule/cart__post_SPLIT_VAR09_BITS_INTO_VAR0D.inc:802 |
| `0x15` | amiga | `LABEL_7787` | src/levels/_unified/capsule/amiga__post_DECREMENT_VAR08_BY_D.inc:372 (+1 more) |
| `0x15` | dos | `LABEL_90DE` | src/levels/_unified/capsule/dos__post_DECREMENT_VAR08_BY_D.inc:389 (+1 more) |
| `0x15` | cart | `LABEL_9147` | src/levels/_unified/capsule/cart__post_DECREMENT_VAR08_BY_D.inc:389 (+1 more) |
| `0x15` | amiga | `LABEL_9267` | src/levels/_unified/capsule/amiga__post_DRAW_CV352_STEP_RIGHT3.inc:126 |
| `0x15` | amiga | `LABEL_9351` | src/levels/_unified/capsule/amiga__post_DRAW_CV352_STEP_RIGHT3.inc:214 |
| `0x15` | dos | `LABEL_BE97` | src/levels/_unified/capsule/dos__post_DRAW_CV352_STEP_RIGHT3.inc:166 |
| `0x15` | cart | `LABEL_BF7B` | src/levels/_unified/capsule/cart__post_DRAW_CV352_STEP_RIGHT3.inc:166 |
| `0x15` | dos | `LABEL_BF81` | src/levels/_unified/capsule/dos__post_DRAW_CV352_STEP_RIGHT3.inc:254 |
| `0x15` | cart | `LABEL_C065` | src/levels/_unified/capsule/cart__post_DRAW_CV352_STEP_RIGHT3.inc:254 |
| `0x16` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_SET_VAR01_TO_6E_KILL_CHANNEL.inc:90 |
| `0x16` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__entry.inc:1555 (+1 more) |
| `0x16` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_SET_VAR01_TO_6E_KILL_CHANNEL.inc:89 |
| `0x16` | amiga | `LABEL_0826` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:174 |
| `0x16` | dos | `LABEL_17D4` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:503 |
| `0x16` | cart | `LABEL_18E2` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:509 |
| `0x16` | amiga | `LABEL_290C` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:273 |
| `0x16` | cart | `LABEL_3E2E` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_F.inc:259 |
| `0x16` | dos | `LABEL_3E62` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_F.inc:258 |
| `0x16` | amiga | `LABEL_8B45` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARE8_TO_F.inc:166 (+2 more) |
| `0x16` | dos | `LABEL_9A21` | src/levels/_unified/capsule/dos__post_INIT_VARS_E6_07_08.inc:24 |
| `0x16` | cart | `LABEL_9A8A` | src/levels/_unified/capsule/cart__post_INIT_VARS_E6_07_08.inc:24 |
| `0x16` | dos | `LABEL_B666` | src/levels/_unified/capsule/dos__entry.inc:1699 (+4 more) |
| `0x16` | cart | `LABEL_B74A` | src/levels/_unified/capsule/cart__entry.inc:1692 (+4 more) |
| `0x17` | cart | `DRAW_CIN_052_THEN_053_PAIR` | src/levels/_unified/capsule/cart__post_INLINE_ADD_VAR50_BY_C.inc:6 (+1 more) |
| `0x17` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:31 (+2 more) |
| `0x17` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:31 (+2 more) |
| `0x17` | amiga | `LABEL_5338` | src/levels/_unified/capsule/amiga__post_DRAW_CV352_STEP_RIGHT3.inc:314 (+1 more) |
| `0x17` | amiga | `LABEL_538C` | src/levels/_unified/capsule/amiga__post_DRAW_CV352_STEP_RIGHT3.inc:587 (+1 more) |
| `0x17` | dos | `LABEL_6AB2` | src/levels/_unified/capsule/dos__post_DRAW_CV352_STEP_RIGHT3.inc:354 (+1 more) |
| `0x17` | cart | `LABEL_6AC1` | src/levels/_unified/capsule/cart__post_DRAW_CV352_STEP_RIGHT3.inc:354 (+1 more) |
| `0x17` | dos | `LABEL_6B1B` | src/levels/_unified/capsule/dos__post_DRAW_CV352_STEP_RIGHT3.inc:637 (+1 more) |
| `0x17` | cart | `LABEL_6B2A` | src/levels/_unified/capsule/cart__post_DRAW_CV352_STEP_RIGHT3.inc:637 (+1 more) |
| `0x18` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:97 |
| `0x18` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:90 |
| `0x18` | amiga | `LABEL_5054` | src/levels/_unified/capsule/amiga__post_INIT_VARS_A1_A4_A7.inc:33 |
| `0x18` | dos | `LABEL_5C58` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:89 |
| `0x18` | cart | `LABEL_5C5B` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:96 |
| `0x18` | dos | `LABEL_67C2` | src/levels/_unified/capsule/dos__post_INIT_VARS_A1_A4_A7.inc:44 |
| `0x18` | cart | `LABEL_67CB` | src/levels/_unified/capsule/cart__post_INIT_VARS_A1_A4_A7.inc:44 |
| `0x19` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:301 (+1 more) |
| `0x19` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:298 (+1 more) |
| `0x19` | dos | `LABEL_200D` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:91 |
| `0x19` | cart | `LABEL_2121` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:98 |
| `0x1A` | amiga | `LABEL_7E0E` | src/levels/_unified/capsule/amiga__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:22 |
| `0x1A` | amiga | `LABEL_7E20` | src/levels/_unified/capsule/amiga__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:9 |
| `0x1A` | dos | `LABEL_9765` | src/levels/_unified/capsule/dos__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:64 (+3 more) |
| `0x1A` | dos | `LABEL_9774` | src/levels/_unified/capsule/dos__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:13 (+3 more) |
| `0x1A` | cart | `LABEL_97CE` | src/levels/_unified/capsule/cart__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:64 (+3 more) |
| `0x1A` | cart | `LABEL_97DD` | src/levels/_unified/capsule/cart__post_COPY_VAR52_TO_VAR02_KILL_CHANNEL.inc:13 (+3 more) |
| `0x1B` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:302 (+2 more) |
| `0x1B` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:299 (+2 more) |
| `0x1B` | dos | `LABEL_28A8` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:728 (+1 more) |
| `0x1B` | cart | `LABEL_2A1F` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:741 (+1 more) |
| `0x1B` | dos | `LABEL_67C2` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:92 |
| `0x1B` | cart | `LABEL_67CB` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:99 |
| `0x1D` | amiga | `HANG_DRAW_CIN_119__AMIGA__POST_INLINE_SET_VARE8_TO_F` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARE8_TO_F.inc:158 |
| `0x1D` | dos | `HANG_DRAW_CIN_430` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE8_TO_F.inc:198 |
| `0x1D` | cart | `HANG_DRAW_CIN_434` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE8_TO_F.inc:206 |
| `0x1D` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:149 (+1 more) |
| `0x1D` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:85 |
| `0x1D` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:142 (+1 more) |
| `0x22` | cart | `INCREMENT_VAR31` | src/levels/_unified/capsule/cart__post_SET_VAR13_TO_FFFF.inc:39 |
| `0x22` | dos | `INCREMENT_VAR31` | src/levels/_unified/capsule/dos__post_SET_VAR13_TO_FFFF.inc:39 |
| `0x22` | amiga | `LABEL_1FD3` | src/levels/_unified/capsule/amiga__post_SET_VAR13_TO_FFFF.inc:39 |
| `0x22` | amiga | `LABEL_2FB5` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:30 (+1 more) |
| `0x22` | cart | `LABEL_4561` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:36 (+1 more) |
| `0x22` | dos | `LABEL_4585` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:36 (+1 more) |
| `0x23` | cart | `INIT_VARS_E6_07_08` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:314 |
| `0x23` | dos | `INIT_VARS_E6_07_08` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:309 |
| `0x23` | cart | `INLINE_SET_VAR29_TO_8` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:390 |
| `0x23` | dos | `INLINE_SET_VAR29_TO_8` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:384 |
| `0x23` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:37 (+5 more) |
| `0x23` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:31 (+2 more) |
| `0x23` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:37 (+5 more) |
| `0x23` | amiga | `LABEL_00B3` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:86 |
| `0x23` | dos | `LABEL_015E` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:275 |
| `0x23` | dos | `LABEL_019F` | src/levels/_unified/capsule/dos__entry.inc:1775 |
| `0x23` | cart | `LABEL_01CB` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:280 |
| `0x23` | dos | `LABEL_01D3` | src/levels/_unified/capsule/dos__entry.inc:1854 |
| `0x23` | cart | `LABEL_020C` | src/levels/_unified/capsule/cart__entry.inc:1803 |
| `0x23` | cart | `LABEL_0240` | src/levels/_unified/capsule/cart__entry.inc:1882 |
| `0x23` | amiga | `LABEL_02D1` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR29_TO_4.inc:69 |
| `0x23` | dos | `LABEL_10B8` | src/levels/_unified/capsule/dos__post_INIT_VARS_0E_29.inc:127 |
| `0x23` | dos | `LABEL_1120` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:297 |
| `0x23` | cart | `LABEL_1199` | src/levels/_unified/capsule/cart__post_INIT_VARS_0E_29.inc:152 |
| `0x23` | cart | `LABEL_1201` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:302 |
| `0x23` | dos | `LABEL_133E` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR29_TO_4.inc:69 |
| `0x23` | cart | `LABEL_142B` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR29_TO_4.inc:69 |
| `0x23` | amiga | `LABEL_2968` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:301 |
| `0x23` | amiga | `LABEL_2C4D` | src/levels/_unified/capsule/amiga__post_PLAY_SFX_005C_CH00.inc:32 |
| `0x23` | amiga | `LABEL_2CA0` | src/levels/_unified/capsule/amiga__post_PLAY_SFX_005C_CH00.inc:34 |
| `0x23` | amiga | `LABEL_355A` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:75 |
| `0x23` | cart | `LABEL_3E8A` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_F.inc:288 |
| `0x23` | dos | `LABEL_3EBE` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_F.inc:287 |
| `0x23` | cart | `LABEL_413C` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:63 |
| `0x23` | dos | `LABEL_4170` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:58 |
| `0x23` | cart | `LABEL_41B7` | src/levels/_unified/capsule/cart__post_PLAY_SFX_005C_CH00.inc:33 |
| `0x23` | dos | `LABEL_41EB` | src/levels/_unified/capsule/dos__post_PLAY_SFX_005C_CH00.inc:32 |
| `0x23` | cart | `LABEL_4210` | src/levels/_unified/capsule/cart__post_PLAY_SFX_005C_CH00.inc:35 |
| `0x23` | dos | `LABEL_4244` | src/levels/_unified/capsule/dos__post_PLAY_SFX_005C_CH00.inc:34 |
| `0x23` | cart | `LABEL_4B06` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:291 |
| `0x23` | dos | `LABEL_4B2A` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:286 |
| `0x23` | dos | `LABEL_80C2` | src/levels/_unified/capsule/dos__post_INIT_VAR6F_TO_A_PAUSE_3.inc:85 |
| `0x23` | cart | `LABEL_812B` | src/levels/_unified/capsule/cart__post_INIT_VAR6F_TO_A_PAUSE_3.inc:85 |
| `0x23` | dos | `LABEL_8189` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:208 |
| `0x23` | cart | `LABEL_81F2` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:213 |
| `0x23` | dos | `LABEL_8E78` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:244 |
| `0x23` | cart | `LABEL_8EE1` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:249 |
| `0x24` | amiga | `LABEL_2FD5` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:32 (+1 more) |
| `0x24` | cart | `LABEL_4581` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:38 (+1 more) |
| `0x24` | dos | `LABEL_45A5` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:38 (+1 more) |
| `0x25` | cart | `INIT_VARS_07_08_29` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:325 |
| `0x25` | amiga | `INIT_VARS_07_08_29` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:97 |
| `0x25` | dos | `INIT_VARS_07_08_29` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:320 |
| `0x25` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__entry.inc:1883 (+7 more) |
| `0x25` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__entry.inc:1635 (+2 more) |
| `0x25` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__entry.inc:1855 (+7 more) |
| `0x25` | dos | `LABEL_0128` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:266 (+1 more) |
| `0x25` | dos | `LABEL_012F` | src/levels/_unified/capsule/dos__entry.inc:1770 |
| `0x25` | cart | `LABEL_0195` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:271 (+1 more) |
| `0x25` | cart | `LABEL_019C` | src/levels/_unified/capsule/cart__entry.inc:1798 |
| `0x25` | amiga | `LABEL_022F` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR29_TO_4.inc:70 |
| `0x25` | dos | `LABEL_129C` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR29_TO_4.inc:70 |
| `0x25` | cart | `LABEL_1389` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR29_TO_4.inc:70 |
| `0x25` | amiga | `LABEL_2C4D` | src/levels/_unified/capsule/amiga__post_PLAY_SFX_005C_CH00.inc:38 |
| `0x25` | amiga | `LABEL_2CA0` | src/levels/_unified/capsule/amiga__post_PLAY_SFX_005C_CH00.inc:40 |
| `0x25` | amiga | `LABEL_355A` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:64 |
| `0x25` | cart | `LABEL_41B7` | src/levels/_unified/capsule/cart__post_PLAY_SFX_005C_CH00.inc:39 |
| `0x25` | dos | `LABEL_41EB` | src/levels/_unified/capsule/dos__post_PLAY_SFX_005C_CH00.inc:38 |
| `0x25` | cart | `LABEL_4210` | src/levels/_unified/capsule/cart__post_PLAY_SFX_005C_CH00.inc:41 |
| `0x25` | dos | `LABEL_4244` | src/levels/_unified/capsule/dos__post_PLAY_SFX_005C_CH00.inc:40 |
| `0x25` | cart | `LABEL_4AC4` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:158 (+2 more) |
| `0x25` | dos | `LABEL_4AE8` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:153 (+2 more) |
| `0x25` | cart | `LABEL_4B06` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:114 (+2 more) |
| `0x25` | dos | `LABEL_4B2A` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:109 (+2 more) |
| `0x25` | dos | `LABEL_80C2` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:220 |
| `0x25` | cart | `LABEL_812B` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:225 |
| `0x25` | dos | `LABEL_8E78` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:177 (+1 more) |
| `0x25` | cart | `LABEL_8EE1` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:182 (+1 more) |
| `0x26` | amiga | `LABEL_3010` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:34 (+1 more) |
| `0x26` | cart | `LABEL_45BC` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:40 (+1 more) |
| `0x26` | dos | `LABEL_45E0` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:40 (+1 more) |
| `0x27` | cart | `INIT_VARS_29_0E` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:260 (+1 more) |
| `0x27` | dos | `INIT_VARS_29_0E` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:255 (+1 more) |
| `0x27` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:41 (+5 more) |
| `0x27` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:35 (+1 more) |
| `0x27` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:41 (+5 more) |
| `0x27` | dos | `LABEL_02D2` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:54 |
| `0x27` | dos | `LABEL_02DA` | src/levels/_unified/capsule/dos__entry.inc:1782 |
| `0x27` | cart | `LABEL_033F` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:57 |
| `0x27` | cart | `LABEL_0347` | src/levels/_unified/capsule/cart__entry.inc:1810 |
| `0x27` | dos | `LABEL_0DE4` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:737 |
| `0x27` | cart | `LABEL_0EC1` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:750 |
| `0x27` | amiga | `LABEL_2C4D` | src/levels/_unified/capsule/amiga__post_PLAY_SFX_005C_CH00.inc:44 |
| `0x27` | amiga | `LABEL_2CA0` | src/levels/_unified/capsule/amiga__post_PLAY_SFX_005C_CH00.inc:46 |
| `0x27` | amiga | `LABEL_3518` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:53 |
| `0x27` | cart | `LABEL_41B7` | src/levels/_unified/capsule/cart__post_PLAY_SFX_005C_CH00.inc:45 |
| `0x27` | dos | `LABEL_41EB` | src/levels/_unified/capsule/dos__post_PLAY_SFX_005C_CH00.inc:44 |
| `0x27` | cart | `LABEL_4210` | src/levels/_unified/capsule/cart__post_PLAY_SFX_005C_CH00.inc:47 |
| `0x27` | dos | `LABEL_4244` | src/levels/_unified/capsule/dos__post_PLAY_SFX_005C_CH00.inc:46 |
| `0x27` | cart | `LABEL_4A84` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:336 |
| `0x27` | cart | `LABEL_4AA4` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:358 |
| `0x27` | dos | `LABEL_4AA8` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:331 |
| `0x27` | cart | `LABEL_4AC4` | src/levels/_unified/capsule/cart__entry.inc:1784 (+4 more) |
| `0x27` | dos | `LABEL_4AC8` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:353 |
| `0x27` | dos | `LABEL_4AE8` | src/levels/_unified/capsule/dos__entry.inc:1756 (+4 more) |
| `0x27` | cart | `LABEL_4B06` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:147 |
| `0x27` | dos | `LABEL_4B2A` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:142 |
| `0x27` | dos | `LABEL_80C2` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:165 (+1 more) |
| `0x27` | cart | `LABEL_812B` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:170 (+1 more) |
| `0x28` | cart | `INCREMENT_VAR31` | src/levels/_unified/capsule/cart__post_SET_VAR13_TO_FFFF.inc:17 (+1 more) |
| `0x28` | dos | `INCREMENT_VAR31` | src/levels/_unified/capsule/dos__post_SET_VAR13_TO_FFFF.inc:17 (+1 more) |
| `0x28` | amiga | `LABEL_1FD3` | src/levels/_unified/capsule/amiga__post_SET_VAR13_TO_FFFF.inc:17 (+1 more) |
| `0x28` | amiga | `LABEL_304B` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:36 (+1 more) |
| `0x28` | cart | `LABEL_45F7` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:42 (+1 more) |
| `0x28` | dos | `LABEL_461B` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:42 (+1 more) |
| `0x2A` | cart | `INCREMENT_VAR31` | src/levels/_unified/capsule/cart__post_SET_VAR13_TO_FFFF.inc:24 (+1 more) |
| `0x2A` | dos | `INCREMENT_VAR31` | src/levels/_unified/capsule/dos__post_SET_VAR13_TO_FFFF.inc:24 (+1 more) |
| `0x2A` | amiga | `LABEL_1FD3` | src/levels/_unified/capsule/amiga__post_SET_VAR13_TO_FFFF.inc:24 (+1 more) |
| `0x2B` | cart | `INIT_VARS_E6_E7_1` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:123 |
| `0x2B` | amiga | `INIT_VARS_E6_E7_1` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:59 |
| `0x2B` | dos | `INIT_VARS_E6_E7_1` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:116 |
| `0x2C` | cart | `INCREMENT_VAR31` | src/levels/_unified/capsule/cart__post_SET_VAR13_TO_FFFF.inc:31 (+1 more) |
| `0x2C` | dos | `INCREMENT_VAR31` | src/levels/_unified/capsule/dos__post_SET_VAR13_TO_FFFF.inc:31 (+1 more) |
| `0x2C` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INIT_VARS_E6_E7_1.inc:5 |
| `0x2C` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_INIT_VARS_E6_E7_1.inc:5 |
| `0x2C` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INIT_VARS_E6_E7_1.inc:5 |
| `0x2C` | amiga | `LABEL_116D` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:60 |
| `0x2C` | amiga | `LABEL_1FD3` | src/levels/_unified/capsule/amiga__post_SET_VAR13_TO_FFFF.inc:31 (+1 more) |
| `0x2C` | dos | `LABEL_22F4` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:117 |
| `0x2C` | cart | `LABEL_2432` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:124 |
| `0x2D` | amiga | `HANG_DRAW_CIN_047` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:34 |
| `0x2D` | dos | `HANG_DRAW_CIN_393` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:34 |
| `0x2D` | cart | `HANG_DRAW_CIN_396` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:34 |
| `0x2D` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:148 (+1 more) |
| `0x2D` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:84 |
| `0x2D` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:141 (+1 more) |
| `0x2E` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INIT_VARS_A1_A4_A7.inc:46 |
| `0x2E` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_INIT_VARS_A1_A4_A7.inc:35 |
| `0x2E` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INIT_VARS_A1_A4_A7.inc:46 |
| `0x2E` | amiga | `LABEL_17D8` | src/levels/_unified/capsule/amiga__post_INIT_VARS_A1_A4_A7.inc:36 |
| `0x2E` | dos | `LABEL_28F7` | src/levels/_unified/capsule/dos__post_INIT_VARS_A1_A4_A7.inc:47 |
| `0x2E` | cart | `LABEL_2A6E` | src/levels/_unified/capsule/cart__post_INIT_VARS_A1_A4_A7.inc:47 |
| `0x2F` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:100 |
| `0x2F` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:93 |
| `0x2F` | amiga | `LABEL_44FB` | src/levels/_unified/capsule/amiga__post_INIT_VARS_A1_A4_A7.inc:34 |
| `0x2F` | dos | `LABEL_5C58` | src/levels/_unified/capsule/dos__post_INIT_VARS_A1_A4_A7.inc:45 |
| `0x2F` | cart | `LABEL_5C5B` | src/levels/_unified/capsule/cart__post_INIT_VARS_A1_A4_A7.inc:45 |
| `0x30` | amiga | `LABEL_419B` | src/levels/_unified/capsule/amiga__post_INLINE_SUB_VAR22_BY_23.inc:117 |
| `0x30` | cart | `LABEL_58D1` | src/levels/_unified/capsule/cart__post_INLINE_SUB_VAR22_BY_23.inc:130 |
| `0x30` | dos | `LABEL_58E1` | src/levels/_unified/capsule/dos__post_INLINE_SUB_VAR22_BY_23.inc:130 |
| `0x31` | amiga | `LABEL_3FF8` | src/levels/_unified/capsule/amiga__post_INLINE_SUB_VAR22_BY_23.inc:126 |
| `0x31` | amiga | `LABEL_41A4` | src/levels/_unified/capsule/amiga__post_INLINE_SUB_VAR22_BY_23.inc:118 |
| `0x31` | cart | `LABEL_56FA` | src/levels/_unified/capsule/cart__post_INLINE_SUB_VAR22_BY_23.inc:139 |
| `0x31` | dos | `LABEL_570A` | src/levels/_unified/capsule/dos__post_INLINE_SUB_VAR22_BY_23.inc:139 |
| `0x31` | cart | `LABEL_58DA` | src/levels/_unified/capsule/cart__post_INLINE_SUB_VAR22_BY_23.inc:131 |
| `0x31` | dos | `LABEL_58EA` | src/levels/_unified/capsule/dos__post_INLINE_SUB_VAR22_BY_23.inc:131 |
| `0x32` | amiga | `LABEL_3FF8` | src/levels/_unified/capsule/amiga__post_INLINE_SUB_VAR22_BY_23.inc:134 |
| `0x32` | amiga | `LABEL_41A4` | src/levels/_unified/capsule/amiga__post_INLINE_SUB_VAR22_BY_23.inc:119 |
| `0x32` | cart | `LABEL_56FA` | src/levels/_unified/capsule/cart__post_INLINE_SUB_VAR22_BY_23.inc:147 |
| `0x32` | dos | `LABEL_570A` | src/levels/_unified/capsule/dos__post_INLINE_SUB_VAR22_BY_23.inc:147 |
| `0x32` | cart | `LABEL_58DA` | src/levels/_unified/capsule/cart__post_INLINE_SUB_VAR22_BY_23.inc:132 |
| `0x32` | dos | `LABEL_58EA` | src/levels/_unified/capsule/dos__post_INLINE_SUB_VAR22_BY_23.inc:132 |
| `0x33` | amiga | `LABEL_3FF8` | src/levels/_unified/capsule/amiga__post_INLINE_SUB_VAR22_BY_23.inc:142 |
| `0x33` | amiga | `LABEL_5240` | src/levels/_unified/capsule/amiga__post_FOLD_BODY_58B_A2D4469A.inc:234 |
| `0x33` | cart | `LABEL_56FA` | src/levels/_unified/capsule/cart__post_INLINE_SUB_VAR22_BY_23.inc:155 |
| `0x33` | dos | `LABEL_570A` | src/levels/_unified/capsule/dos__post_INLINE_SUB_VAR22_BY_23.inc:155 |
| `0x33` | dos | `LABEL_69B2` | src/levels/_unified/capsule/dos__post_FOLD_BODY_58B_A2D4469A.inc:258 (+1 more) |
| `0x33` | cart | `LABEL_69BB` | src/levels/_unified/capsule/cart__post_FOLD_BODY_58B_A2D4469A.inc:258 (+1 more) |
| `0x34` | dos | `HANG_DRAW_CIN_335` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:308 |
| `0x34` | cart | `HANG_DRAW_CIN_336` | src/levels/_unified/capsule/cart__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:313 |
| `0x34` | cart | `INIT_VARS_E7_E8` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:1001 |
| `0x34` | dos | `INIT_VARS_E7_E8` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:965 |
| `0x34` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INIT_VARS_0E_29.inc:72 |
| `0x34` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INIT_VARS_0E_29.inc:72 |
| `0x34` | dos | `LABEL_00BC` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:64 |
| `0x34` | cart | `LABEL_0129` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:71 |
| `0x34` | amiga | `LABEL_1140` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:29 |
| `0x34` | amiga | `LABEL_11C6` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:61 |
| `0x34` | dos | `LABEL_1F1D` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:786 |
| `0x34` | cart | `LABEL_2031` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:802 |
| `0x34` | dos | `LABEL_22C7` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:29 |
| `0x34` | dos | `LABEL_234D` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:118 |
| `0x34` | cart | `LABEL_23FB` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:29 |
| `0x34` | cart | `LABEL_248B` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:125 |
| `0x34` | dos | `LABEL_289B` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:703 |
| `0x34` | cart | `LABEL_2A12` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:716 |
| `0x34` | amiga | `LABEL_5274` | src/levels/_unified/capsule/amiga__post_FOLD_BODY_58B_A2D4469A.inc:224 |
| `0x34` | dos | `LABEL_69E6` | src/levels/_unified/capsule/dos__post_FOLD_BODY_58B_A2D4469A.inc:248 (+1 more) |
| `0x34` | cart | `LABEL_69F2` | src/levels/_unified/capsule/cart__post_FOLD_BODY_58B_A2D4469A.inc:248 (+1 more) |
| `0x34` | amiga | `LABEL_83FA` | src/levels/_unified/capsule/amiga__post_SET_VAR13_TO_FFFF.inc:71 |
| `0x35` | amiga | `HANG_DRAW_CIN_145` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:83 |
| `0x35` | dos | `HANG_DRAW_CIN_456` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:140 (+1 more) |
| `0x35` | cart | `HANG_DRAW_CIN_460` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:147 (+1 more) |
| `0x35` | cart | `INIT_VARS_E9_EA` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:1002 |
| `0x35` | dos | `INIT_VARS_E9_EA` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:966 |
| `0x35` | cart | `LABEL_0545` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:672 (+3 more) |
| `0x35` | amiga | `LABEL_10B1` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:30 |
| `0x35` | amiga | `LABEL_126C` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:10 |
| `0x35` | amiga | `LABEL_127B` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:62 |
| `0x35` | dos | `LABEL_2096` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:94 |
| `0x35` | cart | `LABEL_21AA` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:101 |
| `0x35` | dos | `LABEL_2238` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:30 |
| `0x35` | cart | `LABEL_234C` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:30 |
| `0x35` | dos | `LABEL_23F3` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:10 |
| `0x35` | dos | `LABEL_2402` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:119 |
| `0x35` | cart | `LABEL_2547` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:10 |
| `0x35` | cart | `LABEL_2556` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:126 |
| `0x35` | amiga | `LABEL_83FA` | src/levels/_unified/capsule/amiga__post_SET_VAR13_TO_FFFF.inc:70 |
| `0x36` | dos | `LABEL_035A` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:228 |
| `0x36` | cart | `LABEL_03C7` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:231 |
| `0x36` | cart | `LABEL_0565` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:677 (+2 more) |
| `0x36` | dos | `LABEL_09FB` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:967 |
| `0x36` | cart | `LABEL_0AB1` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:1003 |
| `0x36` | amiga | `LABEL_0E76` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:48 |
| `0x36` | amiga | `LABEL_0E92` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_5.inc:7 (+2 more) |
| `0x36` | amiga | `LABEL_111D` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:31 |
| `0x36` | amiga | `LABEL_120C` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:25 (+1 more) |
| `0x36` | amiga | `LABEL_1233` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:11 |
| `0x36` | amiga | `LABEL_181B` | src/levels/_unified/capsule/amiga__post_SET_VARB3_TO_0000.inc:54 (+4 more) |
| `0x36` | amiga | `LABEL_1833` | src/levels/_unified/capsule/amiga__post_SET_VARB3_TO_0000.inc:84 (+1 more) |
| `0x36` | amiga | `LABEL_19E2` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:87 (+1 more) |
| `0x36` | amiga | `LABEL_1A81` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARE6_TO_4.inc:25 |
| `0x36` | dos | `LABEL_1E24` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:48 |
| `0x36` | dos | `LABEL_1E40` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_5.inc:7 (+2 more) |
| `0x36` | cart | `LABEL_1F38` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:48 |
| `0x36` | cart | `LABEL_1F54` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_5.inc:7 (+2 more) |
| `0x36` | dos | `LABEL_22A4` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:31 |
| `0x36` | dos | `LABEL_2393` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:120 (+1 more) |
| `0x36` | dos | `LABEL_23BA` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:11 |
| `0x36` | cart | `LABEL_23CE` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:31 |
| `0x36` | cart | `LABEL_24E7` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:127 (+1 more) |
| `0x36` | cart | `LABEL_250E` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:11 |
| `0x36` | amiga | `LABEL_28BD` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:125 |
| `0x36` | dos | `LABEL_2A3E` | src/levels/_unified/capsule/dos__post_SET_VARB3_TO_0000.inc:155 (+4 more) |
| `0x36` | dos | `LABEL_2A56` | src/levels/_unified/capsule/dos__post_SET_VARB3_TO_0000.inc:185 (+1 more) |
| `0x36` | cart | `LABEL_2BBB` | src/levels/_unified/capsule/cart__post_SET_VARB3_TO_0000.inc:158 (+4 more) |
| `0x36` | cart | `LABEL_2BD3` | src/levels/_unified/capsule/cart__post_SET_VARB3_TO_0000.inc:188 (+1 more) |
| `0x36` | dos | `LABEL_2C05` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:144 (+2 more) |
| `0x36` | dos | `LABEL_2CA4` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_4.inc:25 |
| `0x36` | cart | `LABEL_2D82` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:151 (+2 more) |
| `0x36` | cart | `LABEL_2E21` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_4.inc:25 |
| `0x36` | cart | `LABEL_3DD3` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:213 |
| `0x36` | dos | `LABEL_3E0B` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:211 |
| `0x37` | amiga | `HANG_DRAW_CIN_004` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:64 |
| `0x37` | dos | `HANG_DRAW_CIN_350` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:121 |
| `0x37` | cart | `HANG_DRAW_CIN_351` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:128 |
| `0x37` | dos | `HANG_DRAW_CIN_491` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:349 |
| `0x37` | cart | `HANG_DRAW_CIN_494` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:355 |
| `0x37` | dos | `HANG_DRAW_CIN_494` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:229 |
| `0x37` | cart | `HANG_DRAW_CIN_497` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:232 |
| `0x37` | dos | `HANG_DRAW_CIN_515` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:400 |
| `0x37` | cart | `HANG_DRAW_CIN_518` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:406 |
| `0x37` | amiga | `LABEL_02A1` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VAR29_TO_4.inc:93 |
| `0x37` | dos | `LABEL_05A7` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:938 |
| `0x37` | cart | `LABEL_0655` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:974 |
| `0x37` | amiga | `LABEL_0895` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:154 |
| `0x37` | dos | `LABEL_09BC` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:968 |
| `0x37` | cart | `LABEL_0A72` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:1004 |
| `0x37` | dos | `LABEL_0AE1` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:911 |
| `0x37` | cart | `LABEL_0B97` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:947 |
| `0x37` | dos | `LABEL_0BD3` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:602 |
| `0x37` | cart | `LABEL_0C92` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:609 |
| `0x37` | dos | `LABEL_0CD0` | src/levels/_unified/capsule/dos__post_INIT_VARS_03_01.inc:324 |
| `0x37` | cart | `LABEL_0DA7` | src/levels/_unified/capsule/cart__post_INIT_VARS_03_01.inc:318 (+1 more) |
| `0x37` | amiga | `LABEL_0ED5` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_5.inc:14 |
| `0x37` | amiga | `LABEL_0F9F` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARE6_TO_4.inc:16 |
| `0x37` | amiga | `LABEL_10ED` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:32 |
| `0x37` | dos | `LABEL_130E` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR29_TO_4.inc:93 |
| `0x37` | cart | `LABEL_13FB` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR29_TO_4.inc:93 |
| `0x37` | dos | `LABEL_1843` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:483 |
| `0x37` | cart | `LABEL_1951` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:489 |
| `0x37` | dos | `LABEL_1EA0` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_5.inc:14 |
| `0x37` | dos | `LABEL_1EFB` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:622 (+1 more) |
| `0x37` | dos | `LABEL_1F0E` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:665 |
| `0x37` | dos | `LABEL_1F40` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:762 |
| `0x37` | dos | `LABEL_1F55` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:581 |
| `0x37` | dos | `LABEL_1F64` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:557 |
| `0x37` | dos | `LABEL_1F89` | src/levels/_unified/capsule/dos__post_SET_VAR22_TO_003E.inc:15 |
| `0x37` | cart | `LABEL_1FB4` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_5.inc:14 |
| `0x37` | dos | `LABEL_1FC7` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:300 |
| `0x37` | dos | `LABEL_1FDE` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:38 |
| `0x37` | dos | `LABEL_2005` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:330 |
| `0x37` | cart | `LABEL_200F` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:629 (+1 more) |
| `0x37` | cart | `LABEL_2022` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:678 |
| `0x37` | cart | `LABEL_2054` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:778 |
| `0x37` | cart | `LABEL_2069` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:588 |
| `0x37` | cart | `LABEL_2078` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:563 |
| `0x37` | cart | `LABEL_209D` | src/levels/_unified/capsule/cart__post_SET_VAR22_TO_003E.inc:16 |
| `0x37` | dos | `LABEL_20B7` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_28.inc:21 |
| `0x37` | dos | `LABEL_20DA` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_14.inc:24 (+1 more) |
| `0x37` | cart | `LABEL_20DB` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:303 |
| `0x37` | cart | `LABEL_20F2` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:38 |
| `0x37` | cart | `LABEL_2119` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:336 |
| `0x37` | dos | `LABEL_2126` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_28.inc:16 (+1 more) |
| `0x37` | cart | `LABEL_21CB` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_28.inc:21 |
| `0x37` | cart | `LABEL_21EE` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_14.inc:24 (+1 more) |
| `0x37` | cart | `LABEL_223A` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_28.inc:16 (+1 more) |
| `0x37` | dos | `LABEL_2274` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:32 |
| `0x37` | cart | `LABEL_2393` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:32 |
| `0x37` | dos | `LABEL_39EC` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:405 |
| `0x37` | cart | `LABEL_3A55` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:411 |
| `0x38` | amiga | `HANG_DRAW_CIN_003_AT_11F4` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:65 |
| `0x38` | dos | `HANG_DRAW_CIN_349_AT_237B` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:122 |
| `0x38` | cart | `HANG_DRAW_CIN_350_AT_24CF` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:129 |
| `0x38` | amiga | `LABEL_0F14` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_5.inc:146 |
| `0x38` | amiga | `LABEL_0F30` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARE6_TO_4.inc:21 |
| `0x38` | amiga | `LABEL_11FD` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:4 |
| `0x38` | amiga | `LABEL_1242` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:17 |
| `0x38` | amiga | `LABEL_1918` | src/levels/_unified/capsule/amiga__post_SET_VARB3_TO_0000.inc:75 |
| `0x38` | amiga | `LABEL_1B1F` | src/levels/_unified/capsule/amiga__post_SET_VARB3_TO_0000.inc:127 |
| `0x38` | dos | `LABEL_1EDF` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_5.inc:154 |
| `0x38` | cart | `LABEL_1FF3` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_5.inc:154 |
| `0x38` | dos | `LABEL_20B7` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_4.inc:21 |
| `0x38` | cart | `LABEL_21CB` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_4.inc:21 |
| `0x38` | dos | `LABEL_2384` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:4 |
| `0x38` | dos | `LABEL_23C9` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARED_TO_6.inc:17 |
| `0x38` | cart | `LABEL_24D8` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:4 |
| `0x38` | cart | `LABEL_251D` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:17 |
| `0x38` | dos | `LABEL_2B3B` | src/levels/_unified/capsule/dos__post_SET_VARB3_TO_0000.inc:176 |
| `0x38` | dos | `LABEL_2C05` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:969 |
| `0x38` | cart | `LABEL_2CB8` | src/levels/_unified/capsule/cart__post_SET_VARB3_TO_0000.inc:179 |
| `0x38` | dos | `LABEL_2D42` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_14.inc:11 (+1 more) |
| `0x38` | cart | `LABEL_2D82` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:1005 |
| `0x38` | cart | `LABEL_2EBF` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_14.inc:11 (+1 more) |
| `0x38` | cart | `LABEL_3D5C` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE8_TO_F.inc:59 |
| `0x38` | dos | `LABEL_3D94` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE8_TO_F.inc:51 |
| `0x39` | cart | `INLINE_SET_VAREF_TO_A0` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:130 |
| `0x39` | amiga | `INLINE_SET_VAREF_TO_A0` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:66 |
| `0x39` | dos | `INLINE_SET_VAREF_TO_A0` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:123 |
| `0x39` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARED_TO_6.inc:18 (+1 more) |
| `0x39` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARED_TO_6.inc:18 (+1 more) |
| `0x39` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:402 (+2 more) |
| `0x39` | amiga | `LABEL_181B` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARE6_TO_4.inc:32 (+2 more) |
| `0x39` | amiga | `LABEL_1833` | src/levels/_unified/capsule/amiga__post_SET_VARB3_TO_0000.inc:69 (+1 more) |
| `0x39` | dos | `LABEL_2A3E` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_4.inc:32 (+2 more) |
| `0x39` | dos | `LABEL_2A56` | src/levels/_unified/capsule/dos__post_SET_VARB3_TO_0000.inc:170 (+1 more) |
| `0x39` | cart | `LABEL_2BBB` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_4.inc:32 (+2 more) |
| `0x39` | cart | `LABEL_2BD3` | src/levels/_unified/capsule/cart__post_SET_VARB3_TO_0000.inc:173 (+1 more) |
| `0x39` | dos | `LABEL_3596` | src/levels/_unified/capsule/dos__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:396 |
| `0x3A` | amiga | `LABEL_0F53` | src/levels/_unified/capsule/amiga__post_INLINE_SET_VARE6_TO_4.inc:8 |
| `0x3A` | amiga | `LABEL_1A81` | src/levels/_unified/capsule/amiga__post_SET_VARB3_TO_0000.inc:134 |
| `0x3A` | dos | `LABEL_20DA` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_4.inc:8 |
| `0x3A` | cart | `LABEL_21EE` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_4.inc:8 |
| `0x3A` | dos | `LABEL_2CA4` | src/levels/_unified/capsule/dos__post_SET_VARB3_TO_0000.inc:235 |
| `0x3A` | cart | `LABEL_2E21` | src/levels/_unified/capsule/cart__post_SET_VARB3_TO_0000.inc:238 |
| `0x3B` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INIT_VARS_A1_A4_A7.inc:3 (+2 more) |
| `0x3B` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_BREAK_5X_THEN_INIT_VAR03_14.inc:34 (+2 more) |
| `0x3B` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INIT_VARS_A1_A4_A7.inc:3 (+2 more) |
| `0x3C` | cart | `COPY_PAGE_40_BREAK_LOOP` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:541 (+6 more) |
| `0x3C` | dos | `COPY_PAGE_40_BREAK_LOOP` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:535 (+6 more) |
| `0x3C` | dos | `JUNK__2E6A` | src/levels/_unified/capsule/dos__post_SCROLL_BLIT_P80_TO_PFF_OFFSET_00C8.inc:67 (+1 more) |
| `0x3C` | cart | `JUNK__2FE7` | src/levels/_unified/capsule/cart__post_SCROLL_BLIT_P80_TO_PFF_OFFSET_00C8.inc:67 (+1 more) |
| `0x3C` | amiga | `LABEL_21C5` | src/levels/_unified/capsule/amiga__entry.inc:1541 (+2 more) |
| `0x3C` | amiga | `LABEL_21F2` | src/levels/_unified/capsule/amiga__post_ADD_VAR11_TO_VAR34.inc:95 (+1 more) |
| `0x3C` | amiga | `LABEL_2268` | src/levels/_unified/capsule/amiga__post_LOAD_RES90_COPY_PAGE0_TO_3_LOAD_RES91.inc:187 |
| `0x3C` | amiga | `LABEL_22A4` | src/levels/_unified/capsule/amiga__post_BREAK_5X_THEN_INIT_VAR03_14.inc:194 (+1 more) |
| `0x3C` | dos | `LABEL_2E43` | src/levels/_unified/capsule/dos__entry.inc:1684 (+3 more) |
| `0x3C` | dos | `LABEL_2E73` | src/levels/_unified/capsule/dos__post_DRAW_CV139_AT_X01_Y02.inc:30 |
| `0x3C` | dos | `LABEL_2E8C` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:598 (+1 more) |
| `0x3C` | dos | `LABEL_2F4F` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:864 |
| `0x3C` | dos | `LABEL_2F8F` | src/levels/_unified/capsule/dos__post_INLINE_SET_VAR02_TO_97.inc:1002 |
| `0x3C` | cart | `LABEL_2FC0` | src/levels/_unified/capsule/cart__entry.inc:1677 (+3 more) |
| `0x3C` | dos | `LABEL_2FCB` | src/levels/_unified/capsule/dos__post_DRAW_TEXT_0174_AT_26_180.inc:116 (+1 more) |
| `0x3C` | dos | `LABEL_2FE9` | src/levels/_unified/capsule/dos__post_SET_VAR13_TO_FFFF.inc:75 |
| `0x3C` | cart | `LABEL_2FF0` | src/levels/_unified/capsule/cart__post_DRAW_CV139_AT_X01_Y02.inc:31 |
| `0x3C` | cart | `LABEL_3009` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:605 (+1 more) |
| `0x3C` | cart | `LABEL_30CC` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:900 |
| `0x3C` | cart | `LABEL_310C` | src/levels/_unified/capsule/cart__post_INLINE_SET_VAR02_TO_97.inc:1039 |
| `0x3C` | cart | `LABEL_3148` | src/levels/_unified/capsule/cart__post_DRAW_TEXT_0174_AT_26_180.inc:116 (+1 more) |
| `0x3C` | cart | `LABEL_3166` | src/levels/_unified/capsule/cart__post_SET_VAR13_TO_FFFF.inc:75 |
| `0x3E` | amiga | `LABEL_81EF` | src/levels/_unified/capsule/amiga__post_SET_VAR04_TO_0024.inc:236 (+2 more) |
| `0x3F` | cart | `BREAK_5X_THEN_INIT_VAR03_14` | src/levels/_unified/capsule/cart__post_DRAW_CV139_AT_X01_Y02.inc:18 (+4 more) |
| `0x3F` | amiga | `BREAK_5X_THEN_INIT_VAR03_14` | src/levels/_unified/capsule/amiga__post_PLAY_SFX_005C_CH00.inc:4 (+2 more) |
| `0x3F` | dos | `BREAK_5X_THEN_INIT_VAR03_14` | src/levels/_unified/capsule/dos__post_DRAW_CV139_AT_X01_Y02.inc:17 (+4 more) |
| `0x3F` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/cart__post_INLINE_SET_VARE6_TO_F.inc:292 (+2 more) |
| `0x3F` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/amiga__post_ACCUMULATE_HASH_INTO_VAR37_38.inc:305 (+2 more) |
| `0x3F` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/capsule/dos__post_INLINE_SET_VARE6_TO_F.inc:291 (+2 more) |
| `0x3F` | amiga | `LABEL_866F` | src/levels/_unified/capsule/amiga__entry.inc:1557 (+1 more) |
| `0x3F` | dos | `LABEL_B53C` | src/levels/_unified/capsule/dos__entry.inc:1703 (+1 more) |
| `0x3F` | cart | `LABEL_B61D` | src/levels/_unified/capsule/cart__entry.inc:1696 (+1 more) |

## ENDING

| channel | branch | routine | source |
| ---: | --- | --- | --- |
| `0x05` | cart | `DRAW_CIN_106_107_FX_57` | src/levels/_unified/ending/cart__post_INIT_VARS_07_08_09.inc:40 |
| `0x05` | amiga | `DRAW_CIN_106_107_FX_57` | src/levels/_unified/ending/amiga__post_INIT_VARS_07_08_09.inc:40 |
| `0x05` | dos | `DRAW_CIN_106_107_FX_57` | src/levels/_unified/ending/dos__post_INIT_VARS_07_08_09.inc:40 |
| `0x05` | cart | `DRAW_CIN_71_72_FADE` | src/levels/_unified/ending/cart__post_SET_VAR_E6_5_PAL_B.inc:60 |
| `0x05` | amiga | `DRAW_CIN_71_72_FADE` | src/levels/_unified/ending/amiga__post_SET_VAR_E6_5_PAL_B.inc:60 |
| `0x05` | dos | `DRAW_CIN_71_72_FADE` | src/levels/_unified/ending/dos__post_SET_VAR_E6_5_PAL_B.inc:60 |
| `0x05` | cart | `HANG_DRAWING_CIN_071` | src/levels/_unified/ending/cart__post_SET_VAR_E6_5_PAL_B.inc:43 |
| `0x05` | amiga | `HANG_DRAWING_CIN_071` | src/levels/_unified/ending/amiga__post_SET_VAR_E6_5_PAL_B.inc:43 |
| `0x05` | dos | `HANG_DRAWING_CIN_071` | src/levels/_unified/ending/dos__post_SET_VAR_E6_5_PAL_B.inc:43 |
| `0x05` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/ending/cart__post_INIT_VARS_07_08_09.inc:64 |
| `0x05` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/ending/amiga__post_INIT_VARS_07_08_09.inc:64 |
| `0x05` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/ending/dos__post_INIT_VARS_07_08_09.inc:64 |
| `0x0A` | amiga | `LABEL_0149` | src/levels/_unified/ending/amiga__post_DRAW_CIN_103_LOOP.inc:25 |
| `0x0A` | dos | `LABEL_0149` | src/levels/_unified/ending/dos__post_DRAW_CIN_103_LOOP.inc:25 |
| `0x0A` | cart | `LABEL_0159` | src/levels/_unified/ending/cart__post_DELETE_ALL_CHANS_AND_KILL.inc:86 |
| `0x0A` | cart | `SET_VAR_E6_5_PAL_B` | src/levels/_unified/ending/cart__post_INIT_VARS_07_08_09.inc:65 |
| `0x0A` | amiga | `SET_VAR_E6_5_PAL_B` | src/levels/_unified/ending/amiga__post_INIT_VARS_07_08_09.inc:65 |
| `0x0A` | dos | `SET_VAR_E6_5_PAL_B` | src/levels/_unified/ending/dos__post_INIT_VARS_07_08_09.inc:65 |
| `0x0A` | cart | `ZOOM_LOOP_CIN_105` | src/levels/_unified/ending/cart__post_SET_VAR_E6_5_PAL_B.inc:34 |
| `0x0A` | amiga | `ZOOM_LOOP_CIN_105` | src/levels/_unified/ending/amiga__post_SET_VAR_E6_5_PAL_B.inc:34 |
| `0x0A` | dos | `ZOOM_LOOP_CIN_105` | src/levels/_unified/ending/dos__post_SET_VAR_E6_5_PAL_B.inc:34 |
| `0x0B` | cart | `DRAW_CIN_101_102_FADE_PAL_C` | src/levels/_unified/ending/cart__post_SET_VAR_E6_5_PAL_B.inc:35 |
| `0x0B` | amiga | `DRAW_CIN_101_102_FADE_PAL_C` | src/levels/_unified/ending/amiga__post_SET_VAR_E6_5_PAL_B.inc:35 |
| `0x0B` | dos | `DRAW_CIN_101_102_FADE_PAL_C` | src/levels/_unified/ending/dos__post_SET_VAR_E6_5_PAL_B.inc:35 |
| `0x0B` | amiga | `DRAW_CIN_58_ANIM_LOOP` | src/levels/_unified/ending/amiga__post_DRAW_CIN_103_LOOP.inc:26 |
| `0x0B` | dos | `DRAW_CIN_58_ANIM_LOOP` | src/levels/_unified/ending/dos__post_DRAW_CIN_103_LOOP.inc:26 |
| `0x0B` | cart | `DRAW_CIN_58_ANIM_LOOP__CART__POST_DELETE_ALL_CHANS_AND_KILL` | src/levels/_unified/ending/cart__post_DELETE_ALL_CHANS_AND_KILL.inc:87 |
| `0x0B` | shared | `KILL_CHANNEL_LANDING` | src/levels/_unified/ending/ending_channel_cleanup.inc:128 |
| `0x0B` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/ending/cart__post_DELETE_ALL_CHANS_AND_KILL.inc:138 |
| `0x0C` | dos | `DRAW_CIN_086_087_088_SEQ` | src/levels/_unified/ending/dos__post_DRAW_CIN_59_TO_64_VAR_POS.inc:15 |
| `0x0C` | cart | `DRAW_CIN_086_087_SEQ` | src/levels/_unified/ending/cart__post_DELETE_ALL_CHANS_AND_KILL.inc:130 |
| `0x0C` | amiga | `DRAW_CIN_86_87_88_89` | src/levels/_unified/ending/amiga__post_DRAW_CIN_59_TO_64_VAR_POS.inc:15 |
| `0x0C` | cart | `DRAW_CIN_97_TO_100` | src/levels/_unified/ending/cart__post_SET_VAR_E6_5_PAL_B.inc:36 |
| `0x0C` | amiga | `DRAW_CIN_97_TO_100` | src/levels/_unified/ending/amiga__post_SET_VAR_E6_5_PAL_B.inc:36 |
| `0x0C` | dos | `DRAW_CIN_97_TO_100` | src/levels/_unified/ending/dos__post_SET_VAR_E6_5_PAL_B.inc:36 |
| `0x0C` | amiga | `DRIFT_VAR07_PLUS_2_3X__AMIGA__POST_INIT_VARS_07_08_09` | src/levels/_unified/ending/amiga__post_INIT_VARS_07_08_09.inc:20 |
| `0x0C` | cart | `DRIFT_VAR07_PLUS_2_3X__CART__POST_INIT_VARS_07_08_09` | src/levels/_unified/ending/cart__post_INIT_VARS_07_08_09.inc:20 |
| `0x0C` | dos | `DRIFT_VAR07_PLUS_2_3X__DOS__POST_INIT_VARS_07_08_09` | src/levels/_unified/ending/dos__post_INIT_VARS_07_08_09.inc:20 |
| `0x0C` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/ending/cart__post_INIT_VARS_07_08_09.inc:26 |
| `0x0C` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/ending/amiga__post_INIT_VARS_07_08_09.inc:26 |
| `0x0C` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/ending/dos__post_INIT_VARS_07_08_09.inc:26 |
| `0x0D` | dos | `DRAW_CIN_075_076_077_SEQ` | src/levels/_unified/ending/dos__post_DRAW_CIN_59_TO_64_VAR_POS.inc:16 |
| `0x0D` | cart | `DRAW_CIN_075_076_SEQ` | src/levels/_unified/ending/cart__post_DELETE_ALL_CHANS_AND_KILL.inc:131 |
| `0x0D` | amiga | `LABEL_00AF` | src/levels/_unified/ending/amiga__post_SET_VAR_E6_5_PAL_B.inc:37 |
| `0x0D` | dos | `LABEL_00AF` | src/levels/_unified/ending/dos__post_SET_VAR_E6_5_PAL_B.inc:37 |
| `0x0D` | cart | `LABEL_00BF` | src/levels/_unified/ending/cart__post_SET_VAR_E6_5_PAL_B.inc:37 |
| `0x0D` | amiga | `LABEL_046F` | src/levels/_unified/ending/amiga__post_DRAW_CIN_59_TO_64_VAR_POS.inc:16 |
| `0x0E` | cart | `HANG_DRAWING_CIN_066_VAR03` | src/levels/_unified/ending/cart__post_DELETE_ALL_CHANS_AND_KILL.inc:88 |
| `0x0E` | amiga | `HANG_DRAWING_CIN_066_VAR03` | src/levels/_unified/ending/amiga__post_DRAW_CIN_103_LOOP.inc:27 |
| `0x0E` | dos | `HANG_DRAWING_CIN_066_VAR03` | src/levels/_unified/ending/dos__post_DRAW_CIN_103_LOOP.inc:27 |
| `0x0F` | amiga | `DRAW_CIN_59_TO_64_VAR_POS` | src/levels/_unified/ending/amiga__post_DRAW_CIN_103_LOOP.inc:28 |
| `0x0F` | dos | `DRAW_CIN_59_TO_64_VAR_POS` | src/levels/_unified/ending/dos__post_DRAW_CIN_103_LOOP.inc:28 |
| `0x0F` | cart | `DRAW_CIN_59_TO_64_VAR_POS__CART__POST_DELETE_ALL_CHANS_AND_KILL` | src/levels/_unified/ending/cart__post_DELETE_ALL_CHANS_AND_KILL.inc:89 |
| `0x10` | shared | `INIT_VARE_TO_12` | src/levels/_unified/ending/ending_channel_cleanup.inc:138 |
| `0x10` | cart | `INIT_VARE_TO_12` | src/levels/_unified/ending/cart__post_DELETE_ALL_CHANS_AND_KILL.inc:145 |
| `0x11` | amiga | `DRAW_CIN_024_LOOP__AMIGA__POST_INIT_VARS_07_08_09` | src/levels/_unified/ending/amiga__post_INIT_VARS_07_08_09.inc:17 |
| `0x11` | cart | `DRAW_CIN_024_LOOP__CART__POST_INIT_VARS_07_08_09` | src/levels/_unified/ending/cart__post_INIT_VARS_07_08_09.inc:17 |
| `0x11` | dos | `DRAW_CIN_024_LOOP__DOS__POST_INIT_VARS_07_08_09` | src/levels/_unified/ending/dos__post_INIT_VARS_07_08_09.inc:17 |
| `0x11` | shared | `DRAW_CIN_70_ANIM_LOOP` | src/levels/_unified/ending/ending_channel_cleanup.inc:139 |
| `0x11` | cart | `DRAW_CIN_70_ANIM_LOOP` | src/levels/_unified/ending/cart__post_DELETE_ALL_CHANS_AND_KILL.inc:146 |
| `0x12` | amiga | `DRAW_COMMON_VIDS_148_151_152_153` | src/levels/_unified/ending/amiga__post_INIT_VARS_07_08_09.inc:18 |
| `0x12` | cart | `DRAW_CV_192_195_196_SEQ__CART__POST_INIT_VARS_07_08_09` | src/levels/_unified/ending/cart__post_INIT_VARS_07_08_09.inc:18 |
| `0x12` | dos | `DRAW_CV_192_195_196_SEQ__DOS__POST_INIT_VARS_07_08_09` | src/levels/_unified/ending/dos__post_INIT_VARS_07_08_09.inc:18 |
| `0x13` | amiga | `DRAW_COMMON_VIDS_149_141_137_10` | src/levels/_unified/ending/amiga__post_INIT_VARS_07_08_09.inc:19 |
| `0x13` | cart | `DRAW_CV_193_185_181_SEQ__CART__POST_INIT_VARS_07_08_09` | src/levels/_unified/ending/cart__post_INIT_VARS_07_08_09.inc:19 |
| `0x13` | dos | `DRAW_CV_193_185_181_SEQ__DOS__POST_INIT_VARS_07_08_09` | src/levels/_unified/ending/dos__post_INIT_VARS_07_08_09.inc:19 |
| `0x14` | cart | `INIT_VARS_07_08_09` | src/levels/_unified/ending/cart__post_SET_VAR_E6_5_PAL_B.inc:123 |
| `0x14` | amiga | `INIT_VARS_07_08_09` | src/levels/_unified/ending/amiga__post_SET_VAR_E6_5_PAL_B.inc:123 |
| `0x14` | dos | `INIT_VARS_07_08_09` | src/levels/_unified/ending/dos__post_SET_VAR_E6_5_PAL_B.inc:123 |
| `0x14` | cart | `PAL_FADE_18_TO_1D` | src/levels/_unified/ending/cart__post_INIT_VARE_TO_12.inc:92 (+1 more) |
| `0x14` | amiga | `PAL_FADE_18_TO_1D` | src/levels/_unified/ending/amiga__post_DRAW_CIN_70_ANIM_LOOP.inc:39 |
| `0x14` | dos | `PAL_FADE_18_TO_1D` | src/levels/_unified/ending/dos__post_DRAW_CIN_70_ANIM_LOOP.inc:41 (+1 more) |
| `0x1E` | cart | `KILL_CHANNEL_LANDING` | src/levels/_unified/ending/cart__post_INIT_VARS_07_08_09.inc:47 |
| `0x1E` | amiga | `KILL_CHANNEL_LANDING` | src/levels/_unified/ending/amiga__post_INIT_VARS_07_08_09.inc:47 |
| `0x1E` | dos | `KILL_CHANNEL_LANDING` | src/levels/_unified/ending/dos__post_INIT_VARS_07_08_09.inc:47 |
| `0x1E` | amiga | `LABEL_0558` | src/levels/_unified/ending/amiga__entry.inc:284 |
| `0x1E` | dos | `LABEL_0662` | src/levels/_unified/ending/dos__entry.inc:287 |
| `0x1E` | cart | `LABEL_0676` | src/levels/_unified/ending/cart__entry.inc:287 |
| `0x36` | shared | `LABEL_022B` | src/levels/_unified/ending/ending_var_setups.inc:39 |
| `0x36` | cart | `LABEL_023B` | src/levels/_unified/ending/cart__post_INIT_VARE_TO_12.inc:22 |
| `0x3C` | cart | `BLITTER_LOOP_COPY_PAGE_00` | src/levels/_unified/ending/cart__entry.inc:281 |
| `0x3C` | amiga | `BLITTER_LOOP_COPY_PAGE_00` | src/levels/_unified/ending/amiga__entry.inc:278 |
| `0x3C` | dos | `BLITTER_LOOP_COPY_PAGE_00` | src/levels/_unified/ending/dos__entry.inc:281 |
| `0x3C` | cart | `BLITTER_LOOP_COPY_PAGE_80` | src/levels/_unified/ending/cart__post_INIT_VARE_TO_12.inc:85 |
| `0x3C` | amiga | `BLITTER_LOOP_COPY_PAGE_80` | src/levels/_unified/ending/amiga__post_DRAW_CIN_70_ANIM_LOOP.inc:32 |
| `0x3C` | dos | `BLITTER_LOOP_COPY_PAGE_80` | src/levels/_unified/ending/dos__post_DRAW_CIN_70_ANIM_LOOP.inc:34 |
| `0x3C` | cart | `SCROLL_Y_BLIT_DISPATCHER` | src/levels/_unified/ending/cart__post_INIT_VARE_TO_12.inc:211 |
| `0x3C` | dos | `SCROLL_Y_BLIT_DISPATCHER` | src/levels/_unified/ending/dos__post_DRAW_CIN_70_ANIM_LOOP.inc:117 |

## Channel role inference (per stage)

Compact heatmap: for each (stage, channel) the routine names setup-called on that channel are binned by well-known prefix patterns; the dominant category is shown. Empty cells mean the stage doesn't use that channel; `?` means every routine on that channel is a `LABEL_HHHH` placeholder (no semantic signal yet).

Categories: `blit` (BLIT_*), `cin-draw` (DRAW_CIN_*),
`cv-draw` (DRAW_CV_* / INLINE_DRAW_CV_*),
`framebuf` (CLEAR_/FILL_/COPY_PAGE_*),
`actor` (HERO_/BEAST_/…), `anim` (*_LOOP, ANIM_*),
`init` (INIT_/SETUP_/INLINE_SET_), `cleanup` (KILL_CHANNEL_*),
`music` (MUSIC_/SFX_/PLAY_*), `delay`, `scroll`,
`unnamed` (only LABEL_HHHH), `mixed` (no clear winner).

| channel | CAPSULE | CAVES | CODE_WHEEL | ENDING | INTRO | LAKE | PASSCODE | PRISON | TANK |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `0x00` | unnamed | unnamed |  |  |  | other |  | unnamed | mixed |
| `0x01` | unnamed | unnamed |  |  | mixed | other |  | unnamed | mixed |
| `0x02` | mixed | init |  |  | init | other |  | unnamed | unnamed |
| `0x03` | unnamed | mixed |  |  | mixed | other |  | unnamed |  |
| `0x04` | unnamed | mixed |  |  | cleanup | anim |  | unnamed | unnamed |
| `0x05` | unnamed | unnamed |  | cin-draw | cleanup | other |  | unnamed |  |
| `0x06` | unnamed | unnamed |  |  | cleanup | actor |  |  | unnamed |
| `0x07` | cleanup | unnamed |  |  | cleanup | mixed |  |  |  |
| `0x08` | other | unnamed |  |  | mixed | actor |  | mixed |  |
| `0x09` |  |  |  |  | other | actor |  |  | unnamed |
| `0x0A` |  |  | unnamed | mixed | mixed | other |  | mixed | unnamed |
| `0x0B` |  |  |  | cin-draw | mixed | other |  |  | mixed |
| `0x0C` |  |  |  | cin-draw | mixed | mixed |  |  |  |
| `0x0D` |  |  |  | unnamed | mixed | other |  |  |  |
| `0x0E` |  |  | unnamed | other | mixed | mixed |  |  | cin-draw |
| `0x0F` | mixed | unnamed |  | cin-draw | mixed | other |  |  | init |
| `0x10` | unnamed | unnamed |  | init | mixed | actor |  | unnamed |  |
| `0x11` |  |  |  | cin-draw | mixed | other |  | cin-draw |  |
| `0x12` |  |  |  | cv-draw | init | actor |  | cin-draw |  |
| `0x13` | other | mixed |  | cv-draw | anim | anim |  |  |  |
| `0x14` | unnamed | unnamed | init | mixed | mixed | actor | init | unnamed | unnamed |
| `0x15` | mixed | unnamed |  |  | mixed | mixed |  | mixed | unnamed |
| `0x16` | unnamed | mixed |  |  | anim | mixed |  | unnamed | unnamed |
| `0x17` | unnamed | unnamed |  |  | anim | other |  | unnamed | other |
| `0x18` | unnamed | unnamed |  |  | anim | actor |  | unnamed | unnamed |
| `0x19` | cleanup | unnamed |  |  | anim |  |  |  | unnamed |
| `0x1A` | unnamed | unnamed |  |  | anim |  |  | unnamed | unnamed |
| `0x1B` | mixed | init |  |  | anim |  |  |  |  |
| `0x1C` |  | unnamed |  |  | anim |  |  |  | unnamed |
| `0x1D` | mixed |  |  |  | anim |  |  |  |  |
| `0x1E` |  |  | mixed | mixed | anim |  |  |  |  |
| `0x1F` |  |  |  |  | anim |  |  |  | unnamed |
| `0x20` |  |  |  |  |  |  |  |  | mixed |
| `0x21` |  | cleanup |  |  |  |  |  | unnamed | unnamed |
| `0x22` | unnamed | unnamed |  |  |  |  |  | unnamed | cin-draw |
| `0x23` | unnamed | unnamed |  |  |  |  |  | unnamed | mixed |
| `0x24` | unnamed | unnamed |  |  |  | other |  | unnamed | unnamed |
| `0x25` | mixed | mixed |  |  |  | other |  | unnamed | unnamed |
| `0x26` | unnamed | unnamed |  |  |  |  |  | unnamed | unnamed |
| `0x27` | unnamed | mixed |  |  |  |  |  | unnamed |  |
| `0x28` | unnamed | unnamed |  |  |  | actor |  | unnamed | mixed |
| `0x29` |  | unnamed |  |  |  | mixed |  | unnamed |  |
| `0x2A` | other | mixed |  |  |  |  |  | unnamed | init |
| `0x2B` | init | mixed |  |  |  | actor |  | unnamed |  |
| `0x2C` | mixed | init | other |  |  | mixed |  |  |  |
| `0x2D` | mixed | init |  |  |  | other |  |  |  |
| `0x2E` | mixed | unnamed |  |  |  | actor |  |  |  |
| `0x2F` | mixed | unnamed |  |  |  | anim |  | unnamed | unnamed |
| `0x30` | unnamed | unnamed |  |  |  | delay |  | unnamed | cin-draw |
| `0x31` | unnamed | unnamed |  |  |  | other |  | unnamed | cin-draw |
| `0x32` | unnamed | unnamed | other |  |  |  |  | unnamed |  |
| `0x33` | unnamed | unnamed |  |  |  | init |  | unnamed |  |
| `0x34` | unnamed | unnamed |  |  |  | mixed |  | mixed | unnamed |
| `0x35` | unnamed | mixed |  |  |  | other |  | unnamed | init |
| `0x36` | unnamed | unnamed |  | unnamed |  | cleanup |  | unnamed |  |
| `0x37` | unnamed | mixed |  |  |  | other |  | unnamed | unnamed |
| `0x38` | unnamed | unnamed |  |  |  | mixed |  | mixed | unnamed |
| `0x39` | unnamed | unnamed |  |  |  |  |  | unnamed | mixed |
| `0x3A` | unnamed | unnamed |  |  |  |  |  | unnamed |  |
| `0x3B` | cleanup | unnamed |  |  |  | other |  | mixed | mixed |
| `0x3C` | unnamed | unnamed | unnamed | blit | blit | blit | mixed | mixed | other |
| `0x3E` | unnamed | mixed |  |  |  |  |  |  |  |
| `0x3F` | mixed | unnamed | unnamed |  |  | mixed |  | unnamed | unnamed |

