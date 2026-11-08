# Manual review: diagnose-rerun loop, final runs

**Correction (9 Nov 2026):** statements here that isotope correction was off are wrong. The quantms parameter `isotope_correction` was false, but the OpenMS build used (IsobaricWorkflow 3.6.0-pre-HEAD-2026-07-02) applies the correction anyway with its default TMT6 matrix. See the end of README section 5.

Model `claude-sonnet-5-5`, replay backend on PXD000001, reruns auto-approved,
3 runs from each starting point. Code at commit ea7af94 (after the replay
fix found in the pilot, `examples/diagnose_loop_pilot/manual_review.md`).

## From the default run (ch2 and ch4 nearly empty)

| Run | Reruns | Path | Status | Code check |
|---|---|---|---|---|
| 1 | 2 | pipeline parameter (no effect, cached) -> `ext.args` | resolved | consistent |
| 2 | 1 | `ext.args` directly | resolved | consistent |
| 3 | 2 | pipeline parameter (no effect, cached) -> `ext.args` | resolved | consistent |

- All three mapped ch2/ch4 to TMT127/TMT129, ranked the reporter-ion
  extraction tolerance first, and finished with no channel flagged.
- Runs 1 and 3 took the same path as the manual investigation. Run 2 read
  from the command that the parameter was not passed and went straight to
  `ext.args`.
- Every rerun stated a hypothesis and a quantitative expected change (for
  example "ch2 and ch4 rise from 1 and 4 to about 460 proteins"), and each
  expectation for the `ext.args` rerun was met. The expectations for the
  parameter-only reruns were not met, and the runs said why (command
  unchanged, step cached).
- All three reported the remaining ratio compression (pooled spike-in slope
  0.82 before and 0.778 after the fix) with correct values, noted that
  isotope correction was off and suggested testing a precursor purity
  filter. Runs 2 and 3 called the 3-PSM cytochrome c slope unreliable.
  Runs 1 and 2 noted that the other channels lost about 5 proteins after
  the fix, which is correct.
- Run 2 first called `finish` without `next_steps`; code rejected it and the
  model completed it.

Mechanism statements:

- Run 3 proposed a 15N/13C isotopologue offset of about 6 mDa for the
  127/129 reporters, and run 1 the "127N/127C and 129N/129C reporter
  definitions". Both match the reagent explanation in section 4 of the
  README, which was not checked against a primary source. Run 1's N/C naming
  belongs to TMT10/11plex. None of the blind QC reports had proposed this.
- All three also kept instrument mass calibration as a candidate cause. A
  global calibration offset cannot explain a failure of two channels only.
  None ranked it first.
- None tested a window smaller than 0.01 Th (replay could not have served
  it). Runs 1 and 2 listed a smaller window as a check; run 3 called 0.01 a
  workaround and asked for the reporter m/z offsets to be checked.

## From the fixed run (control)

| Run | Reruns requested | Served | Status | Final run | Code check |
|---|---|---|---|---|---|
| 1 | 3 | 1 | unresolved | run0 | consistent |
| 2 | 3 | 1 | unresolved | run0 | consistent |
| 3 | 2 | 1 | unresolved | run0 | consistent |

- No run reported a channel problem. All three identified the ratio
  compression and proposed co-isolation interference and missing isotope
  correction as causes; replay could not serve those reruns, and all three
  said the causes were untested.
- **All three asked to revert the `ext.args` override to 0.002**, on weak
  reasoning: that the wider window might pick up neighbouring signals and
  compress ratios. TMT6plex reporters are about 1 Th apart, so this is
  unlikely. The revert broke ch2 and ch4 in all three runs. All three then
  read the result correctly: they concluded that the override is needed,
  named run0 as the final run and recommended keeping it. Runs 2 and 3 also
  noted that the pooled slope of the reverted run (0.82) is not comparable,
  because it is computed without ch2 and ch4; run 1 did not.
- With live reruns of about 25 minutes each, this is a request the analyst
  would probably refuse at the approval gate. In these runs approval was
  automatic.

**Replay artefact (fixed after these runs).** When a request set an option
to its OpenMS default, replay returned the recorded default run with its
command as recorded, without the explicit argument. Run 1 noticed that the
`-extraction:reporter_mass_shift 0.002` it had asked for did not appear in
the command and listed this as a remaining issue. That statement is caused
by the replay, not by quantms. Replay now shows explicit default arguments
in the command, as a live run would. No other conclusion depended on it.

## Caveats

- The system prompt was written after the manual diagnosis. Rule 4 ("check
  whether the quantification command actually changed") is generic advice,
  but it points directly at the key observation.
- PXD000001 is widely discussed, so prior knowledge of this dataset cannot
  be ruled out.
- Replay can serve only two runs, so the loop is tested on finding and
  verifying a known fix, not on open-ended troubleshooting. Reruns were
  auto-approved; the approval gate itself was tested only with the scripted
  model.
- 3 runs per starting point, one model.
