#!/usr/bin/env python3
"""Generate docs/data/all.js from sessions/*.jsonl and docs/content/**/*.md.

The output is loaded by docs/index.html and populates window.AWA with
everything the static viewer needs. The output file is gitignored.

Shape:
    window.AWA = {
      generated_at: "<UTC ISO-8601>",
      sessions:    [{ id, summary: {user_turns, assistant_turns, ...} }, ...],
      sessionData: { <session_id>: [<JSONL records>], ... },
      content:     { <relative_path_without_md>: "<raw markdown>", ... }
    };
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SESSIONS_DIR = REPO / "sessions"
CONTENT_DIR = REPO / "docs" / "content"
ISSUES_DIR = REPO / "issues"
DATA_DIR = REPO / "docs" / "data"


def summarize(records):
    user_turns = 0
    asst_turns = 0
    thinking_blocks = 0
    first_ts = None
    last_ts = None
    for r in records:
        t = r.get("type")
        if t == "user":
            user_turns += 1
        elif t == "assistant":
            asst_turns += 1
            content = (r.get("message") or {}).get("content")
            if isinstance(content, list):
                for p in content:
                    if isinstance(p, dict) and p.get("type") == "thinking":
                        thinking_blocks += 1
        ts = r.get("timestamp")
        if ts:
            if first_ts is None:
                first_ts = ts
            last_ts = ts
    return {
        "user_turns": user_turns,
        "assistant_turns": asst_turns,
        "thinking_blocks": thinking_blocks,
        "first_ts": first_ts,
        "last_ts": last_ts,
    }


def load_sessions():
    sessions = []
    session_data = {}
    if not SESSIONS_DIR.is_dir():
        return sessions, session_data
    for path in sorted(SESSIONS_DIR.glob("*.jsonl")):
        sid = path.stem
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for lineno, raw in enumerate(f, 1):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    records.append(json.loads(raw))
                except json.JSONDecodeError as e:
                    print(
                        f"warning: {path.name}:{lineno}: {e}; skipping",
                        file=sys.stderr,
                    )
        sessions.append({"id": sid, "summary": summarize(records)})
        session_data[sid] = records
    return sessions, session_data


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
    sessions, session_data = load_sessions()
    content = load_content()

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sessions": sessions,
        "sessionData": session_data,
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
        f"{len(sessions)} session(s), {len(content)} content page(s), "
        f"{size_kb:.1f} KB"
    )


if __name__ == "__main__":
    main()
