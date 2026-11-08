# tmt-agent-workflow

LLM-assisted checks around a quantms/Nextflow TMT proteomics workflow: metadata
validation before a run, contrast drafting, QC reports written from computed
metrics (not plots), and an agent loop that diagnoses a QC problem, requests
reruns with changed settings and compares the runs.

Deterministic code does everything that can be counted or matched. The LLM is
used only where code cannot help: comparing metadata with the researcher's
free-text description of the experiment, explaining problems, writing QC
reports, and, in the agent loop, choosing the next rerun, because after a QC
problem the next step depends on interpreting the result. Every LLM output is
a draft for the analyst to confirm, and every rerun needs the analyst's
approval.

## Status: what was tested on what

The framework was designed for my MSc thesis experiment (below). MS data were
still pending at graduation, so no component has been run on my own MS data.

| Component | Tested on |
|---|---|
| Pre-run SDRF checks | SDRF of my own design, and 16 deliberately corrupted copies |
| Contrast drafting | My own design |
| Post-run QC report | Simulated intensities with planted problems; real quantms output for the public dataset PXD000001 |
| Diagnose-rerun agent loop | PXD000001: replay of two recorded quantms runs, and live quantms reruns |

## The experiment the framework was designed for

RL cells (diffuse large B-cell lymphoma) were grown as six independent
cultures (one flask each) and treated for eight days, three with the EZH2
inhibitor CPI-169 and three with DMSO. From each culture, one aliquot was
labelled by antibody-guided proximity labelling (pA-APEX2) with an anti-EZH2
antibody and one with an IgG control: 12 samples in one TMT run. The primary
readout is the antibody-by-treatment interaction: how CPI-169 changes
labelling with EZH2 relative to IgG.

This is a split-plot design: treatment varies between cultures (n = 3 per
group), antibody within cultures. The interaction is a within-culture
contrast, so culture-to-culture variation cancels; the simple treatment
effects are between-culture contrasts.

Run-level SDRF values (TMTpro 16-plex, instrument, fractionation,
modifications, channel layout) are **assumptions** pending confirmation with
the mass spectrometry facility (`src/tmt_agents/sdrf_io.py`).

## Components

### 1. Pre-run metadata checks

- `sdrf_io.py` builds an SDRF from a sample sheet; it passes the official
  `sdrf-pipelines` validator (templates `ms-proteomics`, `cell-lines`).
- `rules.py` checks it against the expected design (`design.json`): unique
  channels and names, labels within the plex, factor levels, balance,
  run-level consistency, and one sample per antibody for every culture.
- `design_check.py` (LLM) drafts `design.json` from a free-text description,
  compares the SDRF with the description, and explains rule-check results.

**Benchmark** (`examples/benchmark/`): 1 clean SDRF and 16 single-error
corruptions, LLM run 3 times per file.

| Category | Example | sdrf-pipelines | rules.py | rules + LLM |
|---|---|---|---|---|
| A: counting/structure (9) | duplicate channel, missing sample, broken pairing | 1/9 | 9/9 | 9/9 |
| B: consistent but contradicts the description (6) | wrong cell line, enzyme, TMT reagent; treatment labels of two cultures swapped | 0/6 | 0/6 | 6/6 (3/3 runs each) |
| C: undetectable from the description (1) | two channels swapped | 0/1 | 0/1 | 0/1 |
| Clean SDRF | | no error | no error | no findings in 3/3 runs |

`sdrf-pipelines` checks format and ontology terms, not design, so this shows a
division of labour, not a better validator. All 10 further LLM findings were
checked by hand and were correct (`examples/benchmark/manual_review.md`).

### 2. Contrast drafting

`contrasts.py` builds a cell-means design matrix, the four simple effects and
the interaction, and labels each as within- or between-culture. Culture is a
blocking factor (`duplicateCorrelation` in limma), not a fixed effect,
because it is nested in treatment. The LLM proposes the primary contrast and
reference levels; code checks the proposal against `design.json`
(`examples/contrasts/`). The generated limma code has not been run on data.

### 3. Post-run QC on simulated data

`qc_simulate.py` simulates the 2 x 2 split-plot design with one planted
problem per scenario. `qc_metrics.py` computes channel metrics (loading,
correlation with same-antibody channels, PCA scores and their association
with each factor) and a paired-ratio slope per culture, which drops under
ratio compression and turns negative when a culture's two channels are
swapped. The LLM writes the report from the metrics alone (`qc_report.py`).

| Scenario | Threshold baseline | LLM (3 runs) |
|---|---|---|
| Clean | nothing flagged | no issues 3/3 |
| Low loading, ratio compression, outlier, label swap | channel flagged (no issue type) | correct type and channel 3/3 each |
| Lower loading in all CPI-169 channels | missed (no single outlier) | 3/3 |

Most planted problems are large; ratio compression and the treatment-wide
loading shift are the informative cases. All three compression reports gave
the direction of bias on the primary contrast; two also made an incorrect
statement about mechanism (`examples/qc/manual_review.md`).

### 4. Real quantms output (PXD000001)

quantms 1.10.0 (`test_tmt` profile) was run on PXD000001, a TMT6plex dataset
with four proteins spiked at known amounts into a bacterial background.
`quantms_qc.py` reads the MSstats input table and computes channel metrics and
spike-in ratio recovery.

- **Two nearly empty channels.** TMT127 and TMT129 had 1 and 4 of 468
  proteins quantified.
- **Cause.** The pipeline option `--reporter_mass_shift` was recorded in the
  run parameters but not passed to OpenMS `IsobaricWorkflow`, so the default
  reporter tolerance (0.002 Th) was used. Passing 0.01 Th through `ext.args`
  (`configs/`) recovered both channels (459-463 proteins in all channels).
  The IsobaricWorkflow log shows why: the 127 and 129 reporters are offset by
  about 6.3 mDa more than the other four channels, matching the 13C/15N
  reporter isotopologue difference
  ([McAlister et al. 2012](https://pubmed.ncbi.nlm.nih.gov/22880955/)) and
  consistent with older TMT6 reagents (lot not checked).
- **Ratio compression.** Pooled spike-in slope 0.78: a true 10-fold
  difference is measured as about 6-fold, after the default (not
  lot-specific) isotope correction.

Full record: `examples/quantms_pxd000001_investigation.md`.

**Blind LLM report** (`examples/real_qc_reports/`): given the metrics, SDRF,
parameters and quantification command but not the problem, 3/3 runs reported
ch2/ch4 as TMT127/TMT129 and ranked the reporter tolerance first; after the
fix, 3/3 reported only ratio compression. Two runs also proposed a global
calibration offset, which cannot explain a failure of two channels only.

### 5. Diagnose-rerun agent loop

`diagnose_loop.py` automates the investigation above. The model works through
five tools: `get_qc`, `get_run_config`, `compare_runs` (all computed or read
by code), `request_rerun` (one change to pipeline parameters or `ext.args`,
with a hypothesis and expected effect) and `finish`. Code validates every
rerun request (known parameters and processes, at most 3 reruns and 15 tool
calls), sends it to the analyst for approval, flags channels itself, and
checks the model's final status against those flags.

Reruns run on one of two backends:

- **Replay**: serves only the two recorded runs (default, and fixed via
  `ext.args`); anything else is refused. Used for repeated, auto-approved
  trials.
- **Live**: real `nextflow run bigbio/quantms -resume` from one launch folder,
  so only changed steps are recomputed. Each rerun was approved or refused by
  the analyst at the terminal.

| Start | Replay (3 runs each) | Live |
|---|---|---|
| Default run (ch2, ch4 empty) | 3/3 found the `ext.args` fix, "resolved" | 1/1 found it in one rerun (result from the Nextflow cache of the manual run) |
| Fixed run (control) | 3/3 no channel problem, compression "unresolved" | 2/2 the same |

The model's final status matched the code's flags in every run. Reviews:
`examples/diagnose_loop/`, `examples/diagnose_loop_live/` (each with a
`manual_review.md`); a pilot round that exposed a replay bug is in
`examples/diagnose_loop_pilot/`.

What the reviews showed:

- **Diagnosis.** Two of three replayed runs took the manual path (parameter
  first, no effect, then `ext.args`); two proposed the isotopologue offset,
  which no blind report had. All three also listed instrument calibration
  (ranked lower), which cannot explain a failure of two channels only.
- **Bad requests, and the approval gate.** In every control run, replayed
  or live, the model asked to revert the fix on weak reasoning. Where it was
  executed, ch2 and ch4 failed again and the model then kept the fix. In the
  last live run the analyst refused it, and the model did not ask again.
- **A second ignored option.** In quantms 1.10.0, `isotope_correction` has
  no effect unless `plex_corr_matrix_file` is also set. After the command
  stayed unchanged, the model inferred this and supplied the matrix.
- **Its limit.** Neither isotope correction nor `min_precursor_purity` 0.7
  changed any metric; the MSstats tables and reporter intensities were
  identical. The OpenMS source of the build used (IsobaricWorkflow
  3.6.0-pre, 2 July 2026) explains why: it always applies isotope
  correction with the default TMT6 matrix (the same matrix the model
  supplied), and it never applies the purity filter. The model correctly
  saw "no effect" but, like every report before it, assumed that correction
  was off, because that is what the pipeline parameter said.

## Repository layout

```
src/tmt_agents/   sdrf_io, rules, design_check, corruptions, benchmark,
                  contrasts, qc_simulate, qc_metrics, qc_report,
                  quantms_qc, run_qc_report, diagnose_loop
scripts/          command-line entry points (one per step)
data/             own_design/, corrupted_sdrf/, simulated_qc/, quantms_pxd000001/
examples/         outputs, benchmark results and manual reviews
configs/          Nextflow config used for the fixed quantms run
tests/            103 tests; none calls the API
```

## Reproduce

Requires [uv](https://docs.astral.sh/uv/). LLM steps need an Anthropic API key
in `.env` (`ANTHROPIC_API_KEY=...`); the model is set with `TMT_AGENTS_MODEL`
(results here: `claude-sonnet-5-5`).

```bash
uv sync
uv run pytest -q

# 1. Pre-run checks
uv run python scripts/make_own_sdrf.py
uv run python scripts/check_sdrf.py data/own_design/sdrf.tsv data/own_design/design.json
uv run parse_sdrf validate-sdrf -s data/own_design/sdrf.tsv -t ms-proteomics -t cell-lines --use_ols_cache_only
uv run python scripts/review_sdrf.py data/own_design examples/own_design_review.md
uv run python scripts/run_benchmark.py            # add --no-llm to skip API calls

# 2. Contrasts
uv run python scripts/make_contrasts.py data/own_design examples/contrasts

# 3. QC on simulated data
uv run python scripts/run_qc_benchmark.py         # add --no-llm to skip API calls

# 4. QC on real quantms output
uv run python scripts/check_quantms_output.py data/quantms_pxd000001/msstats_in_shift0.01.csv.gz examples/quantms_pxd000001_shift0.01
uv run python scripts/run_real_qc_report.py data/quantms_pxd000001 shift0.002 examples/real_qc_reports --runs 3

# 5. Agent loop, replay (--start shift0.01 for the control)
uv run python scripts/run_diagnose_loop.py data/quantms_pxd000001 examples/diagnose_loop --start shift0.002 --runs 3 --auto-approve
# live (Nextflow + Docker): launch from the folder of an earlier quantms run to reuse its cache;
# the config must not contain the ext.args fix
uv run python scripts/run_diagnose_loop.py data/quantms_pxd000001 examples/diagnose_loop_live --start shift0.002 \
  --live ~/quantms_test --nf-config ~/quantms_test/small_base.config \
  --nf-param root_folder=/home/ubuntu/pxd000001 --nf-param local_input_type=raw
```

The quantms run itself (Nextflow, Docker; about 25 min on 2 vCPU / 8 GB):

```bash
nextflow run bigbio/quantms -r 1.10.0 -profile test_tmt,docker \
  -c configs/quantms_reporter_shift_0.01.config --outdir results
```

## Limitations

- Benchmarks are small and were designed by the person who built the system;
  prompt rules were added after pilot runs, so final runs are not fully held
  out.
- LLM outputs vary; each benchmark used 3 runs. Classifications and main
  impact statements were reliable; secondary statements about mechanism were
  not always correct.
- The PXD000001 reports and the agent loop were tested on one dataset with a
  known fix: the prompts were written after the manual diagnosis, PXD000001
  is widely discussed, and replay can reach only two recorded runs. Only
  three live runs were made.
- Contrast drafting supports 2 x 2 designs with one within-unit factor; only
  the MSstats input table of quantms is read.

## Next steps

- Apply to the thesis data once available.
- Report to quantms: `reporter_mass_shift` is not passed to IsobaricWorkflow,
  and `isotope_correction` and `min_precursor_purity` do not control what it
  does.
- Give the agent the IsobaricWorkflow log as a tool (its calibration
  statistics show the 127/129 offset directly).
- Detection-strength curves (vary the size of planted problems), and an
  automatic check that every number in an LLM report appears in the metrics.

Developed with the help of an AI coding assistant (Claude). All runs,
benchmarks and manual reviews were carried out and checked by the author.
