"""LLM QC report written from computed metrics only (no plots)."""

import json

from tmt_agents.design_check import _structured_call
from tmt_agents.qc_metrics import METRIC_DEFINITIONS

ISSUE_TYPES = [
    "low_loading",
    "ratio_compression",
    "outlier_sample",
    "label_swap",
    "loading_confounded_with_treatment",
    "other",
]

QC_SCHEMA = {
    "type": "object",
    "properties": {
        "overall": {"type": "string", "enum": ["no_issues", "minor_issues", "major_issues"]},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "issue_type": {"type": "string", "enum": ISSUE_TYPES},
                    "samples": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Affected channels; empty if the issue is not channel-specific.",
                    },
                    "evidence": {
                        "type": "string",
                        "description": "Metric names and values that support the issue, quoted from the input.",
                    },
                    "impact": {
                        "type": "string",
                        "description": "Which contrasts are affected and why, using the contrast strata.",
                    },
                    "recommendation": {"type": "string"},
                },
                "required": ["issue_type", "samples", "evidence", "impact", "recommendation"],
                "additionalProperties": False,
            },
        },
        "summary": {"type": "string"},
    },
    "required": ["overall", "issues", "summary"],
    "additionalProperties": False,
}

QC_SYSTEM = (
    "You write the quality-control section of a TMT proteomics report. You "
    "see computed QC metrics and their definitions, never plots.\n"
    "1. Base every issue on metric values, and quote the values in 'evidence'.\n"
    "2. Report only departures that are clearly larger than the variation "
    "between the other channels; do not report ordinary variation. If "
    "nothing stands out, return an empty issues list and overall 'no_issues'.\n"
    "3. Consider both single channels and patterns shared by all channels "
    "of one factor level.\n"
    "4. In 'impact', say which contrasts are affected, using the within- or "
    "between-culture stratum of each contrast.\n"
        "5. Do not speculate about causes the metrics cannot distinguish; say "
    "what further check would distinguish them.\n"
    "6. Where the metrics allow it, say in which direction an issue would "
    "bias the primary contrast."
)



def qc_prompt(description: str, qc: dict, strata: dict[str, str]) -> str:
    definitions = "\n".join(f"- {k}: {v}" for k, v in METRIC_DEFINITIONS.items())
    contrasts = "\n".join(f"- {k}: {v}" for k, v in strata.items())
    return (
        f"Design description:\n{description}\n\n"
        f"Contrasts and their strata:\n{contrasts}\n\n"
        f"Metric definitions:\n{definitions}\n\n"
        f"QC metrics (JSON):\n{json.dumps(qc, indent=1)}"
    )


def write_qc_report(description: str, qc: dict, strata: dict[str, str], client, model=None) -> dict:
    return _structured_call(client, model, QC_SYSTEM, qc_prompt(description, qc, strata), QC_SCHEMA)


def format_qc_report(report: dict) -> str:
    lines = [f"**Overall:** {report['overall']}", "", report["summary"], ""]
    for n, i in enumerate(report["issues"], 1):
        where = ", ".join(i["samples"]) or "not channel-specific"
        lines += [
            f"### {n}. {i['issue_type']} ({where})",
            f"- Evidence: {i['evidence']}",
            f"- Impact: {i['impact']}",
            f"- Recommendation: {i['recommendation']}",
            "",
        ]
    return "\n".join(lines)


def score_report(report: dict, issue_type: str | None, targets: list[str]) -> dict:
    """Did the report name the planted issue type for a planted channel?

    For a clean control (issue_type None), 'detected' is True when the
    report lists no issues.
    """
    issues = report["issues"]
    if issue_type is None:
        return {"detected": not issues, "extra_issues": len(issues)}
    hit = [
        i for i in issues
        if i["issue_type"] == issue_type
        and (issue_type == "loading_confounded_with_treatment" or set(i["samples"]) & set(targets))
    ]
    return {"detected": bool(hit), "extra_issues": len(issues) - len(hit)}
