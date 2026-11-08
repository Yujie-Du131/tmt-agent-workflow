# Diagnose-rerun loop (start shift0.002, run 3, model `claude-sonnet-5-5`)

**get_qc** `{"run_id": "run0"}`

```
Run run0 (first run)
Channel metrics (n_quantified = proteins quantified; raw_median = median log2 intensity; raw_median_z = robust z across channels; corr_to_others = correlation with the mean of the other channels, NaN if too few complete proteins):
     n_quantified  raw_median  raw_median_z  corr_to_others
ch1           465      20.447         0.405             NaN
ch2             1      11.363       -34.490             NaN
ch3           468      20.587         0.944             NaN
ch4             4      13.187       -27.485             NaN
ch5           468      20.264        -0.299             NaN
ch6           468      20.419         0.299             NaN

Flagged by code (n_quantified < 0.5 x median, or |raw_median_z| > 3.0): ['ch2', 'ch4']

Spike-in recovery (slope 1 = full recovery):
accession              protein  psms  expected_range_log2  slope
   P00924 sp|P00924|ENO1_YEAST    31                3.322  0.882
   P02769 sp|P02769|ALBU_BOVIN    31                3.322  0.740
   P00489 sp|P00489|PYGM_RABIT    48                1.000  0.753
   P62894  sp|P62894|CYC_BOVIN     3                1.000  1.156
Pooled spike-in slope: 0.82
```

**get_run_config** `{"run_id": "run0"}`

```
Run run0 (first run)
ext.args overrides: none

Pipeline parameters:
{
 "outdir": "results",
 "root_folder": "/home/ubuntu/pxd000001",
 "local_input_type": "raw",
 "database": "https://raw.githubusercontent.com/bigbio/quantms-test-datasets/quantms/testdata/tmt_ci/erwinia_carotovora.fasta",
 "id_only": false,
 "input": "https://raw.githubusercontent.com/bigbio/quantms-test-datasets/quantms/testdata/tmt_ci/PXD000001.sdrf.tsv",
 "validate_ontologies": true,
 "skip_ms_validation": false,
 "skip_factor_validation": true,
 "skip_experimental_design_validation": false,
 "use_ols_cache_only": true,
 "add_decoys": true,
 "skip_rescoring": false,
 "search_engines": "comet,msgf",
 "sage_processes": 1,
 "run_fdr_cutoff": 0.1,
 "protein_level_fdr_cutoff": 0.01,
 "psm_level_fdr_cutoff": 1.0,
 "fdr_conservative": true,
 "psm_clean": false,
 "decoydatabase_debug": 0,
 "pp_debug": 0,
 "iso_debug": 0,
 "db_debug": 0,
 "percolator_debug": 0,
 "onsite_debug": 0,
 "protein_inference_debug": 0,
 "plfq_debug": 0,
 "protein_quant_debug": 0,
 "decoy_string": "rev",
 "decoy_string_position": "prefix",
 "decoy_method": "reverse",
 "shuffle_max_attempts": 30,
 "shuffle_sequence_identity_threshold": 0.5,
 "openms_peakpicking": false,
 "peakpicking_inmemory": false,
 "peakpicking_ms_levels": null,
 "reindex_mzml": true,
 "mzml_statistics": false,
 "mzml_features": false,
 "isotope_correction": false,
 "plex_corr_matrix_file": null,
 "reference_channel": "126",
 "min_precursor_intensity": 1.0,
 "reporter_mass_shift": 0.002,
 "quant_activation_method": "HCD",
 "iso_normalization": false,
 "min_reporter_intensity": 0.0,
 "min_precursor_purity": 0.0,
 "precursor_isotope_deviation": 10.0,
 "met_excision": true,
 "num_enzyme_termini": "fully",
 "allowed_missed_cleavages": 2,
 "precursor_mass_tolerance": 5,
 "precursor_mass_tolerance_unit": "ppm",
 "variable_mods": "Oxidation (M)",
 "enable_mod_localization": false,
 "fragment_mass_tolerance": 0.03,
 "fragment_mass_tolerance_unit": "Da",
 "ms2_fragment_method": "HCD",
 "isotope_error_range": "0,1",
 "instrument": null,
 "protocol": "TMT",
 "min_precursor_charge": 2,
 "max_precursor_charge": 4,
 "min_peptide_length": 6,
 "max_peptide_length": 40,
 "num_hits": 1,
 "max_mods": 3,
 "min_peaks": 10,
 "ms2features_enable": false,
 "ms2features_model_dir": null,
 "ms2features_model": "generic",
 "ms2features_generators": "deeplc,alphapeptdeep",
 "ms2features_calibration": 0.15,
 "ms2features_tolerance": 0.05,
 "ms2features_tolerance_unit": "Da",
 "ms2features_best": true,
 "ms2features_force": false,
 "ms2features_modloss": false,
 "ms2features_snr": false,
 "ms2features_fine_tuning": false,
 "fine_tuning_sample_run": 1,
 "force_transfer_learning": false,
 "epoch_to_train_ms2": 20,
 "transfer_learning_test_ratio": 0.3,
 "ms2features_debug": false,
 "IL_equivalent": true,
 "unmatched_action": "warn",
 "export_decoy_psm": true,
 "train_FDR": 0.05,
 "test_FDR": 0.05,
 "fdr_level": "psm_level_fdrs",
 "klammer": false,
 "description_correct_feat
[...]
```

**request_rerun** `{"base_run": "run0", "param_changes": {}, "ext_args": {"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.01"}, "hypothesis": "The reporter-ion matching window (0.002 Da, and the param reporter_mass_shift is not visible in the command) is too tight for ch2 (127) and ch4 (129), so their reporters are missed in most spectra. Widening to 0.01 Da should recover them.", "expected_change": "ch2 and ch4 n_quantified rise to ~465 and raw_median to ~20; no channels flagged; the command gains the -extraction:reporter_mass_shift argument."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_done*: {"run_id": "run1", "note": "rerun of run0", "source": "replay of recorded run 'shift0.01'"}

```
Rerun finished as run1 (rerun of run0). Use get_qc or compare_runs.
```

**compare_runs** `{"run_a": "run0", "run_b": "run1"}`

```
run0 -> run1
            run0                      run1             
    n_quantified raw_median_z n_quantified raw_median_z
ch1          465        0.405          460        1.300
ch2            1      -34.490          459       -0.235
ch3          468        0.944          463        1.114
ch4            4      -27.485          461       -0.203
ch5          468       -0.299          463       -1.798
ch6          468        0.299          463        0.203

Flagged: run0=['ch2', 'ch4']; run1=none
Pooled spike-in slope: 0.82 -> 0.778
Changed parameters (old, new): none
IsobaricWorkflow command arguments: {'removed': [], 'added': ['-extraction:reporter_mass_shift', '0.01']}
Notes: run0: first run; run1: rerun of run0
```

**get_qc** `{"run_id": "run1"}`

```
Run run1 (rerun of run0)
Channel metrics (n_quantified = proteins quantified; raw_median = median log2 intensity; raw_median_z = robust z across channels; corr_to_others = correlation with the mean of the other channels, NaN if too few complete proteins):
     n_quantified  raw_median  raw_median_z  corr_to_others
ch1           460      20.750         1.300           0.999
ch2           459      20.602        -0.235           0.995
ch3           463      20.732         1.114           0.999
ch4           461      20.605        -0.203           0.997
ch5           463      20.451        -1.798           0.999
ch6           463      20.644         0.203           0.999

Flagged by code (n_quantified < 0.5 x median, or |raw_median_z| > 3.0): none

Spike-in recovery (slope 1 = full recovery):
accession              protein  psms  expected_range_log2  slope
   P00924 sp|P00924|ENO1_YEAST    32                3.322  0.798
   P02769 sp|P02769|ALBU_BOVIN    32                3.322  0.729
   P00489 sp|P00489|PYGM_RABIT    52                1.000  0.753
   P62894  sp|P62894|CYC_BOVIN     3                1.000  1.152
Pooled spike-in slope: 0.778
```

**finish** `{"status": "resolved", "final_run": "run1", "diagnosis": "Channels ch2 and ch4 (TMT 127 and 129) were almost empty in run0. Widening the reporter-ion matching window to 0.01 Da recovered them. This fits a window that was too tight, but I changed only that one argument, so I have not confirmed the cause. The reporter_mass_shift parameter (0.002) did not appear in the original command, so it was not clear it was being applied. Spike-in ratio compression remains: the pooled slope is about 0.78, and ENO1 and ALBU have slopes of about 0.8 and 0.73 against an expected range of 3.3 log2. This is typical of TMT ratio compression from co-isolation interference. The rerun does not fix it and I did not try to.", "evidence": "run0: ch2 n_quantified=1 (z=-34.5), ch4 n_quantified=4 (z=-27.5), flagged. run1, after adding -extraction:reporter_mass_shift 0.01: ch2=459, ch4=461, no channels flagged, all |z| < 1.8, corr_to_others 0.995-0.999. Pooled spike-in slope went from 0.82 to 0.778. The command diff showed only the added argument.", "remaining_issues": ["Spike-in recovery is compressed (pooled slope 0.78; ENO1 0.80, ALBU 0.73, PYGM 0.75). The pooled slope fell slightly from 0.82 to 0.778, and the rerun changed the PSM counts, so this may be run-to-run variation.", "ch5 has the lowest median (z=-1.8). It is within the threshold but may be worth a look.", "CYC_BOVIN has only 3 PSMs, so its slope of 1.15 is unreliable.", "isotope_correction is false and no plex_corr_matrix_file is set, so reporter impurities are uncorrected. This contributes to ratio compression and cross-channel leakage.", "The 0.01 Da window may be wider than needed, and I did not test a smaller value."], "next_steps": ["Set reporter_mass_shift explicitly in the pipeline config and check whether it was ever applied to the command. If it is not wired through, fix that rather than relying on ext.args.", "Enable isotope_correction with the kit's correction matrix and check whether the spike-in slope improves.", "Use min_precursor_purity (currently 0.0) to filter co-isolated precursors and test whether that raises the spike-in slope.", "Consider normalisation (iso_normalization is false) before comparing samples."]}`

```
Recorded.
```

## Conclusion (model)

- Status: resolved (final run: run1)
- Diagnosis: Channels ch2 and ch4 (TMT 127 and 129) were almost empty in run0. Widening the reporter-ion matching window to 0.01 Da recovered them. This fits a window that was too tight, but I changed only that one argument, so I have not confirmed the cause. The reporter_mass_shift parameter (0.002) did not appear in the original command, so it was not clear it was being applied. Spike-in ratio compression remains: the pooled slope is about 0.78, and ENO1 and ALBU have slopes of about 0.8 and 0.73 against an expected range of 3.3 log2. This is typical of TMT ratio compression from co-isolation interference. The rerun does not fix it and I did not try to.
- Evidence: run0: ch2 n_quantified=1 (z=-34.5), ch4 n_quantified=4 (z=-27.5), flagged. run1, after adding -extraction:reporter_mass_shift 0.01: ch2=459, ch4=461, no channels flagged, all |z| < 1.8, corr_to_others 0.995-0.999. Pooled spike-in slope went from 0.82 to 0.778. The command diff showed only the added argument.
- Remaining issues: ['Spike-in recovery is compressed (pooled slope 0.78; ENO1 0.80, ALBU 0.73, PYGM 0.75). The pooled slope fell slightly from 0.82 to 0.778, and the rerun changed the PSM counts, so this may be run-to-run variation.', 'ch5 has the lowest median (z=-1.8). It is within the threshold but may be worth a look.', 'CYC_BOVIN has only 3 PSMs, so its slope of 1.15 is unreliable.', 'isotope_correction is false and no plex_corr_matrix_file is set, so reporter impurities are uncorrected. This contributes to ratio compression and cross-channel leakage.', 'The 0.01 Da window may be wider than needed, and I did not test a smaller value.']
- Next steps: ['Set reporter_mass_shift explicitly in the pipeline config and check whether it was ever applied to the command. If it is not wired through, fix that rather than relying on ext.args.', "Enable isotope_correction with the kit's correction matrix and check whether the spike-in slope improves.", 'Use min_precursor_purity (currently 0.0) to filter co-isolated precursors and test whether that raises the spike-in slope.', 'Consider normalisation (iso_normalization is false) before comparing samples.']

## Check by code

```
{
 "flagged_run0": [
  "ch2",
  "ch4"
 ],
 "final_run": "run1",
 "flagged_final_run": [],
 "status_consistent": true,
 "conflict": null
}
```
