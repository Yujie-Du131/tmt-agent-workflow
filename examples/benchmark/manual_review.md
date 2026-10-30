# Manual review of LLM findings outside the corrupted column

The automatic score counts any semantic finding on a column other than the
corrupted one as "other". This is not the same as a false alarm, so every
such finding was read and classified by hand.

## Pilot run (1 run per file, original prompt)

| Case | Finding | Verdict |
|---|---|---|
| A03_missing_sample | SDRF has 11 rows; description states 12 samples | Correct: restates the corruption |
| A08_duplicate_source_name | Row 10 is named EZH2 but annotated as IgG | Correct: identifies the root cause |
| A09_replicate_number_shift | Suggests capitalising "homo sapiens" | **False alarm**: lowercase is the SDRF convention, and the description says nothing about it |

After this pilot, rule 5 ("do not comment on formatting conventions") was
added to the review prompt. The pilot cases therefore informed the prompt,
so the final run below is not a fully held-out evaluation.

## Final run (3 runs per file, revised prompt)

All 10 findings outside the corrupted column were correct. None was a
false alarm, and the clean SDRF produced no findings in any run.

| Case | Runs | Finding | Verdict |
|---|---|---|---|
| A03_missing_sample | 3/3 | SDRF has 11 rows; description states 12 samples | Correct: restates the corruption |
| A04_antibody_mislabelled | 3/3 | Source name R1_DMSO_IgG conflicts with antibody annotation EZH2 | Correct: identifies the root cause |
| A08_duplicate_source_name | 2/3 | Row 10 is named EZH2 but annotated as IgG | Correct: identifies the root cause |
| A09_replicate_number_shift | 2/3 | Source name R2_CPI_IgG conflicts with biological replicate 3 | Correct: identifies the root cause |

## Caveat

The diagnoses for A04, A08 and A09 rely on source names that encode the
design (e.g. R2_CPI_IgG). With uninformative names (S1, S2, ...), the LLM
could only restate the rule-check symptoms.
