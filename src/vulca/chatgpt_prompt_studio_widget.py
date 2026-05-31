from __future__ import annotations


PROMPT_STUDIO_WIDGET_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Vulca Prompt Studio</title>
    <style>
      :root {
        color-scheme: light dark;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: Canvas;
        color: CanvasText;
      }
      * { box-sizing: border-box; }
      body { margin: 0; padding: 16px; }
      main { display: grid; gap: 12px; max-width: 760px; }
      header { display: grid; gap: 4px; }
      h1 { font-size: 18px; line-height: 1.25; margin: 0; }
      .meta { color: color-mix(in srgb, CanvasText 68%, transparent); font-size: 13px; }
      label { display: grid; gap: 6px; font-size: 13px; font-weight: 650; }
      textarea {
        width: 100%;
        min-height: 180px;
        resize: vertical;
        border: 1px solid color-mix(in srgb, CanvasText 22%, transparent);
        border-radius: 8px;
        padding: 10px;
        background: Canvas;
        color: CanvasText;
        font: 13px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      }
      .row { display: flex; flex-wrap: wrap; gap: 8px; }
      button {
        border: 1px solid color-mix(in srgb, CanvasText 22%, transparent);
        border-radius: 8px;
        padding: 8px 12px;
        background: Canvas;
        color: CanvasText;
        font: inherit;
        cursor: pointer;
      }
      button.primary {
        background: CanvasText;
        color: Canvas;
        border-color: CanvasText;
      }
      button:disabled { opacity: 0.45; cursor: not-allowed; }
      details {
        border-top: 1px solid color-mix(in srgb, CanvasText 14%, transparent);
        padding-top: 10px;
      }
      summary { cursor: pointer; font-weight: 650; }
      pre {
        margin: 8px 0 0;
        white-space: pre-wrap;
        font: 13px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      }
      .status { min-height: 18px; font-size: 13px; color: color-mix(in srgb, CanvasText 72%, transparent); }
    </style>
  </head>
  <body>
    <main>
      <header>
        <h1 id="title">Vulca Prompt Studio</h1>
        <div class="meta" id="tradition"></div>
      </header>
      <label>
        Final prompt
        <textarea data-field="final_prompt" id="finalPrompt"></textarea>
      </label>
      <div class="row">
        <button class="primary" id="generateButton" type="button">Generate in ChatGPT</button>
        <button id="copyButton" type="button">Copy prompt</button>
      </div>
      <div class="status" id="status" role="status" aria-live="polite"></div>
      <details open>
        <summary>Negative constraints</summary>
        <pre id="negativePrompt"></pre>
      </details>
      <details>
        <summary>Generation notes</summary>
        <pre id="generationNotes"></pre>
      </details>
      <details>
        <summary>Rubric priorities</summary>
        <pre id="rubricSummary"></pre>
      </details>
    </main>
    <script>
      const openai = window.openai || {};
      const toolOutput = openai.toolOutput || {};
      const widgetState = openai.widgetState || {};
      const data = { ...toolOutput, ...widgetState };

      const title = document.getElementById("title");
      const tradition = document.getElementById("tradition");
      const finalPrompt = document.getElementById("finalPrompt");
      const negativePrompt = document.getElementById("negativePrompt");
      const generationNotes = document.getElementById("generationNotes");
      const rubricSummary = document.getElementById("rubricSummary");
      const generateButton = document.getElementById("generateButton");
      const copyButton = document.getElementById("copyButton");
      const status = document.getElementById("status");

      function valueOrNone(value) {
        const text = String(value || "").trim();
        return text || "none";
      }

      function valueOrDefault(value, fallback) {
        const text = String(value || "").trim();
        return text || fallback;
      }

      function buildFollowupMessage() {
        return [
          "Generate an image in ChatGPT using this Vulca prompt. Preserve the tradition, composition, negative constraints, and rubric priorities exactly.",
          "",
          `Title: ${valueOrNone(data.prompt_title)}`,
          `Tradition: ${valueOrNone(data.tradition)}`,
          `Prompt: ${finalPrompt.value.trim()}`,
          `Negative constraints: ${valueOrNone(data.negative_prompt)}`,
          `Generation notes: ${valueOrNone(data.generation_notes)}`,
          `Rubric priorities: ${valueOrDefault(data.rubric_summary, "use Vulca's L1-L5 rubric")}`
        ].join("\\n");
      }

      function syncDisabledState() {
        generateButton.disabled = finalPrompt.value.trim().length === 0;
      }

      async function saveState() {
        data.final_prompt = finalPrompt.value;
        if (window.openai && window.openai.setWidgetState) {
          await window.openai.setWidgetState({ final_prompt: finalPrompt.value });
        }
      }

      async function copyText(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(text);
          return;
        }
        const copyTarget = document.createElement("textarea");
        copyTarget.value = text;
        copyTarget.setAttribute("readonly", "");
        copyTarget.style.position = "fixed";
        copyTarget.style.top = "-1000px";
        document.body.appendChild(copyTarget);
        copyTarget.focus();
        copyTarget.select();
        try {
          document.execCommand("copy");
        } finally {
          copyTarget.remove();
        }
      }

      title.textContent = valueOrNone(data.prompt_title);
      tradition.textContent = `Tradition: ${valueOrNone(data.tradition)}`;
      finalPrompt.value = data.final_prompt || "";
      negativePrompt.textContent = valueOrNone(data.negative_prompt);
      generationNotes.textContent = valueOrNone(data.generation_notes);
      rubricSummary.textContent = valueOrNone(data.rubric_summary);
      syncDisabledState();

      finalPrompt.addEventListener("input", async () => {
        syncDisabledState();
        await saveState();
      });

      copyButton.addEventListener("click", async () => {
        await copyText(buildFollowupMessage());
        status.textContent = "Prompt copied.";
      });

      generateButton.addEventListener("click", async () => {
        await saveState();
        const prompt = buildFollowupMessage();
        if (!(window.openai && window.openai.sendFollowUpMessage)) {
          await copyText(prompt);
          status.textContent = "ChatGPT follow-up is unavailable here. Prompt copied instead.";
          return;
        }
        try {
          await window.openai.sendFollowUpMessage({ prompt, scrollToBottom: true });
          status.textContent = "Sent to ChatGPT.";
        } catch (error) {
          await copyText(prompt);
          status.textContent = "Could not send follow-up. Prompt copied instead.";
        }
      });
    </script>
  </body>
</html>
"""
