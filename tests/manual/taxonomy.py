import json
from collections import Counter


def build_taxonomy(failure_log: str = "data/failure_log.jsonl"):
    with open(failure_log, "r") as f:
        entries = [json.loads(line) for line in f]

    counts = Counter(e["category"] for e in entries)
    print("Failure category frequency:")
    for cat, n in counts.most_common():
        print(f"  {cat}: {n}")
    return counts


if __name__ == "__main__":
    build_taxonomy()
