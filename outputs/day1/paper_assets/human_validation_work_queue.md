# Human Validation Work Queue

This is an assistant-generated triage queue. Treat it as workflow metadata only; validation claims must come from completed blind sheets or explicitly promoted user-confirmed signoff records with provenance.

## Summary

- Active packets: `5`
- Total rows: `301`
- Labeled rows: `301`
- Unlabeled rows: `0`

## Active Packets

| packet | rows | labeled | unlabeled | blind sheet | blind packet |
| --- | --- | --- | --- | --- | --- |
| ICLR 2024 v1 | 40 | 40 | 0 | [blind sheet](experiments/day1/iclr2024_human_validation_v1_blind.tsv) | [blind packet](outputs/day1/iclr2024_human_validation_v1_blind_packet.html) |
| ICLR 2025 repro v2 | 21 | 21 | 0 | [blind sheet](experiments/day1/iclr2025_repro_human_validation_v2_blind.tsv) | [blind packet](outputs/day1/iclr2025_repro_human_validation_v2_blind_packet.html) |
| ICLR 2025 expanded80 v1 | 80 | 80 | 0 | [blind sheet](experiments/day1/iclr2025_expanded80_human_validation_v1_blind.tsv) | [blind packet](outputs/day1/iclr2025_expanded80_human_validation_v1_blind_packet.html) |
| NeurIPS 2024 limit100 v1 | 80 | 80 | 0 | [blind sheet](experiments/day1/neurips2024_limit100_human_validation_v1_blind.tsv) | [blind packet](outputs/day1/neurips2024_limit100_human_validation_v1_blind_packet.html) |
| ICLR 2023 random80 v1 | 80 | 80 | 0 | [blind sheet](experiments/day1/iclr2023_limit80_random80_human_validation_v1_blind.tsv) | [blind packet](outputs/day1/iclr2023_limit80_random80_human_validation_v1_blind_packet.html) |

## Queue Policy

- Pending rows are placed before completed rows.
- Packet order is preserved, then rarer/high-risk audit buckets are prioritized.
- Within a bucket, higher audit_score and priority_score rows are reviewed first.

## Audit Bucket Distribution

| audit bucket | rows |
| --- | --- |
| label_stratum | 57 |
| minority_regressed | 11 |
| minority_unresolved | 175 |
| model_disagreement | 15 |
| model_high_conflict | 10 |
| structured_error | 33 |

## Assistant Label Distribution

| assistant label | rows |
| --- | --- |
| fixed | 27 |
| partially_fixed | 88 |
| regressed | 11 |
| unresolved | 175 |

## Top Pending Rows

| rank | packet | issue_id | bucket | assistant | score | next action |
| --- | --- | --- | --- | --- | --- | --- |
