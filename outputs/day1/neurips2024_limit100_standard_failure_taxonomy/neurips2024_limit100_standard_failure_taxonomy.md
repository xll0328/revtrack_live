# NeurIPS 2024 limit100 Failure Taxonomy

Validation status: `standard_single_user_confirmed`

This taxonomy summarizes model error patterns for the active frontier. If the validation status is provisional, use it for review planning only; do not report it as benchmark evidence.

## Distribution

- Labels: `partially_fixed`=44, `unresolved`=36
- Model errors: `Issue ledger`=40, `ModernBERT`=64, `MPNet`=36, `Structured`=51, `TF-IDF`=36

## Patterns

| failure mode | model | n | gold -> predicted | issue | risk | paper use |
| --- | --- | ---: | --- | --- | --- | --- |
| over_crediting_unresolved | TF-IDF | 36 | unresolved -> partially_fixed | `YO6GVPUrKN__r03` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| partial_under_crediting | Issue ledger | 34 | partially_fixed -> unresolved | `3BNPUDvqMt__r01` | ignores real but incomplete revision evidence | The model misses incremental progress that should not be collapsed into unresolved. |
| partial_vs_fixed_boundary | ModernBERT | 30 | partially_fixed -> fixed | `BRZYhVHvSg__r02` | upgrades partial evidence into a full fix | This is the central rubric-boundary risk for evidence-based labels. |
| partial_vs_fixed_boundary | MPNet | 24 | partially_fixed -> fixed | `3ZAfFoAcUI__r02` | upgrades partial evidence into a full fix | This is the central rubric-boundary risk for evidence-based labels. |
| over_crediting_unresolved | Structured | 20 | unresolved -> partially_fixed | `B3rZZRALhk__r02` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| partial_vs_fixed_boundary | Structured | 20 | partially_fixed -> fixed | `BRZYhVHvSg__r02` | upgrades partial evidence into a full fix | This is the central rubric-boundary risk for evidence-based labels. |
| over_crediting_unresolved | ModernBERT | 18 | unresolved -> partially_fixed | `B3rZZRALhk__r02` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| over_crediting_unresolved | Structured | 11 | unresolved -> fixed | `YO6GVPUrKN__r03` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| over_crediting_unresolved | ModernBERT | 10 | unresolved -> fixed | `owuEcT6BTl__r01` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| over_crediting_unresolved | MPNet | 6 | unresolved -> fixed | `YO6GVPUrKN__r03` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |

## Boundary

- Standard-label taxonomy requires a user-confirmed validation sheet.
- Provisional taxonomy is only a queue-prioritization and reviewer-risk artifact.
- Active-frontier counts should not be described as natural venue prevalence.
