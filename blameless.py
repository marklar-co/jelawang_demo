from __future__ import annotations

import re
from typing import Any


PERSON_ACTIONS = {
    "missed": "missed",
    "forgot": "forgot",
    "broke": "broke",
    "caused": "caused",
}
TEAM_WORDS = {"qa", "dev", "backend", "frontend", "platform", "infra", "engineering"}


def detect_blameful_language(text: str) -> dict[str, Any]:
    """Detect blameful phrasing with deterministic patterns."""
    issues: list[dict[str, str]] = []
    body = _strip_speaker(text)

    for action in PERSON_ACTIONS:
        pattern = re.compile(
            rf"\b(?P<actor>[A-Z][a-z]+)\s+{action}\s+(?P<object>[^.]+?)(?:\.|,| so| but|$)",
            re.IGNORECASE,
        )
        for match in pattern.finditer(body):
            actor = match.group("actor").strip()
            if actor.lower() in TEAM_WORDS:
                continue
            issues.append(
                {
                    "kind": f"person-{action}",
                    "actor": actor,
                    "phrase": match.group(0).strip(),
                    "reason": (
                        f"Names {actor} as the cause. Reframe around process, tooling, "
                        "coverage, or system controls."
                    ),
                }
            )

    team_pattern = re.compile(
        r"\b(?P<actor>QA|Dev|Backend|Frontend|Platform|Infra|Engineering|[A-Za-z]+\s+team)\s+"
        r"(?P<action>missed|forgot|broke|caused|failed to)\s+"
        r"(?P<object>[^.]+?)(?:\.|,| so| but|$)",
        re.IGNORECASE,
    )
    for match in team_pattern.finditer(body):
        actor = match.group("actor").strip()
        issues.append(
            {
                "kind": "team-accusatory",
                "actor": actor,
                "phrase": match.group(0).strip(),
                "reason": (
                    f"Uses accusatory wording around {actor}. Reframe around missing "
                    "coverage, unclear ownership, or weak process controls."
                ),
            }
        )

    return {"triggered": bool(issues), "issues": issues}


def rewrite_blameless(text: str) -> str:
    """Rewrite known blameful wording into systems-focused language."""
    speaker, body = _split_speaker(text)
    rewritten = body

    rewrite_rules = [
        (
            re.compile(r"\b[A-Z][a-z]+\s+missed\s+the\s+cache invalidation step\b.*", re.IGNORECASE),
            "The release process did not make the cache invalidation step explicit.",
        ),
        (
            re.compile(r"\bQA\s+missed\s+the\s+regression\b.*", re.IGNORECASE),
            "The regression suite did not cover this scenario.",
        ),
        (
            re.compile(r"\b[A-Z][a-z]+\s+broke\s+the\s+deployment\b.*", re.IGNORECASE),
            "The deployment process allowed an unsafe change to reach production.",
        ),
        (
            re.compile(r"\bbackend\s+failed to\s+([^.,]+).*", re.IGNORECASE),
            r"The backend ownership and review process did not make \1 explicit.",
        ),
        (
            re.compile(r"\bfrontend\s+failed to\s+([^.,]+).*", re.IGNORECASE),
            r"The frontend ownership and review process did not make \1 explicit.",
        ),
        (
            re.compile(r"\bdev\s+failed to\s+([^.,]+).*", re.IGNORECASE),
            r"The engineering process did not make \1 explicit.",
        ),
        (
            re.compile(r"\bQA\s+failed to\s+([^.,]+).*", re.IGNORECASE),
            r"The test plan did not make \1 explicit.",
        ),
        (
            re.compile(r"\b[A-Z][a-z]+\s+forgot\s+to\s+([^.,]+).*", re.IGNORECASE),
            r"The team checklist did not make it explicit to \1.",
        ),
        (
            re.compile(r"\b[A-Z][a-z]+\s+missed\s+([^.,]+).*", re.IGNORECASE),
            r"The team process did not make \1 explicit.",
        ),
        (
            re.compile(r"\b[A-Z][a-z]+\s+caused\s+([^.,]+).*", re.IGNORECASE),
            r"The system allowed \1 to occur without an earlier control catching it.",
        ),
        (
            re.compile(r"\b[A-Z][a-z]+\s+broke\s+([^.,]+).*", re.IGNORECASE),
            r"The change process allowed \1 to break without an earlier safeguard.",
        ),
    ]

    for pattern, replacement in rewrite_rules:
        if pattern.search(rewritten):
            rewritten = pattern.sub(replacement, rewritten).strip()
            break

    return f"{speaker}: {rewritten}" if speaker else rewritten


def normalize_transcript_for_postmortem(text: str) -> dict[str, Any]:
    """Return raw and normalized wording plus a prevention-oriented guardrail result."""
    detection = detect_blameful_language(text)
    rewrite = rewrite_blameless(text) if detection["triggered"] else text
    prevention_task = ""
    if detection["triggered"]:
        prevention_task = _prevention_task(rewrite)

    return {
        "raw_transcript": text,
        "normalized_transcript": rewrite,
        "blameless_guardrail": {
            "triggered": detection["triggered"],
            "issues": detection["issues"],
            "rewrite": rewrite,
            "prevention_task": prevention_task,
        },
    }


def _prevention_task(rewrite: str) -> str:
    lower = rewrite.lower()
    if "cache invalidation" in lower:
        return "Add cache invalidation as an explicit release checklist item."
    if "regression suite" in lower or "test plan" in lower:
        return "Add regression coverage for the scenario and document the expected test signal."
    if "deployment process" in lower:
        return "Add a deployment safety check that catches unsafe changes before production."
    if "ownership and review" in lower:
        return "Clarify ownership and review expectations for this workflow."
    return "Add a process check that makes the expected step explicit and observable."


def _split_speaker(text: str) -> tuple[str, str]:
    if ":" not in text:
        return "", text.strip()
    speaker, body = text.split(":", 1)
    if not speaker.strip():
        return "", body.strip()
    return speaker.strip(), body.strip()


def _strip_speaker(text: str) -> str:
    return _split_speaker(text)[1]
