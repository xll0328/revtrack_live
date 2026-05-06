# Fine-Tuned ModernBERT Probe (2026-05-06)

Model: `answerdotai/ModernBERT-base` (classification head fine-tuned)  
Train set: `data/processed/iclr2024_train_v8.jsonl` (`180` rows)  
Eval splits: clean-dev + three transfer splits  
Command: `scripts/run_transformer_classifier_transfer.py`  
Output dir: `outputs/day1/strong_baselines/modernbert_finetune_v1/`

## Summary Metrics

| Split | Rows | Accuracy | Macro-F1 | fixed F1 | partial F1 | unresolved F1 | regressed F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ICLR 2024 clean dev v7 | 148 | 0.797 | 0.553 | 0.733 | 0.854 | 0.625 | 0.000 |
| ICLR 2025 expanded80 | 80 | 0.038 | 0.033 | 0.056 | 0.077 | 0.000 | 0.000 |
| NeurIPS 2024 limit100 | 80 | 0.325 | 0.134 | 0.000 | 0.536 | 0.000 | 0.000 |
| ICLR 2023 random80 | 80 | 0.450 | 0.219 | 0.211 | 0.667 | 0.000 | 0.000 |

## Readout

- This is a stronger learned baseline than frozen-encoder + linear-head probes, but transfer brittleness remains severe under current split design.
- The probe improves in-domain accuracy/F1 relative to weaker semantic baselines, yet still collapses unresolved/regressed recovery on transfer.
- Treat this as a single-run diagnostic probe (not yet a multi-seed final baseline package).
