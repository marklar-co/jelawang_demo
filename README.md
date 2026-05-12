# jelawang_demo

Local FastAPI demo with a fake Jira UI and an OpenAI Agents SDK browser operator.

## Run the app

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/jira`.

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
