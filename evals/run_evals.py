import json

from evals.judges import judge_faithfulness


def agreement_rate(labeled_path: str = "data/eval_dataset.jsonl"):
    try:
        with open(labeled_path, "r") as file:
            rows = [json.loads(line) for line in file]
    except (FileNotFoundError, OSError) as e:
        print(f"Error opening file: {labeled_path} - reason: {e!s}")
        rows = []

    agree = 0
    for row in rows:  # each row has human_score 1-5
        judge_result = judge_faithfulness(
            context=row["context"],
            response=row["response"],
        )
        # exact match or within 1 point
        if abs(judge_result["score"] - row["human_score"]) <= 1:
            agree += 1

    rate = agree / len(rows)
    print(f"Judge/human agreement: {rate:.0%} over {len(rows)} labeled examples")
    return rate


if __name__ == "__main__":
    agreement_rate()
