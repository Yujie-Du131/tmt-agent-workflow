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

**request_rerun** `{"base_run": "run0", "param_changes": {"reporter_mass_shift": 0.01}, "ext_args": {}, "hypothesis": "Reporter extraction window (\u00b10.002 Da) is too narrow, so reporter peaks of ch2 (127) and ch4 (129) fall outside it (e.g. 15N vs 13C isotopologue offset ~0.006 Da or calibration shift); ch1/3/5/6 are fine, which fits a channel-specific mass offset.", "expected_change": "ch2 and ch4 n_quantified rises from 1 and 4 to ~460, their raw_median rises to ~20, and they are no longer flagged. Other channels unchanged."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_done*: {"run_id": "run1", "note": "rerun of run0; Nextflow reported ISOBARIC_WORKFLOW as cached", "source": "replay of recorded run 'shift0.002'"}

```
Rerun finished as run1 (rerun of run0; Nextflow reported ISOBARIC_WORKFLOW as cached). Use get_qc or compare_runs.
```

**compare_runs** `{"run_a": "run0", "run_b": "run1"}`

```
run0 -> run1
            run0                                     run1                            
    n_quantified raw_median_z corr_to_others n_quantified raw_median_z corr_to_others
ch1          465        0.405            NaN          465        0.405            NaN
ch2            1      -34.490            NaN            1      -34.490            NaN
ch3          468        0.944            NaN          468        0.944            NaN
ch4            4      -27.485            NaN            4      -27.485            NaN
ch5          468       -0.299            NaN          468       -0.299            NaN
ch6          468        0.299            NaN          468        0.299            NaN

Flagged: run0=['ch2', 'ch4']; run1=['ch2', 'ch4']
Pooled spike-in slope: 0.82 -> 0.82
Changed parameters (old, new): {'reporter_mass_shift': (0.002, 0.01)}
IsobaricWorkflow command arguments: {'removed': [], 'added': []}
Notes: run0: first run; run1: rerun of run0; Nextflow reported ISOBARIC_WORKFLOW as cached
```

**request_rerun** `{"base_run": "run0", "param_changes": {}, "ext_args": {"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.01"}, "hypothesis": "The pipeline parameter reporter_mass_shift never reached the command (run1 was cached, command unchanged). Passing it via ext.args will widen the reporter window from \u00b10.002 to \u00b10.01 Da so ch2 (127) and ch4 (129) reporter peaks, offset from the nominal masses, get extracted.", "expected_change": "Command gains -extraction:reporter_mass_shift 0.01; ch2 and ch4 n_quantified rise from 1 and 4 to ~460, raw_median_z near 0, no flags."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_done*: {"run_id": "run2", "note": "rerun of run0", "source": "replay of recorded run 'shift0.01'"}

```
Rerun finished as run2 (rerun of run0). Use get_qc or compare_runs.
```

**compare_runs** `{"run_a": "run0", "run_b": "run2"}`

```
run0 -> run2
            run0                                     run2                            
    n_quantified raw_median_z corr_to_others n_quantified raw_median_z corr_to_others
ch1          465        0.405            NaN          460        1.300          0.999
ch2            1      -34.490            NaN          459       -0.235          0.995
ch3          468        0.944            NaN          463        1.114          0.999
ch4            4      -27.485            NaN          461       -0.203          0.997
ch5          468       -0.299            NaN          463       -1.798          0.999
ch6          468        0.299            NaN          463        0.203          0.999

Flagged: run0=['ch2', 'ch4']; run2=none
Pooled spike-in slope: 0.82 -> 0.778
Changed parameters (old, new): none
IsobaricWorkflow command arguments: {'removed': [], 'added': ['-extraction:reporter_mass_shift', '0.01']}
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

**finish** `{"status": "resolved", "final_run": "run2", "diagnosis": "In run0, ch2 (127) and ch4 (129) were almost empty because the reporter-ion extraction window was too narrow. I think the reporter peaks for those two channels sit slightly off their nominal masses, but I did not check the spectra. Widening the window to \u00b10.01 Da recovered both channels. The pipeline parameter `reporter_mass_shift` did not reach the IsobaricWorkflow command, so the change in run1 did nothing. Passing `-extraction:reporter_mass_shift 0.01` through ext.args in run2 worked.", "evidence": "run0: ch2 n_quantified=1 (z=-34.5) and ch4 n_quantified=4 (z=-27.5), both flagged. run1: the `reporter_mass_shift` parameter changed from 0.002 to 0.01, but the IsobaricWorkflow command had no added or removed arguments, the step was cached, and the QC was identical. run2: the command gained `-extraction:reporter_mass_shift 0.01`. ch2 now has 459 proteins (z=-0.235, corr 0.995) and ch4 has 461 (z=-0.203, corr 0.997). No channels are flagged, and the other channels are essentially unchanged at 460-463 proteins. The pooled spike-in slope went from 0.82 to 0.778.", "remaining_issues": ["Spike-in ratio recovery is compressed: pooled slope is 0.78 against an ideal of 1. ENO1 is 0.80 and ALBU is 0.73 (expected 3.32 log2), and PYGM is 0.75 (expected 1.0). CYC has only 3 PSMs, so its 1.15 is unreliable. Compression is typical of co-isolation interference. Isotope-impurity correction is off (isotope_correction=false, no plex_corr_matrix_file), and min_precursor_purity is 0.0. I have not tested either as the cause.", "The ch5 median is slightly low (z=-1.8). This is within the flag threshold.", "I inferred the cause of the offset from the pattern of which channels failed. I did not inspect the reporter m/z distributions. A \u00b10.01 Da window is only a workaround."], "next_steps": ["Check the reporter-ion m/z offsets in the raw or mzML data for 127 and 129. This will show whether the TMT6plex masses or the instrument calibration are the cause.", "Make `reporter_mass_shift` actually reach the IsobaricWorkflow command in the pipeline configuration, instead of relying on ext.args.", "Test isotope_correction with the kit's correction matrix, and min_precursor_purity (for example 0.5-0.7), to see whether spike-in slope compression improves.", "Check that the 0.01 Da window does not pick up neighbouring reporter peaks. Channels 126, 128, 130 and 131 should keep the same intensities. The run2 QC suggests they do."]}`

```
Recorded.
```

## Conclusion (model)

- Status: resolved (final run: run2)
- Diagnosis: In run0, ch2 (127) and ch4 (129) were almost empty because the reporter-ion extraction window was too narrow. I think the reporter peaks for those two channels sit slightly off their nominal masses, but I did not check the spectra. Widening the window to ±0.01 Da recovered both channels. The pipeline parameter `reporter_mass_shift` did not reach the IsobaricWorkflow command, so the change in run1 did nothing. Passing `-extraction:reporter_mass_shift 0.01` through ext.args in run2 worked.
- Evidence: run0: ch2 n_quantified=1 (z=-34.5) and ch4 n_quantified=4 (z=-27.5), both flagged. run1: the `reporter_mass_shift` parameter changed from 0.002 to 0.01, but the IsobaricWorkflow command had no added or removed arguments, the step was cached, and the QC was identical. run2: the command gained `-extraction:reporter_mass_shift 0.01`. ch2 now has 459 proteins (z=-0.235, corr 0.995) and ch4 has 461 (z=-0.203, corr 0.997). No channels are flagged, and the other channels are essentially unchanged at 460-463 proteins. The pooled spike-in slope went from 0.82 to 0.778.
- Remaining issues: ['Spike-in ratio recovery is compressed: pooled slope is 0.78 against an ideal of 1. ENO1 is 0.80 and ALBU is 0.73 (expected 3.32 log2), and PYGM is 0.75 (expected 1.0). CYC has only 3 PSMs, so its 1.15 is unreliable. Compression is typical of co-isolation interference. Isotope-impurity correction is off (isotope_correction=false, no plex_corr_matrix_file), and min_precursor_purity is 0.0. I have not tested either as the cause.', 'The ch5 median is slightly low (z=-1.8). This is within the flag threshold.', 'I inferred the cause of the offset from the pattern of which channels failed. I did not inspect the reporter m/z distributions. A ±0.01 Da window is only a workaround.']
- Next steps: ['Check the reporter-ion m/z offsets in the raw or mzML data for 127 and 129. This will show whether the TMT6plex masses or the instrument calibration are the cause.', 'Make `reporter_mass_shift` actually reach the IsobaricWorkflow command in the pipeline configuration, instead of relying on ext.args.', "Test isotope_correction with the kit's correction matrix, and min_precursor_purity (for example 0.5-0.7), to see whether spike-in slope compression improves.", 'Check that the 0.01 Da window does not pick up neighbouring reporter peaks. Channels 126, 128, 130 and 131 should keep the same intensities. The run2 QC suggests they do.']

## Check by code

```
{
 "flagged_run0": [
  "ch2",
  "ch4"
 ],
 "final_run": "run2",
 "flagged_final_run": [],
 "status_consistent": true,
 "conflict": null
}
```
