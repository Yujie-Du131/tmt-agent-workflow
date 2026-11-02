# QC report on quantms output (shift0.01, run 3, model `claude-sonnet-5-5`)

**Overall:** minor_issues

Channel-level QC looks consistent. n_quantified is 459-463 in all channels, corr_to_others is 0.995-0.999, and the raw_median spread is about 0.3 log2 (z from -1.8 to 1.3), which is not a clear outlier. The one finding is moderate ratio compression in the spike-ins: ENO1 0.80, ALBU 0.73 and PYGM 0.75, against an expected 1. This is most likely from TMT co-isolation interference and the lack of isotope correction (isotope_correction=false, min_precursor_purity=0.0). CYC_BOVIN has only 3 PSMs, so its slope of 1.15 is unreliable. The mismatch between reporter_mass_shift in the parameters (0.002) and in the command (0.01) is worth noting but is unlikely to be the main cause.

### 1. [minor] ch1, ch2, ch3, ch4, ch5, ch6
- Observation: Spike-in ratios are compressed. The two proteins with the widest expected range (10-fold, 3.32 log2) and the 2-fold PYGM_RABIT recover only about 73-80% of the expected change. The fourth spike-in, CYC_BOVIN, overshoots (1.15), but it rests on only 3 PSMs. Compression of this size is typical of TMT MS2 quantification. This is what the metrics show; the causes below are inferred.
- Evidence: Slopes: P00924 ENO1_YEAST 0.798 (32 PSMs, range 3.322); P02769 ALBU_BOVIN 0.729 (32 PSMs, range 3.322); P00489 PYGM_RABT 0.753 (52 PSMs, range 1.000); P62894 CYC_BOVIN 1.152 (3 PSMs, range 1.000). Parameters: isotope_correction=false, plex_corr_matrix_file=null, min_precursor_purity=0.0, iso_normalization=false, normalize=false.
- Likely causes:
  1. Co-isolation interference (ratio compression). Background peptides in the isolation window contribute reporter signal that is roughly equal across channels, which pulls ratios toward 1.
     - Reasoning: This is the usual cause of compression in TMT MS2 data. The filename indicates a 2 Da isolation window, and no precursor purity filter is applied (min_precursor_purity=0.0). The compression is similar for the 10-fold and 2-fold spike-ins.
     - How to check: Re-run quantification with min_precursor_purity set to about 0.5-0.7 and compare the slopes. Check the distribution of precursor purity in the isobaric workflow output.
  2. No isotope-impurity correction applied.
     - Reasoning: isotope_correction is false and no correction matrix is supplied, so reporter-channel impurities leak signal between channels. This mostly distorts low-abundance channels and shrinks the ratios.
     - How to check: Re-run with isotope_correction=true and the correct TMT6plex lot matrix (plex_corr_matrix_file) and compare the slopes.
  3. Low-intensity reporter signal or a noise floor in the low-abundance channels.
     - Reasoning: For a 10-fold range, the weakest channels may be near the background level. The slopes for the 10-fold and 2-fold proteins are similar, so this is a less likely contributor.
     - How to check: Inspect the reporter intensities of the spike-in PSMs in the lowest-level channels. Test min_reporter_intensity filtering and check for missing values.
  4. Inconsistent reporter extraction settings.
     - Reasoning: The pipeline parameter reporter_mass_shift is 0.002, but the command uses -extraction:reporter_mass_shift 0.01. A wider window could admit some interfering signal. This is unlikely to explain the compression on its own.
     - How to check: Check the effective value in the log (isobaricworkflow.log) and re-run with 0.002 for comparison.
- Recommendation: Treat quantified fold changes from this run as underestimated by about 20-25% at large ratios. If accurate ratios are needed, enable isotope correction with the correct matrix and apply a precursor purity filter. Do not interpret the CYC_BOVIN slope (3 PSMs) as evidence of over-recovery.
