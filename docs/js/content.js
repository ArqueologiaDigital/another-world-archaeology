// Renders a markdown content page from window.AWA.content.

const Content = (function () {
  function render(path) {
    const data = window.AWA && window.AWA.content;
    if (!data) {
      return `<h1>Content not loaded</h1>`;
    }
    const md = data[path];
    if (md == null) {
      return (
        `<h1>Not found</h1>` +
        `<p>No content at <code>${Markdown.escape(path)}</code>.</p>` +
        `<p><a href="#/">Back to home</a></p>`
      );
    }
    return Markdown.render(md);
  }

  function exists(path) {
    return !!(window.AWA && window.AWA.content && window.AWA.content[path] != null);
  }

  return { render: render, exists: exists };
})();
