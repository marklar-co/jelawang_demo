# jelawang_demo

Local FastAPI demo for a hackathon project called Meeting-to-Jira Agent.

The app simulates a live engineering meeting, surfaces related fake Jira tickets, drafts follow-up work, flags blameful wording, and includes an OpenAI Agents SDK architecture for the next LLM-backed pass.

The blamelessness guardrail is deterministic: transcript lines and fake Jira issue submissions are normalized into systems-focused wording before task drafts or stored issue text are produced.

## Run the app

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/` for the meeting demo.

Fake Jira is at `http://127.0.0.1:8000/jira`.

## Demo flow

1. Click `Reset Demo`.
2. Click `Next Transcript Chunk`.
3. Watch detected topics, related tickets, task drafts, and blameless rewrites update.
4. When related tickets appear, click `Browser Search` to have Playwright search fake Jira.
5. Open `http://127.0.0.1:8000/jira` to inspect search, issue detail, status changes, and issue creation.

## Useful endpoints

```bash
curl -X POST http://127.0.0.1:8000/meeting/reset
curl http://127.0.0.1:8000/meeting/next
curl http://127.0.0.1:8000/meeting/state
curl "http://127.0.0.1:8000/api/search?q=auth%20websocket%20reconnect"
curl "http://127.0.0.1:8000/browser-demo/search?q=auth%20websocket%20reconnect"
curl http://127.0.0.1:8000/meeting/agents
```

The browser demo runs visibly when a display is available and headless otherwise. Set `BROWSER_DEMO_HEADLESS=0` before starting the server to force a visible browser, or `BROWSER_DEMO_HEADLESS=1` to force headless mode.

## Run the agent automation

In another shell:

```bash
source .venv/bin/activate
export OPENAI_API_KEY=...
python automate_jira.py
```

Optional environment variables:

- `JIRA_DEMO_URL`: defaults to `http://127.0.0.1:8000`
- `JIRA_DEMO_ISSUE`: defaults to `JEL-102`
- `JIRA_DEMO_STATUS`: defaults to `In Progress`
- `JIRA_DEMO_HEADLESS`: set to `0` to watch the browser
- `OPENAI_AGENT_MODEL`: set to override the Agents SDK default model
