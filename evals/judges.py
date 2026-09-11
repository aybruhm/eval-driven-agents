import json
import os
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv

from agent.core import calculate_cost

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Identity-linked API keys must declare which workspace a request acts in.
workspace_id = os.environ.get("ANTHROPIC_WORKSPACE_ID", None)
client = anthropic.Anthropic(
    default_headers={"anthropic-workspace-id": workspace_id} if workspace_id else None,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

# Pin the judge model separately from the agent model. When this bumps,
# CI re-measures judge/human agreement (test_judge_agreement_above_threshold).
# For production, pin a dated snapshot so scores can't drift mid-release.
JUDGE_MODEL = "claude-sonnet-4-6"

JUDGE_PROMPT = """You are grading an AI agent's response for faithfulness to its retrieved context.

Context the agent had access to:
{context}

Agent's response:
{response}

Score 1-5:
1 = response contradicts the context
3 = response contains claims not supported by the context and not directly inferable from it, but not contradictory
4 = every claim in the response is supported by the context or follows directly from it (e.g., contrapositives, comparisons with facts stated in the query)
5 = every claim in the response is explicitly stated in the context

Respond ONLY with JSON: {{"score": <int>, "reasoning": "<one sentence>"}}"""


def judge_faithfulness(context: str, response: str) -> dict[str, Any]:
    result = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": JUDGE_PROMPT.format(
                    context=context,
                    response=response,
                ),
            }
        ],
    )
    content = result.content[0]
    if not hasattr(content, "text"):
        raise ValueError(f"Unexpected response block type: {type(content).__name__}")
    parsed = json.loads(content.text)  # type: ignore
    parsed["cost_usd"] = calculate_cost(result)
    return parsed
