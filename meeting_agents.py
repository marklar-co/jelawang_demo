from __future__ import annotations

import os
from typing import Any

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    ModelSettings,
    OutputGuardrailTripwireTriggered,
    Runner,
    input_guardrail,
    output_guardrail,
)

from blameless import normalize_transcript_for_postmortem


AGENT_MODEL = os.getenv("OPENAI_AGENT_MODEL") or None


@input_guardrail(name="blameless_input_guardrail", run_in_parallel=False)
def blameless_input_guardrail(_context: Any, _agent: Agent[Any], input_data: Any) -> GuardrailFunctionOutput:
    text = _input_to_text(input_data)
    normalized = normalize_transcript_for_postmortem(text)
    return GuardrailFunctionOutput(
        output_info=normalized,
        tripwire_triggered=normalized["blameless_guardrail"]["triggered"],
    )


@output_guardrail(name="blameless_output_guardrail")
def blameless_output_guardrail(_context: Any, _agent: Agent[Any], output_data: Any) -> GuardrailFunctionOutput:
    text = str(output_data)
    normalized = normalize_transcript_for_postmortem(text)
    return GuardrailFunctionOutput(
        output_info=normalized,
        tripwire_triggered=normalized["blameless_guardrail"]["triggered"],
    )


TopicExtractorAgent = Agent(
    name="TopicExtractorAgent",
    model=AGENT_MODEL,
    instructions=(
        "Extract only engineering topics from a meeting transcript line. "
        "Return short topic names and avoid creating tasks."
    ),
)

JiraMatcherAgent = Agent(
    name="JiraMatcherAgent",
    model=AGENT_MODEL,
    instructions=(
        "Match meeting topics to likely Jira tickets. Prefer existing ticket keys "
        "mentioned in the transcript and avoid inventing tickets."
    ),
)

TaskDraftAgent = Agent(
    name="TaskDraftAgent",
    model=AGENT_MODEL,
    instructions=(
        "Draft concise follow-up Jira work from action-oriented meeting lines. "
        "Return a title, description, and suggested owner. Use only blameless, "
        "systems-focused language."
    ),
    input_guardrails=[blameless_input_guardrail],
    output_guardrails=[blameless_output_guardrail],
)

BlamelessnessCoachAgent = Agent(
    name="BlamelessnessCoachAgent",
    model=AGENT_MODEL,
    instructions=(
        "Detect blameful language and rewrite it as process-oriented, blameless language. "
        "Suggest one prevention-oriented follow-up task."
    ),
)

MeetingOrchestratorAgent = Agent(
    name="MeetingOrchestratorAgent",
    model=AGENT_MODEL,
    instructions=(
        "Coordinate meeting intelligence by using the specialist agents as tools. "
        "Keep the output practical for a live engineering demo. Do not emit blameful "
        "language; use systems-focused postmortem wording."
    ),
    model_settings=ModelSettings(parallel_tool_calls=False),
    input_guardrails=[blameless_input_guardrail],
    output_guardrails=[blameless_output_guardrail],
    tools=[
        TopicExtractorAgent.as_tool(
            tool_name="extract_meeting_topics",
            tool_description="Extract engineering topics from one transcript line.",
            max_turns=2,
        ),
        JiraMatcherAgent.as_tool(
            tool_name="match_jira_tickets",
            tool_description="Find likely Jira ticket matches from topics and transcript context.",
            max_turns=2,
        ),
        TaskDraftAgent.as_tool(
            tool_name="draft_follow_up_task",
            tool_description="Draft a follow-up Jira task from action language.",
            max_turns=2,
        ),
        BlamelessnessCoachAgent.as_tool(
            tool_name="coach_blameless_language",
            tool_description="Rewrite blameful language and suggest prevention work.",
            max_turns=2,
        ),
    ],
)


async def run_task_draft_agent_with_guardrails(transcript: str) -> dict[str, Any]:
    """Run the task draft agent and normalize any tripwire-triggering language."""
    try:
        result = await Runner.run(TaskDraftAgent, transcript, max_turns=4)
        return {
            "used_openai_agent": True,
            "final_output": str(result.final_output),
            "input_rewritten": False,
            "output_rewritten": False,
            "blameless_guardrail": normalize_transcript_for_postmortem(str(result.final_output))[
                "blameless_guardrail"
            ],
        }
    except InputGuardrailTripwireTriggered as exc:
        normalized = exc.guardrail_result.output.output_info
        retry_input = normalized["normalized_transcript"]
        result = await Runner.run(TaskDraftAgent, retry_input, max_turns=4)
        return {
            "used_openai_agent": True,
            "final_output": str(result.final_output),
            "input_rewritten": True,
            "output_rewritten": False,
            "blameless_guardrail": normalized["blameless_guardrail"],
            "normalized_input": retry_input,
        }
    except OutputGuardrailTripwireTriggered as exc:
        normalized = exc.guardrail_result.output.output_info
        return {
            "used_openai_agent": True,
            "final_output": normalized["normalized_transcript"],
            "input_rewritten": False,
            "output_rewritten": True,
            "blameless_guardrail": normalized["blameless_guardrail"],
        }


def evaluate_blameless_agent_guardrails(text: str) -> dict[str, Any]:
    """Evaluate the SDK guardrail functions locally without calling a model."""
    input_result = blameless_input_guardrail.guardrail_function(None, TaskDraftAgent, text)
    output_result = blameless_output_guardrail.guardrail_function(None, TaskDraftAgent, text)
    return {
        "input_guardrail": {
            "name": blameless_input_guardrail.get_name(),
            "tripwire_triggered": input_result.tripwire_triggered,
            "output_info": input_result.output_info,
        },
        "output_guardrail": {
            "name": blameless_output_guardrail.get_name(),
            "tripwire_triggered": output_result.tripwire_triggered,
            "output_info": output_result.output_info,
        },
    }


def describe_agents() -> dict[str, object]:
    return {
        "orchestrator": MeetingOrchestratorAgent.name,
        "specialists": [
            TopicExtractorAgent.name,
            JiraMatcherAgent.name,
            TaskDraftAgent.name,
            BlamelessnessCoachAgent.name,
        ],
        "architecture": "agents-as-tools",
        "guardrails": [
            blameless_input_guardrail.get_name(),
            blameless_output_guardrail.get_name(),
        ],
        "guardrail_scope": {
            TaskDraftAgent.name: ["input", "output"],
            MeetingOrchestratorAgent.name: ["input", "output"],
        },
        "note": "The main demo endpoints use deterministic local heuristics. The OpenAI-backed agents now have SDK input/output guardrails using the same blameless checker.",
    }


def _input_to_text(input_data: Any) -> str:
    if isinstance(input_data, str):
        return input_data
    if isinstance(input_data, list):
        return "\n".join(str(item.get("content", item)) if isinstance(item, dict) else str(item) for item in input_data)
    return str(input_data)
