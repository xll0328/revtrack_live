# Human Validation Pipeline Report

Status: `ok`
Mode: `dry-run`

## Summary

- Ingest status: `ok`
- Ingest errors: `0`
- Completed batch rows: `0`
- Merged rows: `0`
- Queue rows before ingest: `80`
- Queue rows after pipeline: `80`

## Evaluation Outputs

| packet | labeled | unlabeled | agreement | kappa | metrics |
| --- | --- | --- | --- | --- | --- |
| NeurIPS 2024 Limit100 | 0 | 80 | NA | NA | [metrics](outputs/day1/human_validation_batch_ingest/evaluation/neurips2024_limit100_human_validation_v1_pending_metrics.json) |

## Next Step

Dry run complete. Inspect preview metrics and the merged sheet copies; rerun with `--write-canonical` only after the batch annotations are approved.
