// Renders a Claude Code session JSONL transcript as readable HTML.
// Input: an array of records (one per JSONL line).
// Output: an HTML string.

const SessionViewer = (function () {
  const esc = Markdown.escape;

  function fmtTs(ts) {
    if (!ts) return "";
    return ts.replace("T", " ").replace(/\.\d+Z$/, "Z");
  }

  function renderToolUse(part) {
    const inputJson = part.input
      ? JSON.stringify(part.input, null, 2)
      : "(no input)";
    return (
      `<details class="tool-use">` +
      `<summary>tool: ${esc(part.name)}</summary>` +
      `<pre>${esc(inputJson)}</pre>` +
      `</details>`
    );
  }

  function renderToolResult(part) {
    let body;
    if (typeof part.content === "string") body = part.content;
    else if (Array.isArray(part.content)) {
      body = part.content
        .map((c) => (c.type === "text" ? c.text : JSON.stringify(c)))
        .join("\n");
    } else body = JSON.stringify(part.content, null, 2);
    return (
      `<details class="tool-result">` +
      `<summary>tool result${part.is_error ? " (error)" : ""}</summary>` +
      `<pre>${esc(body)}</pre>` +
      `</details>`
    );
  }

  function renderUserContent(content) {
    if (typeof content === "string") {
      return `<div class="text">${esc(content)}</div>`;
    }
    if (!Array.isArray(content)) return "";
    let html = "";
    for (const part of content) {
      if (part.type === "text") {
        html += `<div class="text">${esc(part.text)}</div>`;
      } else if (part.type === "tool_result") {
        html += renderToolResult(part);
      }
    }
    return html;
  }

  function renderAssistantContent(content) {
    if (!Array.isArray(content)) return "";
    let html = "";
    for (const part of content) {
      if (part.type === "thinking") {
        html += (
          `<details class="thinking">` +
          `<summary>thinking</summary>` +
          `<pre>${esc(part.thinking || "")}</pre>` +
          `</details>`
        );
      } else if (part.type === "text") {
        html += `<div class="text">${Markdown.render(part.text)}</div>`;
      } else if (part.type === "tool_use") {
        html += renderToolUse(part);
      }
    }
    return html;
  }

  function render(records, sessionId) {
    if (!records || !records.length) {
      return `<h1>Session ${esc(sessionId || "")}</h1><p>(empty)</p>`;
    }
    let userTurns = 0,
      asstTurns = 0,
      thinkingBlocks = 0,
      firstTs = null,
      lastTs = null;
    for (const r of records) {
      if (r.type === "user") userTurns++;
      if (r.type === "assistant") asstTurns++;
      if (r.type === "assistant" && Array.isArray(r.message?.content)) {
        for (const p of r.message.content)
          if (p.type === "thinking") thinkingBlocks++;
      }
      if (r.timestamp) {
        if (!firstTs) firstTs = r.timestamp;
        lastTs = r.timestamp;
      }
    }

    let out =
      `<h1>Session <code>${esc(sessionId || "")}</code></h1>` +
      `<div class="session-meta">` +
      `${userTurns} user turns · ${asstTurns} assistant turns · ${thinkingBlocks} thinking blocks<br>` +
      `${esc(fmtTs(firstTs))} → ${esc(fmtTs(lastTs))}` +
      `</div>`;

    for (const r of records) {
      if (r.type === "user") {
        const body = renderUserContent(r.message?.content);
        if (!body) continue;
        out +=
          `<div class="turn user">` +
          `<div class="ts">${esc(fmtTs(r.timestamp))} · user</div>` +
          body +
          `</div>`;
      } else if (r.type === "assistant") {
        const body = renderAssistantContent(r.message?.content);
        if (!body) continue;
        out +=
          `<div class="turn assistant">` +
          `<div class="ts">${esc(fmtTs(r.timestamp))} · assistant</div>` +
          body +
          `</div>`;
      }
      // Skip other record types (permission-mode, file-history-snapshot, attachment, ...).
    }

    return out;
  }

  function renderIndex(sessions) {
    if (!sessions || !sessions.length) {
      return `<h1>Session log</h1><p>No sessions captured yet.</p>`;
    }
    let html = `<h1>Session log</h1>`;
    html += `<p>Each session is a verbatim JSONL transcript captured by the Stop hook (see <code>.claude/hooks/audit-session.sh</code>).</p>`;
    html += `<ul class="session-list">`;
    for (const s of sessions) {
      html += `<li><a href="#/sessions/${esc(s.id)}">${esc(s.id)}</a>`;
      const meta = [];
      if (s.summary) {
        if (s.summary.user_turns != null)
          meta.push(`${s.summary.user_turns} user turns`);
        if (s.summary.assistant_turns != null)
          meta.push(`${s.summary.assistant_turns} assistant turns`);
        if (s.summary.thinking_blocks != null)
          meta.push(`${s.summary.thinking_blocks} thinking blocks`);
        if (s.summary.first_ts && s.summary.last_ts) {
          meta.push(`${fmtTs(s.summary.first_ts)} → ${fmtTs(s.summary.last_ts)}`);
        }
      }
      if (meta.length) html += `<div class="meta">${esc(meta.join(" · "))}</div>`;
      html += `</li>`;
    }
    html += `</ul>`;
    return html;
  }

  return { render: render, renderIndex: renderIndex };
})();
