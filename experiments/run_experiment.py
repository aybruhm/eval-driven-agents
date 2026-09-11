import json
import statistics

from agent.core import run_agent
from evals.judges import judge_faithfulness


def _read_prompt(name: str) -> str:
    with open(name) as f:
        return f.read()


VARIANTS = {
    "baseline": {"system_prompt": _read_prompt("prompts/v1.txt")},
    "variant_a": {"system_prompt": _read_prompt("prompts/v2_shorter.txt")},
}


def run_variant(variant_name: str, cases: list[dict]) -> dict:
    config = VARIANTS[variant_name]
    scores, latencies, costs = [], [], []
    for case in cases:
        result = run_agent(
            case["input"],
            system_prompt=config["system_prompt"],
        )
        judged = judge_faithfulness(case["context"], result["output"])
        scores.append(judged["score"])
        latencies.append(result.get("latency_s", 0))
        costs.append(result.get("cost_usd", 0))

    return {
        "variant": variant_name,
        "mean_score": statistics.mean(scores),
        "stdev_score": statistics.stdev(scores) if len(scores) > 1 else 0,
        "mean_latency_s": statistics.mean(latencies),
        "mean_cost_usd": statistics.mean(costs),
        "n": len(cases),
    }


if __name__ == "__main__":
    with open("data/eval_dataset_holdout.jsonl") as f:
        cases = [json.loads(l) for l in f]

    results = [run_variant(v, cases) for v in VARIANTS]
    for r in results:
        print(
            f"{r['variant']:12} score={r['mean_score']:.2f}±{r['stdev_score']:.2f}  "
            f"latency={r['mean_latency_s']:.2f}s  cost=${r['mean_cost_usd']:.4f}  n={r['n']}"
        )
