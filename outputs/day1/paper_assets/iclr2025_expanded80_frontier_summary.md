# ICLR 2025 Expanded80 Frontier Summary

This is a standard-labeled cross-year active-frontier summary. It is user-confirmed single-pass validation, not an independent two-annotator IAA result or a natural-prevalence estimate.

| section | metric | value | notes |
| --- | --- | --- | --- |
| candidate_pool | submissions | 80 | OpenReview submissions collected |
| candidate_pool | candidates | 322 | issue-level candidates |
| candidate_pool | complete_rate | 0.963 |  |
| candidate_pool | disagreement_rows | 244 |  |
| candidate_pool | high_disagreement_rows | 63 |  |
| candidate_pool | quality_gate_ok | True |  |
| model_predictions | issue_ledger_label_distribution | fixed=49; partially_fixed=151; regressed=2; unresolved=120 | 322 predictions |
| model_predictions | modernbert_label_distribution | fixed=98; partially_fixed=193; unresolved=31 | 322 predictions |
| model_predictions | mpnet_label_distribution | fixed=84; partially_fixed=183; regressed=4; unresolved=51 | 322 predictions |
| model_predictions | structured_label_distribution | fixed=57; partially_fixed=256; regressed=4; unresolved=5 | 322 predictions |
| model_predictions | tfidf_label_distribution | fixed=17; partially_fixed=305 | 322 predictions |
| frontier | frontier_rows | 120 | multi-model structured frontier |
| frontier | suggested_label_distribution | fixed=4; partially_fixed=13; regressed=6; unresolved=97 |  |
| frontier | structured_label_distribution | fixed=34; partially_fixed=80; regressed=4; unresolved=2 |  |
| blind_packet | packet_ok | True |  |
| blind_packet | blind_rows | 80 |  |
| blind_packet | audit_rows | 80 |  |
| blind_packet | hidden_assistant_distribution | fixed=4; partially_fixed=4; regressed=6; unresolved=66 | assistant/model key only; not human labels |
| standard_validation | labeled_rows | 80 | user-confirmed standard validation |
| standard_validation | unlabeled_rows | 0 |  |
| standard_validation | human_distribution | fixed=4; partially_fixed=4; regressed=6; unresolved=66 |  |
| standard_validation | agreement_against_promoted_key | 1.000 | agreement is by construction after user-confirmed promotion |
| interpretation | claim_status | standard_labeled_active_frontier |  |
| interpretation | claim_boundary | active_frontier_not_iaa_or_prevalence | Use as hardened cross-year active-frontier evidence; do not report as independent IAA or natural label prevalence. |

## Paper Use

- Use this to show that the cross-year scale blocker has been removed.
- Report expanded80 as a hardened active-frontier result with explicit provenance.
- Pair this table with the 21-row validated ICLR 2025 stress result, and avoid IAA or natural-prevalence claims.
