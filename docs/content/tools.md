# Tools index

Auto-generated alphabetical list of every `tools/*.py` script in this repo, with the first line of each tool's module docstring as a one-line description. Re-run `python3 tools/build_tool_index.py` after adding a tool (or wire it into `make docs` if you forget often).

**101 tools.**

| Tool | Purpose |
| --- | --- |
| `add_stage_doc_headers.py` | Phase 2: prepend stage-narrative documentation headers to each |
| `asset_references.py` | Scan a port's full disassembly tree for asset references — `video`, |
| `attribute_cut_polygons.py` | For each stage's cut/added polygons, attribute the parent group |
| `audit_raw_annotations.py` | Audit `;@raw=...` annotations. |
| `auto_fold.py` | Auto-fold v5: handles dedup-named multi-label tuples by splitting |
| `auto_fold_dedup.py` | Resolve ambiguous fold candidates: when multiple labels in one |
| `auto_fold_rename.py` | Improved auto-fold renamer — catches more patterns and 2-arm folds. |
| `aw_music_to_wav.py` | Render an Another World MUSIC resource to WAV. |
| `aw_sound_to_wav.py` | Render a single Another World SOUND resource to a WAV file. |
| `awvm_preprocess.py` | Preprocessor for AW VM .asm.in source files with conditional blocks. |
| `batch_render_cut_polys.py` | Batch-render every offset in cut_polygons_amiga_only.json (or |
| `build_channel_map.py` | Extract a per-stage map of `setup channel=NN, address=…` opcodes |
| `build_channel_role_summary.py` | Inferred channel-role summary, complementing |
| `build_reachability_graph.py` | Build a static reachability graph for an AW VM port's bytecode. |
| `build_tool_index.py` | Generate a Markdown index of every `tools/*.py` script. |
| `bytecode_structural_diff.py` | Cross-branch structural-similarity analysis for AW VM bytecode. |
| `canonicalize_bankswitch.py` | Convert `bankSwitch N` mnemonic forms to `load id=0x<HHLL>`. |
| `canonicalize_cinematic_refs.py` | Canonicalize cross-port CINEMATIC_xxxx synonym names by walking |
| `canonicalize_inline_labels.py` | Canonicalize inline `LABEL_NNNN:` labels across branches via structural |
| `canonicalize_labels.py` | Canonicalize synonym labels across N branches' .asm files. |
| `categorize_raw_residue.py` | Categorise the surviving `;@raw=` annotations in the unified |
| `collapse_empty_arms.py` | Collapse empty `;@if`/`;@elif`/`;@else`/`;@endif` arms. |
| `compress_fill_padding.py` | Compress trailing runs of 'db 0xFF, ...' into FILL(n, 0xFF) macros. |
| `consolidate_common_vars.py` | Phase 1b: replace inline var-alias EQUs in per-branch and unified |
| `cross_port_polygon_diff.py` | Cross-port polygon-byte diff for a single stage. |
| `cross_port_used_polygon_diff.py` | Cross-port USED-polygon diff for a single stage. |
| `cross_release_md5_index.py` | Build a cross-release md5 index for AW resources. |
| `detect_setup_gates.py` | Detect setup-then-overwrite gates in AW VM bytecode. |
| `disambiguate_intra_chunk_dups.py` | Disambiguate intra-chunk duplicate label definitions. |
| `equ_alias_for_stuck_literals.py` | For each literal-address operand that `resymbolize_literals.py` |
| `extract_cross_stage_helpers.py` | Phase 6: extract cross-stage shared helpers to `_unified/_helpers/`. |
| `find_cross_stage.py` | Find routines whose bodies match across multiple stages. |
| `find_foldable_routines.py` | Find byte-identical routine pairs across the per-branch arms of a stage. |
| `find_parent_polygons.py` | Find PARENT group polygons that reference a given child polygon. |
| `find_singletons.py` | Find labels with body = single 'ret' or 'killChannel'. |
| `find_unused_polygons.py` | Per-port × per-level unused-polygon scan. |
| `fold_body_rename_round_10.py` | Phase 4 / Round 10: name 2 more FOLD_BODY routines I had skipped |
| `fold_body_rename_round_5.py` | Phase 4 / Round 5: rename FOLD_BODY routines whose 3-instruction |
| `fold_body_rename_round_6.py` | Phase 4 / Round 6: 37 more FOLD_BODY routines named from body shape. |
| `fold_body_rename_round_7.py` | Phase 4 / Round 7: 29 more FOLD_BODY routines named from body shape. |
| `fold_body_rename_round_8.py` | Phase 4 / Round 8: 13 more FOLD_BODY routines named from body shape. |
| `fold_body_rename_round_9.py` | Phase 4 / Round 9: 24 more FOLD_BODY routines named from body shape. |
| `gen_docs_data.py` | Generate docs/data/all.js from sessions/*.jsonl and docs/content/**/*.md. |
| `issues.py` | Issue tracker CLI for the Another World archaeology project. |
| `list_unnamed_setup_targets.py` | List `LABEL_HHHH` placeholder routines that are setup-targets, |
| `localize_single_use_equs.py` | For each `_unified/<STAGE>.asm.in`, find EQU declarations whose |
| `match_arms.py` | Match named routines from one arm to numeric labels in another arm |
| `migrate_raw_to_enc.py` | Rewrite `;@raw=…` annotations as `;@enc=…` (or as explicit |
| `multi_fold.py` | Multi-fold helper. v2: respects per-routine fold-arm sets. |
| `polygon_render.py` | Render an AW polygon (solid or group) from a POLY_CINEMATIC / |
| `polygon_render_png.py` | Render an AW polygon to PNG via Python's cairo binding. |
| `polygon_walker.py` | Walk an AW polygon resource (POLY_CINEMATIC or POLY_ANIM) and emit |
| `raw_annotation_snapshot.py` | Snapshot the load-bearing `;@raw=` residue. |
| `reconstruct_arms.py` | Reconstruct un-split per-arm `.inc` files from a folded `<STAGE>.asm.in` |
| `redisasm_db.py` | Re-disassemble `db` blocks in an AW VM .asm source. |
| `remove_empty_chunks.py` | Remove empty per-arm chunk files and their corresponding ;@include |
| `remove_empty_chunks_safe.py` | Phase 5: remove empty per-arm chunk files (CAVES + ENDING). |
| `rename_chunks.py` | Rename chunk files to match the routine name they follow. |
| `rename_collision_labels.py` | Per-chunk rename of collision-suffering label definitions. |
| `rename_dedup.py` | Rename DEDUP_<STAGE>_<size>B_<seq> routines to body-shape names. |
| `rename_dispatcher_cases.py` | Phase 3: rename `LABEL_<HEX>` case-targets of named dispatchers. |
| `rename_fold_bodies.py` | Aggressive FOLD_BODY renamer. |
| `render_at_all_palettes.py` | Render one polygon offset at every palette in a PALETTE resource. |
| `render_lake_catalog.py` | Render every CINEMATIC_xxx polygon in the amiga LAKE source to SVG + |
| `render_palette_swatches.py` | Render an Another World PALETTE resource as a 32×16 SVG grid |
| `render_unused_assets.py` | Render every unused polygon for a port × level + emit an HTML gallery. |
| `resolve_raw_collisions.py` | Resolve every surviving `;@raw=` annotation by replacing the |
| `resymbolize_literals.py` | Re-symbolise literal-address operands inserted by |
| `roundtrip_bytecode.py` | Per-target round-trip test for AW VM bytecode. |
| `scan_cross_stage_helpers.py` | Phase 6 prep: find routines defined in 2+ stages with byte-identical |
| `simulate_gun_budget.py` | Illustrate the gun-energy quota mechanics from research finding #01. |
| `split_asm_chapter.py` | Helper to split a chapter out of a unified .asm.in into a .inc file. |
| `standardize_cinematic_frame_suffix.py` | Standardize CINEMATIC frame-index suffixes to bare `_N`. |
| `strip_redundant_raw.py` | Strip redundant ;@raw= comments from .asm files. |
| `strip_redundant_raw_annotations.py` | Strip `;@raw=` annotations whose presence does not change the |
| `strip_redundant_raw_chunks.py` | Strip chunks with broader keeper set. |
| `strip_redundant_raw_unified.py` | Strip redundant ;@raw= from unified .asm.in/.inc files. |
| `strip_redundant_raw_unified_chunks.py` | Strip redundant `;@raw=` annotations from per-arm chunks |
| `strip_redundant_raw_unified_shared.py` | Strip redundant `;@raw=` annotations from shared unified chunks. |
| `strip_unused_equs.py` | Strip unused EQU declarations from .asm files. |
| `strip_unused_equs_all_chunks.py` | Strip unused EQUs from ALL chunks under `_unified/<stage>/`, |
| `strip_unused_equs_unified.py` | Strip unused EQU declarations from unified stage chunks. |
| `sync_aggressive.py` | Aggressive sync — abstract LABEL_<HEX>, CINEMATIC_<NNN>, COMMON_VIDEO_<NNN> |
| `sync_all_chunks_to_per_branch.py` | Sync semantic renames from ALL `_unified/<stage>/*.inc` chunks |
| `sync_cross_branch.py` | Sync cart per-branch's named routines to dos/amiga per-branch. |
| `sync_intro_aggressive.py` | Aggressive INTRO sync — abstract CIN/CV operands. |
| `sync_intro_other_branches.py` | Sync semantic renames from cartridge_1992/INTRO.asm into other branches. |
| `sync_intro_renames.py` | Sync semantic renames from unified/intro/*.inc into cartridge_1992/INTRO.asm. |
| `sync_lake_renames.py` | Sync LAKE renames from unified/lake/*.inc into per-branch LAKE.asm sources. |
| `sync_stage_renames.py` | Sync semantic renames from _unified/<stage>/<arm>__*.inc chunks |
| `unify_asm.py` | Generate a unified .asm.in source from two divergent per-branch .asm files. |
| `unify_cross_stage_names.py` | Unify names across stages for routines with identical bodies. |
| `unused_palette_scan.py` | Naive unused-PALETTE scanner. |
| `unused_palette_scan_v2.py` | Unused-PALETTE scanner with reachability filtering (post-#0058). |
| `unused_polygon_scan_v2.py` | Reachability-filtered polygon-reference scanner for #0054. |
| `unused_sound_scan.py` | Naive unused-SOUND scanner for a DOS-format port. |
| `unused_sound_scan_v2.py` | Unused-SOUND scanner with reachability filtering (post-#0058). |
| `verify_references.py` | Verify the integrity of every file listed in `references/MANIFEST.sha256`. |
| `verify_resources.py` | Per-port verification that all extracted resources match expected md5s. |
| `verify_stage.py` | Phase 3a stage-based byte-match verifier. |
| `verify_unified.py` | Verify the unified `.asm.in` → preprocess → assemble path byte-matches |

