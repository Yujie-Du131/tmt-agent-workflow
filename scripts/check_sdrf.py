"""Run the deterministic rule checks on an SDRF.

Usage (from the repository root):
    uv run python scripts/check_sdrf.py data/own_design/sdrf.tsv data/own_design/design.json
"""

import sys

from tmt_agents.rules import load_design, run_all
from tmt_agents.sdrf_io import read_sdrf


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    sdrf = read_sdrf(sys.argv[1])
    design = load_design(sys.argv[2])
    issues = run_all(sdrf, design)

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    print(f"{len(sdrf)} rows checked: {len(errors)} error(s), {len(warnings)} warning(s)")
    for i in issues:
        rows = f" (rows {[r + 1 for r in i.rows]})" if i.rows else ""
        print(f"  [{i.severity.upper()}] {i.rule}: {i.message}{rows}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
