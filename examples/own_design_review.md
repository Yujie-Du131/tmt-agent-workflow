# SDRF review: data/own_design

Model: `claude-sonnet-5-5`

## Design spec drafted from the description

```json
{
  "plex": "TMTpro16",
  "factors": {
    "compound": [
      "CPI-169",
      "DMSO"
    ],
    "antibody": [
      "EZH2",
      "IgG"
    ]
  },
  "replicates_per_condition": 3,
  "culture_defined_by": [
    "compound",
    "biological replicate"
  ],
  "within_culture_factor": "antibody",
  "uncertainties": [
    "Which four TMTpro channels are unused is not stated.",
    "Exact antibody level names (e.g. 'anti-EZH2' vs 'EZH2', 'rabbit IgG' vs 'IgG') are shortened; the description gives both forms.",
    "Whether biological replicate numbering is 1-3 within each compound or 1-6 across all cultures is not stated; assumed 1-3 within each compound.",
    "Channel-to-sample assignment is not stated."
  ]
}
```

Differences from the confirmed design.json: none.

## Rule checks

- [WARNING] unused_channels: 4 channel(s) not assigned to a sample: TMT132C, TMT133N, TMT133C, TMT134N. Confirm these were left empty in the experiment.

## Summary

The SDRF agrees with the description on cell line, organism, compound, antibody, 12-sample count, TMTpro 16-plex and trypsin. The only rule issue is the four unused channels, which the description explicitly expects. I found no mismatches or naming inconsistencies.

## Findings

### 1. [WARNING] rule_issue_explanation: comment[label]
- Evidence: Rule check: "4 channel(s) not assigned to a sample: TMT132C, TMT133N, TMT133C, TMT134N". The description says "Four channels are unused" and that 12 samples were labelled with one TMTpro 16-plex kit.
- Explanation: The 12 samples use TMT126 to TMT132N, leaving the last four TMTpro channels empty. This matches the description (16 - 12 = 4), so it is the expected design and not a labelling error. For analysis, the empty channels carry no sample and should be excluded from normalisation and from any reporter-ion quantification. Their signal should only be background or noise.
- Suggested fix: No change to the SDRF is needed. Optionally note in the project documentation that TMT132C, TMT133N, TMT133C and TMT134N were intentionally left empty.
