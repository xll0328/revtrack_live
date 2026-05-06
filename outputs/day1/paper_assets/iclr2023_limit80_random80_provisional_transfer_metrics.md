# ICLR 2023 random80 stratified Provisional Transfer Metrics

These metrics use provisional assistant-adjudicated labels from an active frontier. They are useful for internal triage and hypothesis generation, but they are not standard human-validation results and must not be reported as benchmark transfer performance.

| model | rows | accuracy | macro-F1 | fixed F1 | partial F1 | unresolved F1 | regressed F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| issue_ledger | 80 | 1.000 | 0.750 | 1.000 | 1.000 | 1.000 | 0.000 |
| tfidf | 80 | 0.662 | 0.422 | 0.909 | 0.780 | 0.000 | 0.000 |

## Interpretation Boundary

- The label distribution is frontier-biased and risk-heavy.
- The result should guide adjudication and error analysis, not final claims.
- The next publishable step is standard labeling of the blind validation sheet.
