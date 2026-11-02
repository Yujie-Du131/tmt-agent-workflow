"""QC on real quantms TMT output: channel metrics and spike-in ratio recovery.

Usage (from the repository root):
    uv run python scripts/check_quantms_output.py \
        data/quantms_pxd000001/msstats_in.csv.gz examples/quantms_pxd000001
"""

import sys
from pathlib import Path

from tmt_agents.quantms_qc import (
    channel_metrics,
    expected_amounts,
    pooled_slope,
    protein_matrix,
    psm_counts,
    read_msstats_in,
    spike_in_recovery,
)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)

    msstats = read_msstats_in(src)
    y = protein_matrix(msstats)
    psms = psm_counts(msstats)
    expected = expected_amounts(msstats)
    per_channel, summary = spike_in_recovery(y, expected, psms)
    spiked = [p for p in summary["protein"] if p]
    metrics = channel_metrics(y, exclude=spiked)
    found = list(summary.dropna(subset=["slope"])["accession"])
    pooled = pooled_slope(per_channel, found)

    y.round(4).to_csv(out / "protein_matrix_log2.csv")
    metrics.to_csv(out / "channel_metrics.csv")
    per_channel.to_csv(out / "spike_in_channels.csv", index=False)
    summary.to_csv(out / "spike_in_summary.csv", index=False)

    lines = [
        "# QC on quantms output: PXD000001 (quantms test_tmt)",
        "",
        f"Input: `{src}` ({len(msstats)} rows; {psms.size} proteins; "
        f"{y.shape[0]} proteins after removing decoys and protein groups).",
        "",
        "## Channel metrics (background proteins only)",
        "",
        metrics.to_markdown(),
        "",
        "## Spike-in ratio recovery",
        "",
        "Slope of measured on expected centred log2 values (1 = full recovery; "
        "below 1 = ratio compression).",
        "",
        summary.to_markdown(index=False),
        "",
        f"Pooled slope over all identified spike-ins: **{pooled}**",
        "",
    ]
    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
