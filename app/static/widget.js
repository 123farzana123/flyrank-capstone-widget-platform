(function () {
  // Find our own <script> tag so we can read its src URL (contains ?id=... and tells us the API's origin)
  const script = document.currentScript;
  const widgetId = new URL(script.src).searchParams.get("id");
  const apiBase = new URL(script.src).origin;

  // Fetch this widget's public config (title, fields, button text)
  fetch(`${apiBase}/widgets/${widgetId}/config`)
    .then((res) => res.json())
    .then((config) => {
      const container = document.createElement("div");
      container.innerHTML = `
        <form id="widget-form">
          <h3>${config.title}</h3>
          <p>${config.description || ""}</p>
          ${(config.config.fields || [])
            .map((f) => `<input name="${f}" placeholder="${f}" />`)
            .join("")}
          <button type="submit">${config.button_text}</button>
        </form>
      `;
      script.parentNode.insertBefore(container, script.nextSibling);

      // Wire up the actual submission — this is the cross-origin POST that CORS must allow
      document.getElementById("widget-form").addEventListener("submit", (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        fetch(`${apiBase}/widgets/${widgetId}/submissions`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ data }),
        }).then(() => {
          container.innerHTML = "<p>Thank you!</p>";
        });
      });
    });
})();