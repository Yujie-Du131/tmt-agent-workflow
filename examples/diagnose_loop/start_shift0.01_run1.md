# Diagnose-rerun loop (start shift0.01, run 1, model `claude-sonnet-5-5`)

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
ext.args overrides: {'ISOBARIC_WORKFLOW': '-extraction:reporter_mass_shift 0.01'}

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
 "fdr_level": "psm_l
[...]
```

**request_rerun** `{"base_run": "run0", "param_changes": {"isotope_correction": true}, "ext_args": {}, "hypothesis": "Spike-in ratios are compressed (pooled slope 0.778) because isotope impurity correction is disabled, so reporter-channel cross-talk flattens large ratios.", "expected_change": "Spike-in slopes move towards 1 (pooled >0.9) and the IsobaricWorkflow command gains an isotope-correction argument. Channel counts stay similar."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_unavailable*: {"reason": "Not available in replay mode: no recorded run changes ['isotope_correction']. This change would have to be run in live mode."}

```
Not available in replay mode: no recorded run changes ['isotope_correction']. This change would have to be run in live mode.
```

**request_rerun** `{"base_run": "run0", "param_changes": {"min_precursor_purity": 0.5}, "ext_args": {}, "hypothesis": "Ratio compression is caused by co-isolation interference; filtering low-purity precursors reduces it.", "expected_change": "Spike-in slopes rise toward 1 (pooled >0.9), fewer proteins quantified; command shows -extraction:min_precursor_purity 0.5."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_unavailable*: {"reason": "Not available in replay mode: no recorded run changes ['min_precursor_purity']. This change would have to be run in live mode."}

```
Not available in replay mode: no recorded run changes ['min_precursor_purity']. This change would have to be run in live mode.
```

**request_rerun** `{"base_run": "run0", "param_changes": {}, "ext_args": {"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.002"}, "hypothesis": "The ext.args override widens the reporter mass shift to 0.01 from the 0.002 param value; this might alter extraction and contribute to compression.", "expected_change": "Little change expected; if the window matters, slopes would move toward 1."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_done*: {"run_id": "run1", "note": "rerun of run0", "source": "replay of recorded run 'shift0.002'"}

```
Rerun finished as run1 (rerun of run0). Use get_qc or compare_runs.
```

**compare_runs** `{"run_a": "run0", "run_b": "run1"}`

```
run0 -> run1
            run0                                     run1                            
    n_quantified raw_median_z corr_to_others n_quantified raw_median_z corr_to_others
ch1          460        1.300          0.999          465        0.405            NaN
ch2          459       -0.235          0.995            1      -34.490            NaN
ch3          463        1.114          0.999          468        0.944            NaN
ch4          461       -0.203          0.997            4      -27.485            NaN
ch5          463       -1.798          0.999          468       -0.299            NaN
ch6          463        0.203          0.999          468        0.299            NaN

Flagged: run0=none; run1=['ch2', 'ch4']
Pooled spike-in slope: 0.778 -> 0.82
Changed parameters (old, new): none
IsobaricWorkflow command arguments: {'removed': ['-extraction:reporter_mass_shift', '0.01'], 'added': []}
Notes: run0: first run; run1: rerun of run0
```

**get_run_config** `{"run_id": "run1"}`

```
Run run1 (rerun of run0)
ext.args overrides: {'ISOBARIC_WORKFLOW': '-extraction:reporter_mass_shift 0.002'}

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
 "fdr_level": "
[...]
```

**get_qc** `{"run_id": "run1"}`

```
Run run1 (rerun of run0)
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

**finish** `{"status": "unresolved", "final_run": "run0", "diagnosis": "run0 has no code-flagged channels, but the spike-in ratios are compressed. The pooled slope is 0.778, and the large 10x spike-ins (ENO1, ALBU) recover only 0.73\u20130.80. I could not test the likely causes: isotope-impurity correction is off (isotope_correction=false, no correction matrix), and co-isolation interference is unfiltered (min_precursor_purity=0.0). Both reruns were refused as unavailable in replay mode. These causes are my inference. The metrics show only the compression. The one rerun that ran tightened the reporter window, and it made things worse. Without -extraction:reporter_mass_shift 0.01, ch2 and ch4 collapsed to 1 and 4 proteins. The pooled slope barely moved (0.778 to 0.82). The wider window in run0 is therefore needed for those channels and should be kept. The compression is a separate problem that is still open.", "evidence": "run0: no channels flagged, n_quantified 459\u2013463 per channel, pooled slope 0.778 (ENO1 0.798, ALBU 0.729, PYGM 0.753, CYC 1.152 from only 3 PSMs). run0 config: isotope_correction=false, min_precursor_purity=0.0, ext.args '-extraction:reporter_mass_shift 0.01'. Requests to change isotope_correction and to set min_precursor_purity 0.5 were both 'Not available in replay mode'. run1 (reporter_mass_shift 0.002): ch2 n_quantified 1 and ch4 n_quantified 4, both flagged, pooled slope 0.82. compare_runs shows the command lost '-extraction:reporter_mass_shift 0.01' and gained no replacement argument. The run1 config still lists ext.args with 0.002 although the command contains no such flag.", "remaining_issues": ["Spike-in ratio compression (pooled slope about 0.78) is unexplained and unresolved.", "Isotope-impurity correction is not applied, and no plex_corr_matrix_file is given.", "No precursor-purity filter is applied, so co-isolation interference is possible.", "In run1 the ext.args 0.002 did not appear in the command, so the reporter_mass_shift pipeline parameter may not reach IsobaricWorkflow. The reason ch2 and ch4 vanish at the default window is not confirmed.", "The CYC_BOVIN slope of 1.15 rests on only 3 PSMs and is unreliable.", "corr_to_others is NaN in run1 because ch2 and ch4 are almost empty."], "next_steps": ["Keep '-extraction:reporter_mass_shift 0.01' on the IsobaricWorkflow command, or check why ch2 and ch4 need it.", "In live mode, rerun with isotope_correction=true and the kit lot's correction matrix in plex_corr_matrix_file. Expect the pooled slope to rise toward 1 and the command to gain a correction argument.", "Rerun with min_precursor_purity around 0.5 to test co-isolation interference. Expect a higher slope and fewer quantified proteins.", "Change one thing at a time, and confirm each change shows up in the IsobaricWorkflow command with compare_runs."]}`

```
Recorded.
```

## Conclusion (model)

- Status: unresolved (final run: run0)
- Diagnosis: run0 has no code-flagged channels, but the spike-in ratios are compressed. The pooled slope is 0.778, and the large 10x spike-ins (ENO1, ALBU) recover only 0.73–0.80. I could not test the likely causes: isotope-impurity correction is off (isotope_correction=false, no correction matrix), and co-isolation interference is unfiltered (min_precursor_purity=0.0). Both reruns were refused as unavailable in replay mode. These causes are my inference. The metrics show only the compression. The one rerun that ran tightened the reporter window, and it made things worse. Without -extraction:reporter_mass_shift 0.01, ch2 and ch4 collapsed to 1 and 4 proteins. The pooled slope barely moved (0.778 to 0.82). The wider window in run0 is therefore needed for those channels and should be kept. The compression is a separate problem that is still open.
- Evidence: run0: no channels flagged, n_quantified 459–463 per channel, pooled slope 0.778 (ENO1 0.798, ALBU 0.729, PYGM 0.753, CYC 1.152 from only 3 PSMs). run0 config: isotope_correction=false, min_precursor_purity=0.0, ext.args '-extraction:reporter_mass_shift 0.01'. Requests to change isotope_correction and to set min_precursor_purity 0.5 were both 'Not available in replay mode'. run1 (reporter_mass_shift 0.002): ch2 n_quantified 1 and ch4 n_quantified 4, both flagged, pooled slope 0.82. compare_runs shows the command lost '-extraction:reporter_mass_shift 0.01' and gained no replacement argument. The run1 config still lists ext.args with 0.002 although the command contains no such flag.
- Remaining issues: ['Spike-in ratio compression (pooled slope about 0.78) is unexplained and unresolved.', 'Isotope-impurity correction is not applied, and no plex_corr_matrix_file is given.', 'No precursor-purity filter is applied, so co-isolation interference is possible.', 'In run1 the ext.args 0.002 did not appear in the command, so the reporter_mass_shift pipeline parameter may not reach IsobaricWorkflow. The reason ch2 and ch4 vanish at the default window is not confirmed.', 'The CYC_BOVIN slope of 1.15 rests on only 3 PSMs and is unreliable.', 'corr_to_others is NaN in run1 because ch2 and ch4 are almost empty.']
- Next steps: ["Keep '-extraction:reporter_mass_shift 0.01' on the IsobaricWorkflow command, or check why ch2 and ch4 need it.", "In live mode, rerun with isotope_correction=true and the kit lot's correction matrix in plex_corr_matrix_file. Expect the pooled slope to rise toward 1 and the command to gain a correction argument.", 'Rerun with min_precursor_purity around 0.5 to test co-isolation interference. Expect a higher slope and fewer quantified proteins.', 'Change one thing at a time, and confirm each change shows up in the IsobaricWorkflow command with compare_runs.']

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
