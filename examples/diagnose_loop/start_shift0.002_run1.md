# Diagnose-rerun loop (start shift0.002, run 1, model `claude-sonnet-5-5`)

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

**request_rerun** `{"base_run": "run0", "param_changes": {"reporter_mass_shift": 0.01}, "ext_args": {}, "hypothesis": "Reporter-ion extraction tolerance (0.002 Da) is too tight, so reporters in ch2 (127) and ch4 (129) are mostly missed (e.g. mass offset/calibration). Widening it should recover them.", "expected_change": "ch2 and ch4 n_quantified rises toward ~465 and raw_median_z moves near 0; other channels unchanged. Command should show a changed reporter tolerance argument."}`

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

**request_rerun** `{"base_run": "run0", "param_changes": {}, "ext_args": {"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.01"}, "hypothesis": "The reporter_mass_shift pipeline param did not reach the command (run1 cached, no argument change). Passing it via ext.args will actually widen the reporter-ion matching window, recovering ch2/ch4 if their reporter peaks are slightly offset.", "expected_change": "Command gains -extraction:reporter_mass_shift 0.01; ch2 and ch4 n_quantified rises toward ~465 and raw_median_z near 0."}`

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

**finish** `{"status": "resolved", "final_run": "run2", "diagnosis": "ch2 and ch4 were almost empty in run0 because the reporter-ion matching window was too narrow at 0.002 Da. This is an inference from the rerun, not something the metrics show directly. Widening it to 0.01 Da through ext.args recovered both channels. The pipeline parameter reporter_mass_shift did not reach the IsobaricWorkflow command. run1 changed only the parameter, and its step was reported as cached with no change to the command or the metrics. The setting only took effect when passed as -extraction:reporter_mass_shift 0.01 in ext.args. The likely cause is a small mass offset in the 127 and 129 reporters, but I did not measure that offset.", "evidence": "run0: ch2 n_quantified=1 (raw_median_z -34.49), ch4 n_quantified=4 (z -27.49), both flagged. Other channels had 465-468 proteins. run1 (param change only): the command was unchanged and the metrics were identical to run0. run2 (ext.args -extraction:reporter_mass_shift 0.01 added to the command): ch2=459, ch4=461 proteins, z=-0.235 and -0.203, no channels flagged, corr_to_others 0.995-0.999.", "remaining_issues": ["The cause of the offset in ch2 and ch4 was not identified. The cause could be mass calibration, or the 127N/127C and 129N/129C reporter definitions. A 0.01 Da window is wider than the 0.002 default, so check it does not admit interference.", "Spike-in recovery is compressed and got slightly worse, from a pooled slope of 0.82 to 0.778. ALBU_BOVIN was 0.74 and PYGM_RABIT 0.753 in run0. This is probably ratio compression from co-isolation, and isotope_correction=false and min_precursor_purity=0.0 may contribute. I did not test it.", "Each channel lost 4-5 proteins (for example ch1 465 to 460, ch5 468 to 463) after the rerun. I did not investigate this.", "ch5 raw_median_z moved from -0.30 to -1.80 after the rerun. This is within the flag threshold but worth noting.", "iso_normalization and normalize are off, so intensities are not normalized."], "next_steps": ["Check the reporter-ion mass error distribution for the 127 and 129 channels in the raw data or the mzML, and use the smallest window that recovers them, for example 0.005.", "Fix the pipeline so the reporter_mass_shift parameter is passed to IsobaricWorkflow as -extraction:reporter_mass_shift, or keep using ext.args.", "Consider testing isotope_correction with the correct plex correction matrix, and min_precursor_purity above 0, to reduce ratio compression. Use one change per rerun and compare the spike-in slopes.", "Check the SDRF channel-to-sample assignment for tmt6plex."]}`

```
Recorded.
```

## Conclusion (model)

- Status: resolved (final run: run2)
- Diagnosis: ch2 and ch4 were almost empty in run0 because the reporter-ion matching window was too narrow at 0.002 Da. This is an inference from the rerun, not something the metrics show directly. Widening it to 0.01 Da through ext.args recovered both channels. The pipeline parameter reporter_mass_shift did not reach the IsobaricWorkflow command. run1 changed only the parameter, and its step was reported as cached with no change to the command or the metrics. The setting only took effect when passed as -extraction:reporter_mass_shift 0.01 in ext.args. The likely cause is a small mass offset in the 127 and 129 reporters, but I did not measure that offset.
- Evidence: run0: ch2 n_quantified=1 (raw_median_z -34.49), ch4 n_quantified=4 (z -27.49), both flagged. Other channels had 465-468 proteins. run1 (param change only): the command was unchanged and the metrics were identical to run0. run2 (ext.args -extraction:reporter_mass_shift 0.01 added to the command): ch2=459, ch4=461 proteins, z=-0.235 and -0.203, no channels flagged, corr_to_others 0.995-0.999.
- Remaining issues: ['The cause of the offset in ch2 and ch4 was not identified. The cause could be mass calibration, or the 127N/127C and 129N/129C reporter definitions. A 0.01 Da window is wider than the 0.002 default, so check it does not admit interference.', 'Spike-in recovery is compressed and got slightly worse, from a pooled slope of 0.82 to 0.778. ALBU_BOVIN was 0.74 and PYGM_RABIT 0.753 in run0. This is probably ratio compression from co-isolation, and isotope_correction=false and min_precursor_purity=0.0 may contribute. I did not test it.', 'Each channel lost 4-5 proteins (for example ch1 465 to 460, ch5 468 to 463) after the rerun. I did not investigate this.', 'ch5 raw_median_z moved from -0.30 to -1.80 after the rerun. This is within the flag threshold but worth noting.', 'iso_normalization and normalize are off, so intensities are not normalized.']
- Next steps: ['Check the reporter-ion mass error distribution for the 127 and 129 channels in the raw data or the mzML, and use the smallest window that recovers them, for example 0.005.', 'Fix the pipeline so the reporter_mass_shift parameter is passed to IsobaricWorkflow as -extraction:reporter_mass_shift, or keep using ext.args.', 'Consider testing isotope_correction with the correct plex correction matrix, and min_precursor_purity above 0, to reduce ratio compression. Use one change per rerun and compare the spike-in slopes.', 'Check the SDRF channel-to-sample assignment for tmt6plex.']

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
