"""Generate the SDRF for the EZH2/IgG x CPI-169/DMSO experiment.

Usage (from the repository root):
    uv run python scripts/make_own_sdrf.py
"""

from pathlib import Path

from tmt_agents.sdrf_io import (
    RUN_PARAMS_OWN_DESIGN,
    build_sdrf,
    read_sample_sheet,
    write_sdrf,
)

DESIGN_DIR = Path("data/own_design")


def main() -> None:
    sheet = read_sample_sheet(DESIGN_DIR / "samples.csv")
    sdrf = build_sdrf(sheet, RUN_PARAMS_OWN_DESIGN)
    out = DESIGN_DIR / "sdrf.tsv"
    write_sdrf(sdrf, out)
    print(f"Wrote {len(sdrf)} rows x {sdrf.shape[1]} columns to {out}")


if __name__ == "__main__":
    main()
