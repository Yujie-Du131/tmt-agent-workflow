"""Scoring helpers for the corrupted-SDRF benchmark."""

import re
import subprocess
from pathlib import Path

from tmt_agents.rules import Issue

SEMANTIC_CATEGORIES = {"metadata_mismatch", "naming_inconsistency", "other"}


def run_sdrf_pipelines(path: str | Path) -> tuple[bool, str]:
    """Run the official validator; return (found_error, first error line)."""
    result = subprocess.run(
        [
            "parse_sdrf", "validate-sdrf",
            "-s", str(path),
            "-t", "ms-proteomics", "-t", "cell-lines",
            "--use_ols_cache_only",
        ],
        capture_output=True,
        text=True,
    )
    lines = (result.stdout + result.stderr).splitlines()
    errors = [ln for ln in lines if ln.startswith("ERROR")]
    return bool(errors), errors[0] if errors else ""


def rule_errors(issues: list[Issue]) -> set[str]:
    return {i.rule for i in issues if i.severity == "error"}


def _inner(column: str) -> str:
    """'characteristics[cell line]' -> 'cell line'."""
    m = re.search(r"\[(.+)\]", column)
    return (m.group(1) if m else column).lower()


def semantic_findings(review: dict) -> list[dict]:
    return [f for f in review["findings"] if f["category"] in SEMANTIC_CATEGORIES]


def finding_hits(finding: dict, target_columns: list[str]) -> bool:
    cols = [c.lower() for c in finding["columns"]]
    return any(_inner(t) in c for t in target_columns for c in cols)


def llm_detected(review: dict, target_columns: list[str]) -> bool:
    """True if a semantic finding names one of the target columns."""
    return any(finding_hits(f, target_columns) for f in semantic_findings(review))


def llm_other_findings(review: dict, target_columns: list[str]) -> int:
    """Semantic findings about columns that were not corrupted."""
    return sum(not finding_hits(f, target_columns) for f in semantic_findings(review))
