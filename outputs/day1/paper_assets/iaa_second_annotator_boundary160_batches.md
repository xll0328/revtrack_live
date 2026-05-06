# IAA Second Annotator Batch Plan

- total rows: `160`
- batches: `4`

## Batch Summary

| batch | rows | labels | sources | file |
| --- | ---: | --- | --- | --- |
| 1 | 40 | fixed:7, partially_fixed:15, regressed:2, unresolved:16 | ICLR 2023 random80 v1:11, ICLR 2024 v1:5, ICLR 2025 expanded80 v1:11, ICLR 2025 repro v2:4, NeurIPS 2024 limit100 v1:9 | `experiments/day1/iaa_second_annotator_boundary160_v1_blind_batch1.tsv` |
| 2 | 40 | fixed:7, partially_fixed:15, regressed:2, unresolved:16 | ICLR 2023 random80 v1:9, ICLR 2024 v1:6, ICLR 2025 expanded80 v1:10, ICLR 2025 repro v2:5, NeurIPS 2024 limit100 v1:10 | `experiments/day1/iaa_second_annotator_boundary160_v1_blind_batch2.tsv` |
| 3 | 40 | fixed:7, partially_fixed:15, regressed:1, unresolved:17 | ICLR 2023 random80 v1:10, ICLR 2024 v1:5, ICLR 2025 expanded80 v1:9, ICLR 2025 repro v2:6, NeurIPS 2024 limit100 v1:10 | `experiments/day1/iaa_second_annotator_boundary160_v1_blind_batch3.tsv` |
| 4 | 40 | fixed:6, partially_fixed:15, regressed:2, unresolved:17 | ICLR 2023 random80 v1:10, ICLR 2024 v1:6, ICLR 2025 expanded80 v1:10, ICLR 2025 repro v2:4, NeurIPS 2024 limit100 v1:10 | `experiments/day1/iaa_second_annotator_boundary160_v1_blind_batch4.tsv` |

## Aggregation After Batch Labeling

1. Merge batch files back into `experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv`.
2. Run:

```bash
python scripts/evaluate_human_validation.py \
  --human-sheet experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv \
  --key experiments/day1/iaa_second_annotator_mini60_v1_key.tsv \
  --output-json outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_metrics.json \
  --mismatch-output outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_mismatches.tsv
```
