// Application entry point. Hash-based router. Handles:
//   #/                       → docs/content/README.md
//   #/<page>                 → docs/content/<page>.md
//   #/research               → docs/content/research/README.md
//   #/research/<slug>        → docs/content/research/<slug>.md
//   #/open-questions[/<slug>]

(function () {
  function emptyState() {
    return (
      `<h1>Run <code>make docs</code></h1>` +
      `<p>The data file <code>docs/data/all.js</code> is missing. It is generated ` +
      `from <code>docs/content/**/*.md</code> ` +
      `by <code>tools/gen_docs_data.py</code>.</p>` +
      `<p>From the repo root:</p>` +
      `<pre><code>make docs</code></pre>` +
      `<p>Then refresh this page.</p>`
    );
  }

  function setGeneratedAt() {
    if (!window.AWA || !window.AWA.generated_at) return;
    const el = document.getElementById("generated-at");
    if (el) el.textContent = "data: " + window.AWA.generated_at;
  }

  function route() {
    const main = document.getElementById("main");
    if (window.__AWA_DATA_MISSING || !window.AWA) {
      main.innerHTML = emptyState();
      return;
    }

    const raw = (location.hash || "#/").slice(2);
    const path = raw.replace(/\/$/, "");

    // Content pages — try the path as-is, then fall back to <path>/README.
    const contentKey = path === "" ? "README" : path;
    if (Content.exists(contentKey)) {
      main.innerHTML = Content.render(contentKey);
      return;
    }
    const indexKey = contentKey + "/README";
    if (Content.exists(indexKey)) {
      main.innerHTML = Content.render(indexKey);
      return;
    }
    main.innerHTML = Content.render(contentKey); // will produce a 404 page
  }

  function init() {
    setGeneratedAt();
    window.addEventListener("hashchange", route);
    route();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
