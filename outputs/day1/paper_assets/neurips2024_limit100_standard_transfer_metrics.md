# neurips2024_limit100 Standard Transfer Metrics

These metrics use a validation sheet with status `standard_single_user_confirmed_2026_04_28`. Report them only under that provenance boundary; this is not an independent two-annotator IAA result unless a separate IAA pass exists.

| model | rows | accuracy | macro-F1 | fixed F1 | partial F1 | unresolved F1 | regressed F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mpnet | 80 | 0.550 | 0.348 | 0.000 | 0.516 | 0.875 | 0.000 |
| issue_ledger | 80 | 0.500 | 0.211 | 0.000 | 0.167 | 0.679 | 0.000 |
| structured | 80 | 0.362 | 0.197 | 0.000 | 0.545 | 0.244 | 0.000 |
| tfidf | 80 | 0.550 | 0.177 | 0.000 | 0.710 | 0.000 | 0.000 |
| modernbert | 80 | 0.200 | 0.137 | 0.000 | 0.229 | 0.320 | 0.000 |

## Reporting Boundary

- Report as standard single-user validation unless a separate second-annotator pass is added.
- Treat active-frontier samples as hard-case/frontier evidence, not natural venue prevalence.
- Keep provisional assistant-adjudication metrics separate from this sheet.
