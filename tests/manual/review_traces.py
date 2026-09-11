import glob
import json
from pathlib import Path
from typing import Any


def load_traces(path: str = "data/traces"):
    for file in glob.glob(f"{path}/*.jsonl"):
        with open(file, "r") as f:
            contents = f.read()
            yield json.loads(contents)


def append_failure(
    trace: dict[str, Any],
    root_cause: str,
    expected: str,
    category: str = "uncategorized",
):
    entry = {
        "trace_id": trace["trace_id"],
        "input": trace["input"],
        "actual_output": trace["steps"][-1].get("output"),
        "expected_output": expected,
        "root_cause": root_cause,
        "category": category,
    }
    Path("data").mkdir(parents=True, exist_ok=True)
    with open("data/failure_log.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    for trace in load_traces():
        print(f"\n--- {trace['trace_id']} ---")
        print("Input:", trace["input"])

        for step in trace["steps"]:
            print(
                " ",
                step["step_type"],
                {k: v for k, v in step.items() if k not in ("step_type",)},
            )

        verdict = input("Failure? (y/n): ")
        if verdict.lower() == "y":
            root_cause = input("Root cause (one line): ")
            expected = input("Expected output: ")
            append_failure(trace, root_cause, expected)
