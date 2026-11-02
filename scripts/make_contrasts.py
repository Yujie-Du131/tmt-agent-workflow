"""Draft the design and contrast matrices for the analyst to confirm.

Usage (from the repository root):
    uv run python scripts/make_contrasts.py data/own_design examples/contrasts
    uv run python scripts/make_contrasts.py data/own_design examples/contrasts --no-llm

Writes samples.csv, design_matrix.csv, contrast_matrix.csv and
contrast_plan.md to the output folder.
"""

import argparse
from pathlib import Path

from dotenv import load_dotenv

from tmt_agents.contrasts import (
    cell_means_design,
    check_selection,
    contrast_catalogue,
    contrast_stratum,
    limma_snippet,
    sample_table,
    select_contrasts,
)
from tmt_agents.design_check import default_model
from tmt_agents.rules import load_design, run_all
from tmt_agents.sdrf_io import read_sdrf


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("design_dir", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--no-llm", action="store_true")
    args = parser.parse_args()

    sdrf = read_sdrf(args.design_dir / "sdrf.tsv")
    design = load_design(args.design_dir / "design.json")
    errors = [i for i in run_all(sdrf, design) if i.severity == "error"]
    if errors:
        print("The SDRF fails the rule checks; fix these before building contrasts:")
        for i in errors:
            print(f"  {i.rule}: {i.message}")
        return 1

    samples = sample_table(sdrf, design)
    x = cell_means_design(samples, design)
    c = contrast_catalogue(design)
    strata = contrast_stratum(samples, c)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    samples.to_csv(args.out_dir / "samples.csv", index=False)
    x.to_csv(args.out_dir / "design_matrix.csv")
    c.to_csv(args.out_dir / "contrast_matrix.csv")

    plan = [
        "# Contrast plan (DRAFT: for the analyst to confirm)",
        "",
        "## Model",
        "",
        "Cell-means design (`~ 0 + group`) with culture as a blocking factor "
        "(`duplicateCorrelation`). Each culture contributes one EZH2 and one IgG "
        "sample, so contrasts that compare samples within the same culture are "
        "estimated with the culture effect cancelled; contrasts that compare "
        "different cultures rely on the three independent cultures per treatment.",
        "",
        f"Reference levels (from design.json): "
        + ", ".join(f"{f} = {lv}" for f, lv in design["reference_levels"].items()),
        "",
        "## Contrasts",
        "",
        "| Contrast | Definition | Stratum |",
        "|---|---|---|",
    ]
    for name in c.columns:
        terms = " ".join(f"{wt:+d} {g}" for g, wt in c[name].items() if wt != 0)
        plan.append(f"| {name} | {terms} | {strata[name]} |")

    if not args.no_llm:
        import anthropic

        load_dotenv()
        description = (args.design_dir / "design_description.md").read_text(encoding="utf-8")
        selection = select_contrasts(description, design, c, anthropic.Anthropic())
        problems = check_selection(selection, design, c)
        plan += [
            "",
            f"## Proposed roles (LLM: `{default_model()}`)",
            "",
            "| Contrast | Role | Reason |",
            "|---|---|---|",
        ]
        plan += [f"| {s['name']} | {s['role']} | {s['reason']} |" for s in selection["contrasts"]]
        plan += ["", "Reference levels proposed from the description:", ""]
        plan += [f"- {r['factor']} = {r['level']}: {r['reason']}" for r in selection["reference_levels"]]
        if selection["requested_but_missing"]:
            plan += ["", "Requested in the description but not in the catalogue:", ""]
            plan += [f"- {m}" for m in selection["requested_but_missing"]]
        plan += ["", "Checks on the proposal: " + ("passed." if not problems else "")]
        plan += [f"- {p}" for p in problems]

    plan += ["", "## limma code", "", "```r", limma_snippet(design), "```", ""]
    (args.out_dir / "contrast_plan.md").write_text("\n".join(plan), encoding="utf-8")
    print(f"Wrote {args.out_dir}/ (samples.csv, design_matrix.csv, contrast_matrix.csv, contrast_plan.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
