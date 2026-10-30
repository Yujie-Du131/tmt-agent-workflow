"""Checks on the benchmark corruptions and scoring helpers (no API calls)."""

from pathlib import Path

import pytest

from tmt_agents.benchmark import llm_detected, llm_other_findings, rule_errors
from tmt_agents.corruptions import CORRUPTIONS
from tmt_agents.rules import load_design, run_all
from tmt_agents.sdrf_io import read_sdrf

DESIGN_DIR = Path(__file__).resolve().parents[1] / "data" / "own_design"
CLEAN = read_sdrf(DESIGN_DIR / "sdrf.tsv")
DESIGN = load_design(DESIGN_DIR / "design.json")


def test_ids_are_unique():
    ids = [c.id for c in CORRUPTIONS]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("c", CORRUPTIONS, ids=lambda c: c.id)
def test_corruption_changes_sdrf(c):
    assert not c.apply(CLEAN.copy()).equals(CLEAN)


@pytest.mark.parametrize("c", CORRUPTIONS, ids=lambda c: c.id)
def test_rules_behave_as_labelled(c):
    errors = rule_errors(run_all(c.apply(CLEAN.copy()), DESIGN))
    if c.category == "A":
        assert set(c.expected_rules) <= errors
    else:
        assert errors == set()  # B and C must slip past the rules


def _finding(category, columns):
    return {
        "category": category, "severity": "error", "columns": columns,
        "rows": [], "evidence": "", "explanation": "", "suggested_fix": "",
    }


def test_llm_scoring_matches_column_and_ignores_explanations():
    review = {"summary": "", "findings": [
        _finding("metadata_mismatch", ["characteristics[cell line]"]),
        _finding("rule_issue_explanation", ["characteristics[organism]"]),
        _finding("other", ["comment[instrument]"]),
    ]}
    assert llm_detected(review, ["characteristics[cell line]"])
    assert not llm_detected(review, ["characteristics[organism]"])
    assert llm_other_findings(review, ["characteristics[cell line]"]) == 1
