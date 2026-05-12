MEETING_DEMO_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Meeting-to-Jira Agent</title>
  <style>
    :root {
      --bg: #f5f7fb;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #637083;
      --line: #dde3ee;
      --blue: #0b63ce;
      --blue-soft: #e8f1ff;
      --green: #217a55;
      --green-soft: #ddf8ea;
      --red: #b42318;
      --red-soft: #fff0ed;
      --yellow: #7a5d00;
      --yellow-soft: #fff5cc;
      --shadow: 0 16px 38px rgba(20, 36, 64, 0.12);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      min-height: 68px;
      padding: 0 28px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }

    h1, h2, h3, p { margin: 0; }
    h1 { font-size: 20px; line-height: 1.25; }
    h2 { font-size: 16px; line-height: 1.35; }
    h3 {
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .08em;
      text-transform: uppercase;
    }

    a { color: var(--blue); font-weight: 700; text-decoration: none; }

    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }

    button {
      min-height: 40px;
      padding: 0 14px;
      border: 1px solid #b8c2d3;
      border-radius: 7px;
      background: #fff;
      color: var(--ink);
      font: inherit;
      font-weight: 750;
      cursor: pointer;
    }

    button.primary {
      border-color: var(--blue);
      background: var(--blue);
      color: #fff;
    }

    button:disabled { opacity: .55; cursor: not-allowed; }

    main {
      display: grid;
      grid-template-columns: minmax(320px, 1fr) minmax(360px, 1.15fr);
      gap: 18px;
      width: min(1240px, calc(100vw - 32px));
      margin: 22px auto;
    }

    .panel {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      padding: 18px 18px 14px;
      border-bottom: 1px solid var(--line);
    }

    .panel-body {
      display: grid;
      gap: 14px;
      padding: 18px;
    }

    .transcript {
      min-height: 138px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcff;
      font-size: 18px;
      font-weight: 700;
      line-height: 1.45;
      overflow-wrap: anywhere;
    }

    .muted { color: var(--muted); }

    .chips, .cards {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .chip {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 4px 9px;
      border-radius: 999px;
      background: var(--blue-soft);
      color: #0747a6;
      font-size: 13px;
      font-weight: 750;
    }

    .ticket, .task, .warning {
      display: grid;
      gap: 8px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcff;
    }

    .ticket strong, .task strong { font-size: 14px; }
    .ticket p, .task p, .warning p { color: #334155; font-size: 14px; line-height: 1.45; }

    .pill {
      display: inline-flex;
      width: fit-content;
      min-height: 24px;
      align-items: center;
      padding: 3px 8px;
      border-radius: 999px;
      background: #eef2f7;
      color: #42526e;
      font-size: 12px;
      font-weight: 800;
    }

    .warning {
      border-color: #ffc9c0;
      background: var(--red-soft);
    }

    .warning strong { color: var(--red); }

    .history {
      display: grid;
      gap: 8px;
      max-height: 420px;
      overflow: auto;
    }

    .history-line {
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #fff;
      color: #334155;
      font-size: 13px;
      line-height: 1.4;
    }

    @media (max-width: 860px) {
      header { align-items: flex-start; flex-direction: column; padding: 16px; }
      main { grid-template-columns: 1fr; width: min(100vw - 24px, 680px); }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Meeting-to-Jira Agent</h1>
      <p class="muted">Live engineering discussion intelligence</p>
    </div>
    <div class="actions">
      <a href="/jira">Fake Jira</a>
      <button type="button" data-testid="reset-demo">Reset Demo</button>
      <button class="primary" type="button" data-testid="next-chunk">Next Transcript Chunk</button>
    </div>
  </header>

  <main>
    <section class="panel">
      <div class="panel-header">
        <h2>Transcript</h2>
        <span class="muted" data-testid="progress"></span>
      </div>
      <div class="panel-body">
        <div class="transcript" data-testid="current-transcript">Ready.</div>
        <div>
          <h3>Detected Topics</h3>
          <div class="chips" data-testid="topics"></div>
        </div>
        <div>
          <h3>History</h3>
          <div class="history" data-testid="history"></div>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <h2>Jira Intelligence</h2>
        <button type="button" data-testid="browser-search" disabled>Browser Search</button>
      </div>
      <div class="panel-body">
        <div>
          <h3>Related Jira Tickets</h3>
          <div class="cards" data-testid="related-issues"></div>
        </div>
        <div>
          <h3>Task Draft</h3>
          <div data-testid="task-draft" class="cards"></div>
        </div>
        <div>
          <h3>Blamelessness Guardrail</h3>
          <div data-testid="blameless" class="cards"></div>
        </div>
      </div>
    </section>
  </main>

  <script>
    const state = { lastStep: null };
    const escapeHtml = (value) => String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

    async function loadState() {
      const response = await fetch("/meeting/state");
      renderState(await response.json());
    }

    async function nextChunk() {
      const response = await fetch("/meeting/next");
      const payload = await response.json();
      if (payload.done) {
        renderState(payload.state);
        document.querySelector('[data-testid="current-transcript"]').textContent = "Transcript complete.";
        document.querySelector('[data-testid="next-chunk"]').disabled = true;
        return;
      }
      state.lastStep = payload.step;
      renderState(payload.state, payload.step);
    }

    async function resetDemo() {
      const response = await fetch("/meeting/reset", {method: "POST"});
      state.lastStep = null;
      document.querySelector('[data-testid="next-chunk"]').disabled = false;
      document.querySelector('[data-testid="browser-search"]').disabled = true;
      renderState(await response.json());
      document.querySelector('[data-testid="current-transcript"]').textContent = "Ready.";
    }

    async function browserSearch() {
      const topics = state.lastStep?.detected_topics || [];
      const query = topics.slice(0, 3).join(" ") || state.lastStep?.normalized_transcript || "";
      if (!query) return;
      const button = document.querySelector('[data-testid="browser-search"]');
      button.disabled = true;
      button.textContent = "Searching...";
      try {
        await fetch(`/browser-demo/search?q=${encodeURIComponent(query)}`);
      } finally {
        button.textContent = "Browser Search";
        button.disabled = false;
      }
    }

    function renderState(demoState, step) {
      const total = demoState.total_transcript_lines || 8;
      document.querySelector('[data-testid="progress"]').textContent =
        `${demoState.current_transcript_index} / ${total}`;

      if (step) {
        document.querySelector('[data-testid="current-transcript"]').textContent =
          step.normalized_transcript || step.transcript_line;
        renderTopics(step.detected_topics);
        renderIssues(step.related_jira_issues);
        renderTask(step.task_draft);
        renderBlameless(step.blameless_guardrail, step.raw_transcript, step.normalized_transcript);
        document.querySelector('[data-testid="browser-search"]').disabled = !step.related_jira_issues.length;
        document.querySelector('[data-testid="next-chunk"]').disabled = !step.has_more && demoState.current_transcript_index >= total;
      } else {
        renderTopics([]);
        renderIssues([]);
        renderTask(null);
        renderBlameless(null, "", "");
      }
      renderHistory(demoState.history || []);
    }

    function renderTopics(topics) {
      const el = document.querySelector('[data-testid="topics"]');
      el.innerHTML = topics.length
        ? topics.map((topic) => `<span class="chip">${escapeHtml(topic)}</span>`).join("")
        : `<span class="muted">No topics yet.</span>`;
    }

    function renderIssues(issues) {
      const el = document.querySelector('[data-testid="related-issues"]');
      el.innerHTML = issues.length
        ? issues.map((issue) => `
          <article class="ticket">
            <span class="pill">${escapeHtml(issue.key)} - ${escapeHtml(issue.status)}</span>
            <strong>${escapeHtml(issue.summary)}</strong>
            <p>${escapeHtml(issue.description)}</p>
          </article>
        `).join("")
        : `<span class="muted">No related tickets for this line.</span>`;
    }

    function renderTask(task) {
      const el = document.querySelector('[data-testid="task-draft"]');
      el.innerHTML = task ? `
        <article class="task">
          <span class="pill">Owner: ${escapeHtml(task.suggested_owner)}</span>
          <strong>${escapeHtml(task.title)}</strong>
          <p>${escapeHtml(task.description)}</p>
        </article>
      ` : `<span class="muted">No task draft for this line.</span>`;
    }

    function renderBlameless(guardrail, rawTranscript, normalizedTranscript) {
      const el = document.querySelector('[data-testid="blameless"]');
      if (!guardrail?.triggered) {
        el.innerHTML = `<span class="muted">No guardrail changes for this line.</span>`;
        return;
      }

      const reasons = (guardrail.issues || [])
        .map((issue) => `<p><b>Why:</b> ${escapeHtml(issue.reason)}</p>`)
        .join("");

      el.innerHTML = `
        <article class="warning">
          <strong>Blameful wording was rewritten before drafting work.</strong>
          <p><b>Original:</b> ${escapeHtml(rawTranscript)}</p>
          ${reasons}
          <p><b>Rewrite:</b> ${escapeHtml(guardrail.rewrite || normalizedTranscript)}</p>
          <p><b>Prevention follow-up:</b> ${escapeHtml(guardrail.prevention_task)}</p>
        </article>
      `;
    }

    function renderHistory(history) {
      const el = document.querySelector('[data-testid="history"]');
      el.innerHTML = history.length
        ? history.slice().reverse().map((item) => `
          <div class="history-line">
            <strong>${item.index + 1}.</strong> ${escapeHtml(item.normalized_transcript || item.transcript_line)}
          </div>
        `).join("")
        : `<span class="muted">No transcript chunks processed.</span>`;
    }

    document.querySelector('[data-testid="next-chunk"]').addEventListener("click", nextChunk);
    document.querySelector('[data-testid="reset-demo"]').addEventListener("click", resetDemo);
    document.querySelector('[data-testid="browser-search"]').addEventListener("click", browserSearch);
    loadState();
  </script>
</body>
</html>
"""


FAKE_JIRA_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Local Jira Demo</title>
  <style>
    :root {
      --bg: #f6f7fb;
      --panel: #ffffff;
      --ink: #172b4d;
      --muted: #5e6c84;
      --line: #dfe3eb;
      --blue: #0c66e4;
      --blue-soft: #e9f2ff;
      --green: #216e4e;
      --green-soft: #dcfff1;
      --yellow: #7f5f01;
      --yellow-soft: #fff7d6;
      --shadow: 0 12px 30px rgba(9, 30, 66, 0.12);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
    }

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
      min-height: 64px;
      padding: 0 28px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }

    h1, h2, h3, p { margin: 0; }
    h1 { font-size: 18px; line-height: 1.25; }
    h2 { font-size: 16px; line-height: 1.35; }
    h3 {
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: .08em;
      text-transform: uppercase;
    }

    a { color: var(--blue); font-weight: 750; text-decoration: none; }

    main {
      display: grid;
      grid-template-columns: minmax(300px, 410px) minmax(0, 1fr);
      gap: 20px;
      width: min(1200px, calc(100vw - 32px));
      margin: 24px auto;
    }

    .panel {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }

    .panel-header {
      display: grid;
      gap: 12px;
      padding: 18px;
      border-bottom: 1px solid var(--line);
    }

    .title-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }

    input, textarea, select, button {
      min-height: 40px;
      border: 1px solid #b8c1d1;
      border-radius: 6px;
      font: inherit;
    }

    input, textarea, select {
      width: 100%;
      padding: 8px 10px;
      background: #fff;
      color: var(--ink);
    }

    textarea { min-height: 90px; resize: vertical; }

    button {
      padding: 0 14px;
      background: var(--blue);
      color: #fff;
      font-weight: 750;
      cursor: pointer;
    }

    .issue-list { display: grid; }

    .issue-row {
      display: grid;
      width: 100%;
      gap: 10px;
      padding: 16px 18px;
      border: 0;
      border-bottom: 1px solid var(--line);
      background: transparent;
      color: inherit;
      text-align: left;
      cursor: pointer;
    }

    .issue-row:hover,
    .issue-row[aria-selected="true"] { background: var(--blue-soft); }

    .issue-topline, .detail-topline {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }

    .issue-key {
      flex: 0 0 auto;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
    }

    .summary {
      min-width: 0;
      overflow-wrap: anywhere;
      font-size: 14px;
      font-weight: 650;
      line-height: 1.35;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      width: fit-content;
      min-height: 24px;
      padding: 3px 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 800;
      line-height: 1.2;
      white-space: nowrap;
    }

    .status-to-do { background: #eef1f6; color: #44546f; }
    .status-in-progress { background: var(--yellow-soft); color: var(--yellow); }
    .status-done { background: var(--green-soft); color: var(--green); }

    .detail-panel {
      display: grid;
      gap: 18px;
      min-height: 560px;
      padding: 24px;
    }

    .detail-topline {
      justify-content: space-between;
      align-items: flex-start;
    }

    .detail-title {
      display: grid;
      gap: 8px;
      min-width: 0;
    }

    .detail-title h2 {
      font-size: 24px;
      line-height: 1.2;
      overflow-wrap: anywhere;
    }

    .description {
      max-width: 760px;
      color: #2f3b52;
      font-size: 15px;
      line-height: 1.55;
    }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }

    .meta-item {
      display: grid;
      gap: 6px;
      min-width: 0;
      padding: 14px;
      border-right: 1px solid var(--line);
      background: #fbfcff;
    }

    .meta-item:last-child { border-right: 0; }
    .meta-label { color: var(--muted); font-size: 12px; font-weight: 800; }
    .meta-value { min-width: 0; overflow-wrap: anywhere; font-size: 14px; font-weight: 650; }

    .transition-box, .create-box {
      display: grid;
      gap: 12px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcff;
    }

    .inline-controls {
      display: flex;
      flex-wrap: wrap;
      align-items: end;
      gap: 12px;
    }

    label {
      display: grid;
      gap: 7px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
    }

    .toast {
      min-height: 20px;
      color: var(--green);
      font-size: 13px;
      font-weight: 650;
    }

    @media (max-width: 820px) {
      header { align-items: flex-start; flex-direction: column; padding: 16px; }
      main { grid-template-columns: 1fr; width: min(100vw - 24px, 680px); }
      .detail-topline, .meta-grid { grid-template-columns: 1fr; }
      .detail-topline { display: grid; }
      .meta-item { border-right: 0; border-bottom: 1px solid var(--line); }
      .meta-item:last-child { border-bottom: 0; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Jelawang Jira Demo</h1>
      <p class="muted">Local fake Jira</p>
    </div>
    <a href="/">Meeting Demo</a>
  </header>

  <main>
    <section class="panel" aria-label="Issues">
      <div class="panel-header">
        <div class="title-row">
          <h2>Issues</h2>
          <span class="issue-key" data-testid="issue-count"></span>
        </div>
        <input data-testid="jira-search-input" type="search" placeholder="Search issues" autocomplete="off" />
      </div>
      <div class="issue-list" data-testid="issue-list"></div>
    </section>

    <section class="panel detail-panel" aria-label="Issue detail">
      <div data-testid="issue-detail"></div>
      <form class="create-box" data-testid="create-issue-form">
        <h3>Create Issue</h3>
        <label>Summary <input data-testid="create-summary" name="summary" required /></label>
        <label>Description <textarea data-testid="create-description" name="description"></textarea></label>
        <div class="inline-controls">
          <label>Assignee <input data-testid="create-assignee" name="assignee" value="Unassigned" /></label>
          <label>Priority
            <select data-testid="create-priority" name="priority">
              <option>Low</option>
              <option selected>Medium</option>
              <option>High</option>
            </select>
          </label>
          <button type="submit">Create</button>
        </div>
        <div class="toast" data-testid="create-toast"></div>
      </form>
    </section>
  </main>

  <script>
    const statuses = ["To Do", "In Progress", "Done"];
    const state = { issues: [], selectedKey: null, query: "" };

    const statusClass = (status) => "status-" + status.toLowerCase().replaceAll(" ", "-");
    const escapeHtml = (value) => String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

    async function loadIssues(preferredKey) {
      const url = state.query ? `/api/issues?q=${encodeURIComponent(state.query)}` : "/api/issues";
      const response = await fetch(url);
      const payload = await response.json();
      state.issues = payload.issues;
      state.selectedKey = preferredKey || state.selectedKey || state.issues[0]?.key || null;
      if (!state.issues.find((issue) => issue.key === state.selectedKey)) {
        state.selectedKey = state.issues[0]?.key || null;
      }
      render();
    }

    function selectedIssue() {
      return state.issues.find((issue) => issue.key === state.selectedKey) || state.issues[0];
    }

    function render() {
      renderIssueList();
      renderDetail();
    }

    function renderIssueList() {
      const list = document.querySelector('[data-testid="issue-list"]');
      document.querySelector('[data-testid="issue-count"]').textContent = `${state.issues.length} shown`;
      list.innerHTML = state.issues.length ? state.issues.map((issue) => `
        <button class="issue-row" type="button" aria-selected="${issue.key === state.selectedKey}"
          data-testid="issue-row-${escapeHtml(issue.key)}" data-issue-key="${escapeHtml(issue.key)}">
          <span class="issue-topline">
            <span class="issue-key">${escapeHtml(issue.key)}</span>
            <span class="pill ${statusClass(issue.status)}" data-testid="issue-status">${escapeHtml(issue.status)}</span>
          </span>
          <span class="summary" data-testid="issue-summary">${escapeHtml(issue.summary)}</span>
        </button>
      `).join("") : `<div class="issue-row"><span class="summary">No issues found.</span></div>`;

      list.querySelectorAll("[data-issue-key]").forEach((row) => {
        row.addEventListener("click", () => {
          state.selectedKey = row.dataset.issueKey;
          render();
        });
      });
    }

    function renderDetail() {
      const issue = selectedIssue();
      const detail = document.querySelector('[data-testid="issue-detail"]');
      if (!issue) {
        detail.innerHTML = `<p class="description">No issue selected.</p>`;
        return;
      }

      detail.innerHTML = `
        <div class="detail-topline">
          <div class="detail-title">
            <span class="issue-key" data-testid="selected-issue-key">${escapeHtml(issue.key)}</span>
            <h2 data-testid="selected-issue-summary">${escapeHtml(issue.summary)}</h2>
          </div>
          <span class="pill ${statusClass(issue.status)}" data-testid="selected-issue-status">${escapeHtml(issue.status)}</span>
        </div>
        <p class="description" data-testid="selected-issue-description">${escapeHtml(issue.description)}</p>
        <div class="meta-grid">
          <div class="meta-item">
            <span class="meta-label">Assignee</span>
            <span class="meta-value" data-testid="selected-issue-assignee">${escapeHtml(issue.assignee)}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Priority</span>
            <span class="meta-value" data-testid="selected-issue-priority">${escapeHtml(issue.priority)}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Labels</span>
            <span class="meta-value" data-testid="selected-issue-labels">${issue.labels.map(escapeHtml).join(", ")}</span>
          </div>
        </div>
        <div class="transition-box">
          <div class="inline-controls">
            <label>Status
              <select data-testid="status-select">
                ${statuses.map((status) => `<option value="${escapeHtml(status)}" ${status === issue.status ? "selected" : ""}>${escapeHtml(status)}</option>`).join("")}
              </select>
            </label>
            <button type="button" data-testid="transition-button">Update status</button>
          </div>
          <div class="toast" role="status" data-testid="transition-toast"></div>
        </div>
      `;

      detail.querySelector('[data-testid="transition-button"]').addEventListener("click", async () => {
        const status = detail.querySelector('[data-testid="status-select"]').value;
        const response = await fetch(`/api/issues/${encodeURIComponent(issue.key)}/transition`, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({status})
        });
        const updated = await response.json();
        state.selectedKey = updated.key;
        await loadIssues(updated.key);
        document.querySelector('[data-testid="transition-toast"]').textContent = `${updated.key} is ${updated.status}`;
      });
    }

    document.querySelector('[data-testid="jira-search-input"]').addEventListener("input", async (event) => {
      state.query = event.target.value;
      await loadIssues();
    });

    document.querySelector('[data-testid="create-issue-form"]').addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = new FormData(event.target);
      const labels = state.query ? state.query.split(/\\s+/).filter(Boolean) : [];
      const response = await fetch("/api/issues", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          summary: form.get("summary"),
          description: form.get("description"),
          assignee: form.get("assignee") || "Unassigned",
          priority: form.get("priority") || "Medium",
          labels
        })
      });
      const issue = await response.json();
      const guardrail = issue.blameless_guardrail;
      event.target.reset();
      state.query = "";
      document.querySelector('[data-testid="jira-search-input"]').value = "";
      state.selectedKey = issue.key;
      await loadIssues(issue.key);
      document.querySelector('[data-testid="create-toast"]').textContent = guardrail?.triggered
        ? `Created ${issue.key} with blameless rewrite: ${guardrail.rewrite}`
        : `Created ${issue.key}`;
    });

    loadIssues();
  </script>
</body>
</html>
"""
