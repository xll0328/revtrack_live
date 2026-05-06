# ICLR 2023 random80 resolved candidate Failure Taxonomy

Validation status: `assistant_resolved_candidate_not_human_validation`

This taxonomy summarizes model error patterns for the active frontier. If the validation status is provisional, use it for review planning only; do not report it as benchmark evidence.

## Distribution

- Labels: `fixed`=5, `partially_fixed`=49, `unresolved`=26
- Model errors: `Issue ledger`=0, `TF-IDF`=27

## Patterns

| failure mode | model | n | gold -> predicted | issue | risk | paper use |
| --- | --- | ---: | --- | --- | --- | --- |
| over_crediting_unresolved | TF-IDF | 26 | unresolved -> partially_fixed | `hChYEyebNm1__r03` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| partial_vs_fixed_boundary | TF-IDF | 1 | partially_fixed -> fixed | `QN_VgTeOYGl__r01` | upgrades partial evidence into a full fix | This is the central rubric-boundary risk for evidence-based labels. |

## Boundary

- Standard-label taxonomy requires a user-confirmed validation sheet.
- Provisional taxonomy is only a queue-prioritization and reviewer-risk artifact.
- Active-frontier counts should not be described as natural venue prevalence.
