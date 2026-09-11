import json
from typing import Any

import pytest

from agent.core import run_agent
from evals.checks import check_tool_called
from evals.judges import judge_faithfulness


def _open_jsonl(file_path: str) -> list[dict[str, Any]]:
    try:
        with open(file_path, "r") as f:
            CASES = [json.loads(l) for l in f]
    except FileNotFoundError:
        CASES = []
    return CASES


CASES = _open_jsonl("data/eval_dataset.jsonl")


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_tool_selection(case):
    result = run_agent(case["input"])
    trace = _open_jsonl(f"data/traces/{result['trace_id']}.jsonl")[0]
    assert check_tool_called(trace, case["expected_tool"]), (
        f"Expected {case['expected_tool']} for input: {case['input']}"
    )


def test_faithfulness_pass_rate():
    scores = []
    for case in CASES:
        result = run_agent(case["input"])
        judged = judge_faithfulness(case["context"], result["output"])
        scores.append(judged["score"])

    pass_rate = sum(s >= 4 for s in scores) / len(scores)
    assert pass_rate >= 0.85, f"Faithfulness pass rate dropped to {pass_rate:.0%}"
