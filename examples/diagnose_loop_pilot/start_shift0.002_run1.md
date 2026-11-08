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

**request_rerun** `{"base_run": "run0", "param_changes": {"reporter_mass_shift": 0.01}, "ext_args": {}, "hypothesis": "Channels 127 (ch2) and 129 (ch4) are almost empty (1 and 4 proteins, median ~11-13 vs ~20) while the others are fine. The reporter tolerance of 0.002 Da is very tight, and these two channels may have reporter masses offset (e.g. N vs C isotopologue, about 6 mDa) from the expected values, so peaks fall outside the window. Widening it should recover them.", "expected_change": "n_quantified for ch2 and ch4 rise to ~465, raw_median rises to ~20, they are no longer flagged. Other channels stay about the same."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_done*: {"run_id": "run1", "note": "rerun of run0; Nextflow reported ISOBARIC_WORKFLOW as cached", "source": "replay of recorded run 'shift0.002'"}

```
Rerun finished as run1 (rerun of run0; Nextflow reported ISOBARIC_WORKFLOW as cached). Use get_qc or compare_runs.
```

**compare_runs** `{"run_a": "run0", "run_b": "run1"}`

```
run0 -> run1
            run0                      run1             
    n_quantified raw_median_z n_quantified raw_median_z
ch1          465        0.405          465        0.405
ch2            1      -34.490            1      -34.490
ch3          468        0.944          468        0.944
ch4            4      -27.485            4      -27.485
ch5          468       -0.299          468       -0.299
ch6          468        0.299          468        0.299

Flagged: run0=['ch2', 'ch4']; run1=['ch2', 'ch4']
Pooled spike-in slope: 0.82 -> 0.82
Changed parameters (old, new): {'reporter_mass_shift': (0.002, 0.01)}
IsobaricWorkflow command arguments: {'removed': [], 'added': []}
Notes: run0: first run; run1: rerun of run0; Nextflow reported ISOBARIC_WORKFLOW as cached
```

**request_rerun** `{"base_run": "run0", "param_changes": {}, "ext_args": {"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.01"}, "hypothesis": "The reporter_mass_shift parameter did not reach the IsobaricWorkflow command (the step was cached and the command had no changes), so the previous test did not test anything. Passing it through ext.args instead should test whether the 0.002 Da reporter tolerance is too tight for channels 127 and 129.", "expected_change": "The command gains -extraction:reporter_mass_shift 0.01. ch2 and ch4 n_quantified rise to ~465 and raw_median to ~20, and they are no longer flagged."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_done*: {"run_id": "run2", "note": "rerun of run0", "source": "replay of recorded run 'shift0.01'"}

```
Rerun finished as run2 (rerun of run0). Use get_qc or compare_runs.
```

**compare_runs** `{"run_a": "run0", "run_b": "run2"}`

```
run0 -> run2
            run0                      run2             
    n_quantified raw_median_z n_quantified raw_median_z
ch1          465        0.405          460        1.300
ch2            1      -34.490          459       -0.235
ch3          468        0.944          463        1.114
ch4            4      -27.485          461       -0.203
ch5          468       -0.299          463       -1.798
ch6          468        0.299          463        0.203

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

**finish** `{"status": "resolved", "final_run": "run2", "diagnosis": "ch2 (127) and ch4 (129) were nearly empty in run0 because the reporter-ion extraction tolerance (0.002 Da) was too tight. This is an inference: run2 supports it, but I did not check the reporter masses directly. Widening the tolerance to 0.01 Da recovered both channels. The likely mechanism is that these reporters sit a few mDa away from the expected masses (the 127N/127C and 129N/129C isotopologues differ by about 6 mDa). The pipeline parameter reporter_mass_shift is not passed to the IsobaricWorkflow command, so it had no effect. Run1 changed that parameter, the step was cached, and the command was unchanged. The fix only worked when I passed -extraction:reporter_mass_shift 0.01 through ext.args.", "evidence": "Run0: ch2 n_quantified=1 (z=-34.5), ch4 n_quantified=4 (z=-27.5), other channels about 465. Run1 (parameter change only): the command had no added or removed arguments and the metrics were identical. Run2 (ext.args -extraction:reporter_mass_shift 0.01): ch2=459, ch4=461, z=-0.235 and -0.203, no flagged channels, corr_to_others 0.995-0.999. Spike-in pooled slope was 0.82 in run0 and 0.778 in run2.", "remaining_issues": ["Spike-in recovery is compressed: pooled slope 0.778. ENO1 is 0.80 and ALBU 0.73, against an expected slope of 1 for a 3.32 log2 range. PYGM is 0.75. CYC is 1.15, based on only 3 PSMs. This is a typical TMT ratio-compression pattern. It was not caused by the channel problem and was not fixed by the rerun.", "isotope_correction is false and no plex_corr_matrix_file is set, so reporter-channel isotope impurities are not corrected. This may contribute to the compression. I did not test it.", "A 0.01 Da tolerance is wider than the original and could admit interference, and the run was not checked for that. ch5 has the lowest median (z=-1.8), which is within the threshold. Run0 did not flag it, so it is not clearly a new problem.", "The reporter_mass_shift pipeline parameter has no effect on the quantification command."], "next_steps": ["Check the actual reporter-ion masses for 127 and 129 in the raw data and the tmt6plex definition in this OpenMS version. Set a tolerance that fits them, for example 0.005-0.01 Da.", "Report that the reporter_mass_shift parameter does not reach IsobaricWorkflow, or keep using ext.args for it.", "Consider enabling isotope_correction with the lot-specific correction matrix (plex_corr_matrix_file) and, if appropriate, iso_normalization. Then check whether the spike-in slopes move towards 1.", "Consider raising min_precursor_purity above 0 to reduce co-isolation interference, which is a common cause of ratio compression."]}`

```
Recorded.
```

## Conclusion (model)

- Status: resolved (final run: run2)
- Diagnosis: ch2 (127) and ch4 (129) were nearly empty in run0 because the reporter-ion extraction tolerance (0.002 Da) was too tight. This is an inference: run2 supports it, but I did not check the reporter masses directly. Widening the tolerance to 0.01 Da recovered both channels. The likely mechanism is that these reporters sit a few mDa away from the expected masses (the 127N/127C and 129N/129C isotopologues differ by about 6 mDa). The pipeline parameter reporter_mass_shift is not passed to the IsobaricWorkflow command, so it had no effect. Run1 changed that parameter, the step was cached, and the command was unchanged. The fix only worked when I passed -extraction:reporter_mass_shift 0.01 through ext.args.
- Evidence: Run0: ch2 n_quantified=1 (z=-34.5), ch4 n_quantified=4 (z=-27.5), other channels about 465. Run1 (parameter change only): the command had no added or removed arguments and the metrics were identical. Run2 (ext.args -extraction:reporter_mass_shift 0.01): ch2=459, ch4=461, z=-0.235 and -0.203, no flagged channels, corr_to_others 0.995-0.999. Spike-in pooled slope was 0.82 in run0 and 0.778 in run2.
- Remaining issues: ['Spike-in recovery is compressed: pooled slope 0.778. ENO1 is 0.80 and ALBU 0.73, against an expected slope of 1 for a 3.32 log2 range. PYGM is 0.75. CYC is 1.15, based on only 3 PSMs. This is a typical TMT ratio-compression pattern. It was not caused by the channel problem and was not fixed by the rerun.', 'isotope_correction is false and no plex_corr_matrix_file is set, so reporter-channel isotope impurities are not corrected. This may contribute to the compression. I did not test it.', 'A 0.01 Da tolerance is wider than the original and could admit interference, and the run was not checked for that. ch5 has the lowest median (z=-1.8), which is within the threshold. Run0 did not flag it, so it is not clearly a new problem.', 'The reporter_mass_shift pipeline parameter has no effect on the quantification command.']
- Next steps: ['Check the actual reporter-ion masses for 127 and 129 in the raw data and the tmt6plex definition in this OpenMS version. Set a tolerance that fits them, for example 0.005-0.01 Da.', 'Report that the reporter_mass_shift parameter does not reach IsobaricWorkflow, or keep using ext.args for it.', 'Consider enabling isotope_correction with the lot-specific correction matrix (plex_corr_matrix_file) and, if appropriate, iso_normalization. Then check whether the spike-in slopes move towards 1.', 'Consider raising min_precursor_purity above 0 to reduce co-isolation interference, which is a common cause of ratio compression.']

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
