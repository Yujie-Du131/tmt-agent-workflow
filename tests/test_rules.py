"""Tests for the deterministic SDRF rule checks.

The correct SDRF must pass with no errors, and each single, deliberate
corruption must be caught by the intended rule.
"""

from pathlib import Path

import pytest

from tmt_agents.rules import load_design, run_all
from tmt_agents.sdrf_io import read_sdrf

DESIGN_DIR = Path(__file__).resolve().parents[1] / "data" / "own_design"


@pytest.fixture
def sdrf():
    return read_sdrf(DESIGN_DIR / "sdrf.tsv")


@pytest.fixture
def design():
    return load_design(DESIGN_DIR / "design.json")


def error_rules(sdrf, design):
    return {i.rule for i in run_all(sdrf, design) if i.severity == "error"}


def set_cell(sdrf, row, column, value):
    sdrf.iloc[row, list(sdrf.columns).index(column)] = value


def test_correct_sdrf_has_no_errors(sdrf, design):
    assert error_rules(sdrf, design) == set()


def test_correct_sdrf_reports_unused_channels(sdrf, design):
    warnings = [i for i in run_all(sdrf, design) if i.severity == "warning"]
    assert [w.rule for w in warnings] == ["unused_channels"]


def test_duplicate_channel(sdrf, design):
    set_cell(sdrf, 1, "comment[label]", "TMT126")  # same as row 0
    assert "unique_channel" in error_rules(sdrf, design)


def test_label_outside_plex(sdrf, design):
    set_cell(sdrf, 0, "comment[label]", "TMT135N")  # TMTpro18 only
    assert "label_in_plex" in error_rules(sdrf, design)


def test_missing_replicate(sdrf, design):
    rules = error_rules(sdrf.drop(index=11).reset_index(drop=True), design)
    assert {"balance", "pairing"} <= rules


def test_antibody_swapped_within_culture(sdrf, design):
    # R1_DMSO_IgG relabelled as EZH2: culture R1/DMSO now has two EZH2 samples
    set_cell(sdrf, 1, "factor value[antibody]", "EZH2")
    set_cell(sdrf, 1, "characteristics[antibody]", "EZH2")
    assert {"balance", "pairing"} <= error_rules(sdrf, design)


def test_factor_disagrees_with_characteristics(sdrf, design):
    set_cell(sdrf, 2, "factor value[compound]", "DMSO")
    assert "factor_matches_characteristics" in error_rules(sdrf, design)


def test_unexpected_level(sdrf, design):
    set_cell(sdrf, 2, "factor value[compound]", "CPI169")
    set_cell(sdrf, 2, "characteristics[compound]", "CPI169")
    assert "factor_levels" in error_rules(sdrf, design)


def test_inconsistent_run_parameter(sdrf, design):
    set_cell(sdrf, 5, "comment[precursor mass tolerance]", "20 ppm")
    assert "run_level_consistency" in error_rules(sdrf, design)


def test_missing_factor_column(sdrf, design):
    sdrf = sdrf.drop(columns=["factor value[antibody]"])
    assert error_rules(sdrf, design) == {"required_columns"}
