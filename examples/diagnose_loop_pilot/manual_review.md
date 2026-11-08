# Manual review: diagnose-rerun loop, pilot runs

**Correction (9 Nov 2026):** statements here that isotope correction was off are wrong. The quantms parameter `isotope_correction` was false, but the OpenMS build used (IsobaricWorkflow 3.6.0-pre-HEAD-2026-07-02) applies the correction anyway with its default TMT6 matrix. See the end of README section 5.

Model `claude-sonnet-5-5`, replay backend on PXD000001, reruns auto-approved,
3 runs from each starting point. Code at commit 9571f6c.

These runs are a **pilot**: they exposed a bug in the replay backend (below)
that affects the control runs. The bug was fixed before the final runs, and
the tool output changed slightly (`compare_runs` now includes
`corr_to_others`), so these transcripts are kept for the record but are not
the reported result.

## From the default run (ch2 and ch4 nearly empty)

| Run | Reruns | Path | Status | Code check |
|---|---|---|---|---|
| 1 | 2 | pipeline parameter (no effect, cached) -> `ext.args` | resolved | consistent |
| 2 | 2 | pipeline parameter (no effect, cached) -> `ext.args` | resolved | consistent |
| 3 | 1 | `ext.args` directly | resolved | consistent |

All three runs mapped ch2/ch4 to TMT127/TMT129 and ranked the reporter-ion
extraction tolerance first. Each rerun stated a hypothesis and a
quantitative expected change, and the expectation was met.

- Runs 1 and 2 followed the same path as the manual investigation: they
  changed `reporter_mass_shift`, saw in `compare_runs` that the command was
  unchanged and the step cached, and then passed the option through
  `ext.args`. Run 3 went straight to `ext.args`, after noticing that the
  parameter did not appear in the command.
- All three reported the remaining ratio compression (pooled spike-in slope
  0.778) with the correct values and noted that isotope correction was off.
  Runs 1 and 3 flagged the 3-PSM cytochrome c slope as unreliable.
- All three chose exactly 0.01 Th. Replay could only have served that
  value, and no run tested a smaller one. All three said so: runs 1 and 2 in
  their next steps, run 3 under remaining issues.

Errors and weak statements:

- Run 1 attributed the offset to "127N/127C and 129N/129C isotopologues"
  differing by about 6 mDa. N/C naming belongs to TMT10/11plex, not TMT6plex.
  The underlying idea (127/129 reporters a few mDa away from the expected
  mass) is consistent with the reagent explanation in section 4 of the
  README, which was not checked against a primary source.
- Run 2 proposed a mass calibration offset as a possible cause. As in the
  blind QC reports, a global offset cannot explain a failure of two channels
  only.
- Run 2 stated that `corr_to_others` was NaN for all channels. That is true
  for run0 only. The run never called `get_qc` on the fixed run, and
  `compare_runs` did not include this metric (now added).
- Runs 1 and 2 suggested that the wider window "could admit interference".
  TMT6plex reporters are about 1 Th apart, so no neighbouring reporter falls
  within 0.01 Th. Both statements were hedged.

## From the fixed run (control)

| Run | Reruns requested | Served | Status | Code check |
|---|---|---|---|---|
| 1 | 3 | 0 | unresolved | consistent |
| 2 | 3 | 0 | unresolved | consistent |
| 3 | 4 | 1 (parameter only, cached) | unresolved | consistent |

No run reported a channel problem. All three identified the ratio
compression and proposed co-isolation interference (`min_precursor_purity`
0.0) and missing isotope-impurity correction as causes. They tried to test
both, but replay could not serve those reruns, and all three said that the
causes were untested inferences.

**Replay bug found.** The fixed run was recorded with
`-extraction:reporter_mass_shift 0.01` passed through `ext.args`, but the
replay backend reported "ext.args overrides: none" for it. All three runs
therefore saw an unexplained mismatch between the parameter (0.002) and the
command (0.01). Runs 1 and 3 each spent a rerun on it. Run 1 asked to set
the option back to 0.002 via `ext.args`, reasoning that a wider window "may
admit neighbouring reporter ions". That reasoning is wrong (see above), and
the change would have re-broken ch2 and ch4. The request was refused because
of the same bug, not because of a check. Fixed: recorded runs now carry
their `ext.args`, and a request is matched against the run without
overrides plus the requested arguments, so reverting the option now returns
the default run with ch2 and ch4 flagged.

## Caveats that apply to the final runs as well

- The system prompt was written after the manual diagnosis. Rule 4 ("check
  whether the quantification command actually changed") is generic advice,
  but it points directly at the key observation.
- PXD000001 is widely discussed, so prior knowledge of this dataset cannot
  be ruled out.
- Replay can serve only two runs, so the loop is tested on finding and
  verifying a known fix, not on open-ended troubleshooting.
