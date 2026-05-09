// Minimal Markdown→HTML renderer for the AWA docs site.
// Intentionally not feature-complete: handles the subset we use in
// docs/content/*.md (headings, paragraphs, lists, code-fences, inline
// formatting, links, tables, horizontal rules). Swap for marked.js if
// it ever becomes a bottleneck.

const Markdown = (function () {
  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function inline(text) {
    text = escapeHtml(text);
    // Code spans first (so other inline rules don't interfere with their content)
    text = text.replace(/`([^`]+)`/g, "<code>$1</code>");
    // Bold + italic + strikethrough
    text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/\b_([^_]+)_\b/g, "<em>$1</em>");
    text = text.replace(/(^|[^\*])\*([^\*\n]+)\*([^\*]|$)/g, "$1<em>$2</em>$3");
    text = text.replace(/~~([^~]+)~~/g, "<del>$1</del>");
    // Images — handle BEFORE links so the `!` prefix isn't lost.
    // Source markdown uses `../assets/...` paths relative to
    // docs/content/<section>/foo.md. The deployed site is served
    // from `docs/`, so `../assets/foo` would resolve outside the
    // site root; rewrite to `assets/foo` (root-relative under
    // docs/) before emitting the <img>.
    text = text.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, (m, alt, src) => {
      const rewritten = src.replace(/^\.\.\/assets\//, "assets/");
      const altEsc = escapeHtml(alt);
      return '<img alt="' + altEsc + '" src="' + rewritten + '">';
    });
    // Links — but if the URL points at an audio file (.wav/.ogg/.mp3),
    // render an <audio controls> player instead of a plain anchor. The
    // link text becomes the player's caption (rendered before the player).
    text = text.replace(/\[([^\]]+)\]\(([^)\s]+\.(?:wav|ogg|mp3))\)/gi,
      '<figure class="audio-figure"><figcaption>$1</figcaption>' +
      '<audio controls preload="none" src="$2">$1</audio></figure>');
    text = text.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2">$1</a>');
    return text;
  }

  function isTableSep(line) {
    return /^[\s\-:|]+$/.test(line) && line.includes("-") && line.includes("|");
  }

  // Render a list (and any nested lists / continuation prose under
  // its items) starting at lines[startIdx]. The first list item's
  // bullet must be at column `indent`. Returns {html, next} where
  // `next` is the index of the first line NOT consumed by the list.
  function renderList(lines, startIdx, indent) {
    const isOrdered = /^\s*\d+\.\s/.test(lines[startIdx]);
    const bulletRe = isOrdered
      ? /^(\s*)\d+\.\s+(.*)$/
      : /^(\s*)[-*+]\s+(.*)$/;
    const anyBulletRe = /^(\s*)(?:[-*+]|\d+\.)\s+(.*)$/;
    const tag = isOrdered ? "ol" : "ul";
    let html = "<" + tag + ">";
    let i = startIdx;
    while (i < lines.length) {
      const line = lines[i];
      if (line.trim() === "") {
        // Blank line — peek ahead. If the next non-blank line is
        // a sibling bullet (same indent) or deeper, the list
        // continues. Otherwise we're done.
        let j = i + 1;
        while (j < lines.length && lines[j].trim() === "") j++;
        if (j >= lines.length) break;
        const peek = lines[j].match(anyBulletRe);
        if (!peek || peek[1].length < indent) break;
        i = j;
        continue;
      }
      const m = line.match(bulletRe);
      if (!m || m[1].length !== indent) {
        // Either the wrong indent or not a list item at all — done.
        break;
      }
      // Task-list syntax: `- [ ] todo` and `- [x] done`. Emit a
      // disabled checkbox at the start of the list-item body and
      // strip the marker from the text.
      let taskBox = "";
      let bodyText = m[2];
      const taskMatch = bodyText.match(/^\[([ xX])\]\s+(.*)$/);
      if (taskMatch) {
        const checked = taskMatch[1].toLowerCase() === "x";
        taskBox = checked
          ? '<input type="checkbox" disabled checked> '
          : '<input type="checkbox" disabled> ';
        bodyText = taskMatch[2];
      }
      // Collect raw text fragments (so multi-line `**bold**` etc.
      // close correctly) AND nested-list HTML separately. Apply
      // inline() to the joined raw text at the end.
      const textParts = [bodyText];
      const nestedParts = [];
      i++;
      while (i < lines.length) {
        const next = lines[i];
        if (next.trim() === "") {
          // Blank — peek to decide
          let j = i + 1;
          while (j < lines.length && lines[j].trim() === "") j++;
          if (j >= lines.length) break;
          const peek = lines[j].match(anyBulletRe);
          if (peek && peek[1].length > indent) {
            // Nested list after a blank line — descend
            const sub = renderList(lines, j, peek[1].length);
            nestedParts.push(sub.html);
            i = sub.next;
            continue;
          }
          break;
        }
        const nm = next.match(anyBulletRe);
        if (nm && nm[1].length === indent) break; // sibling
        if (nm && nm[1].length < indent) break;   // outdented
        if (nm && nm[1].length > indent) {
          // Nested list
          const sub = renderList(lines, i, nm[1].length);
          nestedParts.push(sub.html);
          i = sub.next;
          continue;
        }
        if (/^\s+\S/.test(next)) {
          // Indented prose — continuation of the current item
          textParts.push(next.trim());
          i++;
          continue;
        }
        // Non-indented non-list line — done.
        break;
      }
      html += "<li>" + taskBox + inline(textParts.join(" ")) + nestedParts.join("") + "</li>";
    }
    html += "</" + tag + ">";
    return { html: html, next: i };
  }

  function render(src) {
    if (!src) return "";
    const lines = src.replace(/\r\n/g, "\n").split("\n");
    let out = [];
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];

      // Code fence
      if (/^```/.test(line)) {
        const lang = line.slice(3).trim();
        const buf = [];
        i++;
        while (i < lines.length && !/^```/.test(lines[i])) {
          buf.push(lines[i]);
          i++;
        }
        i++; // skip closer
        out.push(
          `<pre><code${lang ? ` class="lang-${escapeHtml(lang)}"` : ""}>` +
            escapeHtml(buf.join("\n")) +
            "</code></pre>"
        );
        continue;
      }

      // Heading
      const h = line.match(/^(#{1,6})\s+(.+?)\s*#*\s*$/);
      if (h) {
        out.push(`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`);
        i++;
        continue;
      }

      // Horizontal rule
      if (/^([-*_])\1{2,}\s*$/.test(line.trim())) {
        out.push("<hr>");
        i++;
        continue;
      }

      // Blank
      if (line.trim() === "") { i++; continue; }

      // Table: header + separator + rows
      if (line.includes("|") && i + 1 < lines.length && isTableSep(lines[i + 1])) {
        const cells = (l) =>
          l.replace(/^\s*\|/, "").replace(/\|\s*$/, "").split("|").map((c) => c.trim());
        const head = cells(line);
        i += 2;
        const rows = [];
        while (i < lines.length && lines[i].includes("|") && lines[i].trim() !== "") {
          rows.push(cells(lines[i]));
          i++;
        }
        let t = "<table><thead><tr>";
        head.forEach((c) => (t += `<th>${inline(c)}</th>`));
        t += "</tr></thead><tbody>";
        rows.forEach((r) => {
          t += "<tr>";
          r.forEach((c) => (t += `<td>${inline(c)}</td>`));
          t += "</tr>";
        });
        t += "</tbody></table>";
        out.push(t);
        continue;
      }

      // Blockquote: contiguous lines beginning with `>`. Strips the
      // marker (and one optional space) from each line, then runs
      // the result back through inline formatting. No nesting.
      if (/^>\s?/.test(line)) {
        const buf = [];
        while (i < lines.length && /^>\s?/.test(lines[i])) {
          buf.push(lines[i].replace(/^>\s?/, ""));
          i++;
        }
        out.push(`<blockquote>${inline(buf.join(" "))}</blockquote>`);
        continue;
      }

      // Lists (unordered or ordered) with continuation-line absorption
      // and one level of nesting.
      const ulMatch = line.match(/^(\s*)[-*+]\s+(.*)$/);
      const olMatch = line.match(/^(\s*)\d+\.\s+(.*)$/);
      if (ulMatch || olMatch) {
        const result = renderList(lines, i, (ulMatch || olMatch)[1].length);
        out.push(result.html);
        i = result.next;
        continue;
      }

      // Paragraph: collect contiguous non-empty lines that don't start a new block
      const para = [line];
      i++;
      while (
        i < lines.length &&
        lines[i].trim() !== "" &&
        !/^(#{1,6}\s|```|>|\s*[-*+]\s|\s*\d+\.\s)/.test(lines[i]) &&
        !/^([-*_])\1{2,}\s*$/.test(lines[i].trim())
      ) {
        para.push(lines[i]);
        i++;
      }
      out.push(`<p>${inline(para.join(" "))}</p>`);
    }

    return out.join("\n");
  }

  return { render: render, escape: escapeHtml };
})();
