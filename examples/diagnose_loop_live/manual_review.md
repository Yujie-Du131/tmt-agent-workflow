# Manual review: diagnose-rerun loop, live quantms runs

Model `claude-sonnet-5-5`, live Nextflow backend (quantms 1.10.0, Docker),
launched from the folder of the manual investigation with its config and
local raw input, so earlier tasks were reused from the Nextflow cache. One
run from each starting point. Every rerun was approved by the analyst at the
terminal.

## From the default run (ch2 and ch4 nearly empty)

`live_start_shift0.002_run1`: 1 rerun, status "resolved", code check
consistent.

- After `get_run_config`, the model noted that the `reporter_mass_shift`
  parameter did not appear in the command and went straight to
  `ext.args` (`-extraction:reporter_mass_shift 0.01`). Its expected change
  (ch2 and ch4 back to about 465 proteins) was met (459 and 461).
- **The fixed step was not recomputed.** `nextflow log` shows
  `ISOBARIC_WORKFLOW` and `MSSTATS_CONVERTER` as `CACHED`: the same task had
  been run during the manual investigation on 2 November. The metrics are
  therefore identical to the recorded fixed run. The rerun went through
  Nextflow as a real run would, but the result came from the cache.
- Remaining issues (ratio compression, about 5 fewer proteins per channel,
  the 3-PSM cytochrome c slope) were stated correctly.

## From the fixed run (control)

`live_start_shift0.01_run1`: 3 reruns, status "unresolved", final run run0
(the fixed run), code check consistent.

| Rerun | Change | What happened |
|---|---|---|
| run1 | `min_precursor_purity` 0.0 -> 0.7 | Command changed and the step ran again, but every metric was identical (pooled slope 0.778) |
| run2 | `isotope_correction` true | Command unchanged; Nextflow reused the cached task |
| run3 | `ext.args` back to `reporter_mass_shift 0.002` | ch2 and ch4 failed again (1 and 4 proteins) |

- **run1** is the first change in this project that was computed fresh. A
  purity filter of 0.7 with no effect at all on protein counts or
  spike-in slopes is unexpected. The model offered two explanations (no
  purity information in the mzML, or no spectra below 0.7) and said it
  could not test co-isolation. Neither was checked; this is open.
- **run2** hit the second parameter trap: in quantms 1.10.0,
  `isotope_correction` has an effect only when `plex_corr_matrix_file` is
  also set. The model saw from `compare_runs` that the command did not
  change and concluded that the parameter "has no effect on the
  IsobaricWorkflow command", which is correct, and listed supplying a
  correction matrix as a next step. It did not identify the dependency on
  `plex_corr_matrix_file`, and it stated that the matrix parameter is "not
  passed", which is only true while it is unset. **Bug on our side:** the
  bundled correction matrices were not listed for the model, because the
  backend looked for them in the asset layout of older Nextflow versions.
  Fixed afterwards (assets are now searched recursively).
- **run3** reverted the fix on the same weak reasoning as in all three
  replayed control runs (a wider window "may cause mis-assigned reporter
  peaks"). The analyst approved it. It broke ch2 and ch4 again; the model
  then concluded that the 0.01 override is necessary, named run0 as final,
  and correctly called the pooled slope of run3 (0.82) not meaningful with
  two channels lost. This rerun used the last of the 3 reruns, so the
  correction-matrix change was not tried.

## Caveats

- Two live runs, one model. The default-start fix came from the Nextflow
  cache of the manual investigation.
- The system prompt was written after the manual diagnosis; PXD000001 is
  widely discussed.
