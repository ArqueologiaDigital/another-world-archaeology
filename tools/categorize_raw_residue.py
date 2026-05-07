#!/usr/bin/env python3
"""Categorise the surviving `;@raw=` annotations in the unified
tree to guide the per-case investigation in #0086.

For each annotation:
  - Parse the source line (mnemonic, operands).
  - Identify the symbol(s) the annotation's bytes correspond to
    (jump target word, video offset operand, etc.).
  - Look up that symbol's definitions across the unified tree.
  - Bucket: collision (>1 definition) vs single-def vs no-def.

Output: a Markdown report grouping annotations by symbol and
collision status.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

from _paths import AW_SRC, REPO_ROOT

SRC_TREE = AW_SRC
LEVELS = SRC_TREE / "src" / "levels"
UNIFIED = LEVELS / "_unified"

RE_RAW = re.compile(r"\s*;@raw=([0-9a-fA-FxX,\s]+)\s*$")
RE_LABEL_DEF = re.compile(r"^([A-Z_][A-Z0-9_]*):", re.MULTILINE)
RE_EQU = re.compile(r"^([A-Z_][A-Z0-9_]*)\s*EQU\s+(\S+)", re.MULTILINE)


def all_definitions() -> dict[str, list[tuple[Path, int, str]]]:
    """name → list of (file, line, kind)."""
    out: dict[str, list[tuple[Path, int, str]]] = defaultdict(list)
    for path in sorted(LEVELS.rglob("*.inc")) + sorted(
        LEVELS.rglob("*.asm.in")
    ) + sorted(LEVELS.rglob("*.asm")):
        # Skip frozen reference dirs
        rel = path.relative_to(LEVELS)
        if rel.parts and rel.parts[0] in {"_canonicalized", "_phase3b_demo"}:
            continue
        try:
            text = path.read_text()
        except OSError:
            continue
        for m in RE_LABEL_DEF.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            out[m.group(1)].append((path, line_no, "label"))
        for m in RE_EQU.finditer(text):
            line_no = text[: m.start()].count("\n") + 1
            out[m.group(1)].append((path, line_no, f"equ={m.group(2)}"))
    return out


def parse_operand_symbols(line: str) -> list[str]:
    """Extract referenced UPPERCASE symbol names from a source line."""
    body = line.split(";")[0]  # strip comment + raw annotation
    return re.findall(r"\b[A-Z_][A-Z0-9_]{2,}\b", body)


def main() -> int:
    defs = all_definitions()

    # Walk all unified files, find every `;@raw=` line.
    annotations: list[dict] = []
    for path in sorted(UNIFIED.rglob("*.inc")) + sorted(
        UNIFIED.rglob("*.asm.in")
    ):
        try:
            text = path.read_text()
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            m = RE_RAW.search(line)
            if not m:
                continue
            mnemonic = (line.split(None, 1) or [""])[0].strip()
            symbols = parse_operand_symbols(line)
            interesting = [
                s
                for s in symbols
                if s in defs and not _is_trivial(s)
            ]
            annotations.append(
                {
                    "file": path,
                    "line_no": line_no,
                    "src": line[: m.start()].rstrip(),
                    "raw": m.group(1).strip(),
                    "mnemonic": mnemonic,
                    "symbols": interesting,
                }
            )

    # Bucket: for each annotation, classify by max-collision symbol.
    by_symbol: dict[str, list[dict]] = defaultdict(list)
    no_symbol: list[dict] = []
    single_def: list[dict] = []
    for a in annotations:
        bucket_symbol = None
        max_defs = 0
        for s in a["symbols"]:
            n = len(defs.get(s, []))
            if n > max_defs:
                max_defs = n
                bucket_symbol = s
        if not bucket_symbol:
            no_symbol.append(a)
        elif max_defs <= 1:
            single_def.append(a)
        else:
            by_symbol[bucket_symbol].append(a)

    md: list[str] = []
    md.append("# `;@raw=` residue categorisation")
    md.append("")
    md.append(
        f"Total annotations surveyed: **{len(annotations)}** in "
        f"unified tree.\n"
    )
    md.append(
        f"- annotations with a multiply-defined operand symbol: "
        f"**{sum(len(v) for v in by_symbol.values())}** "
        f"(across {len(by_symbol)} distinct symbols)"
    )
    md.append(
        f"- annotations whose symbol has only one definition: "
        f"**{len(single_def)}**"
    )
    md.append(
        f"- annotations with no resolvable symbol: "
        f"**{len(no_symbol)}**"
    )
    md.append("")

    md.append(
        "## Multi-defined symbol groups (probable EQU/label collision)"
    )
    md.append("")
    md.append(
        "Each section: a symbol name + every definition site + every "
        "annotated call site. The symbol values across definitions "
        "tell you whether the collision is genuine "
        "(different addresses/values) or coincidence (same value at "
        "multiple sites — safe to canonicalise)."
    )
    md.append("")
    for symbol, calls in sorted(
        by_symbol.items(), key=lambda kv: -len(kv[1])
    ):
        md.append(f"### `{symbol}` — {len(calls)} annotated call site(s)")
        md.append("")
        md.append("**Definitions:**")
        md.append("")
        for f, ln, kind in defs[symbol]:
            md.append(
                f"- `{f.relative_to(SRC_TREE)}:{ln}` ({kind})"
            )
        md.append("")
        md.append("**Annotated call sites (first 5):**")
        md.append("")
        for a in calls[:5]:
            md.append(
                f"- `{a['file'].relative_to(SRC_TREE)}:{a['line_no']}` — "
                f"`{a['src'].strip()}` ⇒ `;@raw={a['raw']}`"
            )
        if len(calls) > 5:
            md.append(f"- …and {len(calls) - 5} more")
        md.append("")

    if single_def:
        md.append("## Single-defined-symbol residue")
        md.append("")
        md.append(
            "Annotations whose operand symbols are all "
            "single-definition. Likely a different cause "
            "(non-canonical operand encoding the migration didn't "
            "catalogue, or a numeric/literal operand that the "
            "encoder produces differently)."
        )
        md.append("")
        for a in single_def[:30]:
            md.append(
                f"- `{a['file'].relative_to(SRC_TREE)}:{a['line_no']}` — "
                f"`{a['src'].strip()}` ⇒ `;@raw={a['raw']}`"
            )
        if len(single_def) > 30:
            md.append(f"- …and {len(single_def) - 30} more")
        md.append("")

    if no_symbol:
        md.append("## No-symbol residue")
        md.append("")
        md.append(
            "Annotations with no resolvable operand symbol "
            "(e.g., immediate-only instructions). These are "
            "candidates for direct `;@enc=…` patterns we haven't "
            "catalogued yet."
        )
        md.append("")
        for a in no_symbol[:30]:
            md.append(
                f"- `{a['file'].relative_to(SRC_TREE)}:{a['line_no']}` — "
                f"`{a['src'].strip()}` ⇒ `;@raw={a['raw']}`"
            )
        if len(no_symbol) > 30:
            md.append(f"- …and {len(no_symbol) - 30} more")
        md.append("")

    out_path = REPO_ROOT / "docs" / "raw_residue_categorisation.md"
    out_path.write_text("\n".join(md) + "\n")
    print(f"wrote {out_path}")
    return 0


def _is_trivial(s: str) -> bool:
    """Symbols that are too generic to be meaningful for clustering."""
    return s in {
        "BRANCH",
        "OK",
        "FAIL",
        "EQU",
    }


if __name__ == "__main__":
    sys.exit(main())
