#!/usr/bin/env python3
"""Generate a Markdown index of every `tools/*.py` script.

For each tool, extracts the FIRST line of its module docstring as
a one-line description. Outputs `docs/content/tools.md`, sorted
alphabetically. Re-run after adding or significantly editing any
tool.
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

REPO_ROOT = Path("/home/fsanches/compartilhado/another-world-archaeology")
TOOLS = REPO_ROOT / "tools"


def first_doc_line(path: Path) -> str | None:
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError:
        return None
    docstring = ast.get_docstring(tree)
    if not docstring:
        return None
    # Take the first non-empty line; strip leading bullet/punctuation.
    for line in docstring.splitlines():
        s = line.strip()
        if s:
            return s
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "docs" / "content" / "tools.md",
    )
    args = parser.parse_args()

    md: list[str] = []
    md.append("# Tools index")
    md.append("")
    md.append(
        "Auto-generated alphabetical list of every `tools/*.py` "
        "script in this repo, with the first line of each tool's "
        "module docstring as a one-line description. Re-run "
        "`python3 tools/build_tool_index.py` after adding a tool "
        "(or wire it into `make docs` if you forget often)."
    )
    md.append("")

    tool_paths = sorted(TOOLS.glob("*.py"))
    md.append(f"**{len(tool_paths)} tools.**")
    md.append("")
    md.append("| Tool | Purpose |")
    md.append("| --- | --- |")
    for p in tool_paths:
        if p.name == "__init__.py":
            continue
        desc = first_doc_line(p) or "_(no docstring)_"
        # Escape any pipe characters in description for table layout.
        desc = desc.replace("|", "\\|")
        md.append(f"| `{p.name}` | {desc} |")
    md.append("")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(md) + "\n")
    print(f"wrote {args.out} ({len(tool_paths)} tools)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
