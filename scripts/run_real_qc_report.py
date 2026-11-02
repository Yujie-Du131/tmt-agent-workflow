"""Ask the LLM for an open-ended QC report on a real quantms run.

The model is not told what (if anything) is wrong. Each run's report is
saved as JSON and Markdown for manual review.

Usage (from the repository root):
    uv run python scripts/run_real_qc_report.py \
        data/quantms_pxd000001 shift0.002 examples/real_qc_reports --runs 3

The data folder must contain msstats_in_<tag>.csv.gz, params_<tag>.json,
isobaric_command_<tag>.sh and PXD000001.sdrf.tsv.
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from tmt_agents.design_check import default_model
from tmt_agents.quantms_qc import (
    channel_metrics,
    expected_amounts,
    protein_matrix,
    psm_counts,
    read_msstats_in,
    spike_in_recovery,
)
from tmt_agents.run_qc_report import format_run_qc_report, run_qc_prompt, write_run_qc_report
from tmt_agents.sdrf_io import read_sdrf


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("tag")
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()

    d = args.data_dir
    msstats = read_msstats_in(d / f"msstats_in_{args.tag}.csv.gz")
    y = protein_matrix(msstats)
    _, spikes = spike_in_recovery(y, expected_amounts(msstats), psm_counts(msstats))
    metrics = channel_metrics(y, exclude=[p for p in spikes["protein"] if p])
    params = json.loads((d / f"params_{args.tag}.json").read_text(encoding="utf-8"))
    command = (d / f"isobaric_command_{args.tag}.sh").read_text(encoding="utf-8")
    prompt = run_qc_prompt(metrics, spikes, read_sdrf(d / "PXD000001.sdrf.tsv"), params, command)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / f"prompt_{args.tag}.txt").write_text(prompt, encoding="utf-8")

    load_dotenv()
    import anthropic
    client = anthropic.Anthropic()
    for k in range(1, args.runs + 1):
        report = write_run_qc_report(prompt, client)
        stem = f"{args.tag}_run{k}"
        (args.out_dir / f"{stem}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        (args.out_dir / f"{stem}.md").write_text(

            f"# QC report on quantms output ({args.tag}, run {k}, model `{default_model()}`)\n\n"
            + format_run_qc_report(report), encoding="utf-8")
        causes = [c["cause"] for i in report["issues"] for c in i["likely_causes"][:1]]
        print(f"run {k}: overall={report['overall']}; issues={len(report['issues'])}; "
              f"top causes={causes}")
    print(f"Reports written to {args.out_dir}/")


if __name__ == "__main__":
    main()
