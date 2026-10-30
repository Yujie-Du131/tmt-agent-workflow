"""Benchmark: which check catches which corruption of the SDRF.

Writes each corrupted SDRF to data/corrupted_sdrf/, then runs three
checkers on it (sdrf-pipelines, rules.py, and the LLM review) and writes
results to examples/benchmark/.

Usage (from the repository root):
    uv run python scripts/run_benchmark.py            # LLM run 3 times per file
    uv run python scripts/run_benchmark.py --runs 1   # quicker and cheaper
    uv run python scripts/run_benchmark.py --no-llm   # no API calls
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from tmt_agents.benchmark import (
    llm_detected,
    llm_other_findings,
    rule_errors,
    run_sdrf_pipelines,
)
from tmt_agents.corruptions import CORRUPTIONS, Corruption
from tmt_agents.design_check import default_model, review_sdrf
from tmt_agents.rules import load_design, run_all
from tmt_agents.sdrf_io import read_sdrf, write_sdrf

DESIGN_DIR = Path("data/own_design")
CORRUPT_DIR = Path("data/corrupted_sdrf")
OUT_DIR = Path("examples/benchmark")

CLEAN = Corruption("00_clean", "-", "Correct SDRF (false-positive control).", lambda s: s)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3, help="LLM runs per file")
    parser.add_argument("--no-llm", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    client = None
    if not args.no_llm:
        import anthropic
        client = anthropic.Anthropic()

    clean = read_sdrf(DESIGN_DIR / "sdrf.tsv")
    design = load_design(DESIGN_DIR / "design.json")
    description = (DESIGN_DIR / "design_description.md").read_text(encoding="utf-8")
    CORRUPT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "llm").mkdir(parents=True, exist_ok=True)

    manifest, rows = [], []
    for c in [CLEAN] + CORRUPTIONS:
        sdrf = c.apply(clean.copy())
        path = CORRUPT_DIR / f"{c.id}.tsv"
        write_sdrf(sdrf, path)
        manifest.append({
            "id": c.id, "category": c.category, "description": c.description,
            "expected_rules": c.expected_rules, "target_columns": c.target_columns,
        })

        validator_hit, validator_msg = run_sdrf_pipelines(path)
        issues = run_all(sdrf, design)
        errors = rule_errors(issues)
        if c.expected_rules:
            rules_hit = set(c.expected_rules) <= errors
        else:
            rules_hit = bool(errors)  # for B, C and clean, any error is unexpected

        row = {
            "id": c.id,
            "category": c.category,
            "sdrf_pipelines": validator_hit,
            "rules": rules_hit,
            "rule_errors": ", ".join(sorted(errors)),
        }

        if client is not None:
            hits, others = 0, 0
            for k in range(1, args.runs + 1):
                review = review_sdrf(description, sdrf, issues, client)
                (OUT_DIR / "llm" / f"{c.id}_run{k}.json").write_text(
                    json.dumps(review, indent=2), encoding="utf-8"
                )
                hits += llm_detected(review, c.target_columns) if c.target_columns else 0
                others += llm_other_findings(review, c.target_columns)
            row["llm_semantic"] = f"{hits}/{args.runs}" if c.target_columns else "-"
            row["llm_other_findings"] = others
        row["validator_message"] = validator_msg
        rows.append(row)
        print(f"{c.id:36} validator={validator_hit!s:5} rules={rules_hit!s:5} "
              f"llm={row.get('llm_semantic', 'skipped')}")

    (CORRUPT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    table = pd.DataFrame(rows)
    table.to_csv(OUT_DIR / "results.csv", index=False)

    header = [
        "# Corrupted-SDRF benchmark",
        "",
        f"LLM: `{default_model()}`, {args.runs} run(s) per file." if client else "LLM: not run.",
        "",
        "- `sdrf_pipelines`: the official validator reported an error.",
        "- `rules`: for category A, every expected rule fired; for other rows, "
        "True means rules.py reported an error (unexpected).",
        "- `llm_semantic`: runs in which the LLM reported a mismatch on the corrupted column.",
        "- `llm_other_findings`: LLM findings on columns that were not corrupted "
        "(summed over runs; review these for false alarms).",
        "",
    ]
    show = table.drop(columns=["validator_message"])
    (OUT_DIR / "results.md").write_text(
        "\n".join(header) + show.to_markdown(index=False) + "\n", encoding="utf-8"
    )
    print(f"\nWrote {OUT_DIR / 'results.md'} and {OUT_DIR / 'results.csv'}")


if __name__ == "__main__":
    main()
