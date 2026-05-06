# ICLR 2023 random80 resolved candidate Transfer Metrics (Proxy / Pre-Confirmation)

These metrics use a validation sheet with status `assistant_resolved_candidate_not_human_validation`. This is a proxy/pre-confirmation artifact and not standard human-validation evidence.

| model | rows | accuracy | macro-F1 | fixed F1 | partial F1 | unresolved F1 | regressed F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| issue_ledger | 80 | 1.000 | 0.750 | 1.000 | 1.000 | 1.000 | 0.000 |
| tfidf | 80 | 0.662 | 0.422 | 0.909 | 0.780 | 0.000 | 0.000 |

## Reporting Boundary

- Do not report as standard human validation or IAA; this is a pre-confirmation proxy artifact.
- Treat this as queue triage only when labels come from assistant-resolved candidates.
- Keep provisional assistant-adjudication metrics separate from claim-ready benchmark tables.
