# IAA Second Annotator Batch Plan

- total rows: `60`
- batches: `3`

## Batch Summary

| batch | rows | labels | sources | file |
| --- | ---: | --- | --- | --- |
| 1 | 20 | fixed:4, partially_fixed:4, regressed:2, unresolved:10 | ICLR 2023 random80 v1:8, ICLR 2024 v1:4, ICLR 2025 expanded80 v1:4, ICLR 2025 repro v2:2, NeurIPS 2024 limit100 v1:2 | `experiments/day1/iaa_second_annotator_mini60_v1_blind_batch1.tsv` |
| 2 | 20 | fixed:4, partially_fixed:4, regressed:2, unresolved:10 | ICLR 2023 random80 v1:7, ICLR 2024 v1:3, ICLR 2025 expanded80 v1:4, ICLR 2025 repro v2:3, NeurIPS 2024 limit100 v1:3 | `experiments/day1/iaa_second_annotator_mini60_v1_blind_batch2.tsv` |
| 3 | 20 | fixed:4, partially_fixed:4, regressed:2, unresolved:10 | ICLR 2023 random80 v1:5, ICLR 2024 v1:3, ICLR 2025 expanded80 v1:5, ICLR 2025 repro v2:3, NeurIPS 2024 limit100 v1:4 | `experiments/day1/iaa_second_annotator_mini60_v1_blind_batch3.tsv` |

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
