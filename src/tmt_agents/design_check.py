"""LLM layer for SDRF validation.

Two LLM tasks, both returning JSON constrained by a schema (structured outputs):

1. draft_design_spec: turn a free-text experimental design into the
   structured design specification used by rules.py, for the analyst to
   confirm.
2. review_sdrf: compare the SDRF with the free-text description, report
   disagreements that the deterministic rules cannot see (e.g. wrong cell
   line, enzyme or a misspelt factor level), and explain the rule-check
   results in plain language.

Counting and matching stay in rules.py; the LLM is never asked to count.
"""

import json
import os
from dataclasses import asdict

import pandas as pd

from tmt_agents.rules import PLEX_LABELS, Issue

FALLBACK_MODEL = "claude-sonnet-5-5"


def default_model() -> str:
    """Model to use; override with TMT_AGENTS_MODEL in the environment or .env."""
    return os.environ.get("TMT_AGENTS_MODEL", FALLBACK_MODEL)

# ---------------------------------------------------------------------------
# JSON schemas for structured outputs
# ---------------------------------------------------------------------------

DESIGN_SCHEMA = {
    "type": "object",
    "properties": {
        "plex": {
            "type": "string",
            "enum": sorted(PLEX_LABELS),
            "description": "TMT kit used for the run.",
        },
        "factors": {
            "type": "array",
            "description": (
                "Experimental factors. Names must be chosen from the factor names "
                "provided. Levels are short names as they would appear in the "
                "SDRF (e.g. 'DMSO', not 'DMSO vehicle')."
            ),
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "levels": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name", "levels"],
                "additionalProperties": False,
            },
        },
        "replicates_per_condition": {
            "type": "integer",
            "description": "Number of samples in each combination of factor levels.",
        },
        "culture_defined_by": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "Fields that together identify one independent biological unit "
                "(e.g. a culture): a between-unit factor plus 'biological replicate'."
            ),
        },
        "within_culture_factor": {
            "type": "string",
            "description": (
                "Factor whose levels are all applied to material from the same "
                "biological unit (paired within it)."
            ),
        },
        "uncertainties": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Anything the description leaves unclear.",
        },
    },
    "required": [
        "plex",
        "factors",
        "replicates_per_condition",
        "culture_defined_by",
        "within_culture_factor",
        "uncertainties",
    ],
    "additionalProperties": False,
}

REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": [
                            "metadata_mismatch",
                            "naming_inconsistency",
                            "rule_issue_explanation",
                            "other",
                        ],
                    },
                    "severity": {"type": "string", "enum": ["error", "warning"]},
                    "columns": {"type": "array", "items": {"type": "string"}},
                    "rows": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "1-based data rows, empty if run-wide.",
                    },
                    "evidence": {
                        "type": "string",
                        "description": "Quote the description and the SDRF value that disagree.",
                    },
                    "explanation": {"type": "string"},
                    "suggested_fix": {"type": "string"},
                },
                "required": [
                    "category", "severity", "columns", "rows",
                    "evidence", "explanation", "suggested_fix",
                ],
                "additionalProperties": False,
            },
        },
        "summary": {"type": "string"},
    },
    "required": ["findings", "summary"],
    "additionalProperties": False,
}

# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------


def summarise_sdrf(sdrf: pd.DataFrame) -> str:
    """Compact text view of an SDRF.

    Columns with one value across all rows are listed once; columns that vary
    are shown as a per-row table. This keeps prompts short and makes run-level
    metadata easy for the model to compare with the description.
    """
    constant, varying = [], []
    for i, name in enumerate(sdrf.columns):
        values = sdrf.iloc[:, i].unique()
        (constant if len(values) == 1 else varying).append((i, name))

    lines = ["Columns with the same value in every row:"]
    for i, name in constant:
        lines.append(f"- {name}: {sdrf.iloc[0, i]}")
    lines.append("")
    lines.append("Columns that vary between rows (row numbers are 1-based):")
    table = sdrf.iloc[:, [i for i, _ in varying]].copy()
    table.columns = [name for _, name in varying]
    table.index = range(1, len(table) + 1)
    lines.append(table.to_string())
    return "\n".join(lines)


def factor_names(sdrf: pd.DataFrame) -> list[str]:
    return [
        c[len("factor value["):-1]
        for c in sdrf.columns
        if c.startswith("factor value[")
    ]


def _structured_call(client, model: str | None, system: str, user: str, schema: dict) -> dict:
    """Send one request whose reply must be JSON matching `schema`."""
    response = client.messages.create(
        model=model or default_model(),
        max_tokens=8000,
        system=system,
        messages=[{"role": "user", "content": user}],
        output_config={"format": {"type": "json_schema", "schema": schema}},
    )
    if response.stop_reason in ("refusal", "max_tokens"):
        raise RuntimeError(f"Model stopped with reason '{response.stop_reason}'")
    text = next((b.text for b in response.content if b.type == "text"), None)
    if text is None:
        raise RuntimeError("Model returned no text block")
    return json.loads(text)


# ---------------------------------------------------------------------------
# Task 1: free-text description -> structured design spec
# ---------------------------------------------------------------------------

DRAFT_SYSTEM = (
    "You convert a researcher's description of a multiplexed TMT proteomics "
    "experiment into a structured design specification. Use only information "
    "stated in the description. If something is not stated, choose the most "
    "literal reading and list the gap under 'uncertainties'. Do not invent "
    "factors that the description does not mention."
)


def draft_design_spec(description: str, factors: list[str], client, model: str | None = None) -> dict:
    """Ask the model for a design spec; factor keys must use the given names."""
    user = (
        f"Factor names used in the SDRF: {factors}\n"
        "Use exactly these names for the factors. Use 'biological replicate' "
        "for the replicate field.\n\n"
        f"Design description:\n{description}"
    )
    raw = _structured_call(client, model, DRAFT_SYSTEM, user, DESIGN_SCHEMA)
    spec = dict(raw)
    spec["factors"] = {f["name"]: f["levels"] for f in raw["factors"]}
    return spec


def compare_specs(draft: dict, reference: dict) -> list[str]:
    """Deterministic comparison of a drafted spec with a confirmed one."""
    diffs = []
    for key in ["plex", "replicates_per_condition", "within_culture_factor"]:
        if draft.get(key) != reference.get(key):
            diffs.append(f"{key}: draft={draft.get(key)!r}, reference={reference.get(key)!r}")
    if sorted(draft.get("culture_defined_by", [])) != sorted(reference["culture_defined_by"]):
        diffs.append(
            f"culture_defined_by: draft={draft.get('culture_defined_by')}, "
            f"reference={reference['culture_defined_by']}"
        )
    d_f, r_f = draft.get("factors", {}), reference["factors"]
    for name in sorted(set(d_f) | set(r_f)):
        if sorted(d_f.get(name, [])) != sorted(r_f.get(name, [])):
            diffs.append(f"factor {name}: draft={d_f.get(name)}, reference={r_f.get(name)}")
    return diffs


# ---------------------------------------------------------------------------
# Task 2: review SDRF against the description and explain rule issues
# ---------------------------------------------------------------------------

REVIEW_SYSTEM = (
    "You review SDRF metadata for a TMT proteomics run against the "
    "researcher's own description of the experiment.\n"
    "Rules:\n"
    "1. Counting checks (duplicate channels, replicate numbers, pairing, "
    "balance) have already been done by code; their results are given to you. "
    "Do not recount. For each rule issue, add one 'rule_issue_explanation' "
    "finding that says what it means for the analysis and the likely cause.\n"
    "2. Report a 'metadata_mismatch' only when an SDRF value contradicts "
    "something the description states (cell line, organism, enzyme, kit, "
    "treatment, antibody, number of samples). Quote both in 'evidence'.\n"
    "3. Report a 'naming_inconsistency' when the same thing appears to be "
    "written in different ways (e.g. a misspelt level).\n"
    "4. If the description says nothing about a column, do not speculate "
    "about it.\n"
    "5. Do not comment on formatting conventions such as capitalisation or "
    "ontology term style; a separate validator checks format.\n"
    "6. If there are no problems, return an empty findings list."

)


def review_sdrf(
    description: str,
    sdrf: pd.DataFrame,
    rule_issues: list[Issue],
    client,
    model: str | None = None,
) -> dict:
    issues_json = json.dumps([asdict(i) for i in rule_issues], indent=2)
    user = (
        f"Design description:\n{description}\n\n"
        f"SDRF:\n{summarise_sdrf(sdrf)}\n\n"
        "Rule-check results (row indices here are 0-based):\n"
        f"{issues_json}"
    )
    return _structured_call(client, model, REVIEW_SYSTEM, user, REVIEW_SCHEMA)


def format_review(review: dict) -> str:
    """Render a review as Markdown."""
    lines = ["## Summary", "", review["summary"], ""]
    if not review["findings"]:
        lines.append("No findings.")
        return "\n".join(lines)
    lines.append("## Findings")
    for n, f in enumerate(review["findings"], 1):
        where = ", ".join(f["columns"]) or "run-wide"
        rows = f" (rows {f['rows']})" if f["rows"] else ""
        lines += [
            "",
            f"### {n}. [{f['severity'].upper()}] {f['category']}: {where}{rows}",
            f"- Evidence: {f['evidence']}",
            f"- Explanation: {f['explanation']}",
            f"- Suggested fix: {f['suggested_fix']}",
        ]
    return "\n".join(lines)
