# Second Annotator IAA Mini-Slice Manifest

- sample size target: `160`
- per-packet minimum: `20`
- per-packet maximum: `40`
- selected rows: `160`
- blind sheet: `experiments/day1/iaa_second_annotator_boundary160_v1_blind.tsv`
- key sheet: `experiments/day1/iaa_second_annotator_boundary160_v1_key.tsv`

## Label Distribution

| label | selected | candidate_pool |
| --- | ---: | ---: |
| regressed | 7 | 7 |
| fixed | 27 | 27 |
| unresolved | 66 | 135 |
| partially_fixed | 60 | 132 |

## Source Distribution

| source packet | selected |
| --- | ---: |
| ICLR 2023 random80 v1 | 40 |
| ICLR 2025 expanded80 v1 | 40 |
| NeurIPS 2024 limit100 v1 | 39 |
| ICLR 2024 v1 | 22 |
| ICLR 2025 repro v2 | 19 |

## Evaluation Command After Second-Pass Labeling

```bash
python scripts/evaluate_human_validation.py \
  --human-sheet experiments/day1/iaa_second_annotator_boundary160_v1_blind.tsv \
  --key experiments/day1/iaa_second_annotator_boundary160_v1_key.tsv \
  --output-json outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_metrics.json \
  --mismatch-output outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_mismatches.tsv
```

Boundary: this packet is for independent second-pass agreement measurement only. Do not overwrite canonical first-pass standard labels.
