# Human Validation Pipeline Report

Status: `ok`
Mode: `dry-run`

## Summary

- Ingest status: `ok`
- Ingest errors: `0`
- Completed batch rows: `0`
- Merged rows: `0`
- Queue rows before ingest: `301`
- Queue rows after pipeline: `301`

## Evaluation Outputs

| packet | labeled | unlabeled | agreement | kappa | metrics |
| --- | --- | --- | --- | --- | --- |
| ICLR 2024 v1 | 40 | 0 | 1.000 | 1.000 | [metrics](outputs/day1/human_validation_batch_ingest/evaluation/iclr2024_human_validation_v1_pending_metrics.json) |
| ICLR 2025 repro v2 | 21 | 0 | 1.000 | 1.000 | [metrics](outputs/day1/human_validation_batch_ingest/evaluation/iclr2025_repro_human_validation_v2_pending_metrics.json) |
| ICLR 2025 expanded80 v1 | 80 | 0 | 1.000 | 1.000 | [metrics](outputs/day1/human_validation_batch_ingest/evaluation/iclr2025_expanded80_human_validation_v1_standard_metrics.json) |
| NeurIPS 2024 limit100 v1 | 80 | 0 | 0.450 | 0.039 | [metrics](outputs/day1/human_validation_batch_ingest/evaluation/neurips2024_limit100_human_validation_v1_pending_metrics.json) |
| ICLR 2023 random80 v1 | 80 | 0 | 1.000 | 1.000 | [metrics](outputs/day1/human_validation_batch_ingest/evaluation/iclr2023_limit80_random80_human_validation_v1_standard_metrics.json) |

## Readiness

- Overall status: `ready`
- Blockers: `0`
- Warnings: `0`

## Next Step

Dry run complete. Inspect preview metrics and the merged sheet copies; rerun with `--write-canonical` only after the batch annotations are approved.
