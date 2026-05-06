# NeurIPS 2024 limit100 active frontier Regression Verification Packet

Rows: `4` regressed draft labels

This packet verifies whether provisional `regressed` labels have enough response/revision evidence to survive standard-label review. It is a review aid, not a human-validation result.

## Summary

- Risk tiers: `tier_3_regression_candidate_needs_confirmation`=3, `tier_4_regressed_candidate`=1
- Standard-label gates: `candidate_keep_regressed`=1, `manual_same_axis_check_required`=3
- Evidence sources: `revision_summary`=4

## Highest Priority Verification Rows

| rank | review rank | issue | tier | gate | evidence | support | context | action |
| ---: | ---: | --- | --- | --- | --- | ---: | --- | --- |
| 1 | 1 | `BRZYhVHvSg__r02` | tier_3_regression_candidate_needs_confirmation | manual_same_axis_check_required | revision_summary | 1 | present | Confirm the cited response/revision text really worsens, removes, contradicts, or degrades the original concern. |
| 2 | 2 | `BRZYhVHvSg__r03` | tier_3_regression_candidate_needs_confirmation | manual_same_axis_check_required | revision_summary | 1 | present | Confirm the cited response/revision text really worsens, removes, contradicts, or degrades the original concern. |
| 3 | 3 | `DAO2BFzMfy__r04` | tier_3_regression_candidate_needs_confirmation | manual_same_axis_check_required | revision_summary | 1 | present | Confirm the cited response/revision text really worsens, removes, contradicts, or degrades the original concern. |
| 4 | 44 | `eHzIwAhj06__r03` | tier_4_regressed_candidate | candidate_keep_regressed | revision_summary | 2 | present | Regression cues exist in response/revision context, but still require final standard-label confirmation. |

## Promotion Rule

- `tier_1_block_regressed` rows should not remain `regressed` unless missing response/revision context is recovered.
- `tier_2` and `tier_3` rows require same-axis response/revision evidence before promotion.
- This packet does not create standard validation labels; it narrows the review work before filling the blind sheet.
