# AI-Assisted Validation Signoff Manifest

This artifact is for final human review of assistant-generated judgments. It is non-blind, exposes assistant/model evidence, and must not be reported as independent human validation.

- Rows: `61`
- Needs human review: `61`
- Key evidence rows: `41`
- Context fallback evidence rows: `20`
- Signoff sheet: [ai_assisted_validation_signoff.tsv](outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff.tsv)
- Signoff packet: [ai_assisted_validation_signoff.html](outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff.html)

## Distributions

| field | distribution |
| --- | --- |
| assistant labels | fixed 18 / partially_fixed 35 / regressed 1 / unresolved 7 |
| audit buckets | label_stratum 4 / minority_regressed 1 / minority_unresolved 7 / model_disagreement 6 / model_high_conflict 10 / structured_error 33 |

## Required Human Action

For each row, fill `reviewer_decision` as `accept`, `revise`, or `defer`. Fill `reviewer_final_label`, `reviewer_confidence`, `reviewer_evidence_span`, and `reviewer_notes` for accepted or revised rows.
