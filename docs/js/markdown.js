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
    // Bold + italic
    text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/\b_([^_]+)_\b/g, "<em>$1</em>");
    text = text.replace(/(^|[^\*])\*([^\*\n]+)\*([^\*]|$)/g, "$1<em>$2</em>$3");
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

      // Lists (unordered or ordered, no nesting)
      const ulMatch = line.match(/^(\s*)[-*+]\s+(.*)$/);
      const olMatch = line.match(/^(\s*)\d+\.\s+(.*)$/);
      if (ulMatch || olMatch) {
        const isOrdered = !!olMatch;
        const re = isOrdered ? /^\s*\d+\.\s+(.*)$/ : /^\s*[-*+]\s+(.*)$/;
        const tag = isOrdered ? "ol" : "ul";
        let html = `<${tag}>`;
        while (i < lines.length && re.test(lines[i])) {
          const m = lines[i].match(re);
          html += `<li>${inline(m[1])}</li>`;
          i++;
        }
        html += `</${tag}>`;
        out.push(html);
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
