# QC report on quantms output (shift0.002, run 3, model `claude-sonnet-5-5`)

**Overall:** major_issues

Major problem: ch2 (TMT127) and ch4 (TMT129) have 1 and 4 quantified proteins respectively, against about 465-468 in the other channels, and corr_to_others is NaN for every channel as a result. The likely culprit is reporter-ion extraction (reporter_mass_shift = 0.002 Da is very narrow) or a labelling or sample problem in those two channels. The four functioning channels (ch1, ch3, ch5, ch6) look consistent, with similar protein counts and medians (z between -0.3 and 0.9). Spike-in recovery in those channels is mildly compressed (slopes 0.74-0.88, partly computed on a reduced set of channels), which is a minor issue and should be re-evaluated after the channel problem is resolved.

### 1. [major] ch2, ch4
- Observation: Two of the six TMT channels (ch2 = TMT127, ch4 = TMT129) have almost no quantified proteins, while the other four channels each have about 465-468. The raw medians of ch2 and ch4 are far below the others, but they rest on 1 and 4 proteins, so they are not meaningful. As a result, corr_to_others is NaN for all channels, because too few proteins are quantified in every channel. This is what the metrics show. Both channels are effectively lost, and the 6-plex cannot be compared across all channels.
- Evidence: n_quantified: ch1=465, ch2=1, ch3=468, ch4=4, ch5=468, ch6=468. raw_median: ch2=11.363 (z=-34.490), ch4=13.187 (z=-27.485), versus 20.264-20.587 (|z|<1) for ch1, ch3, ch5 and ch6. corr_to_others is NaN in all channels. Pipeline: reporter_mass_shift=0.002, min_reporter_intensity=0.0, isotope_correction=false, -type tmt6plex, reference_channel=126.
- Likely causes:
  1. Reporter-ion extraction tolerance too tight for the data (reporter_mass_shift = 0.002 Da). Reporter peaks in ch2 and ch4 fall outside the window, for example because of mass calibration offset, so they are not matched in most spectra.
     - Reasoning: Only ch2 and ch4 fail, and the other channels are fully populated, so identification and the PSM and protein filters are not the cause. Both failing channels sit at fixed reporter masses (127 and 129), so a systematic extraction problem tied to those masses would match the pattern. A ±2 mDa window is very narrow for Orbitrap Velos HCD data, and the tolerance interpretation depends on the IsobaricWorkflow version. This is an inference.
     - How to check: Look at the reporter-ion m/z region in the raw or mzML MS2 spectra for peaks near 127.1248 and 129.1315. Check the observed mass error against the expected reporter masses. Rerun IsobaricWorkflow with a larger reporter_mass_shift (for example 0.01-0.02 Da) and see whether n_quantified for ch2 and ch4 recovers.
  2. Physical or labelling failure in these two channels: the reagent was missing or hydrolysed, or the sample was not added or was lost.
     - Reasoning: Identical failure in two non-adjacent channels could come from a bad aliquot or failed labelling of those two samples. The SDRF describes all six samples as having spike-ins, so empty channels would be unexpected. Typically a failed channel would still show some background intensity rather than almost no signal, so this is less likely than an extraction problem.
     - How to check: Inspect raw reporter-ion intensities at m/z 127.12 and 129.13 in the MS2 spectra. Check the lab records for the TMT labelling step. Check the labelling efficiency (TMT-modified N-termini and lysines) in the search results.
  3. Mismatch between the SDRF/experimental design and the actual labels, such as a wrong label-to-sample mapping in PXD000001.sdrf_openms_design.tsv or a wrong plex type.
     - Reasoning: If the design file assigned labels incorrectly, some channels would be empty or misassigned. The -type tmt6plex setting and the TMT126-TMT131 labels in the SDRF look consistent with each other, so this is less likely.
     - How to check: Open PXD000001.sdrf_openms_design.tsv and confirm the channel numbers and the label-to-sample mapping. Check the IsobaricWorkflow log (isobaricworkflow.log) for warnings about channels.
- Recommendation: Do not use ch2 and ch4 or any cross-channel comparison that includes them until the cause is found. First inspect reporter-ion peaks in the raw spectra and test a wider reporter_mass_shift. Then check the design file and the labelling records. Rerun quantification and confirm that n_quantified is about 465 in all six channels.

### 2. [minor] ch1, ch3, ch5, ch6
- Observation: Spike-in recovery is compressed relative to the expected ratios for the two proteins with the largest expected range: slopes are 0.74 and 0.88 against 1. The slopes were computed only on the channels where the protein was quantified, probably the four working channels, so they are less reliable and the effective expected range is smaller than listed. CYC_BOVIN rests on only 3 PSMs and has a slope above 1, which is probably noise.
- Evidence: Slope: ENO1_YEAST=0.882 (31 PSMs, expected range 3.322), ALBU_BOVIN=0.740 (31 PSMs, expected range 3.322), PYGM_RABIT=0.753 (48 PSMs, range 1.000), CYC_BOVIN=1.156 (3 PSMs, range 1.000). Parameters: isotope_correction=false, min_precursor_purity=0.0, normalize=false.
- Likely causes:
  1. Ratio compression from co-isolated precursors (no precursor purity filter, min_precursor_purity=0.0) and no isotope impurity correction (isotope_correction=false).
     - Reasoning: These are typical causes of compressed TMT ratios, and the compression is mild (0.74-0.88). This is an inference.
     - How to check: Rerun with isotope_correction enabled and with a plex_corr_matrix_file. Test a min_precursor_purity of about 0.5-0.7 and see if the slopes move toward 1.
  2. Limited or distorted range in the channels used for the fit, because ch2 and ch4 are missing.
     - Reasoning: With ch4 missing, the available ENO1 levels span only 10 to 2.5 instead of 10 to 1, and ALBU's lowest and highest points are also reduced. The fitted slope is then less constrained, and the spike-in test cannot be fully assessed. This is an inference.
     - How to check: Fix ch2 and ch4 first, then recompute the slopes on all six channels.
  3. Low PSM count for CYC_BOVIN (3 PSMs) leading to a noisy slope.
     - Reasoning: With few PSMs, a slope of 1.156 against an expected range of 1.0 is within expected noise.
     - How to check: Check the number of PSMs and the scatter of the individual PSM-level values for P62894.
- Recommendation: Treat the spike-in results as provisional. Re-evaluate them after repairing ch2 and ch4, and consider enabling isotope correction and a precursor purity filter.
