# QC report on quantms output (shift0.002, run 2, model `claude-sonnet-5-5`)

**Overall:** major_issues

Four of the six channels (TMT126, 128, 130, 131) are well quantified and consistent: 465-468 proteins each, with raw medians of 20.26-20.59 and z-scores within ±1. Channels 2 (TMT127) and 4 (TMT129) are essentially empty, with 1 and 4 quantified proteins and robust z-scores of -34.5 and -27.5. This is a major issue and makes corr_to_others uncomputable. It most likely originates in reporter extraction or channel mapping, since the other channels come from the same spectra. A failed labelling of those two samples is also possible, and the raw reporter intensities should settle it. Spike-in slopes (0.74-0.88 for the well-supported proteins) show mild compression and are based on only four channels, so they should be re-assessed after the missing channels are fixed.

### 1. [major] ch2, ch4
- Observation: Two of the six TMT channels (ch2 = TMT127, ch4 = TMT129) have almost no quantified proteins, while the other four channels have about 465-468 each. The metrics show the channels are effectively missing. That also explains why corr_to_others is NaN for every channel, because too few proteins are quantified in all channels. The low raw_median values in ch2 and ch4 come from only 1 and 4 proteins, so they are not interpretable as real signal levels.
- Evidence: n_quantified: ch1=465, ch2=1, ch3=468, ch4=4, ch5=468, ch6=468. raw_median: ch2=11.363, ch4=13.187 vs 20.264-20.587 in the others. raw_median_z: ch2=-34.490, ch4=-27.485 vs -0.299 to 0.944. corr_to_others is NaN in all channels.
- Likely causes:
  1. Reporter-ion extraction or channel assignment fails for TMT127 and TMT129 (inference). Possible reasons are a mismatch between the SDRF comment[label] values and the tmt6plex reporter masses, or the extraction tolerance being too tight for these two channels.
     - Reasoning: The other four channels (126, 128, 130, 131) are quantified for nearly all proteins from the same spectra, so identification and the spectra themselves are fine. The failure is specific to two channels, which points to the reporter extraction or the label-to-channel mapping. The reporter_mass_shift of 0.002 is a very narrow window, and a small systematic mass offset could drop some reporters.
     - How to check: Check the reporter-ion m/z values in the raw/mzML MS2 spectra: 127.1248 for TMT127 and 129.1315 for TMT129, with exact values from the tmt6plex definition. Compare their intensities with the 126 channel. Look at the IsobaricWorkflow log and the consensusXML/mzTab channel columns for 127 and 129. Check that the _openms_design.tsv labels map 1-6 to TMT126-TMT131. Re-run with a wider reporter_mass_shift, e.g. 0.01 Da.
  2. The two samples were genuinely empty or the labelling failed for these channels (inference).
     - Reasoning: If the labelling reaction or the pooling failed for these two samples, their reporters would be at noise level. The low medians of the few quantified proteins are consistent with noise. This is less likely for a public reference dataset where all six channels are expected to carry signal.
     - How to check: Inspect raw reporter-ion intensities for 127 and 129 across all MS2 spectra. Check whether they are consistently near noise. Check the TMT labelling efficiency (fraction of PSMs with TMT on N-terminus and lysine) and the sample pooling records.
  3. Filtering during protein quantification or a quantification-step bug removes these channels (less likely).
     - Reasoning: min_reporter_intensity is 0.0, min_precursor_purity is 0.0, and isotope_correction and normalization are off, so the stated settings do not explain selective loss. A side effect of the aggregation or unique_peptides settings in the pipeline cannot be excluded without the logs.
     - How to check: Compare PSM-level or peptide-level reporter intensities for ch2 and ch4 in the consensusXML with the protein-level table to see where the values disappear.
- Recommendation: Do not use ch2 and ch4 for any downstream analysis until the cause is found. First inspect the raw reporter intensities at 127.1248 and 129.1315 and verify the label-to-channel mapping in the SDRF and design file. If the signal is present in the spectra, re-run IsobaricWorkflow with a wider reporter mass window. If the signal is absent, treat the samples as failed.

### 2. [minor] ch1, ch3, ch5, ch6
- Observation: Spike-in recovery is somewhat compressed for ALBU and PYGM, but only four channels contribute. The two missing channels remove the mid-level ENO1 sample (ch2, 5 units) and the extreme points for ENO1 (1 unit in ch4) and ALBU (10 units in ch4). This reduces the quantified dynamic range and makes the slopes less reliable. CYC has only 3 PSMs and a slope above 1. Its expected log2 range is 1 and only ch6 differs, so this value is not informative.
- Evidence: Slopes: P00924 (ENO1) 0.882 (31 PSMs, expected range 3.322 log2); P02769 (ALBU) 0.740 (31 PSMs, 3.322); P00489 (PYGM) 0.753 (48 PSMs, range 1.000); P62894 (CYC) 1.156 (3 PSMs, range 1.000). isotope_correction=false, normalize=false.
- Likely causes:
  1. Ratio compression from co-isolation interference and uncorrected isotope impurities (inference).
     - Reasoning: Slopes below 1 are typical of TMT MS2 quantification with co-isolation. isotope_correction is false and min_precursor_purity is 0.0, so neither is mitigated. The 0.74-0.75 values are moderately below 1.
     - How to check: Check the precursor purity distribution. Re-run with isotope_correction using a plex correction matrix and with min_precursor_purity > 0, e.g. 0.5-0.75, and see whether the slopes improve.
  2. The slopes are computed from only the 4 working channels, so they are less robust (inference).
     - Reasoning: With four points and the 127 and 129 channels absent, the fit is sensitive to single channels. The slopes may change once the missing channels are recovered.
     - How to check: After fixing ch2 and ch4, recompute the slopes on all six channels and compare. For CYC and PYGM, check the per-channel measured vs expected values.
- Recommendation: Re-evaluate spike-in recovery once all six channels are quantified. If compression persists, consider isotope correction and a purity filter. Do not interpret the CYC slope because it rests on 3 PSMs.
