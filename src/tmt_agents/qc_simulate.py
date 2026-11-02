"""Simulate protein-level TMT intensities for the 2 x 2 split-plot design,
with optional, known QC problems planted in specific channels.

The output is a protein x sample matrix of log2 intensities, the same shape
the QC metrics use for real quantms output. The simulation is deliberately
simple; it is a test bed for the QC report, not a model of the experiment.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

N_PROTEINS = 1500
N_ENRICHED = 200  # proteins labelled more by EZH2 than by IgG
N_LOST = 30  # enriched proteins whose EZH2 labelling drops under CPI-169
N_GAINED = 15  # enriched proteins whose EZH2 labelling rises under CPI-169
N_BACKGROUND_SHIFT = 80  # proteins that rise under CPI-169 with both antibodies
DETECTION_LIMIT = 16.5  # log2 intensities below this are missing


def simulate_intensities(
    samples: pd.DataFrame,
    seed: int = 1,
    channel_offsets: dict[str, float] | None = None,
    compression: dict[str, float] | None = None,
    extra_noise: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Return log2 intensities (proteins x samples, NaN = not quantified).

    channel_offsets: sample -> log2 shift of the whole channel (loading).
    compression: sample -> factor in (0, 1]; the channel is pulled towards
        the across-channel mean of each protein (ratio compression).
    extra_noise: sample -> additional noise SD for that channel.
    """
    rng = np.random.default_rng(seed)
    n = N_PROTEINS
    ezh2 = (samples["antibody"] == "EZH2").to_numpy()
    cpi = (samples["compound"] != "DMSO").to_numpy()

    abundance = rng.normal(20, 1.5, n)
    enrich = np.zeros(n)
    enrich[:N_ENRICHED] = 2.0
    interaction = np.zeros(n)
    interaction[:N_LOST] = -1.5
    interaction[N_LOST:N_LOST + N_GAINED] = 1.0
    background = np.zeros(n)
    background[N_ENRICHED:N_ENRICHED + N_BACKGROUND_SHIFT] = 0.8

    cultures = samples["culture"].astype("category")
    culture_effect = rng.normal(0, 0.2, (n, len(cultures.cat.categories)))

    y = (
        abundance[:, None]
        + np.outer(enrich, ezh2)
        + np.outer(interaction, ezh2 & cpi)
        + np.outer(background, cpi)
        + culture_effect[:, cultures.cat.codes.to_numpy()]
        + rng.normal(0, 0.25, (n, len(samples)))
        + rng.normal(0, 0.05, len(samples))  # small loading differences
    )
    cols = list(samples["sample"])
    for s, shift in (channel_offsets or {}).items():
        y[:, cols.index(s)] += shift
    for s, sd in (extra_noise or {}).items():
        y[:, cols.index(s)] += rng.normal(0, sd, n)
    mixture_mean = y.mean(axis=1)
    for s, factor in (compression or {}).items():
        j = cols.index(s)
        y[:, j] = mixture_mean + factor * (y[:, j] - mixture_mean)

    y[y < DETECTION_LIMIT] = np.nan
    y[rng.random(y.shape) < 0.01] = np.nan  # random missingness
    index = pd.Index([f"P{i:04d}" for i in range(n)], name="protein")
    return pd.DataFrame(y, index=index, columns=cols)


@dataclass
class QCScenario:
    id: str
    description: str
    make: Callable[[pd.DataFrame], pd.DataFrame]
    issue_type: str | None = None  # None for the clean control
    samples: list[str] = field(default_factory=list)  # any one named counts


def _swap_columns(df: pd.DataFrame, a: str, b: str) -> pd.DataFrame:
    out = df.copy()
    out[[a, b]] = df[[b, a]].to_numpy()
    return out


def _cpi(samples: pd.DataFrame) -> list[str]:
    return list(samples.loc[samples["compound"] != "DMSO", "sample"])


def scenarios(samples: pd.DataFrame) -> list[QCScenario]:
    return [
        QCScenario(
            "Q00_clean", "No planted problem (false-positive control).",
            lambda s: simulate_intensities(s),
        ),
        QCScenario(
            "Q01_low_loading", "R2_CPI_EZH2 loaded about 2.3-fold lower (-1.2 log2).",
            lambda s: simulate_intensities(s, channel_offsets={"R2_CPI_EZH2": -1.2}),
            "low_loading", ["R2_CPI_EZH2"],
        ),
        QCScenario(
            "Q02_ratio_compression", "R2_CPI_EZH2 ratios compressed to 40% towards the mixture mean.",
            lambda s: simulate_intensities(s, compression={"R2_CPI_EZH2": 0.4}),
            "ratio_compression", ["R2_CPI_EZH2"],
        ),
        QCScenario(
            "Q03_outlier_sample", "R3_DMSO_IgG has extra noise (SD 0.8 log2).",
            lambda s: simulate_intensities(s, extra_noise={"R3_DMSO_IgG": 0.8}),
            "outlier_sample", ["R3_DMSO_IgG"],
        ),
        QCScenario(
            "Q04_label_swap", "Data of R1_DMSO_EZH2 and R1_DMSO_IgG swapped (metadata unchanged).",
            lambda s: _swap_columns(simulate_intensities(s), "R1_DMSO_EZH2", "R1_DMSO_IgG"),
            "label_swap", ["R1_DMSO_EZH2", "R1_DMSO_IgG"],
        ),
        QCScenario(
            "Q05_treatment_loading", "All CPI-169 channels loaded lower (-0.6 log2).",
            lambda s: simulate_intensities(s, channel_offsets={x: -0.6 for x in _cpi(s)}),
            "loading_confounded_with_treatment", _cpi(samples),
        ),
    ]
