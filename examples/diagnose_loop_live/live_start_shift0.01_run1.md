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
 "outdir": "results_agent_20261108123554_run0",
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

**request_rerun** `{"base_run": "run0", "param_changes": {"min_precursor_purity": 0.7}, "ext_args": {}, "hypothesis": "Spike-in ratios are compressed (pooled slope 0.778) due to co-isolation interference, since min_precursor_purity is 0.0 so no impure spectra are removed.", "expected_change": "Command shows -extraction:min_precursor_purity 0.7; spike-in slopes move toward 1 (pooled >0.85); n_quantified drops modestly; no channels flagged."}`

- *approval*: {"approved": true, "note": ""}

- *rerun_done*: {"run_id": "run1", "note": "rerun of run0", "source": "live run agent_20261108123554_run1, outputs in results_agent_20261108123554_run1"}

```
Rerun finished as run1 (rerun of run0). Use get_qc or compare_runs.
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
Changed parameters (old, new): {'min_precursor_purity': (0.0, '0.7')}
IsobaricWorkflow command arguments: {'removed': ['0.0'], 'added': ['0.7']}
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

**request_rerun** `{"base_run": "run0", "param_changes": {"isotope_correction": true}, "ext_args": {}, "hypothesis": "Ratio compression arises from uncorrected TMT reporter isotope impurities (isotope_correction false); purity filtering had no effect.", "expected_change": "Command gains an isotope-correction argument; spike-in slopes increase toward 1 (pooled >0.85); channels not flagged."}`

- *approval*: {"approved": true, "note": ""}

- *rerun_done*: {"run_id": "run2", "note": "rerun of run0; ISOBARIC_WORKFLOW command unchanged (Nextflow reused the cached task)", "source": "live run agent_20261108123554_run2, outputs in results_agent_20261108123554_run2"}

```
Rerun finished as run2 (rerun of run0; ISOBARIC_WORKFLOW command unchanged (Nextflow reused the cached task)). Use get_qc or compare_runs.
```

**request_rerun** `{"base_run": "run0", "param_changes": {}, "ext_args": {"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.002"}, "hypothesis": "The ext.args override sets reporter_mass_shift 0.01 (5x the pipeline param 0.002), which may cause mis-assigned reporter peaks/interference and ratio compression.", "expected_change": "Command shows -extraction:reporter_mass_shift 0.002; spike-in slopes move toward 1 (pooled >0.85)."}`

- *approval*: {"approved": true, "note": ""}

- *rerun_done*: {"run_id": "run3", "note": "rerun of run0", "source": "live run agent_20261108123554_run3, outputs in results_agent_20261108123554_run3"}

```
Rerun finished as run3 (rerun of run0). Use get_qc or compare_runs.
```

**compare_runs** `{"run_a": "run0", "run_b": "run3"}`

```
run0 -> run3
            run0                                     run3                            
    n_quantified raw_median_z corr_to_others n_quantified raw_median_z corr_to_others
ch1          460        1.300          0.999          465        0.405            NaN
ch2          459       -0.235          0.995            1      -34.490            NaN
ch3          463        1.114          0.999          468        0.944            NaN
ch4          461       -0.203          0.997            4      -27.485            NaN
ch5          463       -1.798          0.999          468       -0.299            NaN
ch6          463        0.203          0.999          468        0.299            NaN

Flagged: run0=none; run3=['ch2', 'ch4']
Pooled spike-in slope: 0.778 -> 0.82
Changed parameters (old, new): none
IsobaricWorkflow command arguments: {'removed': ['0.01'], 'added': ['0.002']}
Notes: run0: first run; run3: rerun of run0
```

**get_qc** `{"run_id": "run3"}`

```
Run run3 (rerun of run0)
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

**finish** `{"status": "unresolved", "final_run": "run0", "diagnosis": "No channel-level fault was found. The only issue is that the spike-in ratios look compressed. The pooled slope is 0.778 against an ideal of 1, and ENO1, ALBU and PYGM sit at 0.73 to 0.80. I did not fix this. Three reruns ruled out three candidate causes, but I did not find the cause. Compression like this is common in MS2-level TMT data. I infer, without having tested it, that it comes from co-isolation interference and/or uncorrected reporter isotope impurities. CYC_BOVIN reads 1.15, but it has only 3 PSMs, so I would not rely on it. The ext.args override `-extraction:reporter_mass_shift 0.01` looked suspicious, but it turned out to be necessary. Tightening it to the pipeline-parameter value of 0.002 (run3) made quantification fail in ch2 and ch4. Those channels dropped to 1 and 4 proteins quantified, against about 465 in the other channels.", "evidence": "run0: no flagged channels, 459 to 463 proteins quantified per channel, corr_to_others 0.995 to 0.999, pooled slope 0.778. run1 (min_precursor_purity 0.7): the command changed (0.0 -> 0.7), but every metric was identical and the pooled slope stayed at 0.778. run2 (isotope_correction true): Nextflow reused the cached task and the command was unchanged, so the parameter has no effect on the IsobaricWorkflow command. run3 (reporter_mass_shift 0.002): flagged ch2 (n=1, z=-34.5) and ch4 (n=4, z=-27.5). The pooled slope was 0.82, but it is not meaningful with two channels lost.", "remaining_issues": ["Spike-in ratio compression is unexplained: pooled slope 0.778, with ALBU at 0.729 and PYGM at 0.753.", "The isotope_correction parameter and plex_corr_matrix_file are not passed to the IsobaricWorkflow command. It is not known whether impurity correction is applied.", "The min_precursor_purity filter had no measurable effect. The mzML may lack purity information, or no spectra fall below 0.7, so I could not test co-isolation.", "The reporter_mass_shift parameter (0.002) and the ext.args value (0.01) disagree. The parameter is not used in the command, and the ext.args value is the one that works."], "next_steps": ["Keep -extraction:reporter_mass_shift at 0.01. Do not tighten it to 0.002, because ch2 and ch4 are lost.", "Check whether the IsobaricWorkflow version applies isotope correction by default. If it does not, supply the TMT6plex lot-specific impurity matrix through plex_corr_matrix_file or an ext.args option. I did not test any such ext.args option.", "Check how the QC script computes the spike-in slope, and check the precursor purity values in the mzML, before concluding that interference is the cause.", "Treat the compression as a known limitation of MS2-based TMT quantification. Report spike-in-based fold changes as compressed. Consider MS3 or SPS acquisition for future runs."]}`

```
Recorded.
```

## Conclusion (model)

- Status: unresolved (final run: run0)
- Diagnosis: No channel-level fault was found. The only issue is that the spike-in ratios look compressed. The pooled slope is 0.778 against an ideal of 1, and ENO1, ALBU and PYGM sit at 0.73 to 0.80. I did not fix this. Three reruns ruled out three candidate causes, but I did not find the cause. Compression like this is common in MS2-level TMT data. I infer, without having tested it, that it comes from co-isolation interference and/or uncorrected reporter isotope impurities. CYC_BOVIN reads 1.15, but it has only 3 PSMs, so I would not rely on it. The ext.args override `-extraction:reporter_mass_shift 0.01` looked suspicious, but it turned out to be necessary. Tightening it to the pipeline-parameter value of 0.002 (run3) made quantification fail in ch2 and ch4. Those channels dropped to 1 and 4 proteins quantified, against about 465 in the other channels.
- Evidence: run0: no flagged channels, 459 to 463 proteins quantified per channel, corr_to_others 0.995 to 0.999, pooled slope 0.778. run1 (min_precursor_purity 0.7): the command changed (0.0 -> 0.7), but every metric was identical and the pooled slope stayed at 0.778. run2 (isotope_correction true): Nextflow reused the cached task and the command was unchanged, so the parameter has no effect on the IsobaricWorkflow command. run3 (reporter_mass_shift 0.002): flagged ch2 (n=1, z=-34.5) and ch4 (n=4, z=-27.5). The pooled slope was 0.82, but it is not meaningful with two channels lost.
- Remaining issues: ['Spike-in ratio compression is unexplained: pooled slope 0.778, with ALBU at 0.729 and PYGM at 0.753.', 'The isotope_correction parameter and plex_corr_matrix_file are not passed to the IsobaricWorkflow command. It is not known whether impurity correction is applied.', 'The min_precursor_purity filter had no measurable effect. The mzML may lack purity information, or no spectra fall below 0.7, so I could not test co-isolation.', 'The reporter_mass_shift parameter (0.002) and the ext.args value (0.01) disagree. The parameter is not used in the command, and the ext.args value is the one that works.']
- Next steps: ['Keep -extraction:reporter_mass_shift at 0.01. Do not tighten it to 0.002, because ch2 and ch4 are lost.', 'Check whether the IsobaricWorkflow version applies isotope correction by default. If it does not, supply the TMT6plex lot-specific impurity matrix through plex_corr_matrix_file or an ext.args option. I did not test any such ext.args option.', 'Check how the QC script computes the spike-in slope, and check the precursor purity values in the mzML, before concluding that interference is the cause.', 'Treat the compression as a known limitation of MS2-based TMT quantification. Report spike-in-based fold changes as compressed. Consider MS3 or SPS acquisition for future runs.']

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
