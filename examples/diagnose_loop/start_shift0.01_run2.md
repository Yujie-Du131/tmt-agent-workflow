# Diagnose-rerun loop (start shift0.01, run 2, model `claude-sonnet-5-5`)

**get_qc** `{"run_id": "run0"}`

```
Run run0 (first run)
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

**request_rerun** `{"base_run": "run0", "param_changes": {"min_precursor_purity": 0.6}, "ext_args": {}, "hypothesis": "Ratio compression (pooled spike-in slope 0.778, no channel flagged) is caused by co-isolation interference, since min_precursor_purity=0.0 accepts all spectra. Filtering low-purity precursors should reduce it.", "expected_change": "Pooled spike-in slope rises toward 1 (e.g. >0.85); fewer proteins quantified; command shows -extraction:min_precursor_purity 0.6."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_unavailable*: {"reason": "Not available in replay mode: no recorded run changes ['min_precursor_purity']. This change would have to be run in live mode."}

```
Not available in replay mode: no recorded run changes ['min_precursor_purity']. This change would have to be run in live mode.
```

**request_rerun** `{"base_run": "run0", "param_changes": {"isotope_correction": true}, "ext_args": {}, "hypothesis": "Ratio compression is due to uncorrected TMT isotope impurity cross-talk between channels (isotope_correction=false).", "expected_change": "Pooled spike-in slope rises toward 1, mostly for the 10x spike-ins; the command should change to include a correction option."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_unavailable*: {"reason": "Not available in replay mode: no recorded run changes ['isotope_correction']. This change would have to be run in live mode."}

```
Not available in replay mode: no recorded run changes ['isotope_correction']. This change would have to be run in live mode.
```

**request_rerun** `{"base_run": "run0", "param_changes": {}, "ext_args": {"ISOBARIC_WORKFLOW": "-extraction:min_precursor_purity 0.6"}, "hypothesis": "Ratio compression is caused by co-isolation interference; filtering by precursor purity should reduce it.", "expected_change": "Pooled spike-in slope rises toward 1; fewer proteins quantified."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_unavailable*: {"reason": "Not available in replay mode: the resulting IsobaricWorkflow command (extra arguments: '-extraction:min_precursor_purity 0.6') matches no recorded run. This change would have to be run in live mode."}

```
Not available in replay mode: the resulting IsobaricWorkflow command (extra arguments: '-extraction:min_precursor_purity 0.6') matches no recorded run. This change would have to be run in live mode.
```

**finish** `{"status": "unresolved", "final_run": "run0", "diagnosis": "No channel is flagged, but the spike-in ratios are compressed: the pooled slope is 0.778 against an ideal of 1. I could not test the cause because all three reruns I requested were unavailable in replay mode. The most likely cause is co-isolation interference, because min_precursor_purity is 0.0, so no spectra are filtered by purity. Uncorrected TMT isotope impurity is the second candidate, because isotope_correction is false. Both explanations are inferences from the parameters and the command. Neither has been tested.", "evidence": "get_qc: flagged channels none. The raw_median_z values range from -1.80 to 1.30. n_quantified is 459\u2013463 in every channel. corr_to_others is 0.995\u20130.999. Spike-in slopes: ENO1 0.798, ALBU 0.729, PYGM 0.753, CYC 1.152 (only 3 PSMs). Pooled slope 0.778. get_run_config: min_precursor_purity 0.0, isotope_correction false, plex_corr_matrix_file null, iso_normalization false, no ext.args overrides. Reruns for min_precursor_purity=0.6 (as a parameter and as ext_args) and isotope_correction=true were all refused as \"Not available in replay mode\".", "remaining_issues": ["Ratio compression is about 20-27% for ENO1, ALBU and PYGM (slopes 0.73\u20130.80). The cause is not confirmed.", "The CYC slope of 1.152 rests on only 3 PSMs and is unreliable.", "The IsobaricWorkflow command contains -extraction:reporter_mass_shift 0.01, but the pipeline parameter says 0.002. Check where the 0.01 comes from. I don't expect it to explain the compression, because the TMT reporter channels are about 1 Da apart.", "The command has no isotope-correction option and no correction matrix is supplied. Normalization is off (iso_normalization false), so the channel medians are raw."], "next_steps": ["In live mode, rerun with min_precursor_purity around 0.6 and check that the command contains -extraction:min_precursor_purity 0.6. Expect the pooled slope to rise toward 1 and fewer proteins to be quantified.", "Separately, rerun with isotope_correction=true or a plex_corr_matrix_file using the lot-specific TMT6plex impurities. Use compare_runs to confirm the command actually changes.", "Compare the pooled slope across runs, and the 10x spike-ins (ENO1, ALBU) against the 2x spike-ins (PYGM, CYC). Impurity cross-talk should affect the 10x spike-ins more. Interference should compress all ratios.", "Interpret fold changes with caution until this is resolved, because dynamic range is underestimated."]}`

```
Recorded.
```

## Conclusion (model)

- Status: unresolved (final run: run0)
- Diagnosis: No channel is flagged, but the spike-in ratios are compressed: the pooled slope is 0.778 against an ideal of 1. I could not test the cause because all three reruns I requested were unavailable in replay mode. The most likely cause is co-isolation interference, because min_precursor_purity is 0.0, so no spectra are filtered by purity. Uncorrected TMT isotope impurity is the second candidate, because isotope_correction is false. Both explanations are inferences from the parameters and the command. Neither has been tested.
- Evidence: get_qc: flagged channels none. The raw_median_z values range from -1.80 to 1.30. n_quantified is 459–463 in every channel. corr_to_others is 0.995–0.999. Spike-in slopes: ENO1 0.798, ALBU 0.729, PYGM 0.753, CYC 1.152 (only 3 PSMs). Pooled slope 0.778. get_run_config: min_precursor_purity 0.0, isotope_correction false, plex_corr_matrix_file null, iso_normalization false, no ext.args overrides. Reruns for min_precursor_purity=0.6 (as a parameter and as ext_args) and isotope_correction=true were all refused as "Not available in replay mode".
- Remaining issues: ['Ratio compression is about 20-27% for ENO1, ALBU and PYGM (slopes 0.73–0.80). The cause is not confirmed.', 'The CYC slope of 1.152 rests on only 3 PSMs and is unreliable.', "The IsobaricWorkflow command contains -extraction:reporter_mass_shift 0.01, but the pipeline parameter says 0.002. Check where the 0.01 comes from. I don't expect it to explain the compression, because the TMT reporter channels are about 1 Da apart.", 'The command has no isotope-correction option and no correction matrix is supplied. Normalization is off (iso_normalization false), so the channel medians are raw.']
- Next steps: ['In live mode, rerun with min_precursor_purity around 0.6 and check that the command contains -extraction:min_precursor_purity 0.6. Expect the pooled slope to rise toward 1 and fewer proteins to be quantified.', 'Separately, rerun with isotope_correction=true or a plex_corr_matrix_file using the lot-specific TMT6plex impurities. Use compare_runs to confirm the command actually changes.', 'Compare the pooled slope across runs, and the 10x spike-ins (ENO1, ALBU) against the 2x spike-ins (PYGM, CYC). Impurity cross-talk should affect the 10x spike-ins more. Interference should compress all ratios.', 'Interpret fold changes with caution until this is resolved, because dynamic range is underestimated.']

## Check by code

```
{
 "flagged_run0": [],
 "final_run": "run0",
 "flagged_final_run": [],
 "status_consistent": true,
 "conflict": null
}
```
