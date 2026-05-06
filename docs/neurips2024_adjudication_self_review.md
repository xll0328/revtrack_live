# NeurIPS 2024 Adjudication Self-Review

Date: 2026-04-27

Scope: `experiments/day1/neurips2024_limit100_assistant_adjudication_v1.tsv` and the associated blind/key/audit validation packet.

## Review Verdict

Do **not** promote the raw assistant draft automatically to standard validation.

The earlier 783-row NeurIPS pool exposed an extraction bug: author rebuttals whose invitations contained `Official_Review*/-/Rebuttal` were misclassified as official reviews. That bug is fixed, the NeurIPS candidate pool has been rebuilt, and the old 73-regression draft is retired.

The repaired NeurIPS 2024 limit100 frontier is structurally ready for review: packet audit passes, row identity is clean, evidence spans are present, and provenance is correctly marked as not human validation.

A conservative resolved-label candidate now exists for all 80 rows. It downgrades the four provisional `regressed` rows to `partially_fixed` because none has strict same-axis negative-change evidence, and it upgrades weak `unresolved` rows only when concrete response/revision fix cues and model support agree. This is a standard-label candidate for user confirmation, not independent human validation.

## Self-Check Summary

| check | result | finding |
| --- | --- | --- |
| Extraction repair | pass | Author rebuttals are now classified as responses before official-review matching |
| Packet integrity | pass | 80 blind rows, 80 key rows, 80 audit rows; 0 errors, 0 warnings |
| Candidate gate | pass | 393 candidates, complete rate 1.000, 316 disagreement rows, 93 high-disagreement rows |
| Row identity | pass | adjudication, blind, key, and frontier IDs align exactly; no duplicates |
| Label/evidence completeness | pass | all draft rows have valid labels, confidence, and evidence spans |
| Provenance boundary | pass | all rows are explicitly `provisional_assistant_adjudication_not_human_validation` |
| Distribution sanity | warning | label distribution is concentrated: unresolved=76, regressed=4 |
| Model-support sanity | warning | 43 rows have only one model supporting the assistant label |
| Regression-cue sanity | pass | the 4 regressed rows have response/revision context |
| Resolved-candidate gate | pass | 80 resolved candidates; distribution: partially_fixed=44, unresolved=36 |

The audit report is `outputs/day1/paper_assets/neurips2024_limit100_assistant_adjudication_v1_audit.md`.

Additional guardrail: the standard-transfer exporter refuses to produce standard metrics while the NeurIPS blind sheet has empty `human_label` fields. This keeps provisional assistant adjudication separate from standard validation.

Review queue: `outputs/day1/paper_assets/neurips2024_limit100_review_queue.md` and `outputs/day1/paper_assets/neurips2024_limit100_review_queue.csv` rank all 80 rows by promotion risk.

Regression verification packet: `outputs/day1/paper_assets/neurips2024_limit100_regression_verification.md` and `outputs/day1/paper_assets/neurips2024_limit100_regression_verification.csv` now gate the 4 provisional `regressed` rows. It marks 3 rows as `manual_same_axis_check_required` and 1 row as `candidate_keep_regressed`; none are hard-blocked for missing response/revision context.

Resolved candidate artifacts:

- `experiments/day1/neurips2024_limit100_resolved_adjudication_v1.tsv`
- `experiments/day1/neurips2024_limit100_standard_label_candidate_blind.tsv`
- `outputs/day1/neurips2024_limit100_resolution_manifest.json`
- `outputs/day1/paper_assets/neurips2024_limit100_resolution_summary.md`
- `outputs/day1/neurips2024_limit100_standard_validation_promotion_dry_run.json`

Promotion dry-run status: `ok`; promotable rows: `80`; promoted canonical rows: `0`.

## Draft Label Distribution

| label | rows |
| --- | ---: |
| unresolved | 76 |
| regressed | 4 |

Confidence distribution:

| confidence | rows |
| --- | ---: |
| low | 43 |
| low_medium | 32 |
| medium | 5 |

Evidence source distribution:

| source | rows |
| --- | ---: |
| aligned_response_excerpt | 76 |
| revision_summary | 4 |

## Provisional Metrics Are Not Paper Results

The provisional metrics use assistant-draft labels and must not be reported as benchmark results.

| model | accuracy | macro-F1 | unresolved F1 | regressed F1 |
| --- | ---: | ---: | ---: | ---: |
| mpnet | 0.400 | 0.385 | 0.538 | 1.000 |
| issue_ledger | 0.887 | 0.340 | 0.959 | 0.400 |
| modernbert | 0.175 | 0.078 | 0.311 | 0.000 |
| structured | 0.062 | 0.031 | 0.123 | 0.000 |
| tfidf | 0.000 | 0.000 | 0.000 | 0.000 |

These numbers reflect the current frontier construction and assistant labels. Treat them as triage signals, not method results.

## Resolved Candidate Metrics

These metrics use the assistant-resolved candidate sheet with status `assistant_resolved_candidate_user_review_required`. They are useful for planning and sanity checking; report them as standard results only after the user-confirmed sheet is promoted through the canonical validation path.

| model | accuracy | macro-F1 | partial F1 | unresolved F1 |
| --- | ---: | ---: | ---: | ---: |
| mpnet | 0.550 | 0.348 | 0.516 | 0.875 |
| issue_ledger | 0.500 | 0.211 | 0.167 | 0.679 |
| structured | 0.362 | 0.197 | 0.545 | 0.244 |
| tfidf | 0.550 | 0.177 | 0.710 | 0.000 |
| modernbert | 0.200 | 0.137 | 0.229 | 0.320 |

Resolved-candidate outputs:

- `data/processed/neurips2024_limit100_resolved_candidate_validation_v1.jsonl`
- `outputs/day1/paper_assets/neurips2024_limit100_resolved_candidate_transfer_metrics.md`
- `outputs/day1/paper_assets/neurips2024_limit100_resolved_candidate_failure_taxonomy.md`

## Provisional Failure Taxonomy Preview

The provisional taxonomy is written to `outputs/day1/paper_assets/neurips2024_limit100_provisional_failure_taxonomy.md`. It is useful for review planning, but it is not paper-facing evidence until the 80 rows are standard-labeled.

Current preview:

- Label distribution: `unresolved=76`, `regressed=4`.
- Dominant provisional pattern: `over_crediting_unresolved`.
- Secondary provisional pattern: `regression_blindness` for the 4 regressed rows.
- Formal standard taxonomy should be regenerated after user-confirmed labels are promoted to the canonical blind sheet.

## Review Recommendation

Use the raw assistant draft as a review queue and the resolved candidate as the current user-confirmation candidate.

Priority order:

1. Inspect the 44 changed rows in `neurips2024_limit100_resolution_summary.md`.
2. Confirm that the four former `regressed` rows should be non-regression labels.
3. Spot-check upgraded weak-support rows where fix cues and open-scope cues both appear.
4. Promote to standard validation only after every row has a confirmed label, confidence, evidence span, and note.

## Current Safe Claim

Safe:

- NeurIPS 2024 limit100 is a feasible cross-venue active frontier after extraction repair.
- The full-stack candidate gate passes.
- A blind/key/audit validation packet exists and passes audit.
- A resolved 80-row standard-label candidate exists for user confirmation.

Not safe:

- NeurIPS independent human-validation results.
- NeurIPS transfer metrics as benchmark results before user-confirmed promotion.
- Cross-venue generalization.
- Natural NeurIPS label prevalence.
- Independent IAA.
