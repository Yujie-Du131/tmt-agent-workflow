"""QC benchmark: simulated intensities with planted problems.

For each scenario, simulates protein intensities for the own design,
computes QC metrics, applies a simple threshold baseline, and asks the LLM
to write a QC report from the metrics alone. Results go to examples/qc/.

Usage (from the repository root):
    uv run python scripts/run_qc_benchmark.py            # 3 LLM runs per scenario
    uv run python scripts/run_qc_benchmark.py --runs 1
    uv run python scripts/run_qc_benchmark.py --no-llm
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from tmt_agents.contrasts import contrast_catalogue, contrast_stratum, sample_table
from tmt_agents.design_check import default_model
from tmt_agents.qc_metrics import SLOPE_LIMIT, Z_LIMIT, compute_qc, threshold_flags
from tmt_agents.qc_report import format_qc_report, score_report, write_qc_report
from tmt_agents.qc_simulate import scenarios
from tmt_agents.rules import load_design
from tmt_agents.sdrf_io import read_sdrf

DESIGN_DIR = Path("data/own_design")
DATA_DIR = Path("data/simulated_qc")
OUT_DIR = Path("examples/qc")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--no-llm", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    client = None
    if not args.no_llm:
        import anthropic
        client = anthropic.Anthropic()

    design = load_design(DESIGN_DIR / "design.json")
    samples = sample_table(read_sdrf(DESIGN_DIR / "sdrf.tsv"), design)
    strata = contrast_stratum(samples, contrast_catalogue(design))
    description = (DESIGN_DIR / "design_description.md").read_text(encoding="utf-8")
    for d in [DATA_DIR, OUT_DIR / "metrics", OUT_DIR / "reports"]:
        d.mkdir(parents=True, exist_ok=True)

    rows, manifest = [], []
    for sc in scenarios(samples):
        y = sc.make(samples)
        y.round(4).to_csv(DATA_DIR / f"{sc.id}.csv")
        qc = compute_qc(y, samples)
        (OUT_DIR / "metrics" / f"{sc.id}.json").write_text(json.dumps(qc, indent=1), encoding="utf-8")
        manifest.append({"id": sc.id, "description": sc.description,
                         "issue_type": sc.issue_type, "samples": sc.samples})

        flagged = threshold_flags(qc)
        if sc.issue_type is None:
            baseline = not flagged
        else:
            baseline = bool(flagged & set(sc.samples))
        row = {"id": sc.id, "planted": sc.issue_type or "none",
               "threshold_baseline": baseline,
               "baseline_flagged": ", ".join(sorted(flagged))}

        if client is not None:
            detected, extra = 0, 0
            for k in range(1, args.runs + 1):
                report = write_qc_report(description, qc, strata, client)
                (OUT_DIR / "reports" / f"{sc.id}_run{k}.json").write_text(
                    json.dumps(report, indent=2), encoding="utf-8")
                (OUT_DIR / "reports" / f"{sc.id}_run{k}.md").write_text(
                    f"# QC report: {sc.id} (run {k})\n\n" + format_qc_report(report),
                    encoding="utf-8")
                s = score_report(report, sc.issue_type, sc.samples)
                detected += s["detected"]
                extra += s["extra_issues"]
            row["llm_correct"] = f"{detected}/{args.runs}"
            row["llm_extra_issues"] = extra
        rows.append(row)
        print(f"{sc.id:26} baseline={baseline!s:5} llm={row.get('llm_correct', 'skipped')}")

    (DATA_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    table = pd.DataFrame(rows)
    table.to_csv(OUT_DIR / "results.csv", index=False)
    header = [
        "# QC benchmark (simulated data)",
        "",
        f"LLM: `{default_model()}`, {args.runs} run(s) per scenario." if client else "LLM: not run.",
        "",
        f"- `threshold_baseline`: a channel in the planted set was flagged by |robust z| > {Z_LIMIT} "
        f"or paired-ratio slope < {SLOPE_LIMIT} (clean row: nothing flagged). The baseline gives no issue type.",
        "- `llm_correct`: runs in which the report named the planted issue type for a planted "
        "channel (clean row: runs with no issues reported).",
        "- `llm_extra_issues`: other issues reported, summed over runs; reviewed by hand.",
        "",
    ]
    (OUT_DIR / "results.md").write_text("\n".join(header) + table.to_markdown(index=False) + "\n",
                                        encoding="utf-8")
    print(f"\nWrote {OUT_DIR / 'results.md'}")


if __name__ == "__main__":
    main()
