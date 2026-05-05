#!/usr/bin/env python3
"""Generate docs/data/all.js from docs/content/**/*.md and issues/*.md.

The output is loaded by docs/index.html and populates window.AWA with
everything the static viewer needs. The output file is gitignored.

Shape:
    window.AWA = {
      generated_at: "<UTC ISO-8601>",
      content:     { <relative_path_without_md>: "<raw markdown>", ... }
    };
"""

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO / "docs" / "content"
ISSUES_DIR = REPO / "issues"
DATA_DIR = REPO / "docs" / "data"


def load_content():
    out = {}
    if CONTENT_DIR.is_dir():
        for path in sorted(CONTENT_DIR.rglob("*.md")):
            key = path.relative_to(CONTENT_DIR).with_suffix("").as_posix()
            out[key] = path.read_text(encoding="utf-8")
    # Also surface the issue tracker — the structured issue files in
    # `issues/` (not under docs/content/) need to be browsable from
    # the static site. Keys are namespaced under `issues/<id-slug>`,
    # plus the auto-generated index at `issues` and the schema at
    # `issues/SCHEMA`.
    if ISSUES_DIR.is_dir():
        for path in sorted(ISSUES_DIR.rglob("*.md")):
            rel = path.relative_to(ISSUES_DIR).with_suffix("")
            if rel.as_posix() == "README":
                key = "issues"
            else:
                key = "issues/" + rel.as_posix()
            out[key] = path.read_text(encoding="utf-8")
    return out


def main():
    content = load_content()

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "content": content,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / "all.js"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("window.AWA = ")
        json.dump(payload, f, ensure_ascii=False)
        f.write(";\n")

    size_kb = out_path.stat().st_size / 1024
    print(
        f"wrote {out_path.relative_to(REPO)}: "
        f"{len(content)} content page(s), {size_kb:.1f} KB"
    )


if __name__ == "__main__":
    main()
