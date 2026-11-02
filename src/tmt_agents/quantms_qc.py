"""Read quantms TMT output (MSstats input table) and compute QC on it.

quantms 1.10.0 writes `quant_tables/<sdrf>_openms_design_msstats_in.csv`:
one row per PSM and channel, with columns including ProteinName,
PeptideSequence, Charge, Channel, Condition, Intensity and Reference
(the spectrum). This module turns that table into a protein x channel
matrix and, for spike-in designs, measures how well known ratios are
recovered.
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd

from tmt_agents.qc_metrics import median_normalise, robust_z

REQUIRED = ["ProteinName", "PeptideSequence", "Charge", "Channel", "Condition", "Intensity", "Reference"]


def read_msstats_in(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Not a quantms MSstats input table; missing columns: {missing}")
    return df


def protein_matrix(msstats: pd.DataFrame) -> pd.DataFrame:
    """log2 protein intensities (proteins x channels).

    Each protein's intensity in a channel is the sum of its PSM reporter
    intensities. Decoys, protein groups (names with ';') and non-positive
    intensities are removed. Columns are named 'ch<Channel>'.
    """
    d = msstats[msstats["Intensity"] > 0]
    d = d[~d["ProteinName"].str.contains("DECOY", case=False)]
    d = d[~d["ProteinName"].str.contains(";")]
    wide = d.pivot_table(index="ProteinName", columns="Channel", values="Intensity", aggfunc="sum")
    # keep channels with no quantified protein as all-NaN columns, so that an
    # empty channel is reported rather than silently dropped
    wide = wide.reindex(columns=sorted(msstats["Channel"].unique()))
    wide.columns = [f"ch{c}" for c in wide.columns]

    return np.log2(wide)


def psm_counts(msstats: pd.DataFrame) -> pd.Series:
    """Number of distinct PSMs (spectrum, peptide, charge) per protein."""
    key = msstats[["ProteinName", "Reference", "PeptideSequence", "Charge"]].drop_duplicates()
    return key.groupby("ProteinName").size()


def expected_amounts(msstats: pd.DataFrame) -> pd.DataFrame:
    """Spiked amounts per channel, parsed from the Condition column.

    Condition strings look like 'SP=Yeast;CT=protein;AC=P00924;QY=10|...'.
    Returns a table with rows = accessions, columns = 'ch<Channel>'.
    """
    rows = {}
    for channel, cond in msstats[["Channel", "Condition"]].drop_duplicates().itertuples(index=False):
        for part in str(cond).split("|"):
            acc = re.search(r"AC=([^;|]+)", part)
            qy = re.search(r"QY=([0-9.]+)", part)
            if acc and qy:
                rows.setdefault(acc.group(1), {})[f"ch{channel}"] = float(qy.group(1))
    table = pd.DataFrame(rows).T
    return table[sorted(table.columns, key=lambda c: int(c[2:]))]


def _match(index: pd.Index, accession: str) -> str | None:
    hits = [p for p in index if p == accession or f"|{accession}|" in p]
    return hits[0] if len(hits) == 1 else None


def channel_metrics(y: pd.DataFrame, exclude: list[str] | None = None) -> pd.DataFrame:
    """Design-free channel metrics, computed on background proteins only."""
    bg = y.drop(index=[p for p in (exclude or []) if p in y.index])
    norm = median_normalise(bg).dropna()
    out = pd.DataFrame(index=y.columns)
    out["n_quantified"] = y.notna().sum()
    out["raw_median"] = bg.median()
    out["raw_median_z"] = robust_z(out["raw_median"])
    out["corr_to_others"] = [norm[c].corr(norm.drop(columns=c).mean(axis=1)) for c in y.columns]
    return out.round(3)


def spike_in_recovery(y: pd.DataFrame, expected: pd.DataFrame, psms: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compare measured with expected log2 ratios for spiked proteins.

    Channels are normalised by the median of the background proteins (all
    non-spiked proteins), which are assumed equal across channels. For each
    spiked protein, measured and expected log2 values are centred on their
    mean across channels; the least-squares slope (through the origin) of
    measured on expected is 1 for perfect recovery and below 1 under ratio
    compression.

    Returns (per-channel table, per-protein summary).
    """
    names = {acc: _match(y.index, acc) for acc in expected.index}
    spiked = [n for n in names.values() if n]
    background = y.drop(index=spiked)
    offsets = background.median() - background.median().median()
    norm = y - offsets

    long, summary = [], []
    for acc, name in names.items():
        exp = np.log2(expected.loc[acc, y.columns].astype(float))
        if name is None:
            summary.append({"accession": acc, "protein": None, "psms": 0, "slope": None,
                            "expected_range_log2": round(float(exp.max() - exp.min()), 3)})
            continue
        meas = norm.loc[name]
        ok = meas.notna()
        e = exp[ok] - exp[ok].mean()
        m = meas[ok] - meas[ok].mean()
        slope = float((m * e).sum() / (e * e).sum()) if (e * e).sum() > 0 else None
        summary.append({
            "accession": acc, "protein": name, "psms": int(psms.get(name, 0)),
            "expected_range_log2": round(float(exp.max() - exp.min()), 3),
            "slope": None if slope is None else round(slope, 3),
        })
        for c in y.columns:
            long.append({"accession": acc, "channel": c,
                         "expected_log2_centred": round(float(exp[c] - exp[ok].mean()), 3),
                         "measured_log2_centred": None if not ok[c] else round(float(m[c]), 3)})
    return pd.DataFrame(long), pd.DataFrame(summary)


def pooled_slope(per_channel: pd.DataFrame, accessions: list[str]) -> float:
    d = per_channel[per_channel["accession"].isin(accessions)].dropna()
    e, m = d["expected_log2_centred"], d["measured_log2_centred"]
    return round(float((m * e).sum() / (e * e).sum()), 3)
