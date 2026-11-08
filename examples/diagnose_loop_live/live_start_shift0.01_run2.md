# Diagnose-rerun loop (live, start shift0.01, run 1, model `claude-sonnet-5-5`)

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
 "outdir": "results_agent_20261108124710_run0",
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
 "test_FDR": 
[...]
```

**request_rerun** `{"base_run": "run0", "param_changes": {"isotope_correction": true}, "ext_args": {}, "hypothesis": "Spike-in ratios are compressed (pooled slope 0.778, no channel flagged) because isotope_correction is false, so TMT6 reporter impurity spill-over is not corrected, which compresses ratios in a 10x spike-in.", "expected_change": "Pooled spike-in slope rises toward 1 (e.g. >0.9) and the IsobaricWorkflow command gains a correction matrix argument. Channel counts and medians stay about the same."}`

- *approval*: {"approved": true, "note": ""}

- *rerun_done*: {"run_id": "run1", "note": "rerun of run0; ISOBARIC_WORKFLOW command unchanged (Nextflow reused the cached task)", "source": "live run agent_20261108124710_run1, outputs in results_agent_20261108124710_run1"}

```
Rerun finished as run1 (rerun of run0; ISOBARIC_WORKFLOW command unchanged (Nextflow reused the cached task)). Use get_qc or compare_runs.
```

**compare_runs** `{"run_a": "run0", "run_b": "run1"}`

```
run0 -> run1
            run0                                     run1                            
    n_quantified raw_median_z corr_to_others n_quantified raw_median_z corr_to_others
ch1          460        1.300          0.999          460        1.300          0.999
ch2          459       -0.235          0.995          459       -0.235          0.995
ch3          463        1.114          0.999          463        1.114          0.999
ch4          461       -0.203          0.997          461       -0.203          0.997
ch5          463       -1.798          0.999          463       -1.798          0.999
ch6          463        0.203          0.999          463        0.203          0.999

Flagged: run0=none; run1=none
Pooled spike-in slope: 0.778 -> 0.778
Changed parameters (old, new): {'isotope_correction': (False, 'true')}
IsobaricWorkflow command arguments: {'removed': [], 'added': []}
Notes: run0: first run; run1: rerun of run0; ISOBARIC_WORKFLOW command unchanged (Nextflow reused the cached task)
```

**request_rerun** `{"base_run": "run0", "param_changes": {"isotope_correction": true, "plex_corr_matrix_file": "assets/tmt6plex_default_correction.matrix"}, "ext_args": {}, "hypothesis": "Uncorrected reporter isotope impurities compress spike-in ratios; isotope_correction alone did not alter the command, so the correction matrix file must be supplied for it to take effect.", "expected_change": "Command gains a correction-matrix argument; pooled spike-in slope rises from 0.778 toward ~0.9-1."}`

- *approval*: {"approved": true, "note": ""}

- *rerun_done*: {"run_id": "run2", "note": "rerun of run0", "source": "live run agent_20261108124710_run2, outputs in results_agent_20261108124710_run2"}

```
Rerun finished as run2 (rerun of run0). Use get_qc or compare_runs.
```

**compare_runs** `{"run_a": "run0", "run_b": "run2"}`

```
run0 -> run2
            run0                                     run2                            
    n_quantified raw_median_z corr_to_others n_quantified raw_median_z corr_to_others
ch1          460        1.300          0.999          460        1.300          0.999
ch2          459       -0.235          0.995          459       -0.235          0.995
ch3          463        1.114          0.999          463        1.114          0.999
ch4          461       -0.203          0.997          461       -0.203          0.997
ch5          463       -1.798          0.999          463       -1.798          0.999
ch6          463        0.203          0.999          463        0.203          0.999

Flagged: run0=none; run2=none
Pooled spike-in slope: 0.778 -> 0.778
Changed parameters (old, new): {'isotope_correction': (False, 'true'), 'plex_corr_matrix_file': (None, 'assets/tmt6plex_default_correction.matrix')}
IsobaricWorkflow command arguments: {'removed': [], 'added': ['-quantification:isotope_correction', '-tmt6plex:correction_matrix', '0.0/0.0/8.6/0.3', '0.0/0.1/7.8/0.1', '0.0/1.5/5.7/0.1', '0.0/1.5/6.2/0.2', '0.0/3.1/3.6/0.0', '0.1/2.9/3.8/0.0', 'true']}
Notes: run0: first run; run2: rerun of run0
```

**get_qc** `{"run_id": "run2"}`

```
Run run2 (rerun of run0)
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

**request_rerun** `{"base_run": "run0", "param_changes": {"min_precursor_purity": 0.7}, "ext_args": {}, "hypothesis": "Ratio compression comes from co-isolation interference (min_precursor_purity 0.0 keeps all spectra). Filtering impure precursors should reduce it.", "expected_change": "Command shows -extraction:min_precursor_purity 0.7; pooled spike-in slope increases above 0.778 (toward ~0.9); n_quantified drops somewhat."}`

- *approval*: {"approved": false, "note": "already tested in an earlier live run: purity 0.7 changed the command but no metric changed"}

```
The analyst did not approve this rerun. Note: already tested in an earlier live run: purity 0.7 changed the command but no metric changed
```

**request_rerun** `{"base_run": "run0", "param_changes": {}, "ext_args": {"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.002"}, "hypothesis": "The ext.args override sets reporter_mass_shift to 0.01 Da (5x the 0.002 default); a wider window may mis-extract reporter peaks and distort ratios.", "expected_change": "Command shows reporter_mass_shift 0.002 instead of 0.01; the pooled spike-in slope increases from 0.778 toward 1 if the window was the cause; otherwise no change."}`

- *approval*: {"approved": false, "note": "0.002 makes ch2 and ch4 fail (1 and 4 proteins), shown in earlier live and replayed runs; keep 0.01"}

```
The analyst did not approve this rerun. Note: 0.002 makes ch2 and ch4 fail (1 and 4 proteins), shown in earlier live and replayed runs; keep 0.01
```

**finish** `{"status": "unresolved", "final_run": "run0", "diagnosis": "No channel is flagged, but the spike-in ratios are compressed: pooled slope is 0.778 and individual spike-ins range from 0.73 to 0.80. I could not change this. I did not find a parameter or command change that moves the slope. The compression is probably caused by co-isolation interference, which is typical of MS2-level TMT quantification. That is an inference. I did not test it directly, because the purity-filter rerun was not approved. The earlier note says purity 0.7 changed nothing. The reporter_mass_shift override of 0.01 looks odd, but it is needed: the analyst reports that 0.002 makes ch2 and ch4 fail with 1 and 4 proteins. It should stay.", "evidence": "run0 QC: channels all have 459-463 proteins and |z| <= 1.8, so none are flagged. Slopes are ENO1 0.798, ALBU 0.729, PYGM 0.753 and CYC 1.152 (only 3 PSMs). Pooled slope is 0.778. run1 (isotope_correction=true alone) left the command unchanged (Nextflow reused the cached task) and the slope at 0.778. run2 added the tmt6plex correction matrix (-quantification:isotope_correction and -tmt6plex:correction_matrix 0.0/0.0/8.6/0.3 ...). Its slope stayed at 0.778 and every channel metric was identical. The rerun at purity 0.7 was not approved, with a note that it had been tested before and changed no metric. The rerun at reporter_mass_shift 0.002 was not approved, with a note that ch2 and ch4 fail at that value.", "remaining_issues": ["Spike-in ratio compression remains (pooled slope 0.778, below 1).", "run2's matrix is applied in the command but the QC metrics did not change. The QC slope may be computed from uncorrected intensities, or the correction may be negligible. I cannot tell which from these results.", "CYC_BOVIN has only 3 PSMs and a slope of 1.152, so it is unreliable.", "The reporter_mass_shift of 0.01 is required for ch2 and ch4 to quantify, which suggests a reporter m/z calibration offset for those channels. The cause is not investigated."], "next_steps": ["Treat the quantification as usable for relative comparisons, but expect fold changes to be underestimated by about 20%. Do not read the compression as a channel failure.", "Confirm which intensities the QC slope uses, and check whether run2's correction matrix changes the final protein ratios.", "Check the mass accuracy of the reporter ions for ch2 and ch4, and the instrument calibration.", "If accurate ratios matter, use an acquisition method with less interference (MS3/SPS or narrower isolation windows), or apply a ratio-compression correction.", "Use the tmt6plex lot-specific correction matrix (assets/tmt6plex_90064_XL352952_correction.matrix) if it matches the kit used."]}`

```
Recorded.
```

## Conclusion (model)

- Status: unresolved (final run: run0)
- Diagnosis: No channel is flagged, but the spike-in ratios are compressed: pooled slope is 0.778 and individual spike-ins range from 0.73 to 0.80. I could not change this. I did not find a parameter or command change that moves the slope. The compression is probably caused by co-isolation interference, which is typical of MS2-level TMT quantification. That is an inference. I did not test it directly, because the purity-filter rerun was not approved. The earlier note says purity 0.7 changed nothing. The reporter_mass_shift override of 0.01 looks odd, but it is needed: the analyst reports that 0.002 makes ch2 and ch4 fail with 1 and 4 proteins. It should stay.
- Evidence: run0 QC: channels all have 459-463 proteins and |z| <= 1.8, so none are flagged. Slopes are ENO1 0.798, ALBU 0.729, PYGM 0.753 and CYC 1.152 (only 3 PSMs). Pooled slope is 0.778. run1 (isotope_correction=true alone) left the command unchanged (Nextflow reused the cached task) and the slope at 0.778. run2 added the tmt6plex correction matrix (-quantification:isotope_correction and -tmt6plex:correction_matrix 0.0/0.0/8.6/0.3 ...). Its slope stayed at 0.778 and every channel metric was identical. The rerun at purity 0.7 was not approved, with a note that it had been tested before and changed no metric. The rerun at reporter_mass_shift 0.002 was not approved, with a note that ch2 and ch4 fail at that value.
- Remaining issues: ['Spike-in ratio compression remains (pooled slope 0.778, below 1).', "run2's matrix is applied in the command but the QC metrics did not change. The QC slope may be computed from uncorrected intensities, or the correction may be negligible. I cannot tell which from these results.", 'CYC_BOVIN has only 3 PSMs and a slope of 1.152, so it is unreliable.', 'The reporter_mass_shift of 0.01 is required for ch2 and ch4 to quantify, which suggests a reporter m/z calibration offset for those channels. The cause is not investigated.']
- Next steps: ['Treat the quantification as usable for relative comparisons, but expect fold changes to be underestimated by about 20%. Do not read the compression as a channel failure.', "Confirm which intensities the QC slope uses, and check whether run2's correction matrix changes the final protein ratios.", 'Check the mass accuracy of the reporter ions for ch2 and ch4, and the instrument calibration.', 'If accurate ratios matter, use an acquisition method with less interference (MS3/SPS or narrower isolation windows), or apply a ratio-compression correction.', 'Use the tmt6plex lot-specific correction matrix (assets/tmt6plex_90064_XL352952_correction.matrix) if it matches the kit used.']

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
