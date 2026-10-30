"""List LLM findings that fall outside the corrupted column, for manual review.

Usage (from the repository root, after run_benchmark.py):
    uv run python scripts/list_other_findings.py
"""

import json
from pathlib import Path

from tmt_agents.benchmark import finding_hits, semantic_findings

MANIFEST = Path("data/corrupted_sdrf/manifest.json")
LLM_DIR = Path("examples/benchmark/llm")


def main() -> None:
    cases = {c["id"]: c for c in json.loads(MANIFEST.read_text(encoding="utf-8"))}
    for path in sorted(LLM_DIR.glob("*_run*.json")):
        case_id, run = path.stem.rsplit("_run", 1)
        targets = cases[case_id]["target_columns"]
        review = json.loads(path.read_text(encoding="utf-8"))
        for f in semantic_findings(review):
            if finding_hits(f, targets):
                continue
            print(f"== {case_id}  run {run}  [{f['category']}]")
            print(f"   columns:  {f['columns']}")
            print(f"   evidence: {f['evidence']}")
            print()


if __name__ == "__main__":
    main()
