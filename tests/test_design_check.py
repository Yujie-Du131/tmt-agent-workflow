"""Tests for the LLM layer that do not call the API.

A fake client stands in for anthropic.Anthropic so the tests check prompt
construction and output handling, not model quality. Model quality is
measured separately in the benchmark.
"""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tmt_agents.design_check import (
    compare_specs,
    draft_design_spec,
    factor_names,
    format_review,
    review_sdrf,
    summarise_sdrf,
)
from tmt_agents.rules import load_design, run_all
from tmt_agents.sdrf_io import read_sdrf

DESIGN_DIR = Path(__file__).resolve().parents[1] / "data" / "own_design"


class FakeClient:
    """Returns a fixed JSON reply and records the request."""

    def __init__(self, payload, stop_reason="end_turn"):
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)
        self._response = SimpleNamespace(
            content=[SimpleNamespace(type="text", text=json.dumps(payload))],
            stop_reason=stop_reason,
        )

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self._response


@pytest.fixture
def sdrf():
    return read_sdrf(DESIGN_DIR / "sdrf.tsv")


@pytest.fixture
def reference():
    return load_design(DESIGN_DIR / "design.json")


@pytest.fixture
def description():
    return (DESIGN_DIR / "design_description.md").read_text(encoding="utf-8")


def test_summary_lists_constant_columns_once(sdrf):
    text = summarise_sdrf(sdrf)
    assert "- characteristics[cell line]: RL" in text
    assert text.count("CVCL_1660") == 1
    assert "R2_CPI_EZH2" in text  # varying column shown per row


def test_factor_names(sdrf):
    assert factor_names(sdrf) == ["compound", "antibody"]


def test_compare_identical_specs(reference):
    assert compare_specs(dict(reference), reference) == []


def test_compare_detects_wrong_levels_and_pairing(reference):
    draft = dict(reference)
    draft["factors"] = {"compound": ["DMSO", "CPI169"], "antibody": ["EZH2", "IgG"]}
    draft["within_culture_factor"] = "compound"
    diffs = compare_specs(draft, reference)
    assert any(d.startswith("factor compound") for d in diffs)
    assert any(d.startswith("within_culture_factor") for d in diffs)


def test_draft_uses_schema_and_converts_factors(sdrf, description, reference):
    payload = {
        **{k: reference[k] for k in reference if k != "description"},
        "factors": [{"name": k, "levels": v} for k, v in reference["factors"].items()],
        "uncertainties": [],
    }
    client = FakeClient(payload)
    draft = draft_design_spec(description, factor_names(sdrf), client, model="test")
    call = client.calls[0]
    assert call["output_config"]["format"]["type"] == "json_schema"
    assert "['compound', 'antibody']" in call["messages"][0]["content"]
    assert compare_specs(draft, reference) == []


def test_review_prompt_contains_sdrf_and_rule_issues(sdrf, description, reference):
    issues = run_all(sdrf.drop(index=11).reset_index(drop=True), reference)
    finding = {
        "category": "rule_issue_explanation", "severity": "error",
        "columns": ["factor value[antibody]"], "rows": [],
        "evidence": "x", "explanation": "y", "suggested_fix": "z",
    }
    client = FakeClient({"findings": [finding], "summary": "s"})
    review = review_sdrf(description, sdrf, issues, client, model="test")
    prompt = client.calls[0]["messages"][0]["content"]
    assert "Design description:" in prompt
    assert '"rule": "pairing"' in prompt
    assert "### 1. [ERROR] rule_issue_explanation" in format_review(review)


def test_refusal_raises(sdrf, description):
    client = FakeClient({}, stop_reason="refusal")
    with pytest.raises(RuntimeError):
        draft_design_spec(description, factor_names(sdrf), client, model="test")
