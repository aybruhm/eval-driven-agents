import json
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any


class Trace:
    def __init__(self, run_input: str) -> None:
        self.trace_id = str(uuid.uuid4())
        self.run_input = run_input
        self.steps: list[dict[str, Any]] = []
        self.start_time = time.time()

    def log_step(self, step_type: str, **data) -> None:
        self.steps.append(
            {
                "step_type": step_type,  # "model_call" | "tool_call" | "tool_result" | "final_output"
                "timestamp": time.time() - self.start_time,
                **data,
            }
        )

    @contextmanager
    def instrument(self, step_type: str, **data):
        t0 = time.time()
        yield
        data["duration_s"] = time.time() - t0
        self.log_step(step_type, **data)

    def save(self, path: str = "data/traces"):
        Path(path).mkdir(parents=True, exist_ok=True)
        record = {
            "trace_id": self.trace_id,
            "input": self.run_input,
            "steps": self.steps,
        }
        with open(f"{path}/{self.trace_id}.jsonl", "w") as f:
            f.write(json.dumps(record) + "\n")
        return record
