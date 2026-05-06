# NeurIPS 2024 limit100 active frontier Failure Taxonomy

Validation status: `provisional_assistant_adjudication_not_human_validation`

This taxonomy summarizes model error patterns for the active frontier. If the validation status is provisional, use it for review planning only; do not report it as benchmark evidence.

## Distribution

- Labels: `regressed`=4, `unresolved`=76
- Model errors: `Issue ledger`=9, `ModernBERT`=66, `MPNet`=48, `Structured`=75, `TF-IDF`=80

## Patterns

| failure mode | model | n | gold -> predicted | issue | risk | paper use |
| --- | --- | ---: | --- | --- | --- | --- |
| over_crediting_unresolved | TF-IDF | 76 | unresolved -> partially_fixed | `3ZAfFoAcUI__r02` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| over_crediting_unresolved | Structured | 44 | unresolved -> partially_fixed | `3BNPUDvqMt__r01` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| over_crediting_unresolved | ModernBERT | 36 | unresolved -> fixed | `owuEcT6BTl__r01` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| over_crediting_unresolved | MPNet | 30 | unresolved -> fixed | `3ZAfFoAcUI__r02` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| over_crediting_unresolved | Structured | 27 | unresolved -> fixed | `3ZAfFoAcUI__r02` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| over_crediting_unresolved | ModernBERT | 26 | unresolved -> partially_fixed | `LxxIiInmuF__r02` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| over_crediting_unresolved | MPNet | 18 | unresolved -> partially_fixed | `3BNPUDvqMt__r01` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| over_crediting_unresolved | Issue ledger | 5 | unresolved -> fixed | `3ZAfFoAcUI__r01` | over-credits an unresolved concern as resolved | A revision assistant would stop tracking an issue that still needs attention. |
| regression_blindness | ModernBERT | 4 | regressed -> fixed | `BRZYhVHvSg__r02` | misses a regression or newly worsened concern | Regression cases are rare but high-risk in revision workflows. |
| regression_blindness | Structured | 4 | regressed -> fixed | `BRZYhVHvSg__r02` | misses a regression or newly worsened concern | Regression cases are rare but high-risk in revision workflows. |
| regression_blindness | TF-IDF | 4 | regressed -> partially_fixed | `BRZYhVHvSg__r02` | misses a regression or newly worsened concern | Regression cases are rare but high-risk in revision workflows. |
| regression_blindness | Issue ledger | 3 | regressed -> partially_fixed | `BRZYhVHvSg__r02` | misses a regression or newly worsened concern | Regression cases are rare but high-risk in revision workflows. |

## Boundary

- Standard-label taxonomy requires a user-confirmed validation sheet.
- Provisional taxonomy is only a queue-prioritization and reviewer-risk artifact.
- Active-frontier counts should not be described as natural venue prevalence.
