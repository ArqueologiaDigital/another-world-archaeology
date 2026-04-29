# Another World Archaeology — top-level pipeline.
#
# Most stages are gated on infrastructure that is still being built up;
# unimplemented targets fail loudly with a pointer to the relevant TODO
# rather than silently doing nothing.

PYTHON ?= python3

.PHONY: help all docs tools fetch extract disasm verify-references clean

help:
	@echo "Targets:"
	@echo "  make docs                Regenerate docs/data/all.js from sessions/ + docs/content/"
	@echo "  make tools               Clone or update sibling AnotherWorld_VMTools at pinned commit"
	@echo "  make fetch               Download release files listed in metadata.json into original_files/"
	@echo "  make extract             Extract resources for every release"
	@echo "  make extract SLUG=<slug> Extract a single release (by metadata.json slug)"
	@echo "  make disasm              Disassemble BYTECODE resources via awvm-disasm"
	@echo "  make verify-references   Check sha256 of every file listed in references/MANIFEST.sha256"
	@echo "  make clean               Remove generated artefacts (preserves original_files/, cruft/, sessions/)"

all: docs

docs:
	@$(PYTHON) tools/gen_docs_data.py

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

clean:
	rm -rf docs/data/ work/
	@echo "cleaned: docs/data/, work/"
	@echo "(preserved: original_files/, cruft/, sessions/)"
