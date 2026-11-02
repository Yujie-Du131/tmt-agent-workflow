# Manual review: blind QC report on real quantms output

## Setup

The LLM received the channel metrics, spike-in recovery, the SDRF, the full
pipeline parameters and the command of the quantification step
(`prompt_<tag>.txt`). It was not told what, if anything, was wrong. The
prompt was written after the problem had been diagnosed, while avoiding
hints (checked by `tests/test_run_qc_report.py`). PXD000001 is a widely
discussed public dataset, so prior knowledge of it cannot be ruled out.

- `shift0.002`: before the fix (channels 2 and 4 almost empty).
- `shift0.01`: after the fix (control).

A first batch of 3 + 3 runs gave the same pattern, but its full reports
were overwritten by a file-naming bug in the script (fixed); only the
printed one-line summaries survive. The reports in this folder are the
second batch.

## Before the fix (3 runs)

All 3 runs reported a major issue on ch2 and ch4, mapped them to TMT127
and TMT129 from the SDRF order, and ranked reporter-ion extraction first,
citing `reporter_mass_shift = 0.002`. Run 2 named a mismatch between the
tmt6plex reporter masses and the measured peaks, closest to the actual
mechanism. All runs also reported ratio compression, citing
`isotope_correction=false` and (run 3) `min_precursor_purity=0.0`.

Numbers quoted in run 2 (slopes, PSM counts, expected ranges, parameters)
were checked against the inputs and matched. Run 2 also noted that the
spike-in slopes rested on only four channels and might change once ch2 and
ch4 were recovered; they did (enolase 0.882 to 0.798).

Weaknesses:

- Runs 1 and 3 listed a mass-calibration offset as a cause. A global
  calibration offset would shift all reporter ions and cannot explain why
  only two of six channels failed; these runs did not use that pattern to
  rule it out. Run 3 also listed labelling failure in the two channels
  (reagent missing or hydrolysed, sample lost), which does fit the pattern
  and was ruled out only by the re-run with a wider window.
- No run proposed that the 2012 data may use older TMT6 reagents with
  slightly different 127/129 reporter masses. Run 2 recommended inspecting
  the spectra at 127.1248 and 129.1315, the current reporter masses, which
  is a valid check but not the deeper explanation.
- The top cause was usually a list of alternatives rather than a single
  diagnosis. It pointed in the right direction and gave checks that would
  confirm it.

## After the fix (control, 3 runs)

All 3 runs reported only minor ratio compression attributed to
co-isolation interference, which is present in the data (pooled spike-in
slope 0.78). No run reported missing channels.

Run 3 also noticed, unprompted, that the pipeline parameters give
`reporter_mass_shift` 0.002 while the command uses
`-extraction:reporter_mass_shift 0.01`, quoting both values. This is the
trace of the quantms parameter-passing problem described in
`examples/quantms_pxd000001_investigation.md`. It judged the wider window
unlikely to explain the compression, which is reasonable, but suggested
re-running with 0.002 for comparison without knowing that this would empty
ch2 and ch4 again (the model sees no run history).

Run 3 stated that fold changes are "underestimated by about 20-25% at large
ratios" without giving the scale. A slope of 0.78 is a 22% shortfall on
the log scale, but a true 10-fold difference is measured as about 6-fold,
a 40% shortfall in fold terms.
