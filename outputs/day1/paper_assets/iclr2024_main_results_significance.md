# ICLR 2024 Main-Results Significance

- Dataset: `data/processed/iclr2024_clean_dev_assistant_v7.jsonl`
- Rows: `148`
- Bootstrap iterations: `5000`
- Seed: `20260428`

| Model | Macro-F1 | 95% CI | Δ vs Structured | P(Structured not better) |
| --- | ---: | ---: | ---: | ---: |
| Structured | 0.704 | [0.630, 0.775] | 0.000 | 1.000 |
| Structured (No Overrides) | 0.424 | [0.352, 0.494] | 0.280 | 0.000 |
| MPNet + LinearSVC | 0.389 | [0.320, 0.461] | 0.314 | 0.000 |
| ModernBERT + LinearSVC | 0.387 | [0.311, 0.464] | 0.317 | 0.000 |
| TF-IDF + LinearSVC | 0.376 | [0.305, 0.447] | 0.328 | 0.000 |
| Majority label | 0.184 | [0.184, 0.184] | 0.520 | 0.000 |

Interpretation:
- `P(Structured not better)` is a paired-bootstrap risk indicator; lower is stronger evidence for Structured.
- This assesses sample uncertainty only on the current labeled split and does not include annotator uncertainty.
