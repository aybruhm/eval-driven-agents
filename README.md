# eval-driven-agents

An evaluation-driven agents refresher course: traces, error analysis,
evaluators, CI regression gates, red-teaming, and evidence-backed
optimization. Everything here is runnable against a toy customer support
agent (`agent/core.py` with `search_kb` + `get_order_status` tools).

## Layout

```
agent/
  core.py        # the agent loop + tool calls (capstone agent)
  tools.py       # toy order/KB tool implementations
  tracing.py     # trace capture wrapper (one JSONL per run)
data/
  traces/        # raw run traces, one JSONL file per run
  failure_log.jsonl       # curated reproducible failures
  eval_dataset.jsonl      # labeled cases for evaluators
  eval_dataset_holdout.jsonl  # held-out set for experiments
evals/
  judges.py      # LLM-as-judge (faithfulness rubric)
  checks.py      # code-based evaluators + guardrail checks
  run_evals.py   # judge/human agreement measurement
tests/
  automatic/test_regressions.py  # pytest suite wired into CI
  manual/
    review_traces.py  # interactive trace → failure-log review
    taxonomy.py       # failure-category frequency
redteam/
  attacks.py     # prompt-injection attacks + guardrail checks
experiments/
  run_experiment.py   # variant comparison with stats
prompts/
  v1.txt, v2_shorter.txt  # system-prompt variants for experiments
.github/workflows/eval-ci.yml  # gates PRs on the eval suite
capstone_report.md   # capstone write-up with measured numbers
```

## Setup

```sh
uv sync                 # or: pip install -r requirements.txt
cp .env.template .env   # then add ANTHROPIC_API_KEY (and workspace header if needed)
```

## Build an agent you can measure

```sh
uv run python -m agent.core                     # one example run
uv run python tests/manual/review_traces.py     # tag failures into data/failure_log.jsonl
```

Every run writes `data/traces/<trace_id>.jsonl` with model calls, tool calls,
tool results, and the final output. Traces are committed, so failures can be
reviewed without re-running the model.

## Error analysis and evaluators you trust

```sh
uv run python tests/manual/taxonomy.py          # failure-category frequency
uv run python -m evals.run_evals                # judge/human agreement on data/eval_dataset.jsonl
```

- Code evals: `evals/checks.py` (tool selection, tool args, safety denylist)
- LLM judge: `evals/judges.py` (faithfulness, 1–5, JSON output)
- Agreement: 100% (12/12, ±1 point) as measured in `capstone_report.md`

## CI for regressions and red-teaming

```sh
uv run python -m pytest tests/automatic/test_regressions.py -v
uv run python -c "from redteam.attacks import run_attack_suite; from agent.core import run_agent; print(run_attack_suite(run_agent))"
```

`.github/workflows/eval-ci.yml` runs the suite on every PR (needs
`ANTHROPIC_API_KEY` in repo secrets) and prints the dollar cost of every
agent and judge call next to the scores. The suite also re-measures
judge/human agreement on each run, so bumping `AGENT_MODEL` or `JUDGE_MODEL`
gets revalidated automatically. The suite caught a real regression:
faithfulness pass rate 75% (3 retrieval-miss cases), later fixed by the
retrieval tuning in `agent/tools.py`.

## Optimize with evidence

```sh
uv run python -m experiments.run_experiment      # variants vs the held-out set
```

Reports score ± stdev, latency, and cost together. Results and the
recommendation live in `capstone_report.md`.

> Cost tracking is live: `run_agent` returns `cost_usd` per run (from
> `response.usage`), so `experiments/run_experiment.py` prints real costs.
