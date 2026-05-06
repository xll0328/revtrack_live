# Cross-split Significance Summary

- Splits: `3`
- Bootstrap iterations: `5000`
- Seed: `20260428`

Interpretation:
- `P(anchor not better)` is paired-bootstrap risk for each split anchor.
- This captures sample uncertainty on the current labeled rows; it does not include annotator uncertainty.

## ICLR 2024 clean dev v7

- Rows: `148`
- Anchor model: `Structured`

| Model | Macro-F1 | 95% CI | Delta to anchor | P(anchor not better) |
| --- | ---: | ---: | ---: | ---: |
| Structured | 0.704 | [0.630, 0.775] | 0.000 | 1.000 |
| Structured (No Overrides) | 0.424 | [0.352, 0.494] | 0.280 | 0.000 |
| MPNet + LinearSVC | 0.389 | [0.320, 0.461] | 0.314 | 0.000 |
| ModernBERT + LinearSVC | 0.387 | [0.311, 0.464] | 0.317 | 0.000 |
| TF-IDF + LinearSVC | 0.376 | [0.305, 0.447] | 0.328 | 0.000 |
| Majority label | 0.184 | [0.184, 0.184] | 0.520 | 0.000 |

## ICLR 2025 expanded80 standard frontier

- Rows: `80`
- Anchor model: `Issue ledger`

| Model | Macro-F1 | 95% CI | Delta to anchor | P(anchor not better) |
| --- | ---: | ---: | ---: | ---: |
| Issue ledger | 0.469 | [0.323, 0.577] | 0.000 | 1.000 |
| Structured | 0.298 | [0.218, 0.352] | 0.171 | 0.060 |
| MPNet | 0.276 | [0.140, 0.372] | 0.193 | 0.000 |
| Majority label | 0.226 | [0.226, 0.226] | 0.243 | 0.000 |
| ModernBERT | 0.092 | [0.054, 0.134] | 0.377 | 0.000 |
| TF-IDF | 0.026 | [0.025, 0.028] | 0.443 | 0.000 |

## NeurIPS 2024 limit100 standard frontier

- Rows: `80`
- Anchor model: `MPNet`

| Model | Macro-F1 | 95% CI | Delta to anchor | P(anchor not better) |
| --- | ---: | ---: | ---: | ---: |
| MPNet | 0.348 | [0.299, 0.390] | 0.000 | 1.000 |
| Issue ledger | 0.211 | [0.173, 0.253] | 0.136 | 0.000 |
| Structured | 0.197 | [0.141, 0.250] | 0.150 | 0.000 |
| Majority label | 0.177 | [0.177, 0.177] | 0.170 | 0.000 |
| TF-IDF | 0.177 | [0.177, 0.177] | 0.170 | 0.000 |
| ModernBERT | 0.137 | [0.082, 0.193] | 0.211 | 0.000 |
