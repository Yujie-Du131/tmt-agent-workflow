"""Tests for design/contrast matrices and the contrast-selection checks."""

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from tmt_agents.contrasts import (
    cell_means_design,
    check_selection,
    contrast_catalogue,
    contrast_stratum,
    safe_name,
    sample_table,
    select_contrasts,
)
from tmt_agents.rules import load_design
from tmt_agents.sdrf_io import read_sdrf

DESIGN_DIR = Path(__file__).resolve().parents[1] / "data" / "own_design"
SDRF = read_sdrf(DESIGN_DIR / "sdrf.tsv")
DESIGN = load_design(DESIGN_DIR / "design.json")
SAMPLES = sample_table(SDRF, DESIGN)
X = cell_means_design(SAMPLES, DESIGN)
C = contrast_catalogue(DESIGN)


def test_safe_name():
    assert safe_name("CPI-169") == "CPI169"


def test_six_cultures_each_with_one_ezh2_and_one_igg():
    per_culture = SAMPLES.groupby("culture")["antibody"].apply(sorted)
    assert len(per_culture) == 6
    assert all(v == ["EZH2", "IgG"] for v in per_culture)


def test_design_matrix_is_cell_means():
    assert X.shape == (12, 4)
    assert (X.sum(axis=1) == 1).all()  # each sample in exactly one group
    assert (X.sum(axis=0) == 3).all()  # three samples per group
    assert np.linalg.matrix_rank(X.values) == 4


def test_contrast_columns_sum_to_zero():
    assert (C.sum(axis=0) == 0).all()


def test_interaction_matches_thesis_definition():
    # (EZH2_CPI - EZH2_DMSO) - (IgG_CPI - IgG_DMSO)
    expected = C["CPI169_vs_DMSO_in_EZH2"] - C["CPI169_vs_DMSO_in_IgG"]
    assert (C["interaction"] == expected).all()


def test_strata():
    strata = contrast_stratum(SAMPLES, C)
    assert strata == {
        "EZH2_vs_IgG_in_DMSO": "within-culture",
        "EZH2_vs_IgG_in_CPI169": "within-culture",
        "CPI169_vs_DMSO_in_IgG": "between-culture",
        "CPI169_vs_DMSO_in_EZH2": "between-culture",
        "interaction": "within-culture",
    }


def _estimates(y):
    """Least-squares group means, then contrast estimates."""
    beta, *_ = np.linalg.lstsq(X.values, y, rcond=None)
    return C.T.values @ beta


def test_within_culture_contrasts_ignore_culture_effects():
    """Adding an arbitrary offset to every sample of a culture must not change
    within-culture contrasts, but does change between-culture ones."""
    rng = np.random.default_rng(1)
    y = rng.normal(size=12)
    culture_codes = SAMPLES["culture"].astype("category").cat.codes.values
    shifted = y + rng.normal(scale=5, size=6)[culture_codes]
    diff = _estimates(shifted) - _estimates(y)
    strata = contrast_stratum(SAMPLES, C)
    for name, d in zip(C.columns, diff):
        if strata[name] == "within-culture":
            assert d == pytest.approx(0, abs=1e-10)
        else:
            assert abs(d) > 1e-6


def test_interaction_recovers_known_effect():
    true = {"EZH2.DMSO": 5.0, "EZH2.CPI169": 3.0, "IgG.DMSO": 1.0, "IgG.CPI169": 1.5}
    y = SAMPLES["group"].map(true).values.astype(float)
    est = dict(zip(C.columns, _estimates(y)))
    assert est["interaction"] == pytest.approx((3.0 - 5.0) - (1.5 - 1.0))


class FakeClient:
    def __init__(self, payload):
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)
        self._payload = payload

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=json.dumps(self._payload))],
            stop_reason="end_turn",
        )


GOOD = {
    "reference_levels": [
        {"factor": "compound", "level": "DMSO", "reason": "vehicle"},
        {"factor": "antibody", "level": "IgG", "reason": "isotype control"},
    ],
    "contrasts": [
        {"name": n, "role": "primary" if n == "interaction" else "secondary", "reason": ""}
        for n in C.columns
    ],
    "requested_but_missing": [],
}


def test_selection_prompt_lists_catalogue_and_passes_checks():
    client = FakeClient(GOOD)
    sel = select_contrasts("desc", DESIGN, C, client, model="test")
    prompt = client.calls[0]["messages"][0]["content"]
    assert "- interaction: " in prompt
    assert check_selection(sel, DESIGN, C) == []


def test_selection_checks_catch_problems():
    bad = json.loads(json.dumps(GOOD))
    bad["reference_levels"][1]["level"] = "EZH2"
    bad["contrasts"] = bad["contrasts"][:4] + [{"name": "made_up", "role": "secondary", "reason": ""}]
    problems = check_selection(bad, DESIGN, C)
    assert any("Reference level for antibody" in p for p in problems)
    assert any("Unknown contrast names" in p for p in problems)
    assert any("without a role" in p for p in problems)
    assert any("No contrast marked primary" in p for p in problems)
