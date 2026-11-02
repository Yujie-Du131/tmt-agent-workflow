# QC report on quantms output (shift0.01, run 1, model `claude-sonnet-5-5`)

**Overall:** minor_issues

Background-protein metrics show no channel outliers. n_quantified is 459-463 in every channel. raw_median spans 20.45-20.75 (robust z between -1.80 and 1.30). corr_to_others is 0.995-0.999, with ch2 slightly lowest at 0.995. These differences are within normal channel-to-channel variation. The one departure is spike-in compression: slopes of 0.73-0.80 for ENO1, ALBU and PYGM, against 1 for full recovery. I infer that co-isolation interference and the absence of isotope-impurity correction are the most probable causes, but the metrics alone do not confirm this. CYC_BOVIN (3 PSMs) is too sparsely supported to interpret.

### 1. [minor] ch1, ch2, ch3, ch4, ch5, ch6
- Observation: Measured spike-in ratios are compressed relative to the expected ratios for the three well-supported spike-in proteins. The slopes are about 0.73-0.80, so a nominal 10-fold change is recovered as roughly 5-6-fold. The compression is similar for the 10-fold proteins and the 2-fold protein, which points to a systematic effect on all channels rather than one bad channel. The background channels look consistent with each other (see summary), so the problem seems confined to dynamic-range recovery.
- Evidence: Slopes: P00924 ENO1_YEAST 0.798 (psms 32, expected_range_log2 3.322); P02769 ALBU_BOVIN 0.729 (psms 32, 3.322); P00489 PYGM_RABIT 0.753 (psms 52, 1.000). P62894 CYC_BOVIN slope is 1.152 but rests on only 3 PSMs. Parameters: isotope_correction=false, plex_corr_matrix_file=null, min_precursor_purity=0.0, precursor_isotope_deviation=10.0, iso_normalization=false, normalize=false.
- Likely causes:
  1. Ratio compression from co-isolated interfering peptides in TMT MS2 quantification
     - Reasoning: This is a well-known effect of MS2-level reporter quantification. Co-isolated background peptides contribute near-equal reporter signal in all channels and pull ratios toward 1. Precursor purity filtering is disabled (min_precursor_purity=0.0), so interfered spectra are kept. The compression affects all three proteins, which fits this explanation.
     - How to check: Re-run with min_precursor_purity set to about 0.5-0.75 and see whether the slopes move toward 1. Also check the isolation width and the precursor-interference distribution in the mzML or pmultiqc output.
  2. No reporter-ion isotope impurity correction was applied
     - Reasoning: isotope_correction=false and no plex_corr_matrix_file was supplied. Uncorrected impurities leak signal between neighbouring channels and flatten ratios between channels with very different spike levels, such as 10 vs 1.
     - How to check: Re-run with isotope_correction=true and the TMT6plex lot-specific correction matrix. Compare the slopes before and after.
  3. Spike-in quantity metadata or spike-in preparation does not match the true amounts
     - Reasoning: The expected values come from the SDRF QY values. If the actual spiked amounts differed from them, or the proteins carried background contribution from the matrix, the slope would be below 1 for the same reason. This is less likely because the slopes are consistent across three different proteins.
     - How to check: Compare the SDRF QY values with the wet-lab spike-in protocol. Check the raw reporter intensities of the spike-in PSMs for a floor in the low-amount channels.
  4. Reporter extraction tolerance mismatch between the parameters and the command
     - Reasoning: The reporter_mass_shift parameter is 0.002 but the command passes -extraction:reporter_mass_shift 0.01. This is probably the actual value used. A tolerance of 0.01 is still narrow enough that wrong-peak extraction is unlikely, so I consider this a minor factor and would check it only for consistency.
     - How to check: Check the IsobaricWorkflow log and the effective reporter tolerance. Confirm which value was applied.
- Recommendation: Treat the spike-in fold changes as underestimated by about 20-30% in log2 space. If accurate ratios matter, enable isotope correction with the TMT6plex lot matrix and set a precursor-purity filter, then recompute the spike-in slopes. Do not read much into the CYC_BOVIN slope of 1.152, which comes from only 3 PSMs.
