# tmt-agent-workflow

LLM-assisted checks around a quantms/Nextflow TMT proteomics workflow: metadata
validation before a run, contrast drafting for the analyst to confirm, QC
reports written from computed metrics (not plots) after a run, and an agent
loop that diagnoses a QC problem, requests reruns with changed settings
(approved by the analyst) and compares the runs.

Deterministic code does everything that can be counted or matched. The LLM is
used only where code cannot help: comparing metadata with the researcher's
free-text description of the experiment, explaining problems, and turning QC
metrics into a report with likely causes and checks. The agent loop is the
one place where the model chooses the next action, because after a QC problem
the next step depends on interpreting the result. Every LLM output is a draft
for the analyst to confirm.

## Status: what was tested on what

The framework was designed for my MSc thesis experiment (EZH2 proximity
proteomics in RL cells, below). MS data were still pending at graduation, so
no component has been run on my own MS data.

| Component | Tested on |
|---|---|
| Pre-run SDRF checks | SDRF of my own experimental design, and 16 deliberately corrupted copies |
| Contrast drafting | My own experimental design |
| Post-run QC report | Simulated intensities with planted problems; real quantms output for the public dataset PXD000001 |
| Diagnose-rerun agent loop | Replay of the two recorded PXD000001 quantms runs (LLM: 3 runs from each start; scripted model in tests). Live reruns not executed. |

## The experiment the framework was designed for

RL cells (diffuse large B-cell lymphoma) were grown as six independent
cultures (one flask each) and treated for eight days, three with the EZH2
inhibitor CPI-169 and three with DMSO.
From each culture, one aliquot was labelled by antibody-guided proximity
labelling (pA-APEX2) with an anti-EZH2 antibody and one with an IgG control,
giving 12 samples in one TMT run. The primary comparison is the
antibody-by-treatment interaction: how CPI-169 changes labelling with EZH2
relative to IgG.

This is a split-plot design. Treatment varies between cultures (n = 3 per
group); antibody varies within cultures. The interaction is a within-culture
contrast, so culture-to-culture variation cancels; the simple treatment
effects are between-culture contrasts.

Run-level SDRF values (TMTpro 16-plex, instrument, fractionation,
modifications, channel layout) are **assumptions** pending confirmation with
the mass spectrometry facility; see `src/tmt_agents/sdrf_io.py`.

## Components

### 1. Pre-run metadata checks

- `sdrf_io.py`: builds an SDRF from a simple sample sheet. The generated SDRF
  passes the official `sdrf-pipelines` validator (templates `ms-proteomics`
  and `cell-lines`).
- `rules.py`: deterministic checks against an expected design (`design.json`):
  unique channels and sample names, labels within the plex, factor levels,
  balance, run-level consistency and, for paired designs, that every culture
  has one sample per antibody.
- `design_check.py` (LLM): drafts `design.json` from a free-text description,
  compares the SDRF with the description, and explains rule-check results.

**Benchmark** (`examples/benchmark/`): 1 clean SDRF and 16 single-error
corruptions; LLM run 3 times per file.

| Category | Example | sdrf-pipelines | rules.py | rules + LLM |
|---|---|---|---|---|
| A: counting/structure (9) | duplicate channel, missing sample, broken pairing | 1/9 | 9/9 | 9/9 |
| B: consistent but contradicts the description (6) | wrong cell line, enzyme, TMT reagent; treatment labels of two cultures swapped | 0/6 | 0/6 | 6/6 (3/3 runs each) |
| C: undetectable from the description (1) | two channels swapped | 0/1 | 0/1 | 0/1 |
| Clean SDRF | | no error | no error | no findings in 3/3 runs |

`sdrf-pipelines` checks format and ontology terms, not experimental design,
so the comparison shows a division of labour, not a better validator. All 10
LLM findings outside the corrupted column were reviewed by hand and were
correct (`examples/benchmark/manual_review.md`). After a pilot run, one rule
was added to the prompt to stop comments on formatting conventions.

### 2. Contrast drafting

`contrasts.py` builds a cell-means design matrix, the four simple effects and
the interaction, and classifies each contrast as within- or between-culture.
Culture is a blocking factor (`duplicateCorrelation` in limma) rather than a
fixed effect, because culture is nested in treatment. The LLM proposes which
contrast is primary and which levels are references; code checks the proposal
against `design.json`. Output: `examples/contrasts/`. The generated limma code
has not been run on data.

### 3. Post-run QC on simulated data

`qc_simulate.py` simulates protein intensities for the 2 x 2 split-plot design
with one planted problem per scenario; `qc_metrics.py` computes channel
metrics (loading, correlation with same-antibody channels, PCA scores and
their association with each factor), including a paired-ratio slope for each
culture (log2 EZH2/IgG regressed on the other cultures), which drops under
ratio compression and turns negative when the two channels of a culture are
swapped. The LLM writes the report from the metrics alone (`qc_report.py`).

| Scenario | Threshold baseline | LLM (3 runs) |
|---|---|---|
| Clean | nothing flagged | no issues 3/3 |
| Low loading, ratio compression, outlier, label swap | channel flagged (no issue type) | correct type and channel 3/3 each |
| Lower loading in all CPI-169 channels | missed (no single outlier) | 3/3 |

The planted problems in four scenarios are large; ratio compression and the
treatment-wide loading shift are the informative cases. On review, all three
compression reports stated the direction of bias on the primary contrast
(towards an apparent loss of EZH2-proximal proteins); two of three contained
an incorrect secondary statement about mechanism
(`examples/qc/manual_review.md`). One prompt rule was added after a pilot run.

### 4. Real quantms output (PXD000001)

quantms 1.10.0 (`test_tmt` profile) was run on PXD000001, a TMT6plex dataset
with four proteins spiked at known amounts into a bacterial background.
`quantms_qc.py` reads the MSstats input table and computes channel metrics and
spike-in ratio recovery.

- **QC found two nearly empty channels.** Channels 2 and 4 (TMT127, TMT129)
  had 1 and 4 of 468 proteins quantified (robust z of median -34 and -27).
- **Diagnosis.** The default reporter-ion extraction tolerance (0.002 Th) was
  used. The pipeline option `--reporter_mass_shift` was recorded in the run
  parameters but not passed to the OpenMS `IsobaricWorkflow` step. Passing
  the option through `ext.args` (`configs/`) with 0.01 Th recovered both
  channels (459-463 proteins in all channels). The pattern is consistent with
  older TMT6 reagents whose 127/129 reporter masses differ slightly from the
  expected values; the reagent masses were not checked against a primary
  source.
- **Ratio compression.** Pooled spike-in slope 0.78 (1 = full recovery): a
  true 10-fold difference was measured as about 6-fold. Isotope correction was
  off in this run.

Full record: `examples/quantms_pxd000001_investigation.md`.

**Blind LLM report** (`examples/real_qc_reports/`): the LLM received the
metrics, SDRF, pipeline parameters and the quantification command, without
being told what was wrong. Before the fix, 3/3 runs reported ch2 and ch4,
mapped them to TMT127/TMT129 and ranked reporter-ion extraction tolerance
first. After the fix (control), 3/3 runs reported only ratio compression; one
also noticed the mismatch between the recorded parameter and the command.
Weaknesses found on review: two runs proposed a global calibration offset,
which cannot explain a failure of two channels only, and no run proposed the
reagent explanation. The prompt was written after the diagnosis, and the
dataset is widely discussed, so prior knowledge cannot be ruled out.

### 5. Diagnose-rerun agent loop

`diagnose_loop.py` automates the investigation in section 4. The model works
through five tools: `get_qc` and `get_run_config` (metrics, flagged channels,
parameters and the IsobaricWorkflow command, all computed or read by code),
`request_rerun` (one change: pipeline parameters and/or `ext.args` for a
process, with a stated hypothesis and expected effect), `compare_runs`
(per-channel changes, flags, changed parameters and changed command
arguments) and `finish`.

Code keeps control of everything that can be checked:

- Each rerun request is validated (known parameter names and process names,
  at most 3 reruns, at most 15 tool calls) and then needs the analyst's
  approval. A refused or unavailable rerun is returned to the model as
  information.
- Channels are flagged by code (fewer than half the median number of
  quantified proteins, or |robust z of median| > 3).
- When the model finishes, its status is checked against these flags: for
  example, "resolved" while channels are still flagged, or without any
  rerun, is recorded as a conflict.

Reruns are executed by one of two backends:

- **Replay** (used here): returns only runs that were actually executed. For
  PXD000001 these are the default run and the run with
  `-extraction:reporter_mass_shift 0.01` passed through `ext.args`. Changing
  only the `reporter_mass_shift` pipeline parameter returns the default run
  again, with the IsobaricWorkflow command unchanged, as observed in quantms
  1.10.0. Any other request is refused as not available in replay mode.
  File names and output folders that would hint at the fix are not shown to
  the model.
- **Nextflow** (live): every run, including the first, is a real
  `nextflow run bigbio/quantms -r 1.10.0 -resume` from one launch folder,
  with its own output folder, an `ext.args` config and the parameter
  overrides accumulated from the base run, so only steps whose inputs
  changed are rerun. In quantms 1.10.0, `isotope_correction` has an effect
  only when `plex_corr_matrix_file` is also set (checked in the module
  source); quantms's bundled correction matrices are copied into the launch
  folder and listed for the model. Tested against a fake `nextflow` in the
  tests; not yet run for real.

The tests drive the loop with a scripted model through the
manual path of section 4 (the parameter change has no effect; the `ext.args`
change clears both flagged channels) and through refused, invalid,
unavailable and over-budget requests, and status conflicts.

**LLM runs** (`examples/diagnose_loop/`, 3 runs from each start, reruns
auto-approved):

| Start | Outcome | Reruns | Code check |
|---|---|---|---|
| Default run (ch2, ch4 nearly empty) | 3/3 found the `ext.args` fix and finished "resolved"; 2/3 took the manual path (parameter first, no effect, then `ext.args`) | 1-2 | consistent 3/3 |
| Fixed run (control) | 3/3 reported no channel problem and left the ratio compression unresolved (proposed reruns not available in replay) | 1 served | consistent 3/3 |

On review (`examples/diagnose_loop/manual_review.md`):

- From the default run, two runs proposed that the 127/129 reporters are
  offset by an isotopologue mass difference, which matches the reagent
  explanation above; none of the blind QC reports had. All three also kept
  instrument calibration as a candidate, which cannot explain a failure of
  two channels only.
- All three control runs asked to revert the `ext.args` override on weak
  reasoning, which broke ch2 and ch4 again. All three then concluded that
  the override is needed and named the fixed run as final. With live
  reruns, the approval gate is where such a request would be stopped.
- A pilot round (`examples/diagnose_loop_pilot/`) exposed a replay bug,
  fixed before these runs. One replay artefact found in these runs (an
  explicit default argument missing from the replayed command) affected one
  remaining-issue statement and was fixed afterwards.

## Repository layout

```
src/tmt_agents/   sdrf_io, rules, design_check, corruptions, benchmark,
                  contrasts, qc_simulate, qc_metrics, qc_report,
                  quantms_qc, run_qc_report, diagnose_loop
scripts/          command-line entry points (one per step)
data/             own_design/, corrupted_sdrf/, simulated_qc/, quantms_pxd000001/
examples/         outputs, benchmark results and manual reviews
configs/          Nextflow config used for the fixed quantms run
tests/            102 tests; none calls the API
```

## Reproduce

Requires [uv](https://docs.astral.sh/uv/). LLM steps need an Anthropic API key
in `.env` (`ANTHROPIC_API_KEY=...`); the model can be set with
`TMT_AGENTS_MODEL` (results here: `claude-sonnet-5-5`).

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

# 5. Diagnose-rerun loop (replay); without --auto-approve each rerun is approved at the terminal
uv run python scripts/run_diagnose_loop.py data/quantms_pxd000001 examples/diagnose_loop --start shift0.002 --runs 3 --auto-approve
uv run python scripts/run_diagnose_loop.py data/quantms_pxd000001 examples/diagnose_loop --start shift0.01 --runs 3 --auto-approve
# live (Nextflow + Docker), launched from the folder of an earlier quantms run to reuse its cache
uv run python scripts/run_diagnose_loop.py data/quantms_pxd000001 examples/diagnose_loop_live --start shift0.002 \
  --live ~/quantms_test --nf-config ~/quantms_test/small.config --nf-param root_folder=/home/ubuntu/pxd000001 --nf-param local_input_type=raw
```

The quantms run itself (Nextflow, Docker; about 25 min on 2 vCPU / 8 GB):

```bash
nextflow run bigbio/quantms -r 1.10.0 -profile test_tmt,docker \
  -c configs/quantms_reporter_shift_0.01.config --outdir results
```

## Limitations

- Benchmarks are small and were designed by the same person who built the
  system; two prompt rules were added after pilot runs, so the final runs are
  not fully held out.
- LLM outputs vary between runs; each benchmark used 3 runs. Classifications
  and main impact statements were reliable; secondary mechanistic statements
  were not always correct.
- Contrast drafting supports 2 x 2 designs with one within-unit factor.
- quantms 1.10.0 also writes results in the qpx format; only the MSstats
  input table is read.
- In replay mode the agent loop can reach only two recorded runs, so it
  tests whether the model finds and verifies the known fix, not open-ended
  troubleshooting. Its system prompt was written after the manual
  diagnosis, and reruns in the LLM runs were auto-approved. The live
  Nextflow backend has not been run.

## Next steps

- Run the agent loop with the live Nextflow backend, starting with the ratio
  compression reruns it proposed (isotope correction, precursor purity).
- Apply to the thesis data once available.
- Detection-strength curves (vary the size of planted problems).
- An automatic check that every number quoted in an LLM report appears in the
  metrics.
- Report the parameter-passing issue to quantms.

Developed with the help of an AI coding assistant (Claude). All runs,
benchmarks and manual reviews were carried out and checked by the author.
