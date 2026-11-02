"""Tests for reading quantms MSstats input and spike-in recovery (synthetic data)."""

import numpy as np
import pandas as pd
import pytest

from tmt_agents.quantms_qc import (
    expected_amounts,
    pooled_slope,
    protein_matrix,
    psm_counts,
    spike_in_recovery,
)

CONDITIONS = {
    1: "SP=Yeast;CT=protein;AC=P00924;QY=10|SP=BOVIN;CT=protein;AC=P02769;QY=1",
    2: "SP=Yeast;CT=protein;AC=P00924;QY=5|SP=BOVIN;CT=protein;AC=P02769;QY=2.5",
    3: "SP=Yeast;CT=protein;AC=P00924;QY=2.5|SP=BOVIN;CT=protein;AC=P02769;QY=5",
    4: "SP=Yeast;CT=protein;AC=P00924;QY=1|SP=BOVIN;CT=protein;AC=P02769;QY=10",
}
SPIKES = {"sp|P00924|ENO1_YEAST": "P00924", "sp|P02769|ALBU_BOVIN": "P02769"}
COMPRESSION = 0.6


def make_msstats(seed=0):
    """Synthetic table: 60 background proteins, two spikes compressed to 0.6."""
    rng = np.random.default_rng(seed)
    rows = []
    proteins = [f"ECA{i:04d}" for i in range(60)] + list(SPIKES)
    for p in proteins:
        for k in range(3):  # three PSMs per protein
            base = rng.normal(20, 1)
            for ch, cond in CONDITIONS.items():
                if p in SPIKES:
                    qy = float(cond.split(f"AC={SPIKES[p]};QY=")[1].split("|")[0])
                    signal = COMPRESSION * np.log2(qy)
                else:
                    signal = 0.0
                log2i = base + signal + 0.3 * (ch == 2) + rng.normal(0, 0.02)
                rows.append({"ProteinName": p, "PeptideSequence": f"PEP{k}", "Charge": 2,
                             "Channel": ch, "Condition": cond, "Intensity": 2**log2i,
                             "Reference": f"scan={p}_{k}"})
    rows.append({"ProteinName": "DECOY_X", "PeptideSequence": "X", "Charge": 2, "Channel": 1,
                 "Condition": CONDITIONS[1], "Intensity": 1e6, "Reference": "scan=d"})
    rows.append({"ProteinName": "A;B", "PeptideSequence": "Y", "Charge": 2, "Channel": 1,
                 "Condition": CONDITIONS[1], "Intensity": 1e6, "Reference": "scan=g"})
    return pd.DataFrame(rows)


MS = make_msstats()
Y = protein_matrix(MS)


def test_protein_matrix_shape_and_filtering():
    assert list(Y.columns) == ["ch1", "ch2", "ch3", "ch4"]
    assert "DECOY_X" not in Y.index and "A;B" not in Y.index
    assert Y.shape[0] == 62


def test_psm_counts():
    assert psm_counts(MS)["sp|P00924|ENO1_YEAST"] == 3


def test_expected_amounts_parsed_from_condition():
    exp = expected_amounts(MS)
    assert exp.loc["P00924", "ch1"] == 10
    assert exp.loc["P02769", "ch4"] == 10


def test_spike_in_recovery_measures_compression():
    per_channel, summary = spike_in_recovery(Y, expected_amounts(MS), psm_counts(MS))
    for slope in summary["slope"]:
        assert slope == pytest.approx(COMPRESSION, abs=0.05)
    assert pooled_slope(per_channel, ["P00924", "P02769"]) == pytest.approx(COMPRESSION, abs=0.05)


def test_channel_offset_is_removed_by_background_normalisation():
    # channel 2 was loaded 0.3 log2 higher; recovery must not depend on it
    per_channel, _ = spike_in_recovery(Y, expected_amounts(MS), psm_counts(MS))
    resid = per_channel.assign(r=per_channel["measured_log2_centred"]
                               - COMPRESSION * per_channel["expected_log2_centred"])
    assert resid["r"].abs().max() < 0.1
