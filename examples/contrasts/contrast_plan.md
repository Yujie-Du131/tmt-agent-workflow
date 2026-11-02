# Contrast plan (DRAFT: for the analyst to confirm)

## Model

Cell-means design (`~ 0 + group`) with culture as a blocking factor (`duplicateCorrelation`). Each culture contributes one EZH2 and one IgG sample, so contrasts that compare samples within the same culture are estimated with the culture effect cancelled; contrasts that compare different cultures rely on the three independent cultures per treatment.

Reference levels (from design.json): compound = DMSO, antibody = IgG

## Contrasts

| Contrast | Definition | Stratum |
|---|---|---|
| EZH2_vs_IgG_in_DMSO | +1 EZH2.DMSO -1 IgG.DMSO | within-culture |
| EZH2_vs_IgG_in_CPI169 | +1 EZH2.CPI169 -1 IgG.CPI169 | within-culture |
| CPI169_vs_DMSO_in_IgG | -1 IgG.DMSO +1 IgG.CPI169 | between-culture |
| CPI169_vs_DMSO_in_EZH2 | -1 EZH2.DMSO +1 EZH2.CPI169 | between-culture |
| interaction | -1 EZH2.DMSO +1 EZH2.CPI169 +1 IgG.DMSO -1 IgG.CPI169 | within-culture |

## Proposed roles (LLM: `claude-sonnet-5-5`)

| Contrast | Role | Reason |
|---|---|---|
| EZH2_vs_IgG_in_DMSO | secondary | Shows EZH2-specific enrichment over IgG under vehicle conditions, which is one component of the interaction and a sanity check on the proximity labelling. |
| EZH2_vs_IgG_in_CPI169 | secondary | Shows EZH2-specific enrichment over IgG under CPI-169, which is the other component of the interaction. |
| CPI169_vs_DMSO_in_IgG | secondary | Checks how the drug changes background labelling with the IgG control, which is needed to interpret the interaction. |
| CPI169_vs_DMSO_in_EZH2 | secondary | Gives the drug effect on EZH2-antibody labelling, a component of the interaction, though on its own it does not remove background changes. |
| interaction | primary | The description names the antibody-by-treatment interaction as the main comparison: how CPI-169 changes EZH2 labelling relative to IgG. |

Reference levels proposed from the description:

- compound = DMSO: DMSO is the vehicle control; the description says three cultures were treated with DMSO vehicle versus CPI-169.
- antibody = IgG: Rabbit IgG is the isotype control for the anti-EZH2 antibody, and the description frames the question as labelling with the EZH2 antibody relative to the IgG control.

Checks on the proposal: passed.

## limma code

```r
library(limma)
samples   <- read.csv("samples.csv")
design    <- as.matrix(read.csv("design_matrix.csv", row.names = 1))
contrasts <- as.matrix(read.csv("contrast_matrix.csv", row.names = 1))
# y: log2 protein intensities, columns in the order of samples$sample
corfit <- duplicateCorrelation(y, design, block = samples$culture)
fit    <- lmFit(y, design, block = samples$culture,
                correlation = corfit$consensus.correlation)
fit2   <- eBayes(contrasts.fit(fit, contrasts))
topTable(fit2, coef = "interaction", number = Inf)
```
