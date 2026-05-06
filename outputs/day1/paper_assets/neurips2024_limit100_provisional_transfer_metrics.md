# NeurIPS 2024 limit100 active frontier Provisional Transfer Metrics

These metrics use provisional assistant-adjudicated labels from an active frontier. They are useful for internal triage and hypothesis generation, but they are not standard human-validation results and must not be reported as benchmark transfer performance.

| model | rows | accuracy | macro-F1 | fixed F1 | partial F1 | unresolved F1 | regressed F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mpnet | 80 | 0.400 | 0.385 | 0.000 | 0.000 | 0.538 | 1.000 |
| issue_ledger | 80 | 0.887 | 0.340 | 0.000 | 0.000 | 0.959 | 0.400 |
| modernbert | 80 | 0.175 | 0.078 | 0.000 | 0.000 | 0.311 | 0.000 |
| structured | 80 | 0.062 | 0.031 | 0.000 | 0.000 | 0.123 | 0.000 |
| tfidf | 80 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

## Interpretation Boundary

- The label distribution is frontier-biased and risk-heavy.
- The result should guide adjudication and error analysis, not final claims.
- The next publishable step is standard labeling of the blind validation sheet.
