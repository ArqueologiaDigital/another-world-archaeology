#!/bin/bash
# Stop hook: capture the live Claude Code session JSONL into sessions/
# and commit it as a tamper-evident, per-turn audit trail.
#
# Stdin payload (per Claude Code Stop hook docs):
#   { "session_id": "...", "transcript_path": "...", "cwd": "...",
#     "permission_mode": "...", "hook_event_name": "Stop",
#     "stop_reason": "..." }
#
# The hook commits ONLY sessions/<id>.jsonl (using `git commit --only`),
# leaving any other staged changes the assistant is preparing untouched.
# It is idempotent: if the JSONL has not changed since the last capture,
# it exits without creating an empty commit.

set -uo pipefail

INPUT=$(cat)

if ! command -v jq >/dev/null 2>&1; then
  echo "audit-session: jq not installed; cannot parse hook input" >&2
  exit 0
fi

SESSION_ID=$(jq -r '.session_id // ""' <<<"$INPUT")
TRANSCRIPT_PATH=$(jq -r '.transcript_path // ""' <<<"$INPUT")
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(jq -r '.cwd // ""' <<<"$INPUT")}"

if [[ -z "$SESSION_ID" ]]; then
  echo "audit-session: no session_id in stdin; skipping" >&2
  exit 0
fi
if [[ -z "$PROJECT_DIR" || ! -d "$PROJECT_DIR" ]]; then
  echo "audit-session: project dir '$PROJECT_DIR' not usable; skipping" >&2
  exit 0
fi
if [[ ! -f "$TRANSCRIPT_PATH" ]]; then
  echo "audit-session: transcript not found at '$TRANSCRIPT_PATH'; skipping" >&2
  exit 0
fi

DEST_REL="sessions/${SESSION_ID}.jsonl"
DEST_ABS="$PROJECT_DIR/$DEST_REL"

mkdir -p "$PROJECT_DIR/sessions"
cp -f "$TRANSCRIPT_PATH" "$DEST_ABS"

cd "$PROJECT_DIR"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "audit-session: '$PROJECT_DIR' is not a git repo; transcript copied but not committed" >&2
  exit 0
fi

git add -- "$DEST_REL" 2>/dev/null || true

if git diff --cached --quiet -- "$DEST_REL"; then
  exit 0
fi

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if ! git commit --only --quiet \
      -m "session log: ${SESSION_ID} @ ${TS}" \
      -- "$DEST_REL" 2>/dev/null; then
  echo "audit-session: commit failed; sessions/${SESSION_ID}.jsonl staged but uncommitted" >&2
  exit 0
fi
