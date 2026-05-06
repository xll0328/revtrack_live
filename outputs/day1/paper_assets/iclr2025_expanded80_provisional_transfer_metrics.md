# ICLR 2025 Expanded80 Provisional Transfer Metrics

These metrics use provisional assistant-adjudicated labels from the expanded80 frontier. They are useful for internal triage and writing hypotheses, but they are not standard human-validation results and must not be reported as benchmark transfer performance.

| model | rows | accuracy | macro-F1 | fixed F1 | partial F1 | unresolved F1 | regressed F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| issue_ledger | 80 | 0.850 | 0.469 | 0.429 | 0.000 | 0.947 | 0.500 |
| structured | 80 | 0.150 | 0.298 | 0.229 | 0.163 | 0.000 | 0.800 |
| mpnet | 80 | 0.312 | 0.276 | 0.174 | 0.000 | 0.432 | 0.500 |
| modernbert | 80 | 0.125 | 0.092 | 0.056 | 0.170 | 0.141 | 0.000 |
| tfidf | 80 | 0.050 | 0.026 | 0.000 | 0.104 | 0.000 | 0.000 |

## Interpretation Boundary

- The label distribution is frontier-biased and risk-heavy.
- The result should guide adjudication and error analysis, not final claims.
- The next publishable step is standard labeling of `experiments/day1/iclr2025_expanded80_human_validation_v1_blind.tsv`.
