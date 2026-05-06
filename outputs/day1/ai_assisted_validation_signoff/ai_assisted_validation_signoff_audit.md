# AI-Assisted Validation Signoff Audit

Artifact: `outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff.tsv`
Overall status: `pass`
Rows: `61`
Errors: `0`
Warnings: `0`

## Six Review Passes

| pass | status | errors | warnings | summary |
| --- | --- | --- | --- | --- |
| pass_1_schema_identity | pass | 0 | 0 | Required fields, row identity, and rank ordering are valid. |
| pass_2_queue_coverage | pass | 0 | 0 | Signoff rows should exactly cover pending queue rows, or all queue rows after promotion. |
| pass_3_context_completeness | pass | 0 | 0 | Every signoff row should include full review, response, aligned context, and revision text. |
| pass_4_assistant_evidence | pass | 0 | 0 | Assistant labels and evidence should be valid and inspectable. |
| pass_5_non_blind_isolation | pass | 0 | 0 | AI-assisted signoff must stay separate from independent blind validation. |
| pass_6_high_risk_triage | pass | 0 | 0 | High-risk and minority-label rows should be visible early for final review. |

## pass_1_schema_identity

Required fields, row identity, and rank ordering are valid.

## pass_2_queue_coverage

Signoff rows should exactly cover pending queue rows, or all queue rows after promotion.

## pass_3_context_completeness

Every signoff row should include full review, response, aligned context, and revision text.

## pass_4_assistant_evidence

Assistant labels and evidence should be valid and inspectable.

Rows using context fallback evidence spans:
- `sLQb8q0sUi__r02`
- `HX5ujdsSon__r01`
- `AyXIDfvYg8__r03`
- `lF2aip4Scn__r02`
- `KS8mIvetg2__r02`
- `AyXIDfvYg8__r02`
- `dCHbFDsCZz__r01`
- `tEgrUrUuwA__r01`
- `AqN23oqraW__r04`
- `HX5ujdsSon__r03`
- `OsGUnYOzii__r04`
- `hv3SklibkL__r01`
- `AZGIwqCyYY__r03`
- `GN921JHCRw__r03`
- `KTtEICH4TO__r01`
- `OsGUnYOzii__r03`
- `5JWAOLBxwp__r04`
- `EmQSOi1X2f__r01`
- `tEgrUrUuwA__r04`
- `uGtfk2OphU__r01`

## pass_5_non_blind_isolation

AI-assisted signoff must stay separate from independent blind validation.

## pass_6_high_risk_triage

High-risk and minority-label rows should be visible early for final review.

Top audit-score cases:
| rank | issue | assistant | bucket | score |
| --- | --- | --- | --- | --- |
| 2 | My7lkRNnL9__r01 | unresolved | minority_unresolved | 24.620 |
| 3 | sLQb8q0sUi__r02 | unresolved | minority_unresolved | 24.620 |
| 4 | qBL04XXex6__r05 | unresolved | minority_unresolved | 22.620 |
| 5 | HX5ujdsSon__r01 | unresolved | minority_unresolved | 21.620 |
| 9 | KS8mIvetg2__r02 | fixed | structured_error | 20.620 |
| 10 | 9k0krNzvlV__r02 | partially_fixed | structured_error | 20.620 |
| 11 | ADDCErFzev__r02 | partially_fixed | structured_error | 20.620 |
| 12 | buC4E91xZE__r01 | partially_fixed | structured_error | 20.620 |
| 13 | buC4E91xZE__r04 | partially_fixed | structured_error | 20.620 |
| 41 | ONfWFluZBI__r01 | partially_fixed | structured_error | 19.550 |

## Interpretation

All six review passes are clean. The signoff artifact is ready for human final review.
