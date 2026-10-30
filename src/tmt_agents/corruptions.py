"""Deliberate corruptions of a correct SDRF, with the expected detector.

Each corruption changes one thing and records which kind of check should
catch it:

- category A: counting or structural errors that rules.py should catch
- category B: errors that are internally consistent, so rules.py cannot see
  them, but that contradict the design description (the LLM's job)
- category C: errors that neither layer can see, because the description
  holds no information about them (a negative control)
"""

from collections.abc import Callable
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class Corruption:
    id: str
    category: str  # "A", "B" or "C"
    description: str
    apply: Callable[[pd.DataFrame], pd.DataFrame]
    expected_rules: list[str] = field(default_factory=list)  # rules.py ids
    target_columns: list[str] = field(default_factory=list)  # for LLM scoring


def _set(sdrf: pd.DataFrame, row: int | slice, column: str, value) -> pd.DataFrame:
    """Set a value in every column with this name (SDRF may repeat names)."""
    out = sdrf.copy()
    for j, name in enumerate(out.columns):
        if name == column:
            out.iloc[row, j] = value
    return out


def _row(sdrf: pd.DataFrame, source_name: str) -> int:
    names = sdrf.iloc[:, list(sdrf.columns).index("source name")]
    return int(names[names == source_name].index[0])


def _swap(sdrf: pd.DataFrame, a: str, b: str, column: str) -> pd.DataFrame:
    out = sdrf.copy()
    j = list(out.columns).index(column)
    ra, rb = _row(out, a), _row(out, b)
    out.iloc[ra, j], out.iloc[rb, j] = sdrf.iloc[rb, j], sdrf.iloc[ra, j]
    return out


def _both(column: str) -> list[str]:
    return [f"characteristics[{column}]", f"factor value[{column}]"]


def _set_both(sdrf, row, column, value):
    for c in _both(column):
        sdrf = _set(sdrf, row, c, value)
    return sdrf


def _replace_tmt(sdrf: pd.DataFrame) -> pd.DataFrame:
    out = sdrf.copy()
    for j, name in enumerate(out.columns):
        if name == "comment[modification parameters]":
            out.iloc[:, j] = out.iloc[:, j].str.replace(
                "NT=TMTpro;AC=UNIMOD:2016", "NT=TMT6plex;AC=UNIMOD:737", regex=False
            )
    return out


def _swap_compound_r1(sdrf: pd.DataFrame) -> pd.DataFrame:
    """Swap the compound of cultures DMSO-1 and CPI-1, keeping sample names."""
    out = sdrf
    for column in _both("compound"):
        out = _swap(out, "R1_DMSO_EZH2", "R1_CPI_EZH2", column)
        out = _swap(out, "R1_DMSO_IgG", "R1_CPI_IgG", column)
    return out


CORRUPTIONS = [
    # --- A: rules.py should catch these -----------------------------------
    Corruption(
        "A01_duplicate_channel", "A",
        "R1_DMSO_IgG relabelled TMT126, the channel already used by R1_DMSO_EZH2.",
        lambda s: _set(s, _row(s, "R1_DMSO_IgG"), "comment[label]", "TMT126"),
        ["unique_channel"],
    ),
    Corruption(
        "A02_label_outside_plex", "A",
        "R1_DMSO_EZH2 labelled TMT135N, which exists only in TMTpro 18-plex.",
        lambda s: _set(s, _row(s, "R1_DMSO_EZH2"), "comment[label]", "TMT135N"),
        ["label_in_plex"],
    ),
    Corruption(
        "A03_missing_sample", "A",
        "Row for R3_CPI_IgG deleted.",
        lambda s: s.drop(index=_row(s, "R3_CPI_IgG")).reset_index(drop=True),
        ["balance", "pairing"],
    ),
    Corruption(
        "A04_antibody_mislabelled", "A",
        "R1_DMSO_IgG annotated as EZH2, so culture DMSO-1 has two EZH2 samples.",
        lambda s: _set_both(s, _row(s, "R1_DMSO_IgG"), "antibody", "EZH2"),
        ["balance", "pairing"],
    ),
    Corruption(
        "A05_factor_disagrees", "A",
        "factor value[compound] of R1_CPI_EZH2 set to DMSO; characteristics left as CPI-169.",
        lambda s: _set(s, _row(s, "R1_CPI_EZH2"), "factor value[compound]", "DMSO"),
        ["factor_matches_characteristics"],
    ),
    Corruption(
        "A06_misspelt_level", "A",
        "Compound of R2_CPI_IgG written as 'CPI169' instead of 'CPI-169'.",
        lambda s: _set_both(s, _row(s, "R2_CPI_IgG"), "compound", "CPI169"),
        ["factor_levels"],
        _both("compound"),
    ),
    Corruption(
        "A07_inconsistent_tolerance", "A",
        "Precursor tolerance of one channel set to 20 ppm; the others are 10 ppm.",
        lambda s: _set(s, _row(s, "R2_DMSO_IgG"), "comment[precursor mass tolerance]", "20 ppm"),
        ["run_level_consistency"],
    ),
    Corruption(
        "A08_duplicate_source_name", "A",
        "R3_DMSO_IgG renamed R3_DMSO_EZH2, duplicating another sample name.",
        lambda s: _set(s, _row(s, "R3_DMSO_IgG"), "source name", "R3_DMSO_EZH2"),
        ["unique_source_name"],
    ),
    Corruption(
        "A09_replicate_number_shift", "A",
        "Biological replicate of R2_CPI_IgG set to 3: condition counts stay "
        "balanced, but culture CPI-2 loses its IgG and CPI-3 has two.",
        lambda s: _set(s, _row(s, "R2_CPI_IgG"), "characteristics[biological replicate]", "3"),
        ["pairing"],
    ),
    # --- B: consistent within the SDRF, contradicts the description ----------
    Corruption(
        "B01_wrong_cell_line", "B",
        "Cell line written as HEK293 (description: RL).",
        lambda s: _set(s, slice(None), "characteristics[cell line]", "HEK293"),
        target_columns=["characteristics[cell line]"],
    ),
    Corruption(
        "B02_wrong_enzyme", "B",
        "Enzyme written as Lys-C (description: trypsin).",
        lambda s: _set(s, slice(None), "comment[cleavage agent details]", "NT=Lys-C;AC=MS:1001309"),
        target_columns=["comment[cleavage agent details]"],
    ),
    Corruption(
        "B03_wrong_organism", "B",
        "Organism written as mus musculus (description: human RL cells).",
        lambda s: _set(s, slice(None), "characteristics[organism]", "mus musculus"),
        target_columns=["characteristics[organism]"],
    ),
    Corruption(
        "B04_wrong_tmt_reagent", "B",
        "TMT modifications written as TMT6plex (description: TMTpro 16-plex).",
        _replace_tmt,
        target_columns=["comment[modification parameters]"],
    ),
    Corruption(
        "B05_wrong_disease", "B",
        "Disease written as Burkitt lymphoma (description: diffuse large B-cell lymphoma).",
        lambda s: _set(s, slice(None), "characteristics[disease]", "Burkitt lymphoma"),
        target_columns=["characteristics[disease]"],
    ),
    Corruption(
        "B06_treatment_swapped_names_kept", "B",
        "Compound of cultures DMSO-1 and CPI-1 swapped in both annotation "
        "columns; counts stay balanced, but the sample names still say the "
        "original treatment.",
        _swap_compound_r1,
        target_columns=_both("compound"),
    ),
    # --- C: undetectable from the description (negative control) ------------
    Corruption(
        "C01_channels_swapped", "C",
        "Channels of R1_DMSO_EZH2 and R1_CPI_EZH2 swapped. The description "
        "does not give the channel layout, so nothing can detect this.",
        lambda s: _swap(s, "R1_DMSO_EZH2", "R1_CPI_EZH2", "comment[label]"),
        target_columns=["comment[label]"],
    ),
]
