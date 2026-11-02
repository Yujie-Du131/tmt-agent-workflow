"""Design and contrast matrices for a two-factor split-plot TMT design.

The design has one between-culture factor (compound: each culture receives
one level) and one within-culture factor (antibody: each culture is split
across all levels). Everything here is deterministic; the LLM only proposes
which contrasts matter and which levels are references (see
select_contrasts), and the analyst confirms.

Scope: two factors with two levels each. Larger designs raise an error
rather than producing a silently wrong matrix.
"""

import re

import numpy as np
import pandas as pd

from tmt_agents.rules import _col


def safe_name(level: str) -> str:
    """Make a level usable as an R/limma column name ('CPI-169' -> 'CPI169')."""
    return re.sub(r"[^A-Za-z0-9]", "", level)


def _factors(design: dict) -> tuple[str, str]:
    """Return (within, between) factor names and check the supported scope."""
    within = design["within_culture_factor"]
    between = [f for f in design["factors"] if f != within]
    if len(between) != 1 or any(len(v) != 2 for v in design["factors"].values()):
        raise NotImplementedError("Only 2 x 2 designs with one within-culture factor are supported")
    return within, between[0]


def _levels(design: dict, factor: str) -> tuple[str, str]:
    """Return (non-reference, reference) levels of a factor."""
    ref = design["reference_levels"][factor]
    other = [lv for lv in design["factors"][factor] if lv != ref]
    if len(other) != 1:
        raise ValueError(f"Reference level {ref!r} not found among {design['factors'][factor]}")
    return other[0], ref


def sample_table(sdrf: pd.DataFrame, design: dict) -> pd.DataFrame:
    """One row per channel: sample, group and culture identifiers."""
    within, between = _factors(design)
    w = _col(sdrf, f"factor value[{within}]")
    b = _col(sdrf, f"factor value[{between}]")
    rep = _col(sdrf, "characteristics[biological replicate]")
    return pd.DataFrame({
        "sample": _col(sdrf, "source name").values,
        "label": _col(sdrf, "comment[label]").values,
        within: w.values,
        between: b.values,
        "group": [f"{safe_name(x)}.{safe_name(y)}" for x, y in zip(w, b)],
        "culture": [f"{safe_name(y)}_{r}" for y, r in zip(b, rep)],
    })


def group_names(design: dict) -> list[str]:
    """Groups in a fixed order: within (test, ref) x between (test, ref)."""
    within, between = _factors(design)
    w1, w0 = _levels(design, within)
    b1, b0 = _levels(design, between)
    return [f"{safe_name(w)}.{safe_name(b)}" for w in (w1, w0) for b in (b0, b1)]


def cell_means_design(samples: pd.DataFrame, design: dict) -> pd.DataFrame:
    """Design matrix with one column per group (limma: ~0 + group)."""
    groups = group_names(design)
    x = pd.DataFrame(0, index=samples["sample"], columns=groups)
    for s, g in zip(samples["sample"], samples["group"]):
        x.loc[s, g] = 1
    return x


def contrast_catalogue(design: dict) -> pd.DataFrame:
    """The four simple effects and the interaction, as columns over groups."""
    within, between = _factors(design)
    w1, w0 = (safe_name(v) for v in _levels(design, within))
    b1, b0 = (safe_name(v) for v in _levels(design, between))
    g = lambda w, b: f"{w}.{b}"  # noqa: E731
    defs = {
        f"{w1}_vs_{w0}_in_{b0}": {g(w1, b0): 1, g(w0, b0): -1},
        f"{w1}_vs_{w0}_in_{b1}": {g(w1, b1): 1, g(w0, b1): -1},
        f"{b1}_vs_{b0}_in_{w0}": {g(w0, b1): 1, g(w0, b0): -1},
        f"{b1}_vs_{b0}_in_{w1}": {g(w1, b1): 1, g(w1, b0): -1},
        "interaction": {g(w1, b1): 1, g(w1, b0): -1, g(w0, b1): -1, g(w0, b0): 1},
    }
    c = pd.DataFrame(0, index=group_names(design), columns=list(defs), dtype=int)
    for name, weights in defs.items():
        for grp, wt in weights.items():
            c.loc[grp, name] = wt
    return c


def contrast_stratum(samples: pd.DataFrame, contrasts: pd.DataFrame) -> dict[str, str]:
    """Classify each contrast as within-culture or between-culture.

    Each contrast is spread over the samples (weight c_g / n_g per sample of
    group g). If those weights sum to zero inside every culture, the
    culture effect cancels and the contrast is estimated within cultures.
    If not, it compares different cultures and its precision is set by the
    number of independent cultures.
    """
    n = samples["group"].value_counts()
    out = {}
    for name in contrasts.columns:
        w = samples["group"].map(lambda g: contrasts.loc[g, name] / n[g])
        per_culture = w.groupby(samples["culture"]).sum()
        out[name] = "within-culture" if np.allclose(per_culture, 0) else "between-culture"
    return out


def limma_snippet(design: dict) -> str:
    """R code for the analyst, matching the generated files."""
    return "\n".join([
        "library(limma)",
        'samples   <- read.csv("samples.csv")',
        'design    <- as.matrix(read.csv("design_matrix.csv", row.names = 1))',
        'contrasts <- as.matrix(read.csv("contrast_matrix.csv", row.names = 1))',
        "# y: log2 protein intensities, columns in the order of samples$sample",
        "corfit <- duplicateCorrelation(y, design, block = samples$culture)",
        "fit    <- lmFit(y, design, block = samples$culture,",
        "                correlation = corfit$consensus.correlation)",
        "fit2   <- eBayes(contrasts.fit(fit, contrasts))",
        'topTable(fit2, coef = "interaction", number = Inf)',
    ])


# ---------------------------------------------------------------------------
# LLM: which contrasts matter, and which levels are references
# ---------------------------------------------------------------------------

SELECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "reference_levels": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "factor": {"type": "string"},
                    "level": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["factor", "level", "reason"],
                "additionalProperties": False,
            },
        },
        "contrasts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "role": {"type": "string", "enum": ["primary", "secondary", "not_needed"]},
                    "reason": {"type": "string"},
                },
                "required": ["name", "role", "reason"],
                "additionalProperties": False,
            },
        },
        "requested_but_missing": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Comparisons the description asks for that are not in the catalogue.",
        },
    },
    "required": ["reference_levels", "contrasts", "requested_but_missing"],
    "additionalProperties": False,
}

SELECTION_SYSTEM = (
    "You help plan the statistical comparisons for a designed proteomics "
    "experiment. You are given the researcher's description, the factors "
    "and levels, and a fixed catalogue of contrasts with their definitions.\n"
    "1. For each factor, name the reference (control) level, citing the "
    "description.\n"
    "2. Give every catalogue contrast a role: 'primary' only if the "
    "description names it as the main question; 'secondary' if it supports "
    "interpreting the primary result (e.g. a sanity check or a component of "
    "an interaction); otherwise 'not_needed'. Use the catalogue names exactly.\n"
    "3. List any comparison the description asks for that the catalogue does "
    "not contain. Do not invent new contrasts or change their definitions."
)


def describe_catalogue(contrasts: pd.DataFrame) -> str:
    lines = []
    for name in contrasts.columns:
        terms = [f"{wt:+d} {grp}" for grp, wt in contrasts[name].items() if wt != 0]
        lines.append(f"- {name}: {' '.join(terms)}")
    return "\n".join(lines)


def select_contrasts(description: str, design: dict, contrasts: pd.DataFrame, client, model=None) -> dict:
    from tmt_agents.design_check import _structured_call

    factors = "\n".join(f"- {f}: {lv}" for f, lv in design["factors"].items())
    user = (
        f"Design description:\n{description}\n\n"
        f"Factors and levels:\n{factors}\n\n"
        "Group names are '<antibody>.<compound>' with non-alphanumeric "
        "characters removed.\n\n"
        f"Contrast catalogue (weights on group means):\n{describe_catalogue(contrasts)}"
    )
    return _structured_call(client, model, SELECTION_SYSTEM, user, SELECTION_SCHEMA)


def check_selection(selection: dict, design: dict, contrasts: pd.DataFrame) -> list[str]:
    """Deterministic checks on the LLM's proposal."""
    problems = []
    proposed = {r["factor"]: r["level"] for r in selection["reference_levels"]}
    for factor, ref in design["reference_levels"].items():
        if proposed.get(factor) != ref:
            problems.append(
                f"Reference level for {factor}: proposed {proposed.get(factor)!r}, "
                f"design.json has {ref!r}"
            )
    names = [c["name"] for c in selection["contrasts"]]
    unknown = sorted(set(names) - set(contrasts.columns))
    missing = sorted(set(contrasts.columns) - set(names))
    if unknown:
        problems.append(f"Unknown contrast names: {unknown}")
    if missing:
        problems.append(f"Catalogue contrasts without a role: {missing}")
    if not any(c["role"] == "primary" for c in selection["contrasts"]):
        problems.append("No contrast marked primary")
    return problems
