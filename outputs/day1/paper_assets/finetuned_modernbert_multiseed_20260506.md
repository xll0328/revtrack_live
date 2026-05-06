# Fine-Tuned ModernBERT Multi-Seed Probe (2026-05-06)

Seeds: `3`

Seed run dirs:
- `/data/sony/emnlp2026_revtrack/outputs/day1/strong_baselines/modernbert_finetune_seed7`
- `/data/sony/emnlp2026_revtrack/outputs/day1/strong_baselines/modernbert_finetune_seed13`
- `/data/sony/emnlp2026_revtrack/outputs/day1/strong_baselines/modernbert_finetune_seed42`

| Split | Rows | Accuracy | Macro-F1 | Unresolved F1 | Fixed F1 | Regressed F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| iclr2023_random80 | 80 | 0.433 ± 0.016 | 0.211 ± 0.008 | 0.022 ± 0.031 | 0.188 ± 0.063 | 0.000 ± 0.000 |
| iclr2024_clean_dev_v7 | 148 | 0.739 ± 0.016 | 0.531 ± 0.021 | 0.671 ± 0.065 | 0.662 ± 0.026 | 0.000 ± 0.000 |
| iclr2025_expanded80 | 80 | 0.054 ± 0.012 | 0.047 ± 0.010 | 0.000 ± 0.000 | 0.073 ± 0.016 | 0.000 ± 0.000 |
| neurips2024_limit100 | 80 | 0.329 ± 0.012 | 0.141 ± 0.007 | 0.017 ± 0.024 | 0.000 ± 0.000 | 0.000 ± 0.000 |

Readout:
- In-domain performance is materially higher than simple semantic baselines.
- Transfer unresolved/regressed recovery remains near-zero across seeds on frontier splits.
- This supports a stronger version of the transfer-brittleness claim while reducing single-seed variance concerns.
