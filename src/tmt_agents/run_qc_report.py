"""LLM QC report for a real quantms run.

Unlike qc_report.py (simulated data, fixed list of issue types), this report
is open-ended: the model receives the computed channel metrics, spike-in
recovery, the SDRF and the run parameters, and must say what is wrong and
rank possible causes. It is not told what the problem is.
"""

import json

import pandas as pd

from tmt_agents.design_check import _structured_call, summarise_sdrf

RUN_QC_SCHEMA = {
    "type": "object",
    "properties": {
        "overall": {"type": "string", "enum": ["no_issues", "minor_issues", "major_issues"]},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "channels": {"type": "array", "items": {"type": "string"}},
                    "severity": {"type": "string", "enum": ["minor", "major"]},
                    "observation": {"type": "string"},
                    "evidence": {
                        "type": "string",
                        "description": "Metric values and parameters quoted from the input.",
                    },
                    "likely_causes": {
                        "type": "array",
                        "description": "Most likely first.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "cause": {"type": "string"},
                                "reasoning": {"type": "string"},
                                "how_to_check": {"type": "string"},
                            },
                            "required": ["cause", "reasoning", "how_to_check"],
                            "additionalProperties": False,
                        },
                    },
                    "recommendation": {"type": "string"},
                },
                "required": ["channels", "severity", "observation", "evidence",
                             "likely_causes", "recommendation"],
                "additionalProperties": False,
            },
        },
        "summary": {"type": "string"},
    },
    "required": ["overall", "issues", "summary"],
    "additionalProperties": False,
}

RUN_QC_SYSTEM = (
    "You write the quality-control section for a TMT proteomics run processed "
    "with the quantms pipeline. You see computed metrics, the sample metadata "
    "(SDRF), the pipeline parameters and the command of the quantification "
    "step; you never see plots.\n"
    "1. Quote metric values and parameter values in 'evidence'.\n"
    "2. Report only departures clearly larger than the variation between "
    "channels. If nothing stands out, return no issues.\n"
    "3. For each issue, list possible causes, most likely first, using the "
    "metadata and parameters where relevant, and say how each could be checked.\n"
    "4. Distinguish what the metrics show from what you infer."
)


def run_qc_prompt(metrics: pd.DataFrame, spike_summary: pd.DataFrame,
                  sdrf: pd.DataFrame, params: dict, command: str) -> str:
    return (
        "Channel metrics (computed on non-spiked background proteins; channels "
        "ch1..chN follow the order of comment[label] in the SDRF):\n"
        f"{metrics.to_string()}\n\n"
        "Definitions: n_quantified = proteins with a reporter intensity in the "
        "channel; raw_median = median log2 protein intensity; raw_median_z = "
        "robust z-score of raw_median across channels; corr_to_others = "
        "correlation with the mean of the other channels (NaN if too few "
        "proteins are quantified in all channels).\n\n"
        "Spike-in recovery (slope of measured on expected centred log2 values; "
        "1 = full recovery; computed on the channels where the protein was "
        "quantified):\n"
        f"{spike_summary.to_string(index=False)}\n\n"
        f"SDRF:\n{summarise_sdrf(sdrf)}\n\n"
        f"Pipeline parameters (JSON):\n{json.dumps(params, indent=1)}\n\n"
        f"Command of the quantification step:\n{command}"
    )


def write_run_qc_report(prompt: str, client, model=None) -> dict:
    return _structured_call(client, model, RUN_QC_SYSTEM, prompt, RUN_QC_SCHEMA)


def format_run_qc_report(report: dict) -> str:
    lines = [f"**Overall:** {report['overall']}", "", report["summary"], ""]
    for n, i in enumerate(report["issues"], 1):
        lines += [
            f"### {n}. [{i['severity']}] {', '.join(i['channels']) or 'run-wide'}",
            f"- Observation: {i['observation']}",
            f"- Evidence: {i['evidence']}",
            "- Likely causes:",
        ]
        for k, c in enumerate(i["likely_causes"], 1):
            lines += [
                f"  {k}. {c['cause']}",
                f"     - Reasoning: {c['reasoning']}",
                f"     - How to check: {c['how_to_check']}",
            ]
        lines += [f"- Recommendation: {i['recommendation']}", ""]
    return "\n".join(lines)
