# Another World Archaeology — top-level pipeline.
#
# Most stages are gated on infrastructure that is still being built up;
# unimplemented targets fail loudly with a pointer to the relevant TODO
# rather than silently doing nothing.

PYTHON ?= python3

.PHONY: help all docs docs-deploy tools fetch extract disasm verify-references check clean

help:
	@echo "Targets:"
	@echo "  make docs                Full local rebuild: channel-map regen + docs/data/all.js"
	@echo "  make docs-deploy         Bake docs/data/all.js only (CI-safe; no source-reconstruction needed)"
	@echo "  make tools               Clone or update sibling AnotherWorld_VMTools at pinned commit"
	@echo "  make fetch               Download release files listed in metadata.json into original_files/"
	@echo "  make extract             Extract resources for every release"
	@echo "  make extract SLUG=<slug> Extract a single release (by metadata.json slug)"
	@echo "  make disasm              Disassemble BYTECODE resources via awvm-disasm"
	@echo "  make verify-references   Check sha256 of every file listed in references/MANIFEST.sha256"
	@echo "  make check               Quick health checks: issue-tracker schema + ;@raw= ban + reference hashes"
	@echo "  make clean               Remove generated artefacts (preserves original_files/, cruft/, sessions/)"

all: docs

docs: docs-channel-map docs-deploy

# CI-safe subset: bakes the static site bundle from already-committed
# markdown under docs/content/ and JSON/CSV under docs/. Does NOT touch
# tools that read the sibling another-world-source-reconstruction repo
# (those run via `docs-channel-map` only on machines that have it).
docs-deploy:
	@$(PYTHON) tools/gen_docs_data.py

# Regenerate per-stage VM channel map (research/17), the
# role-inference heatmap section, and the unnamed-setup-target
# working list (`docs/unnamed_setup_targets.md`). Run whenever a
# semantic-rename round lands so the docs reflect the current
# source state. Requires the sibling `another-world-source-reconstruction`
# checkout — not safe to run on CI without it.
.PHONY: docs-channel-map
docs-channel-map:
	@$(PYTHON) tools/build_channel_map.py
	@$(PYTHON) tools/build_channel_role_summary.py
	@$(PYTHON) tools/list_unnamed_setup_targets.py
	@$(PYTHON) tools/build_tool_index.py

tools:
	@echo "make tools: not yet implemented (TODO: tools/sync_external_tools.py to clone or fast-forward AWVM_Tools at the commit pinned in tools/AWVM_Tools.lock)"
	@exit 1

fetch:
	@echo "make fetch: not yet implemented (TODO: tools/fetch.py to download metadata.json[*].download URLs into original_files/<md5>/, verify md5, and archive sources to the Wayback Machine)"
	@exit 1

extract:
	@$(PYTHON) extract.py $(if $(SLUG),--slug $(SLUG))

disasm:
	@echo "make disasm: not yet implemented (depends on AWVM_Tools sibling clone + extract output)"
	@exit 1

verify-references:
	@$(PYTHON) tools/verify_references.py

# Quick health-check sweep: fast tools that detect known regressions.
# - Issue tracker schema/reference integrity (`tools/issues.py validate`)
# - `;@raw=` annotation ban (Phase 2 of #0083; should remain at zero
#   in active source forever after the migration completed 2026-05-04)
# - References-manifest hashes (frozen-file integrity)
.PHONY: check
check:
	@$(PYTHON) tools/issues.py validate
	@$(PYTHON) tools/audit_raw_annotations.py --strict
	@$(PYTHON) tools/verify_references.py

clean:
	rm -rf docs/data/ work/
	@echo "cleaned: docs/data/, work/"
	@echo "(preserved: original_files/, cruft/, sessions/)"
