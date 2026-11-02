"""QC metrics for a protein x sample matrix of log2 TMT intensities.

All numbers the QC report uses are computed here. The LLM sees these
numbers (and their definitions), never plots.
"""

import numpy as np
import pandas as pd

METRIC_DEFINITIONS = {
    "n_quantified": "Number of proteins with a value in this channel.",
    "raw_median": "Median log2 intensity of the channel before normalisation.",
    "raw_median_z": "Robust z-score of raw_median across all channels (median/MAD).",
    "antibody_corr": (
        "Pearson correlation, after median normalisation, between this channel "
        "and the mean of the other channels with the same antibody."
    ),
    "antibody_corr_z": "Robust z-score of antibody_corr across all channels.",
    "pc1, pc2": "Sample scores on the first two principal components (normalised, complete proteins).",
    "pc1_z_within_antibody": "Robust z-score of pc1 among the channels with the same antibody.",
    "pc_factor_association": (
        "Absolute correlation between each PC's scores and each factor "
        "(0/1 indicator); shows which factor each PC separates."
    ),
    "loading_by_level": "Mean raw_median of the channels at each factor level.",
    "paired ratio": (
        "For each culture, log2(EZH2) - log2(IgG) per protein after normalisation. "
        "ratio_iqr is its interquartile range. slope_vs_other_cultures is the "
        "least-squares slope of this culture's ratios on the mean ratio of the "
        "other cultures (proteins quantified in all channels)."
    ),
}


def robust_z(x: pd.Series) -> pd.Series:
    mad = 1.4826 * (x - x.median()).abs().median()
    if mad == 0:
        return x * 0.0
    return (x - x.median()) / mad


def median_normalise(y: pd.DataFrame) -> pd.DataFrame:
    return y - y.median() + y.median().median()


def compute_qc(y: pd.DataFrame, samples: pd.DataFrame) -> dict:
    """Compute QC metrics. `samples` is the table from contrasts.sample_table."""
    samples = samples.set_index("sample").loc[list(y.columns)]
    norm = median_normalise(y)
    complete = norm.dropna()

    per = pd.DataFrame(index=y.columns)
    per["group"] = samples["group"]
    per["culture"] = samples["culture"]
    per["n_quantified"] = y.notna().sum()
    per["raw_median"] = y.median()
    per["raw_median_z"] = robust_z(per["raw_median"])

    antibody = samples["antibody"]
    corr = {}
    for s in y.columns:
        mates = [m for m in y.columns if m != s and antibody[m] == antibody[s]]
        corr[s] = complete[s].corr(complete[mates].mean(axis=1))
    per["antibody_corr"] = pd.Series(corr)
    per["antibody_corr_z"] = robust_z(per["antibody_corr"])

    centred = complete.sub(complete.mean(axis=1), axis=0).T.to_numpy()
    u, d, _ = np.linalg.svd(centred, full_matrices=False)
    scores = u * d
    var_explained = (d**2 / (d**2).sum())[:3]
    per["pc1"], per["pc2"] = scores[:, 0], scores[:, 1]
    per["pc1_z_within_antibody"] = per.groupby(antibody)["pc1"].transform(robust_z)

    indicators = {
        "antibody": (samples["antibody"] == "EZH2").astype(float).to_numpy(),
        "compound": (samples["compound"] != "DMSO").astype(float).to_numpy(),
    }
    pc_assoc = {
        f"PC{k + 1}": {f: round(abs(float(np.corrcoef(scores[:, k], v)[0, 1])), 3)
                       for f, v in indicators.items()}
        for k in range(3)
    }

    loading = {
        f: {lv: round(float(per.loc[samples[f] == lv, "raw_median"].mean()), 3)
            for lv in samples[f].unique()}
        for f in ["antibody", "compound"]
    }

    ratios = {}
    for culture, grp in samples.groupby("culture"):
        e = grp.index[grp["antibody"] == "EZH2"][0]
        g = grp.index[grp["antibody"] == "IgG"][0]
        ratios[culture] = (e, g, complete[e] - complete[g])
    paired = []
    for culture, (e, g, r) in ratios.items():
        others = pd.concat([v[2] for k, v in ratios.items() if k != culture], axis=1).mean(axis=1)
        slope = float(np.cov(r, others)[0, 1] / others.var())
        paired.append({
            "culture": culture, "ezh2_sample": e, "igg_sample": g,
            "median_ratio": round(float(r.median()), 3),
            "ratio_iqr": round(float(r.quantile(0.75) - r.quantile(0.25)), 3),
            "slope_vs_other_cultures": round(slope, 3),
        })

    return {
        "n_proteins": int(len(y)),
        "n_proteins_complete": int(len(complete)),
        "samples": per.reset_index(names="sample").round(3).to_dict(orient="records"),
        "pca_variance_explained": [round(float(v), 3) for v in var_explained],
        "pc_factor_association": pc_assoc,
        "loading_by_level": loading,
        "paired_ratios": paired,
    }


# Illustrative baseline thresholds, chosen by hand (not tuned or validated).
Z_LIMIT = 3.0
SLOPE_LIMIT = 0.7


def threshold_flags(qc: dict) -> set[str]:
    """Samples a simple threshold rule would flag (baseline, no issue type)."""
    flagged = set()
    for s in qc["samples"]:
        zs = [s["raw_median_z"], s["antibody_corr_z"], s["pc1_z_within_antibody"]]
        if any(abs(z) > Z_LIMIT for z in zs):
            flagged.add(s["sample"])
    for p in qc["paired_ratios"]:
        if p["slope_vs_other_cultures"] < SLOPE_LIMIT:
            flagged.update([p["ezh2_sample"], p["igg_sample"]])
    return flagged
