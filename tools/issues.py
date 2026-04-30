#!/usr/bin/env python3
"""Issue tracker CLI for the Another World archaeology project.

The canonical state is the per-issue files under `issues/`. This
tool reads them, validates schemas, regenerates the auto-generated
index, and lets new issues be created with the next available ID.

See `issues/SCHEMA.md` for the schema and policies.

Subcommands:
    issues.py list [--status STATUS] [--tier TIER] [--tag TAG]
    issues.py new --title TITLE --tier TIER [--tags TAG1,TAG2 ...]
    issues.py index
    issues.py validate
    issues.py show ID
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
ISSUES_DIR = REPO / "issues"
INDEX_FILE = ISSUES_DIR / "README.md"

VALID_STATUSES = ("open", "in-progress", "blocked", "done", "wontfix")
VALID_TIERS = ("A", "B", "C", "D", "none")

REQUIRED_FIELDS = ("id", "title", "status", "tier", "created", "updated")
ID_RE = re.compile(r"^\d{4}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FILENAME_RE = re.compile(r"^(\d{4})-([a-z0-9][a-z0-9-]*)\.md$")
FRONTMATTER_SPLIT = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = FRONTMATTER_SPLIT.match(text)
    if not m:
        raise ValueError("missing or malformed frontmatter (expected '---' fences)")
    fm: dict[str, Any] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"frontmatter line lacks ':': {line!r}")
        k, _, v = line.partition(":")
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            v = [tok.strip() for tok in inner.split(",") if tok.strip()] if inner else []
        fm[k.strip()] = v
    return fm, m.group(2)


def load_issues() -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if not ISSUES_DIR.is_dir():
        return issues
    for path in sorted(ISSUES_DIR.iterdir()):
        if not path.is_file():
            continue
        if path.name in ("README.md", "SCHEMA.md"):
            continue
        if not FILENAME_RE.match(path.name):
            sys.exit(f"{path}: filename does not match <NNNN>-<slug>.md")
        try:
            fm, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        except ValueError as e:
            sys.exit(f"{path}: {e}")
        for field in REQUIRED_FIELDS:
            if field not in fm:
                sys.exit(f"{path}: missing required field '{field}'")
        fm.setdefault("depends_on", [])
        fm.setdefault("blocks", [])
        fm.setdefault("tags", [])
        for list_field in ("depends_on", "blocks", "tags"):
            if not isinstance(fm[list_field], list):
                sys.exit(f"{path}: '{list_field}' must be a list")
        if not ID_RE.match(str(fm["id"])):
            sys.exit(f"{path}: id {fm['id']!r} must be 4 digits")
        fname_id = path.name[:4]
        if fm["id"] != fname_id:
            sys.exit(f"{path}: filename id {fname_id} != frontmatter id {fm['id']}")
        if fm["status"] not in VALID_STATUSES:
            sys.exit(f"{path}: status {fm['status']!r} not in {VALID_STATUSES}")
        if fm["tier"] not in VALID_TIERS:
            sys.exit(f"{path}: tier {fm['tier']!r} not in {VALID_TIERS}")
        for date_field in ("created", "updated"):
            if not DATE_RE.match(fm[date_field]):
                sys.exit(f"{path}: '{date_field}' must be YYYY-MM-DD")
        fm["_path"] = path
        fm["_body"] = body
        issues.append(fm)
    return issues


def cmd_list(args, issues):
    rows = issues
    if args.status:
        rows = [i for i in rows if i["status"] == args.status]
    if args.tier:
        rows = [i for i in rows if i["tier"] == args.tier]
    if args.tag:
        rows = [i for i in rows if args.tag in i.get("tags", [])]
    for i in sorted(rows, key=lambda x: x["id"]):
        print(f"#{i['id']}  {i['status']:<11}  tier={i['tier']:<4}  {i['title']}")


def cmd_show(args, issues):
    target = args.id.zfill(4)
    for i in issues:
        if i["id"] == target:
            print(i["_path"].read_text(encoding="utf-8"), end="")
            return
    sys.exit(f"no issue #{target}")


def cmd_new(args, issues):
    next_id = 1
    if issues:
        next_id = int(max(i["id"] for i in issues)) + 1
    if next_id > 9999:
        sys.exit("ID space exhausted (would exceed 9999)")
    nid = f"{next_id:04d}"
    slug = re.sub(r"[^a-z0-9]+", "-", args.title.lower()).strip("-")[:60]
    if not slug:
        sys.exit("title slugified to empty string")
    path = ISSUES_DIR / f"{nid}-{slug}.md"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    tags = ", ".join(args.tags.split(",")) if args.tags else ""
    body = f"""---
id: {nid}
title: {args.title}
status: open
tier: {args.tier}
created: {today}
updated: {today}
depends_on: []
blocks: []
tags: [{tags}]
---

# Context

(Describe why this issue exists and what's been learned about it.)

# Acceptance criteria

- [ ] Specific deliverable 1
- [ ] Specific deliverable 2

# Log

- {today}: opened
"""
    ISSUES_DIR.mkdir(exist_ok=True)
    path.write_text(body, encoding="utf-8")
    print(f"created {path.relative_to(REPO)}")


def cmd_validate(args, issues):
    ok = True
    valid_ids = {i["id"] for i in issues}
    for i in issues:
        for dep in i["depends_on"]:
            if dep not in valid_ids:
                print(f"  #{i['id']}: depends_on references unknown #{dep}", file=sys.stderr)
                ok = False
        for blk in i["blocks"]:
            if blk not in valid_ids:
                print(f"  #{i['id']}: blocks references unknown #{blk}", file=sys.stderr)
                ok = False
        if i["status"] in ("done", "wontfix"):
            for blk in i["blocks"]:
                ref = next((j for j in issues if j["id"] == blk), None)
                if ref and ref["status"] not in ("done", "wontfix"):
                    pass  # not an error — closed issue can still appear in 'blocks' history
    if ok:
        print(f"OK — {len(issues)} issue(s), schemas valid, references resolve.")
    else:
        sys.exit("VALIDATION FAILED")


def cmd_index(args, issues):
    open_issues = [i for i in issues if i["status"] in ("open", "in-progress", "blocked")]
    closed_issues = [i for i in issues if i["status"] in ("done", "wontfix")]

    L: list[str] = []
    L.append("# Issue tracker")
    L.append("")
    L.append("_Auto-generated by `tools/issues.py index` — do not edit by hand. "
             "Source of truth is the individual `<NNNN>-<slug>.md` files in this directory._")
    L.append("")
    L.append(f"**Open: {len(open_issues)} · Closed: {len(closed_issues)} · "
             f"Total: {len(issues)}**")
    L.append("")
    L.append("See [SCHEMA.md](./SCHEMA.md) for the issue file format + policies.")
    L.append("")

    L.append("## Status × tier")
    L.append("")
    L.append("| status | A | B | C | D | other |")
    L.append("|---|---|---|---|---|---|")
    for status in VALID_STATUSES:
        cells = [f"**{status}**"]
        for tier in VALID_TIERS:
            n = sum(1 for i in issues if i["status"] == status and i["tier"] == tier)
            cells.append(str(n) if n else "·")
        L.append("| " + " | ".join(cells) + " |")
    L.append("")

    L.append("## Open work, by tier")
    for tier in VALID_TIERS:
        rows = [i for i in open_issues if i["tier"] == tier]
        if not rows:
            continue
        L.append("")
        L.append(f"### Tier {tier}")
        L.append("")
        for i in sorted(rows, key=lambda x: x["id"]):
            mark = {"open": "○", "in-progress": "⏵", "blocked": "⏸"}[i["status"]]
            tagstr = " ".join(f"`{t}`" for t in i.get("tags", [])[:4])
            deps = ""
            if i["depends_on"]:
                deps = f" — needs {', '.join('#' + d for d in i['depends_on'])}"
            L.append(f"- {mark} [#{i['id']}](./{i['_path'].name}) — {i['title']} "
                     f"{tagstr}{deps}")
    L.append("")

    if closed_issues:
        L.append("## Closed")
        L.append("")
        L.append("<details><summary>Click to expand closed issues</summary>")
        L.append("")
        for i in sorted(closed_issues, key=lambda x: x["id"]):
            mark = "✅" if i["status"] == "done" else "🚫"
            L.append(f"- {mark} [#{i['id']}](./{i['_path'].name}) — {i['title']} "
                     f"_(status: {i['status']})_")
        L.append("")
        L.append("</details>")
        L.append("")

    INDEX_FILE.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {INDEX_FILE.relative_to(REPO)}: "
          f"{len(issues)} issue(s) ({len(open_issues)} open, "
          f"{len(closed_issues)} closed)")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    sp = p.add_subparsers(dest="cmd", required=True)

    pl = sp.add_parser("list", help="list issues")
    pl.add_argument("--status", choices=VALID_STATUSES)
    pl.add_argument("--tier", choices=VALID_TIERS)
    pl.add_argument("--tag")

    pn = sp.add_parser("new", help="create a new issue")
    pn.add_argument("--title", required=True)
    pn.add_argument("--tier", required=True, choices=VALID_TIERS)
    pn.add_argument("--tags", default="", help="comma-separated tag list")

    sp.add_parser("index", help="regenerate issues/README.md")
    sp.add_parser("validate", help="verify all issue files conform to the schema")

    ps = sp.add_parser("show", help="print an issue's full text")
    ps.add_argument("id", help="issue ID (1-4 digits, leading zeros optional)")

    args = p.parse_args()
    issues = load_issues()
    {
        "list": cmd_list,
        "new": cmd_new,
        "index": cmd_index,
        "validate": cmd_validate,
        "show": cmd_show,
    }[args.cmd](args, issues)


if __name__ == "__main__":
    main()
