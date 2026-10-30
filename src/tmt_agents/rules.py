"""Deterministic rule checks for a TMT SDRF against an expected design.

Each check returns a list of Issue objects. These checks do not use an LLM:
anything that can be decided by counting or matching is done here, so that
the LLM layer is only used for comparing the SDRF with a free-text design
description and explaining problems.
"""

import json
import math
from dataclasses import dataclass, field
from itertools import product
from pathlib import Path

import pandas as pd

PLEX_LABELS = {
    "TMT10": [
        "TMT126", "TMT127N", "TMT127C", "TMT128N", "TMT128C",
        "TMT129N", "TMT129C", "TMT130N", "TMT130C", "TMT131",
    ],
    "TMT11": [
        "TMT126", "TMT127N", "TMT127C", "TMT128N", "TMT128C",
        "TMT129N", "TMT129C", "TMT130N", "TMT130C", "TMT131N", "TMT131C",
    ],
    "TMTpro16": [
        "TMT126", "TMT127N", "TMT127C", "TMT128N", "TMT128C",
        "TMT129N", "TMT129C", "TMT130N", "TMT130C", "TMT131N",
        "TMT131C", "TMT132N", "TMT132C", "TMT133N", "TMT133C", "TMT134N",
    ],
}
PLEX_LABELS["TMTpro18"] = PLEX_LABELS["TMTpro16"] + ["TMT134C", "TMT135N"]

REQUIRED_COLUMNS = [
    "source name",
    "characteristics[biological replicate]",
    "comment[data file]",
    "comment[fraction identifier]",
    "comment[label]",
]

# Columns that describe how a run was acquired and searched; they must not
# change between channels of the same raw file.
RUN_LEVEL_COLUMNS = [
    "comment[instrument]",
    "comment[cleavage agent details]",
    "comment[modification parameters]",
    "comment[precursor mass tolerance]",
    "comment[fragment mass tolerance]",
    "comment[dissociation method]",
    "comment[proteomics data acquisition method]",
]


@dataclass
class Issue:
    rule: str
    severity: str  # "error" or "warning"
    message: str
    rows: list[int] = field(default_factory=list)  # 0-based data rows


def load_design(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _col(sdrf: pd.DataFrame, name: str) -> pd.Series:
    """Return the first column with this name (SDRF may repeat names)."""
    idx = list(sdrf.columns).index(name)
    return sdrf.iloc[:, idx]


def check_required_columns(sdrf: pd.DataFrame, design: dict) -> list[Issue]:
    needed = REQUIRED_COLUMNS + [f"factor value[{f}]" for f in design["factors"]]
    missing = [c for c in needed if c not in sdrf.columns]
    return [
        Issue("required_columns", "error", f"Missing required column: {c}")
        for c in missing
    ]


def check_unique_source_names(sdrf: pd.DataFrame, design: dict) -> list[Issue]:
    names = _col(sdrf, "source name")
    dup = names[names.duplicated(keep=False)]
    return [
        Issue(
            "unique_source_name",
            "error",
            f"Source name '{n}' is used more than once",
            dup.index[dup == n].tolist(),
        )
        for n in dup.unique()
    ]


def check_labels_in_plex(sdrf: pd.DataFrame, design: dict) -> list[Issue]:
    allowed = set(PLEX_LABELS[design["plex"]])
    labels = _col(sdrf, "comment[label]")
    bad = labels[~labels.isin(allowed)]
    return [
        Issue(
            "label_in_plex",
            "error",
            f"Label '{lab}' is not a {design['plex']} channel",
            bad.index[bad == lab].tolist(),
        )
        for lab in bad.unique()
    ]


def check_unique_channels(sdrf: pd.DataFrame, design: dict) -> list[Issue]:
    """Each (raw file, fraction, label) must be assigned to only one sample."""
    key = pd.DataFrame({
        "file": _col(sdrf, "comment[data file]"),
        "fraction": _col(sdrf, "comment[fraction identifier]"),
        "label": _col(sdrf, "comment[label]"),
    })
    issues = []
    for (f, fr, lab), grp in key.groupby(["file", "fraction", "label"]):
        if len(grp) > 1:
            issues.append(Issue(
                "unique_channel",
                "error",
                f"Channel {lab} in {f} (fraction {fr}) is assigned to "
                f"{len(grp)} samples",
                grp.index.tolist(),
            ))
    return issues


def check_factor_matches_characteristics(sdrf: pd.DataFrame, design: dict) -> list[Issue]:
    """factor value[x] should equal characteristics[x] when both exist."""
    issues = []
    for f in design["factors"]:
        fv, ch = f"factor value[{f}]", f"characteristics[{f}]"
        if fv in sdrf.columns and ch in sdrf.columns:
            mismatch = _col(sdrf, fv) != _col(sdrf, ch)
            if mismatch.any():
                issues.append(Issue(
                    "factor_matches_characteristics",
                    "error",
                    f"'{fv}' disagrees with '{ch}'",
                    sdrf.index[mismatch].tolist(),
                ))
    return issues


def check_factor_levels(sdrf: pd.DataFrame, design: dict) -> list[Issue]:
    issues = []
    for f, levels in design["factors"].items():
        col = f"factor value[{f}]"
        if col not in sdrf.columns:
            continue
        values = _col(sdrf, col)
        bad = values[~values.isin(levels)]
        for v in bad.unique():
            issues.append(Issue(
                "factor_levels",
                "error",
                f"Unexpected level '{v}' in {col} (expected one of {levels})",
                bad.index[bad == v].tolist(),
            ))
    return issues


def check_balance(sdrf: pd.DataFrame, design: dict) -> list[Issue]:
    """Every combination of factor levels has the expected number of samples."""
    factors = list(design["factors"])
    cols = [f"factor value[{f}]" for f in factors]
    if any(c not in sdrf.columns for c in cols):
        return []
    table = pd.DataFrame({f: _col(sdrf, c) for f, c in zip(factors, cols)})
    counts = table.value_counts()
    n = design["replicates_per_condition"]
    issues = []
    for combo in product(*design["factors"].values()):
        got = int(counts.get(combo, 0))
        if got != n:
            label = ", ".join(f"{f}={v}" for f, v in zip(factors, combo))
            issues.append(Issue(
                "balance",
                "error",
                f"Condition ({label}) has {got} samples; expected {n}",
            ))
    return issues


def check_pairing(sdrf: pd.DataFrame, design: dict) -> list[Issue]:
    """Each culture must contain exactly one sample per level of the
    within-culture factor (here: one EZH2 and one IgG)."""
    inner = design["within_culture_factor"]
    inner_col = f"factor value[{inner}]"
    keys = design["culture_defined_by"]
    key_cols = [
        f"factor value[{k}]" if k in design["factors"] else f"characteristics[{k}]"
        for k in keys
    ]
    if any(c not in sdrf.columns for c in key_cols + [inner_col]):
        return []
    table = pd.DataFrame({k: _col(sdrf, c) for k, c in zip(keys, key_cols)})
    table[inner] = _col(sdrf, inner_col)
    expected = sorted(design["factors"][inner])
    issues = []
    for culture, grp in table.groupby(keys):
        got = sorted(grp[inner])
        if got != expected:
            label = ", ".join(f"{k}={v}" for k, v in zip(keys, culture))
            issues.append(Issue(
                "pairing",
                "error",
                f"Culture ({label}) has {inner} = {got}; expected {expected}",
                grp.index.tolist(),
            ))
    n_cultures = table.groupby(keys).ngroups
    culture_factors = [k for k in keys if k in design["factors"]]
    expected_cultures = design["replicates_per_condition"] * math.prod(
        len(design["factors"][k]) for k in culture_factors
    )
    if n_cultures != expected_cultures:
        issues.append(Issue(
            "pairing",
            "error",
            f"Found {n_cultures} cultures; expected {expected_cultures}",
        ))
    return issues


def check_run_level_consistency(sdrf: pd.DataFrame, design: dict) -> list[Issue]:
    """Run-level parameters must be identical across channels of one raw file."""
    files = _col(sdrf, "comment[data file]")
    issues = []
    for i, name in enumerate(sdrf.columns):
        if name not in RUN_LEVEL_COLUMNS:
            continue
        col = sdrf.iloc[:, i]
        for f in files.unique():
            values = col[files == f].unique()
            if len(values) > 1:
                issues.append(Issue(
                    "run_level_consistency",
                    "error",
                    f"'{name}' has {len(values)} different values within {f}",
                    col.index[files == f].tolist(),
                ))
    return issues


def report_unused_channels(sdrf: pd.DataFrame, design: dict) -> list[Issue]:
    used = set(_col(sdrf, "comment[label]"))
    unused = [lab for lab in PLEX_LABELS[design["plex"]] if lab not in used]
    if not unused:
        return []
    return [Issue(
        "unused_channels",
        "warning",
        f"{len(unused)} channel(s) not assigned to a sample: {', '.join(unused)}. "
        "Confirm these were left empty in the experiment.",
    )]


ALL_CHECKS = [
    check_required_columns,
    check_unique_source_names,
    check_labels_in_plex,
    check_unique_channels,
    check_factor_matches_characteristics,
    check_factor_levels,
    check_balance,
    check_pairing,
    check_run_level_consistency,
    report_unused_channels,
]


def run_all(sdrf: pd.DataFrame, design: dict) -> list[Issue]:
    issues = check_required_columns(sdrf, design)
    if issues:  # later checks need these columns
        return issues
    for check in ALL_CHECKS[1:]:
        issues.extend(check(sdrf, design))
    return issues