## Final run (3 runs per scenario, prompt with rule 6)

All six scenarios were classified correctly in 3/3 runs, with no extra
issues and no findings on the clean data.

Direction of bias for Q02 (rule 6): stated correctly in 3/3 runs. Each run
said that compression of the EZH2 channel in one CPI-169 culture biases the
interaction towards an apparent loss of EZH2-specific labelling under
CPI-169 for EZH2-enriched proteins (two runs added that the sign reverses
for proteins depleted in EZH2). A technical artefact could therefore be
read as the biological result of interest.

Errors found on review (2 of 3 runs):

- Run 3 says the channel was compressed "toward the IgG level". In the
  simulation it is pulled towards the mean of all 12 channels, which lies
  between EZH2 and IgG; the conclusion holds, but the mechanism is imprecise.
- Run 1 says compression would "reduce the apparent CPI-169 vs DMSO change
  in the EZH2 channels" for enriched proteins. The opposite is true: pulling
  R2_CPI_EZH2 towards the mixture mean lowers the CPI-169 EZH2 mean, which
  creates or exaggerates an apparent decrease. This contradicts the run's own
  (correct) statement about the interaction.

The classifications and the main impact statements were reliable; secondary
mechanistic statements were not always correct and need expert review.
