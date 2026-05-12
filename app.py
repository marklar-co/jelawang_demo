# app.py
from copy import deepcopy

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()


ISSUE_SEED = [
    {
        "key": "JEL-101",
        "summary": "Create customer CSV import preview",
        "description": "Operations wants to review parsed rows before committing a CSV import.",
        "status": "To Do",
        "assignee": "Maya Chen",
        "priority": "High",
        "labels": ["import", "ops"],
    },
    {
        "key": "JEL-102",
        "summary": "Add audit trail to ticket transitions",
        "description": "Every status change should record who changed it and when.",
        "status": "To Do",
        "assignee": "Ravi Menon",
        "priority": "Medium",
        "labels": ["workflow", "audit"],
    },
    {
        "key": "JEL-103",
        "summary": "Tighten validation on account mapping",
        "description": "Reject duplicate external IDs before the sync job starts.",
        "status": "In Progress",
        "assignee": "Ana Silva",
        "priority": "Medium",
        "labels": ["sync", "validation"],
    },
]

VALID_STATUSES = {"To Do", "In Progress", "Done"}
issues = {issue["key"]: deepcopy(issue) for issue in ISSUE_SEED}


class TransitionRequest(BaseModel):
    status: str


@app.get("/")
def root():
    return {"hello": "world", "fake_jira": "/jira"}


@app.get("/jira", response_class=HTMLResponse)
def fake_jira():
    return HTMLResponse(FAKE_JIRA_HTML)


@app.get("/api/issues")
def list_issues():
    return {"issues": list(issues.values())}


@app.get("/api/issues/{issue_key}")
def get_issue(issue_key: str):
    issue = issues.get(issue_key)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@app.post("/api/issues/{issue_key}/transition")
def transition_issue(issue_key: str, request: TransitionRequest):
    issue = issues.get(issue_key)
    if issue is None:
        raise HTTPException(status_code=404, detail="Issue not found")
    if request.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")

    issue["status"] = request.status
    return issue


@app.post("/api/reset")
def reset_demo():
    issues.clear()
    issues.update({issue["key"]: deepcopy(issue) for issue in ISSUE_SEED})
    return {"issues": list(issues.values())}


FAKE_JIRA_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Local Jira Demo</title>
  <style>
    :root {
      color-scheme: light;
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

    * {
      box-sizing: border-box;
    }

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

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
      font-weight: 700;
    }

    .mark {
      display: grid;
      width: 32px;
      height: 32px;
      place-items: center;
      border-radius: 7px;
      background: var(--blue);
      color: #fff;
      font-size: 14px;
    }

    .toolbar {
      display: flex;
      align-items: center;
      gap: 12px;
      color: var(--muted);
      font-size: 14px;
    }

    main {
      display: grid;
      grid-template-columns: minmax(280px, 380px) minmax(0, 1fr);
      gap: 20px;
      width: min(1180px, calc(100vw - 32px));
      margin: 24px auto;
    }

    .panel {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }

    .list-panel {
      overflow: hidden;
    }

    .panel-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 18px 18px 14px;
      border-bottom: 1px solid var(--line);
    }

    h1,
    h2,
    h3,
    p {
      margin: 0;
    }

    h1 {
      font-size: 18px;
      line-height: 1.25;
    }

    h2 {
      font-size: 16px;
      line-height: 1.35;
    }

    h3 {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }

    .issue-count {
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }

    .issue-list {
      display: grid;
      gap: 0;
    }

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
    .issue-row[aria-selected="true"] {
      background: var(--blue-soft);
    }

    .issue-row:last-child {
      border-bottom: 0;
    }

    .issue-topline,
    .detail-topline,
    .meta-grid {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }

    .issue-key {
      flex: 0 0 auto;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
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
      font-weight: 700;
      line-height: 1.2;
      white-space: nowrap;
    }

    .status-to-do {
      background: #eef1f6;
      color: #44546f;
    }

    .status-in-progress {
      background: var(--yellow-soft);
      color: var(--yellow);
    }

    .status-done {
      background: var(--green-soft);
      color: var(--green);
    }

    .detail-panel {
      min-height: 560px;
      padding: 24px;
    }

    .detail-topline {
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
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
      margin: 18px 0 26px;
      color: #2f3b52;
      font-size: 15px;
      line-height: 1.55;
    }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin: 0 0 28px;
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

    .meta-item:last-child {
      border-right: 0;
    }

    .meta-label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }

    .meta-value {
      min-width: 0;
      overflow-wrap: anywhere;
      font-size: 14px;
      font-weight: 650;
    }

    .transition-box {
      display: flex;
      flex-wrap: wrap;
      align-items: end;
      gap: 12px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fbfcff;
    }

    label {
      display: grid;
      gap: 7px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }

    select,
    button.action {
      min-height: 40px;
      border: 1px solid #b8c1d1;
      border-radius: 6px;
      font: inherit;
    }

    select {
      min-width: 180px;
      padding: 0 34px 0 10px;
      background: #fff;
      color: var(--ink);
    }

    button.action {
      padding: 0 14px;
      background: var(--blue);
      color: #fff;
      font-weight: 700;
      cursor: pointer;
    }

    button.action:hover {
      background: #0055cc;
    }

    .toast {
      min-height: 20px;
      margin-top: 12px;
      color: var(--green);
      font-size: 13px;
      font-weight: 650;
    }

    .board {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 24px;
    }

    .column {
      min-height: 112px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #f9fafc;
    }

    .column h3 {
      margin-bottom: 10px;
    }

    .column-card {
      display: grid;
      gap: 6px;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #fff;
      font-size: 13px;
      line-height: 1.35;
    }

    @media (max-width: 780px) {
      header {
        align-items: flex-start;
        flex-direction: column;
        padding: 16px;
      }

      main {
        grid-template-columns: 1fr;
        width: min(100vw - 24px, 640px);
        margin-top: 16px;
      }

      .detail-panel {
        min-height: 0;
        padding: 18px;
      }

      .detail-topline,
      .meta-grid,
      .board {
        grid-template-columns: 1fr;
      }

      .detail-topline {
        display: grid;
      }

      .meta-item {
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }

      .meta-item:last-child {
        border-bottom: 0;
      }
    }
  </style>
</head>
<body>
  <header>
    <div class="brand">
      <div class="mark" aria-hidden="true">JD</div>
      <h1>Jelawang Jira Demo</h1>
    </div>
    <div class="toolbar">
      <span>Local workspace</span>
      <span aria-hidden="true">/</span>
      <span>Fake Jira</span>
    </div>
  </header>

  <main>
    <section class="panel list-panel" aria-label="Issues">
      <div class="panel-header">
        <h2>Issues</h2>
        <span class="issue-count" data-testid="issue-count"></span>
      </div>
      <div class="issue-list" data-testid="issue-list"></div>
    </section>

    <section class="panel detail-panel" aria-label="Issue detail">
      <div data-testid="issue-detail"></div>
    </section>
  </main>

  <script>
    const statuses = ["To Do", "In Progress", "Done"];
    const state = {
      issues: [],
      selectedKey: null
    };

    const statusClass = (status) => (
      "status-" + status.toLowerCase().replaceAll(" ", "-")
    );

    const escapeHtml = (value) => String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

    async function loadIssues(preferredKey) {
      const response = await fetch("/api/issues");
      const payload = await response.json();
      state.issues = payload.issues;
      state.selectedKey = preferredKey || state.selectedKey || state.issues[0]?.key;
      render();
    }

    function selectedIssue() {
      return state.issues.find((issue) => issue.key === state.selectedKey) || state.issues[0];
    }

    function render() {
      renderIssueList();
      renderDetail();
      renderBoard();
    }

    function renderIssueList() {
      const list = document.querySelector('[data-testid="issue-list"]');
      document.querySelector('[data-testid="issue-count"]').textContent = `${state.issues.length} issues`;

      list.innerHTML = state.issues.map((issue) => `
        <button
          class="issue-row"
          type="button"
          aria-selected="${issue.key === state.selectedKey}"
          data-testid="issue-row-${escapeHtml(issue.key)}"
          data-issue-key="${escapeHtml(issue.key)}"
        >
          <span class="issue-topline">
            <span class="issue-key">${escapeHtml(issue.key)}</span>
            <span class="pill ${statusClass(issue.status)}" data-testid="issue-status">${escapeHtml(issue.status)}</span>
          </span>
          <span class="summary" data-testid="issue-summary">${escapeHtml(issue.summary)}</span>
        </button>
      `).join("");

      list.querySelectorAll(".issue-row").forEach((row) => {
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
        detail.innerHTML = "";
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
          <label>
            Status
            <select data-testid="status-select">
              ${statuses.map((status) => `
                <option value="${escapeHtml(status)}" ${status === issue.status ? "selected" : ""}>${escapeHtml(status)}</option>
              `).join("")}
            </select>
          </label>
          <button class="action" type="button" data-testid="transition-button">Update status</button>
        </div>
        <div class="toast" role="status" data-testid="transition-toast"></div>
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

    function renderBoard() {
      const existing = document.querySelector('[data-testid="status-board"]');
      if (existing) {
        existing.remove();
      }

      const board = document.createElement("div");
      board.className = "board";
      board.dataset.testid = "status-board";
      board.innerHTML = statuses.map((status) => {
        const cards = state.issues
          .filter((issue) => issue.status === status)
          .map((issue) => `
            <div class="column-card" data-testid="board-card-${escapeHtml(issue.key)}">
              <strong>${escapeHtml(issue.key)}</strong>
              <span>${escapeHtml(issue.summary)}</span>
            </div>
          `).join("");

        return `
          <div class="column" data-testid="board-column-${escapeHtml(status)}">
            <h3>${escapeHtml(status)}</h3>
            ${cards || ""}
          </div>
        `;
      }).join("");

      document.querySelector('[data-testid="issue-detail"]').appendChild(board);
    }

    loadIssues();
  </script>
</body>
</html>
"""
