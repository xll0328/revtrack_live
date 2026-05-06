# ICLR 2023 random80 standard slice Standard Transfer Metrics

These metrics use a validation sheet with status `standard_single_user_confirmed`. Report them only under that provenance boundary; this is not an independent two-annotator IAA result unless a separate IAA pass exists.

| model | rows | accuracy | macro-F1 | fixed F1 | partial F1 | unresolved F1 | regressed F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| issue_ledger | 80 | 1.000 | 0.750 | 1.000 | 1.000 | 1.000 | 0.000 |
| tfidf | 80 | 0.662 | 0.422 | 0.909 | 0.780 | 0.000 | 0.000 |

## Reporting Boundary

- Report as standard single-user validation unless a separate second-annotator pass is added.
- Treat random/stratified samples as bounded slice evidence by measured design, not natural venue prevalence.
- Keep provisional assistant-adjudication metrics separate from claim-ready benchmark tables.
