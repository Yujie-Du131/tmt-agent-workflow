# Diagnose-rerun loop (start shift0.01, run 3, model `claude-sonnet-5-5`)

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

**request_rerun** `{"base_run": "run0", "param_changes": {"min_precursor_purity": 0.5}, "ext_args": {}, "hypothesis": "Spike-in ratio compression (pooled slope 0.778, ENO1/ALBU about 0.73-0.80 vs expected 1.0) is caused by co-isolated precursor interference, since min_precursor_purity is 0.0 and nothing is filtered. A purity filter of 0.5 should remove impure MS2 spectra.", "expected_change": "Pooled spike-in slope rises toward 1 (e.g. >0.85). Fewer proteins quantified per channel, but no channel should be flagged. The command should show -extraction:min_precursor_purity 0.5."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_unavailable*: {"reason": "Not available in replay mode: no recorded run changes ['min_precursor_purity']. This change would have to be run in live mode."}

```
Not available in replay mode: no recorded run changes ['min_precursor_purity']. This change would have to be run in live mode.
```

**request_rerun** `{"base_run": "run0", "param_changes": {}, "ext_args": {"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.002"}, "hypothesis": "The ext.args override sets reporter_mass_shift to 0.01 (5x the 0.002 default in params), widening the reporter extraction window and potentially picking up neighbouring signals/ compressing ratios. Reverting to 0.002 tests this.", "expected_change": "Pooled spike-in slope increases modestly toward 1; command shows reporter_mass_shift 0.002 instead of 0.01."}`

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

**finish** `{"status": "unresolved", "final_run": "run0", "diagnosis": "run0 has no flagged channels. The remaining problem is ratio compression in the spike-ins: the pooled slope is 0.778, where 1 means full recovery. I suspect co-isolation interference and no isotope-impurity correction, but I could not test either. The one rerun I could run did not fix compression and showed that the ext.args override `-extraction:reporter_mass_shift 0.01` is needed. With the default 0.002 window, channels ch2 and ch4 (127 and 129 in the 6-plex) lost nearly all their quantification. This is inferred from the rerun, not from a direct check of the reporter masses. Keep the 0.01 override. The compression is probably not caused by the mass window.", "evidence": "run0: all 6 channels have 459\u2013463 proteins quantified, |raw_median_z| \u2264 1.8, and nothing flagged. Pooled spike-in slope is 0.778 (ENO1 0.798, ALBU 0.729, PYGM 0.753, CYC 1.152). run0 config has min_precursor_purity 0.0 and isotope_correction false, and no correction matrix is passed to the command. Replay refused the min_precursor_purity 0.5 rerun (\"Not available in replay mode\"). run1 reverted reporter_mass_shift to 0.002. compare_runs shows only that argument removed. ch2 fell from 459 to 1 protein, ch4 from 461 to 4, and both were flagged (z = -34.5 and -27.5). Pooled slope went from 0.778 to 0.82, but that comes from a data set with two channels missing, so it is not a real improvement.", "remaining_issues": ["Spike-in ratio compression persists (pooled slope 0.78; ALBU 0.73, PYGM 0.75). The cause is not confirmed.", "Cause of the ch2/ch4 loss at the 0.002 window is not confirmed. It may be a reporter m/z offset or calibration issue, and 0.01 Da is a workaround.", "The reporter_mass_shift param (0.002) disagrees with the ext.args override (0.01), which is confusing for provenance.", "CYC_BOVIN has only 3 PSMs, so its slope of 1.152 is not reliable.", "corr_to_others is NaN in run1 because ch2 and ch4 have too few complete proteins."], "next_steps": ["Run live with min_precursor_purity around 0.5 to test co-isolation interference. Expect the pooled slope to rise and the protein count to fall.", "Provide the TMT6plex isotope-impurity matrix via plex_corr_matrix_file and set isotope_correction true. Expect the slope to improve a little.", "Check the reporter ion m/z offsets for 127 and 129 in the raw or mzML data to explain why 0.002 Da fails, and document the 0.01 override deliberately.", "Consider whether MS2-level quantification is limited by compression. MS3 or SPS acquisition would avoid it but needs different data.", "Add more spike-in proteins with more PSMs to get a more robust slope estimate."]}`

```
Recorded.
```

## Conclusion (model)

- Status: unresolved (final run: run0)
- Diagnosis: run0 has no flagged channels. The remaining problem is ratio compression in the spike-ins: the pooled slope is 0.778, where 1 means full recovery. I suspect co-isolation interference and no isotope-impurity correction, but I could not test either. The one rerun I could run did not fix compression and showed that the ext.args override `-extraction:reporter_mass_shift 0.01` is needed. With the default 0.002 window, channels ch2 and ch4 (127 and 129 in the 6-plex) lost nearly all their quantification. This is inferred from the rerun, not from a direct check of the reporter masses. Keep the 0.01 override. The compression is probably not caused by the mass window.
- Evidence: run0: all 6 channels have 459–463 proteins quantified, |raw_median_z| ≤ 1.8, and nothing flagged. Pooled spike-in slope is 0.778 (ENO1 0.798, ALBU 0.729, PYGM 0.753, CYC 1.152). run0 config has min_precursor_purity 0.0 and isotope_correction false, and no correction matrix is passed to the command. Replay refused the min_precursor_purity 0.5 rerun ("Not available in replay mode"). run1 reverted reporter_mass_shift to 0.002. compare_runs shows only that argument removed. ch2 fell from 459 to 1 protein, ch4 from 461 to 4, and both were flagged (z = -34.5 and -27.5). Pooled slope went from 0.778 to 0.82, but that comes from a data set with two channels missing, so it is not a real improvement.
- Remaining issues: ['Spike-in ratio compression persists (pooled slope 0.78; ALBU 0.73, PYGM 0.75). The cause is not confirmed.', 'Cause of the ch2/ch4 loss at the 0.002 window is not confirmed. It may be a reporter m/z offset or calibration issue, and 0.01 Da is a workaround.', 'The reporter_mass_shift param (0.002) disagrees with the ext.args override (0.01), which is confusing for provenance.', 'CYC_BOVIN has only 3 PSMs, so its slope of 1.152 is not reliable.', 'corr_to_others is NaN in run1 because ch2 and ch4 have too few complete proteins.']
- Next steps: ['Run live with min_precursor_purity around 0.5 to test co-isolation interference. Expect the pooled slope to rise and the protein count to fall.', 'Provide the TMT6plex isotope-impurity matrix via plex_corr_matrix_file and set isotope_correction true. Expect the slope to improve a little.', 'Check the reporter ion m/z offsets for 127 and 129 in the raw or mzML data to explain why 0.002 Da fails, and document the 0.01 override deliberately.', 'Consider whether MS2-level quantification is limited by compression. MS3 or SPS acquisition would avoid it but needs different data.', 'Add more spike-in proteins with more PSMs to get a more robust slope estimate.']

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
