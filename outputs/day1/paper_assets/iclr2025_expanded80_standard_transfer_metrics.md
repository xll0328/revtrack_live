# ICLR 2025 Expanded80 Standard Transfer Metrics

These metrics use the user-confirmed standard expanded80 validation sheet. This is single-pass standard validation, not an independent two-annotator IAA result.

| model | rows | accuracy | macro-F1 | fixed F1 | partial F1 | unresolved F1 | regressed F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| issue_ledger | 80 | 0.850 | 0.469 | 0.429 | 0.000 | 0.947 | 0.500 |
| structured | 80 | 0.150 | 0.298 | 0.229 | 0.163 | 0.000 | 0.800 |
| mpnet | 80 | 0.312 | 0.276 | 0.174 | 0.000 | 0.432 | 0.500 |
| modernbert | 80 | 0.125 | 0.092 | 0.056 | 0.170 | 0.141 | 0.000 |
| tfidf | 80 | 0.050 | 0.026 | 0.000 | 0.104 | 0.000 | 0.000 |

## Reporting Boundary

- Report as standard single-user validation, not as inter-annotator agreement.
- The sample is a disagreement-focused standard single-user active frontier and should be described as hardened cross-year frontier evidence.
- Keep the 21-row ICLR 2025 repro result as a separate stress sample.
