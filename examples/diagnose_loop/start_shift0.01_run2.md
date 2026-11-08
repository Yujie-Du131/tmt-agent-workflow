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

**request_rerun** `{"base_run": "run0", "param_changes": {"min_precursor_purity": 0.5}, "ext_args": {}, "hypothesis": "Spike-in ratio compression (pooled slope 0.778; ENO1/ALBU 0.80/0.73) is caused by co-isolation interference, as precursor purity filtering is off (0.0). The reporter_mass_shift 0.01 override is unlikely to matter for 6plex (channels 1 Da apart).", "expected_change": "Pooled spike-in slope rises toward 1 (e.g. >0.85), with modestly fewer proteins quantified per channel; no channels flagged."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_unavailable*: {"reason": "Not available in replay mode: no recorded run changes ['min_precursor_purity']. This change would have to be run in live mode."}

```
Not available in replay mode: no recorded run changes ['min_precursor_purity']. This change would have to be run in live mode.
```

**request_rerun** `{"base_run": "run0", "param_changes": {}, "ext_args": {"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.002"}, "hypothesis": "The non-default ext.args override reporter_mass_shift 0.01 (5x the pipeline default 0.002) widens the reporter extraction window and may cause the reduced spike-in recovery.", "expected_change": "Command shows reporter_mass_shift 0.002; spike-in slope may improve toward 1 if the window matters, otherwise stays ~0.78."}`

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

**request_rerun** `{"base_run": "run0", "param_changes": {"isotope_correction": true}, "ext_args": {}, "hypothesis": "Residual spike-in compression in run0 (slope 0.778) is partly due to uncorrected TMT isotope impurities (isotope_correction=false); the 0.01 mass-shift window must stay since 0.002 loses ch2/ch4.", "expected_change": "Pooled slope rises (>0.85) with all 6 channels still quantified (~460 proteins)."}`

- *approval*: {"approved": true, "note": "auto-approved (benchmark run; no analyst)"}

- *rerun_unavailable*: {"reason": "Not available in replay mode: no recorded run changes ['isotope_correction']. This change would have to be run in live mode."}

```
Not available in replay mode: no recorded run changes ['isotope_correction']. This change would have to be run in live mode.
```

**finish** `{"status": "unresolved", "final_run": "run0", "diagnosis": "run0 has no flagged channels and all six are well populated, so it is the best usable run. Spike-in ratios are still compressed (pooled slope 0.778 against an ideal of 1). My rerun showed that the non-default reporter_mass_shift of 0.01 in run0 is not a fault. It is needed: with the default 0.002, ch2 and ch4 lose almost all their quantifications. The cause of the ratio compression is not established. My hypotheses are co-isolation interference (precursor purity filter off) and uncorrected TMT isotope impurities (isotope_correction false). I could not test either, because those reruns were not available.", "evidence": "run0: n_quantified 459-463 per channel, no flags, pooled slope 0.778 (ENO1 0.798, ALBU 0.729, PYGM 0.753, CYC 1.152). Command has -extraction:reporter_mass_shift 0.01, and the config has min_precursor_purity 0.0 and isotope_correction false. run1 (mass shift reverted to 0.002; compare_runs confirmed the argument was removed): ch2 n_quantified 460->1 (z -34.5), ch4 461->4 (z -27.5), both flagged. Pooled slope 0.82 (ENO1 0.882, ALBU 0.740), but this is computed on only 4 of 6 channels. It is not a real improvement and not comparable with run0.", "remaining_issues": ["Spike-in ratio compression remains: pooled slope 0.778, with ENO1 and ALBU (expected 10-fold) at about 0.73-0.80. The cause is not confirmed.", "CYC_BOVIN has only 3 PSMs, so its slope of 1.15 is unreliable.", "Because ch2 and ch4 vanish at the 0.002 window, their reporter ions appear to sit more than 0.002 Da from the theoretical mass. This points to a mass calibration offset or an instrument/centroiding issue. I did not test this directly.", "The pipeline param reporter_mass_shift (0.002) does not match the effective value (0.01), which is set through ext.args. This is easy to overlook when reproducing the run."], "next_steps": ["Keep the 0.01 mass-shift override for ch2 and ch4. Document it, or check the reporter-ion mass error per channel in the mzML to confirm the offset.", "In live mode, rerun with min_precursor_purity around 0.5, one change at a time. Expect the slope to rise and some proteins to be lost.", "Rerun with isotope_correction true and the plex_corr_matrix_file for your TMT kit lot. Expect a higher slope.", "Check the spike-in design for co-isolation or ratio-compression effects, and consider MS3/SPS acquisition if compression persists."]}`

```
Recorded.
```

## Conclusion (model)

- Status: unresolved (final run: run0)
- Diagnosis: run0 has no flagged channels and all six are well populated, so it is the best usable run. Spike-in ratios are still compressed (pooled slope 0.778 against an ideal of 1). My rerun showed that the non-default reporter_mass_shift of 0.01 in run0 is not a fault. It is needed: with the default 0.002, ch2 and ch4 lose almost all their quantifications. The cause of the ratio compression is not established. My hypotheses are co-isolation interference (precursor purity filter off) and uncorrected TMT isotope impurities (isotope_correction false). I could not test either, because those reruns were not available.
- Evidence: run0: n_quantified 459-463 per channel, no flags, pooled slope 0.778 (ENO1 0.798, ALBU 0.729, PYGM 0.753, CYC 1.152). Command has -extraction:reporter_mass_shift 0.01, and the config has min_precursor_purity 0.0 and isotope_correction false. run1 (mass shift reverted to 0.002; compare_runs confirmed the argument was removed): ch2 n_quantified 460->1 (z -34.5), ch4 461->4 (z -27.5), both flagged. Pooled slope 0.82 (ENO1 0.882, ALBU 0.740), but this is computed on only 4 of 6 channels. It is not a real improvement and not comparable with run0.
- Remaining issues: ['Spike-in ratio compression remains: pooled slope 0.778, with ENO1 and ALBU (expected 10-fold) at about 0.73-0.80. The cause is not confirmed.', 'CYC_BOVIN has only 3 PSMs, so its slope of 1.15 is unreliable.', 'Because ch2 and ch4 vanish at the 0.002 window, their reporter ions appear to sit more than 0.002 Da from the theoretical mass. This points to a mass calibration offset or an instrument/centroiding issue. I did not test this directly.', 'The pipeline param reporter_mass_shift (0.002) does not match the effective value (0.01), which is set through ext.args. This is easy to overlook when reproducing the run.']
- Next steps: ['Keep the 0.01 mass-shift override for ch2 and ch4. Document it, or check the reporter-ion mass error per channel in the mzML to confirm the offset.', 'In live mode, rerun with min_precursor_purity around 0.5, one change at a time. Expect the slope to rise and some proteins to be lost.', 'Rerun with isotope_correction true and the plex_corr_matrix_file for your TMT kit lot. Expect a higher slope.', 'Check the spike-in design for co-isolation or ratio-compression effects, and consider MS3/SPS acquisition if compression persists.']

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
