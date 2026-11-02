# QC report on quantms output (shift0.01, run 2, model `claude-sonnet-5-5`)

**Overall:** minor_issues

Channel-level metrics look healthy. All six channels quantify 459-463 proteins, correlation to the other channels is 0.995-0.999, and raw median log2 intensities span only 20.45-20.75 (robust z between -1.8 and 1.3). This spread is within normal loading variation, so I flag no channel. The only departure is mild ratio compression in the spike-in recovery. The ENO1, ALBU and PYGM slopes are 0.73-0.80, and the CYC slope of 1.152 is unreliable with 3 PSMs. The most likely causes are co-isolation interference and the absence of isotope-impurity correction. Separately, the parameter file and the command do not agree with each other or with the SDRF, which is a configuration observation and not a data-quality finding. reporter_mass_shift is 0.002 in the parameters but 0.01 in the command. The SDRF gives 25 ppm and 0.2 Da tolerances, while the run used 5 ppm and 0.03 Da.

### 1. [minor] ch1, ch2, ch3, ch4, ch5, ch6
- Observation: The three well-measured spike-ins (ENO1, ALBU, PYGM) are recovered with slopes of about 0.73-0.80 rather than 1, so the measured fold-changes are compressed by roughly 20-27%. The CYC_BOVIN slope of 1.152 rests on only 3 PSMs and a 1-fold range, so I do not interpret it. The compression is a metric observation. The causes below are my inference.
- Evidence: slope ENO1_YEAST 0.798 (32 PSMs, expected_range_log2 3.322); ALBU_BOVIN 0.729 (32 PSMs, 3.322); PYGM_RABIT 0.753 (52 PSMs, 1.000); CYC_BOVIN 1.152 (3 PSMs, 1.000). Parameters: isotope_correction=false, plex_corr_matrix_file=null, min_precursor_purity=0.0, iso_normalization=false, normalize=false.
- Likely causes:
  1. Co-isolation interference (ratio compression), typical of MS2-level TMT reporter quantification
     - Reasoning: Background co-isolated peptides add near-constant reporter signal in all channels and pull ratios toward 1. The effect is similar across ENO1, ALBU and PYGM, which fits this cause. No precursor purity filter is applied (min_precursor_purity 0.0), which allows interfering spectra into quantification. The run is a single unfractionated 60 min run, so co-isolation is likely.
     - How to check: Re-run with min_precursor_purity set to roughly 0.5-0.75 and see whether the slopes move toward 1. Check the isolation interference or purity values in the mzML or mzTab.
  2. No reporter isotope-impurity correction
     - Reasoning: isotope_correction is false and no correction matrix is given. Impurity leakage from the high-abundance channels into the neighbouring channels reduces the apparent dynamic range of spikes with a 10-fold range.
     - How to check: Enable isotope_correction with the TMT6plex lot's impurity matrix (plex_corr_matrix_file) and compare the slopes.
  3. Imperfect spike-in amounts, or limited precision at the low-abundance channels
     - Reasoning: If the real spiked amounts deviate from the SDRF quantities (QY), or the low-end channels are near the noise floor, slopes fall below 1. The consistency of the three slopes makes this less likely than a systematic effect.
     - How to check: Inspect the per-channel measured values of ENO1 and ALBU against the expected 10:5:2.5:1:2.5:10 and 1:2.5:5:10:5:1 patterns, and check the reporter intensity levels in the low channels.
- Recommendation: Treat the quantification as usable but compressed. Quantified fold-changes will be underestimated by about 20-25% for large ratios. Re-run with isotope correction and a precursor purity filter if more accurate ratios are needed. Interpret CYC_BOVIN with caution because it has only 3 PSMs.
