from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field

from blameless import normalize_transcript_for_postmortem
from transcript_demo import TRANSCRIPT


TOPICS = [
    "websocket",
    "reconnect",
    "auth",
    "retry",
    "Redis",
    "middleware",
    "regression",
    "token refresh",
    "telemetry",
    "cache invalidation",
]

TOPIC_ALIASES = {
    "websocket": ["websocket", "web socket", "gateway"],
    "reconnect": ["reconnect", "reconnecting"],
    "auth": ["auth", "authentication", "token expires", "token expired"],
    "retry": ["retry"],
    "Redis": ["redis"],
    "middleware": ["middleware"],
    "regression": ["regression"],
    "token refresh": ["token refresh", "refresh token", "token expires", "token expired"],
    "telemetry": ["telemetry"],
    "cache invalidation": ["cache invalidation", "cache invalidation step"],
}

ACTION_MARKERS = ["we need", "action item", "should", "todo", "follow up"]
STOPWORDS = {
    "about",
    "again",
    "already",
    "another",
    "before",
    "briefly",
    "check",
    "could",
    "during",
    "existing",
    "where",
    "which",
    "would",
}


class RelatedIssue(BaseModel):
    key: str
    summary: str
    description: str
    status: str
    assignee: str
    priority: str
    labels: list[str] = Field(default_factory=list)
    score: int


class TaskDraft(BaseModel):
    title: str
    description: str
    suggested_owner: str
    source_line: str
    related_issue_keys: list[str] = Field(default_factory=list)
    reason: str = "action"


class BlamelessNote(BaseModel):
    warning: str
    original: str
    rewrite: str
    prevention_task: TaskDraft


class BlamelessGuardrail(BaseModel):
    triggered: bool = False
    issues: list[dict[str, str]] = Field(default_factory=list)
    rewrite: str = ""
    prevention_task: str = ""


class MeetingStep(BaseModel):
    index: int
    raw_transcript: str
    normalized_transcript: str
    blameless_guardrail: BlamelessGuardrail = Field(default_factory=BlamelessGuardrail)
    transcript_line: str
    detected_topics: list[str] = Field(default_factory=list)
    related_jira_issues: list[RelatedIssue] = Field(default_factory=list)
    task_draft: TaskDraft | None = None
    blameless_note: BlamelessNote | None = None
    has_more: bool


class DemoState(BaseModel):
    current_transcript_index: int = 0
    last_transcript_line: str | None = None
    surfaced_jira_issues: list[RelatedIssue] = Field(default_factory=list)
    generated_task_drafts: list[TaskDraft] = Field(default_factory=list)
    blameless_warnings: list[BlamelessNote] = Field(default_factory=list)
    history: list[MeetingStep] = Field(default_factory=list)


def extract_topics(line: str) -> list[str]:
    lower = line.lower()
    detected = []
    for topic in TOPICS:
        aliases = TOPIC_ALIASES[topic]
        if any(alias in lower for alias in aliases):
            detected.append(topic)
    return detected


def search_jira_issues(
    query: str,
    topics: list[str],
    issue_values: list[dict[str, Any]],
    limit: int = 3,
) -> list[RelatedIssue]:
    explicit_keys = {key.upper() for key in re.findall(r"\b[A-Z]+-\d+\b", query)}
    query_terms = {
        term
        for term in re.findall(r"[a-zA-Z][a-zA-Z-]{3,}", query.lower())
        if term not in STOPWORDS
    }
    scored: list[tuple[int, dict[str, Any]]] = []

    for issue in issue_values:
        haystack = _issue_haystack(issue)
        score = 0
        if issue["key"].upper() in explicit_keys:
            score += 10
        for topic in topics:
            if any(alias in haystack for alias in TOPIC_ALIASES[topic]):
                score += 3
        for term in query_terms:
            if term in haystack:
                score += 1
        if score:
            scored.append((score, issue))

    scored.sort(key=lambda item: (-item[0], item[1]["key"]))
    return [_to_related_issue(issue, score) for score, issue in scored[:limit]]


def make_task_draft(
    line: str,
    topics: list[str],
    related_issues: list[RelatedIssue],
) -> TaskDraft | None:
    lower = line.lower()
    if not any(marker in lower for marker in ACTION_MARKERS):
        return None

    owner = _speaker(line)
    if not owner.replace(" ", "").isalpha():
        owner = "Unassigned"

    if "retry telemetry" in lower:
        title = "Add retry telemetry for websocket reconnect flow"
    elif "test case" in lower and "redis" in lower:
        title = "Add reconnect tests for token expiry and Redis outage"
    elif "existing jira" in lower:
        title = "Check existing Jira coverage for websocket reconnect"
    elif "cache invalidation" in lower:
        title = "Make cache invalidation explicit in the release checklist"
    else:
        topic_text = ", ".join(topics[:2]) if topics else "meeting follow-up"
        title = f"Follow up on {topic_text}"

    keys = [issue.key for issue in related_issues]
    description = (
        f"Source transcript: {line}\n\n"
        f"Detected topics: {', '.join(topics) or 'none'}.\n"
        f"Related Jira: {', '.join(keys) or 'none found'}."
    )
    return TaskDraft(
        title=title,
        description=description,
        suggested_owner=owner,
        source_line=line,
        related_issue_keys=keys,
    )


def detect_blamelessness_issue(line: str) -> BlamelessNote | None:
    guardrail = normalize_transcript_for_postmortem(line)["blameless_guardrail"]
    if not guardrail["triggered"]:
        return None

    rewrite = guardrail["rewrite"]
    prevention_task_title = guardrail["prevention_task"]
    prevention_task = TaskDraft(
        title=prevention_task_title,
        description=(
            "Create a prevention-oriented follow-up from the normalized transcript.\n\n"
            f"Normalized transcript: {rewrite}"
        ),
        suggested_owner="Team",
        source_line=rewrite,
        reason="blameless-prevention",
    )
    return BlamelessNote(
        warning="Blameful language detected. Reframe around process and prevention.",
        original=line,
        rewrite=rewrite,
        prevention_task=prevention_task,
    )


def process_transcript_line(
    index: int,
    line: str,
    issue_values: list[dict[str, Any]],
) -> MeetingStep:
    normalized = normalize_transcript_for_postmortem(line)
    raw_line = normalized["raw_transcript"]
    normalized_line = normalized["normalized_transcript"]
    guardrail = BlamelessGuardrail(**normalized["blameless_guardrail"])
    search_text = f"{raw_line} {normalized_line}"
    topics = extract_topics(search_text)
    related_issues = search_jira_issues(search_text, topics, issue_values)
    task_draft = make_task_draft(normalized_line, topics, related_issues)
    blameless_note = _guardrail_to_note(raw_line, normalized_line, guardrail)
    return MeetingStep(
        index=index,
        raw_transcript=raw_line,
        normalized_transcript=normalized_line,
        blameless_guardrail=guardrail,
        transcript_line=normalized_line,
        detected_topics=topics,
        related_jira_issues=related_issues,
        task_draft=task_draft,
        blameless_note=blameless_note,
        has_more=index + 1 < len(TRANSCRIPT),
    )


def apply_step_to_state(state: DemoState, step: MeetingStep) -> DemoState:
    state.last_transcript_line = step.transcript_line
    state.current_transcript_index = step.index + 1
    state.history.append(step)

    seen_issue_keys = {issue.key for issue in state.surfaced_jira_issues}
    for issue in step.related_jira_issues:
        if issue.key not in seen_issue_keys:
            state.surfaced_jira_issues.append(issue)
            seen_issue_keys.add(issue.key)

    if step.task_draft:
        state.generated_task_drafts.append(step.task_draft)
    if step.blameless_note:
        state.blameless_warnings.append(step.blameless_note)
        state.generated_task_drafts.append(step.blameless_note.prevention_task)
    return state


def reset_state() -> DemoState:
    return DemoState()


def _guardrail_to_note(
    raw_line: str,
    normalized_line: str,
    guardrail: BlamelessGuardrail,
) -> BlamelessNote | None:
    if not guardrail.triggered:
        return None

    prevention_task = TaskDraft(
        title=guardrail.prevention_task,
        description=(
            "Create a prevention-oriented follow-up from the normalized transcript.\n\n"
            f"Normalized transcript: {normalized_line}"
        ),
        suggested_owner="Team",
        source_line=normalized_line,
        reason="blameless-prevention",
    )
    return BlamelessNote(
        warning="Blameful language detected. Reframe around process and prevention.",
        original=raw_line,
        rewrite=normalized_line,
        prevention_task=prevention_task,
    )


def _issue_haystack(issue: dict[str, Any]) -> str:
    labels = " ".join(issue.get("labels", []))
    return " ".join(
        [
            issue.get("key", ""),
            issue.get("summary", ""),
            issue.get("description", ""),
            issue.get("assignee", ""),
            issue.get("priority", ""),
            labels,
        ]
    ).lower()


def _to_related_issue(issue: dict[str, Any], score: int) -> RelatedIssue:
    return RelatedIssue(
        key=issue["key"],
        summary=issue["summary"],
        description=issue.get("description", ""),
        status=issue.get("status", "To Do"),
        assignee=issue.get("assignee", "Unassigned"),
        priority=issue.get("priority", "Medium"),
        labels=list(issue.get("labels", [])),
        score=score,
    )


def _speaker(line: str) -> str:
    if ":" not in line:
        return "Unassigned"
    return line.split(":", 1)[0].strip()
