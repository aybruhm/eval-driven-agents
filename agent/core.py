import os
import time
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv

from agent.tools import TOOL_FUNCTIONS, TOOLS
from agent.tracing import Trace

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Identity-linked API keys must declare which workspace a request acts in.
workspace_id = os.environ.get("ANTHROPIC_WORKSPACE_ID", None)
client = anthropic.Anthropic(
    default_headers={"anthropic-workspace-id": workspace_id} if workspace_id else None,
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

DEFAULT_SYSTEM_PROMPT = (
    "You are a customer support agent for an online store. Use the available "
    "tools to look up order status and knowledge base articles before answering. "
    "Answer with only the facts the tools returned. Do not speculate, do not add "
    "suggestions or recommendations, and do not mention steps the tools did not provide."
)


def run_agent(
    user_input: str,
    max_steps: int = 6,
    system_prompt: str | None = None,
) -> dict:
    trace = Trace(user_input)
    t0 = time.time()
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_input}]

    for _ in range(max_steps):
        with trace.instrument("model_call"):
            create_kwargs = {
                "model": "claude-sonnet-4-6",
                "max_tokens": 1024,
                "system": system_prompt
                if system_prompt is not None
                else DEFAULT_SYSTEM_PROMPT,
                "tools": TOOLS,
                "messages": messages,
            }
            response = client.messages.create(**create_kwargs)

        messages.append({"role": "assistant", "content": response.content})

        tool_uses = [b for b in response.content if b.type == "tool_use"]
        if not tool_uses:
            final_text = next(b.text for b in response.content if b.type == "text")
            trace.log_step("final_output", output=final_text)
            trace.save()
            return {
                "output": final_text,
                "trace_id": trace.trace_id,
                "latency_s": time.time() - t0,
            }

        tool_results = []
        for tool_use in tool_uses:
            trace.log_step("tool_call", tool=tool_use.name, args=tool_use.input)
            result = TOOL_FUNCTIONS[tool_use.name](**tool_use.input)
            trace.log_step("tool_result", tool=tool_use.name, result=result)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": str(result),
                }
            )
        messages.append({"role": "user", "content": tool_results})

    trace.save()
    return {
        "output": None,
        "error": "max_steps_exceeded",
        "trace_id": trace.trace_id,
        "latency_s": time.time() - t0,
    }


if __name__ == "__main__":
    input = "What's the status of order 4472?"
    response = run_agent(
        input,
        max_steps=10,
    )
