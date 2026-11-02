"""Tests for the QC simulation, metrics, baseline and report scoring (no API calls)."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tmt_agents.contrasts import contrast_catalogue, contrast_stratum, sample_table
from tmt_agents.qc_metrics import compute_qc, threshold_flags
from tmt_agents.qc_report import score_report, write_qc_report
from tmt_agents.qc_simulate import scenarios
from tmt_agents.rules import load_design
from tmt_agents.sdrf_io import read_sdrf

DESIGN_DIR = Path(__file__).resolve().parents[1] / "data" / "own_design"
DESIGN = load_design(DESIGN_DIR / "design.json")
SAMPLES = sample_table(read_sdrf(DESIGN_DIR / "sdrf.tsv"), DESIGN)
SCENARIOS = {sc.id: sc for sc in scenarios(SAMPLES)}
QC = {k: compute_qc(sc.make(SAMPLES), SAMPLES) for k, sc in SCENARIOS.items()}


def _sample(qc, name):
    return next(s for s in qc["samples"] if s["sample"] == name)


def _slope(qc, culture):
    return next(p for p in qc["paired_ratios"] if p["culture"] == culture)["slope_vs_other_cultures"]


def test_simulation_is_reproducible():
    sc = SCENARIOS["Q00_clean"]
    assert sc.make(SAMPLES).equals(sc.make(SAMPLES))


def test_clean_pca_separates_antibody_then_compound():
    assoc = QC["Q00_clean"]["pc_factor_association"]
    assert assoc["PC1"]["antibody"] > 0.95
    assert assoc["PC2"]["compound"] > 0.9


def test_planted_signals_are_visible_in_metrics():
    assert _sample(QC["Q01_low_loading"], "R2_CPI_EZH2")["raw_median_z"] < -3
    assert _slope(QC["Q02_ratio_compression"], "CPI169_2") < 0.8
    assert _sample(QC["Q03_outlier_sample"], "R3_DMSO_IgG")["antibody_corr_z"] < -3
    assert _slope(QC["Q04_label_swap"], "DMSO_1") < 0
    loading = QC["Q05_treatment_loading"]["loading_by_level"]["compound"]
    assert loading["DMSO"] - loading["CPI-169"] > 0.4


def test_threshold_baseline():
    assert threshold_flags(QC["Q00_clean"]) == set()
    assert threshold_flags(QC["Q05_treatment_loading"]) == set()  # group-level, not per channel
    for k in ["Q01_low_loading", "Q02_ratio_compression", "Q03_outlier_sample", "Q04_label_swap"]:
        assert threshold_flags(QC[k]) & set(SCENARIOS[k].samples)


def _issue(issue_type, samples):
    return {"issue_type": issue_type, "samples": samples, "evidence": "",
            "impact": "", "recommendation": ""}


def test_scoring():
    clean = {"overall": "no_issues", "issues": [], "summary": ""}
    assert score_report(clean, None, [])["detected"]
    hit = {"overall": "major_issues", "summary": "",
           "issues": [_issue("ratio_compression", ["R2_CPI_EZH2"]), _issue("other", [])]}
    assert score_report(hit, "ratio_compression", ["R2_CPI_EZH2"]) == {"detected": True, "extra_issues": 1}
    wrong_type = {"overall": "major_issues", "summary": "",
                  "issues": [_issue("outlier_sample", ["R2_CPI_EZH2"])]}
    assert not score_report(wrong_type, "ratio_compression", ["R2_CPI_EZH2"])["detected"]


def test_report_prompt_contains_metrics_and_strata():
    payload = {"overall": "no_issues", "issues": [], "summary": "ok"}
    calls = []

    def create(**kw):
        calls.append(kw)
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps(payload))],
                               stop_reason="end_turn")

    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    strata = contrast_stratum(SAMPLES, contrast_catalogue(DESIGN))
    report = write_qc_report("desc", QC["Q00_clean"], strata, client, model="test")
    prompt = calls[0]["messages"][0]["content"]
    assert "interaction: within-culture" in prompt
    assert "slope_vs_other_cultures" in prompt
    assert report["overall"] == "no_issues"


@pytest.mark.parametrize("k", list(SCENARIOS))
def test_metrics_are_json_serialisable(k):
    json.dumps(QC[k])
