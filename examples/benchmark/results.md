# Corrupted-SDRF benchmark

LLM: `claude-sonnet-5-5`, 3 run(s) per file.

- `sdrf_pipelines`: the official validator reported an error.
- `rules`: for category A, every expected rule fired; for other rows, True means rules.py reported an error (unexpected).
- `llm_semantic`: runs in which the LLM reported a mismatch on the corrupted column.
- `llm_other_findings`: LLM findings on columns that were not corrupted (summed over runs; review these for false alarms).
| id                               | category   | sdrf_pipelines   | rules   | rule_errors                                      | llm_semantic   |   llm_other_findings |
|:---------------------------------|:-----------|:-----------------|:--------|:-------------------------------------------------|:---------------|---------------------:|
| 00_clean                         | -          | False            | False   |                                                  | -              |                    0 |
| A01_duplicate_channel            | A          | False            | True    | unique_channel                                   | -              |                    0 |
| A02_label_outside_plex           | A          | False            | True    | label_in_plex                                    | -              |                    0 |
| A03_missing_sample               | A          | False            | True    | balance, pairing                                 | -              |                    3 |
| A04_antibody_mislabelled         | A          | False            | True    | balance, pairing                                 | -              |                    3 |
| A05_factor_disagrees             | A          | False            | True    | balance, factor_matches_characteristics, pairing | -              |                    0 |
| A06_misspelt_level               | A          | False            | True    | balance, factor_levels, pairing                  | 3/3            |                    0 |
| A07_inconsistent_tolerance       | A          | False            | True    | run_level_consistency                            | -              |                    0 |
| A08_duplicate_source_name        | A          | True             | True    | unique_source_name                               | -              |                    2 |
| A09_replicate_number_shift       | A          | False            | True    | pairing                                          | -              |                    2 |
| B01_wrong_cell_line              | B          | False            | False   |                                                  | 3/3            |                    0 |
| B02_wrong_enzyme                 | B          | False            | False   |                                                  | 3/3            |                    0 |
| B03_wrong_organism               | B          | False            | False   |                                                  | 3/3            |                    0 |
| B04_wrong_tmt_reagent            | B          | False            | False   |                                                  | 3/3            |                    0 |
| B05_wrong_disease                | B          | False            | False   |                                                  | 3/3            |                    0 |
| B06_treatment_swapped_names_kept | B          | False            | False   |                                                  | 3/3            |                    0 |
| C01_channels_swapped             | C          | False            | False   |                                                  | 0/3            |                    0 |
