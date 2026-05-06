# Second Annotator IAA Mini-Slice Manifest

- sample size target: `60`
- selected rows: `60`
- blind sheet: `experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv`
- key sheet: `experiments/day1/iaa_second_annotator_mini60_v1_key.tsv`

## Label Distribution

| label | selected | candidate_pool |
| --- | ---: | ---: |
| regressed | 6 | 7 |
| fixed | 12 | 27 |
| unresolved | 25 | 135 |
| partially_fixed | 17 | 132 |

## Source Distribution

| source packet | selected |
| --- | ---: |
| ICLR 2023 random80 v1 | 47 |
| ICLR 2024 v1 | 6 |
| ICLR 2025 expanded80 v1 | 6 |
| ICLR 2025 repro v2 | 1 |

## Evaluation Command After Second-Pass Labeling

```bash
python scripts/evaluate_human_validation.py \
  --human-sheet experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv \
  --key experiments/day1/iaa_second_annotator_mini60_v1_key.tsv \
  --output-json outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_metrics.json \
  --mismatch-output outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_mismatches.tsv
```

Boundary: this packet is for independent second-pass agreement measurement only. Do not overwrite canonical first-pass standard labels.
