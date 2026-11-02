# QC benchmark (simulated data)

LLM: `claude-sonnet-5-5`, 3 run(s) per scenario.

- `threshold_baseline`: a channel in the planted set was flagged by |robust z| > 3.0 or paired-ratio slope < 0.7 (clean row: nothing flagged). The baseline gives no issue type.
- `llm_correct`: runs in which the report named the planted issue type for a planted channel (clean row: runs with no issues reported).
- `llm_extra_issues`: other issues reported, summed over runs; reviewed by hand.
| id                    | planted                           | threshold_baseline   | baseline_flagged          | llm_correct   |   llm_extra_issues |
|:----------------------|:----------------------------------|:---------------------|:--------------------------|:--------------|-------------------:|
| Q00_clean             | none                              | True                 |                           | 3/3           |                  0 |
| Q01_low_loading       | low_loading                       | True                 | R2_CPI_EZH2               | 3/3           |                  0 |
| Q02_ratio_compression | ratio_compression                 | True                 | R2_CPI_EZH2, R2_CPI_IgG   | 3/3           |                  0 |
| Q03_outlier_sample    | outlier_sample                    | True                 | R3_DMSO_IgG               | 3/3           |                  0 |
| Q04_label_swap        | label_swap                        | True                 | R1_DMSO_EZH2, R1_DMSO_IgG | 3/3           |                  0 |
| Q05_treatment_loading | loading_confounded_with_treatment | False                |                           | 3/3           |                  0 |
