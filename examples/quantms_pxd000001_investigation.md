# Real quantms output: two empty TMT channels, diagnosed and fixed

Data: PXD000001 (TMT6plex, Erwinia background with four spiked proteins at
known amounts), processed with the quantms `test_tmt` profile, quantms 1.10.0,
OpenMS image `ghcr.io/bigbio/openms-tools-thirdparty:2026.07.02`.

## 1. QC flagged two channels

With the default reporter-ion extraction tolerance (0.002 Th), channels 2
and 4 (TMT127 and TMT129) were almost empty:

| Channel | Proteins quantified | Robust z of median |
|---|---|---|
| ch2 | 1 of 468 | -34.5 |
| ch4 | 4 of 468 | -27.5 |
| others | 465-468 | within +/-1 |

All six channels had the same number of PSM rows (2,713); in channels 2 and
4 almost every reporter intensity was zero. Output:
`examples/quantms_pxd000001_shift0.002/`.

## 2. Diagnosis

`reporter_mass_shift` was 0.002 in the run parameters. Setting
`--reporter_mass_shift 0.01` on the command line had no effect: the
`ISOBARIC_WORKFLOW` step was cached and its command did not contain the
option. In quantms 1.10.0 the pipeline parameter is not passed to
OpenMS `IsobaricWorkflow`, which therefore used its own default
(`-extraction:reporter_mass_shift 2.0e-03`, confirmed with `--helphelp`).

The option was passed through `ext.args`
(`configs/quantms_reporter_shift_0.01.config`).

## 3. After the fix

| Channel | Proteins quantified | Robust z of median | Correlation to other channels |
|---|---|---|---|
| ch1-ch6 | 459-463 | -1.8 to 1.3 | 0.995-0.999 |

Output: `examples/quantms_pxd000001_shift0.01/`.

Only the 127 and 129 channels were affected, and their signal lies outside
0.002 Th but within 0.01 Th of the expected position. This is consistent
with older TMT6 reagents whose 127 and 129 reporters differ slightly in mass
from the values the software expects; the exact reagent masses were not
checked against a primary source.

## 4. Ratio compression measured on the spike-ins

| Protein | PSMs | Slope (1 = full recovery) |
|---|---|---|
| Enolase (P00924) | 32 | 0.80 |
| Serum albumin (P02769) | 32 | 0.73 |
| Glycogen phosphorylase (P00489) | 52 | 0.75 |
| Cytochrome c (P62894) | 3 | 1.15 (too few PSMs to interpret) |
| Pooled | | 0.78 |

A true 10-fold difference was measured as about 5-6 fold. Caveats:
isotope-impurity correction was off in this run, so the slope mixes
co-isolation interference with channel crosstalk; the calculation assumes
equal background protein in every channel (channel medians agree within
0.3 log2); one dataset, one run.

The simulated QC benchmark (scenario Q02) used much stronger compression
(factor 0.4) than observed here and should be read as a stress test.
