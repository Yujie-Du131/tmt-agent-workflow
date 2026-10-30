"""Check an SDRF with the rules and the LLM layer, and write a Markdown report.

Usage (from the repository root):
    uv run python scripts/review_sdrf.py data/own_design examples/own_design_review.md

The design folder must contain sdrf.tsv, design.json and design_description.md.
Requires ANTHROPIC_API_KEY in .env.
"""

import json
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from tmt_agents.design_check import (
    compare_specs,
    default_model,
    draft_design_spec,
    factor_names,
    format_review,
    review_sdrf,
)
from tmt_agents.rules import load_design, run_all
from tmt_agents.sdrf_io import read_sdrf


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    design_dir, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    load_dotenv()
    client = anthropic.Anthropic()

    sdrf = read_sdrf(design_dir / "sdrf.tsv")
    description = (design_dir / "design_description.md").read_text(encoding="utf-8")
    reference = load_design(design_dir / "design.json")

    # 1. LLM drafts the design spec from the description; compare with the
    #    analyst-confirmed design.json.
    draft = draft_design_spec(description, factor_names(sdrf), client)
    diffs = compare_specs(draft, reference)

    # 2. Deterministic rules, then LLM review of the SDRF.
    issues = run_all(sdrf, reference)
    review = review_sdrf(description, sdrf, issues, client)

    report = [
        f"# SDRF review: {design_dir}",
        "",
        f"Model: `{default_model()}`",
        "",
        "## Design spec drafted from the description",
        "",
        "```json",
        json.dumps(draft, indent=2),
        "```",
        "",
        "Differences from the confirmed design.json: "
        + ("none." if not diffs else ""),
    ]
    report += [f"- {d}" for d in diffs]
    report += ["", "## Rule checks", ""]
    report += [f"- [{i.severity.upper()}] {i.rule}: {i.message}" for i in issues] or ["- No issues."]
    report += ["", format_review(review)]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"Spec differences: {len(diffs)}; rule issues: {len(issues)}; "
          f"LLM findings: {len(review['findings'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
