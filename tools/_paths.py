"""Canonical filesystem paths for the archaeology repo + sibling repos.

Exports `REPO_ROOT` (this repo), `AW_SRC` (the source-reconstruction
sibling), `AWVM_TOOLS` (the AnotherWorld_VMTools sibling), and
`AWVM_ASM` (the disassembler binary inside it). All resolved relative
to this file's location, so the paths follow the checkout — no
per-machine hardcoding. Replaces the `/home/fsanches/compartilhado/...`
string literals that used to be copy-pasted into every tool.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AW_SRC = REPO_ROOT.parent / "another-world-source-reconstruction"
AWVM_TOOLS = REPO_ROOT.parent / "AnotherWorld_VMTools"
AWVM_ASM = AWVM_TOOLS / "target/release/awvm-asm"
