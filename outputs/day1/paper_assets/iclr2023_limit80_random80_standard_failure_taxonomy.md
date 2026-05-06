# ICLR 2023 random80 standard slice Failure Taxonomy

Validation status: `standard_single_user_confirmed`

This taxonomy summarizes model error patterns for a user-confirmed random/stratified slice. Report it by measured slice design; do not use it as an unmeasured natural-prevalence estimate.

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
- Random/stratified slice counts should be reported by measured design, not as unmeasured natural venue prevalence.
