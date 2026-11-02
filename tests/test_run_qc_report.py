"""Tests for the open-ended QC report prompt and formatting (no API calls)."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from tmt_agents.quantms_qc import (
    channel_metrics,
    expected_amounts,
    protein_matrix,
    psm_counts,
    spike_in_recovery,
)
from tmt_agents.run_qc_report import (
    RUN_QC_SYSTEM,
    format_run_qc_report,
    run_qc_prompt,
    write_run_qc_report,
)
from tmt_agents.sdrf_io import read_sdrf

sys.path.insert(0, str(Path(__file__).parent))
from test_quantms_qc import make_msstats  # noqa: E402

SDRF = read_sdrf(Path(__file__).resolve().parents[1] / "data" / "own_design" / "sdrf.tsv")


def _prompt(ms):
    y = protein_matrix(ms)
    _, spikes = spike_in_recovery(y, expected_amounts(ms), psm_counts(ms))
    metrics = channel_metrics(y, exclude=[p for p in spikes["protein"] if p])
    return run_qc_prompt(metrics, spikes, SDRF, {"reporter_mass_shift": 0.002}, "IsobaricWorkflow -in x")


def test_prompt_contains_metrics_parameters_and_command():
    p = _prompt(make_msstats())
    assert "raw_median_z" in p
    assert '"reporter_mass_shift": 0.002' in p
    assert "IsobaricWorkflow -in x" in p
    assert "ENO1_YEAST" in p


def test_prompt_template_does_not_name_the_answer():
    """The fixed instructions must not hint at the problem; the data itself
    (e.g. TMT127 labels in an SDRF) may of course mention channels."""
    empty = run_qc_prompt(pd.DataFrame(), pd.DataFrame(), pd.DataFrame({"source name": ["s1"]}), {}, "")
    for text in [RUN_QC_SYSTEM.lower(), empty.lower()]:
        for hint in ["empty channel", "mass tolerance", "mass_shift", "127", "129", "reagent"]:
            assert hint not in text


def test_report_round_trip():
    payload = {
        "overall": "major_issues", "summary": "s",
        "issues": [{
            "channels": ["ch2"], "severity": "major", "observation": "o", "evidence": "e",
            "likely_causes": [{"cause": "c1", "reasoning": "r", "how_to_check": "h"}],
            "recommendation": "rec",
        }],
    }
    resp = SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps(payload))],
                           stop_reason="end_turn")
    client = SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: resp))
    report = write_run_qc_report("prompt", client, model="test")
    md = format_run_qc_report(report)
    assert "### 1. [major] ch2" in md and "1. c1" in md
