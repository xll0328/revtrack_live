# ICLR 2025 Repro Mini-Transfer Summary

## Source

This mini-transfer run uses the locally generated OpenReview repro file:

- raw repro: [iclr2025_repro.jsonl](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro.jsonl)
- successful probe report: [openreview_probe_iclr2025_current_env_rerun_20260424.json](/data/sony/emnlp2026_revtrack/outputs/day1/openreview_probe_iclr2025_current_env_rerun_20260424.json)

The probe report shows `v2-notes` succeeds for `ICLR.cc/2025/Conference` with `20 / 20` submissions yielding issue candidates. `v2-search` is reachable but returns a `400` query/API error for this request, so the stable collection path is `--api-mode v2-notes`.

## Extracted Pool

- submissions: `5`
- issue candidates: `21`
- per-paper issue counts: `PwxYoMvmvy 4 / ONfWFluZBI 5 / odjMSBSWRt 4 / imT03YXlG2 4 / w7P92BEsb2 4`

Derived files:

- issue candidates: [iclr2025_repro_issue_candidates.jsonl](/data/sony/emnlp2026_revtrack/data/processed/iclr2025_repro_issue_candidates.jsonl)
- exported examples: [iclr2025_repro_candidate_examples.jsonl](/data/sony/emnlp2026_revtrack/data/processed/iclr2025_repro_candidate_examples.jsonl)

## ICLR 2024 Train V8 Transfer

Prediction distributions over `21` ICLR 2025 issue candidates:

- `TF-IDF`: `partially_fixed 21`
- `ModernBERT`: `fixed 9 / partially_fixed 11 / unresolved 1`
- `MPNet`: `fixed 8 / partially_fixed 9 / unresolved 3 / regressed 1`
- `Issue-Ledger`: `fixed 5 / partially_fixed 9 / unresolved 7`
- `Structured`: `fixed 5 / partially_fixed 15 / unresolved 1`

Prediction files:

- [iclr2025_repro_candidates_tfidf_train_iclr2024_v8_transfer_predictions.jsonl](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_candidates_tfidf_train_iclr2024_v8_transfer_predictions.jsonl)
- [iclr2025_repro_candidates_modernbert_train_iclr2024_v8_transfer_predictions.jsonl](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_candidates_modernbert_train_iclr2024_v8_transfer_predictions.jsonl)
- [iclr2025_repro_candidates_mpnet_train_iclr2024_v8_transfer_predictions.jsonl](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_candidates_mpnet_train_iclr2024_v8_transfer_predictions.jsonl)
- [iclr2025_repro_candidates_issue_ledger_train_iclr2024_v8_transfer_predictions.jsonl](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_candidates_issue_ledger_train_iclr2024_v8_transfer_predictions.jsonl)
- [iclr2025_repro_candidates_structured_train_iclr2024_v8_transfer_predictions.jsonl](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_candidates_structured_train_iclr2024_v8_transfer_predictions.jsonl)

## Disagreement Frontier

Structured-vs-other disagreements:

- `structured vs tfidf`: `6`
- `structured vs modernbert`: `5`
- `structured vs mpnet`: `8`
- `structured vs issue_ledger`: `9`

Annotation assets:

- multi-model structured frontier sheet: [iclr2025_repro_multi_frontier_structured_prefilled.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_multi_frontier_structured_prefilled.tsv)
- multi-model structured frontier packet: [iclr2025_repro_multi_frontier_structured_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_multi_frontier_structured_packet.html)
- structured-vs-MPNet sheet: [iclr2025_repro_priority_sheet_structured_vs_mpnet_prefilled.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_priority_sheet_structured_vs_mpnet_prefilled.tsv)
- structured-vs-MPNet packet: [iclr2025_repro_priority_packet_structured_vs_mpnet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_priority_packet_structured_vs_mpnet.html)
- structured-vs-issue-ledger sheet: [iclr2025_repro_priority_sheet_structured_vs_issue_ledger_prefilled.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_priority_sheet_structured_vs_issue_ledger_prefilled.tsv)
- structured-vs-issue-ledger packet: [iclr2025_repro_priority_packet_structured_vs_issue_ledger.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_priority_packet_structured_vs_issue_ledger.html)

The de-duplicated multi-model frontier has `16` rows. Suggested-label distribution is `unresolved 7 / partially_fixed 6 / fixed 2 / regressed 1`.

## Interpretation

This is not yet a benchmark result because it has only `5` submissions and no ICLR 2025 labels. It is still a useful pipeline proof: ICLR 2024 train v8 transfers to ICLR 2025, the candidate extractor works on the newer venue schema, and model disagreement produces immediate annotation targets. The next scale step is to collect a larger `v2-notes` ICLR 2025 pool and adjudicate the first transfer frontier.

## Assistant-Adjudicated Mini Frontier

Assistant adjudication has been added for the de-duplicated multi-model frontier:

- sheet: [iclr2025_repro_multi_frontier_structured_assistant.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_multi_frontier_structured_assistant.tsv)
- data: [iclr2025_repro_multi_frontier_structured_assistant.jsonl](/data/sony/emnlp2026_revtrack/data/processed/iclr2025_repro_multi_frontier_structured_assistant.jsonl)
- rows: `16`
- label distribution: `partially_fixed 12 / fixed 4`

Transfer sanity-check metrics on this stress frontier:

- `TF-IDF`: accuracy `0.750`, macro-F1 `0.214`
- `ModernBERT`: accuracy `0.438`, macro-F1 `0.216`
- `MPNet`: accuracy `0.250`, macro-F1 `0.146`
- `Issue-Ledger`: accuracy `0.188`, macro-F1 `0.094`
- `Structured`: accuracy `0.500`, macro-F1 `0.215`

Metric files:

- [iclr2025_repro_multi_frontier_tfidf_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_multi_frontier_tfidf_metrics.json)
- [iclr2025_repro_multi_frontier_modernbert_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_multi_frontier_modernbert_metrics.json)
- [iclr2025_repro_multi_frontier_mpnet_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_multi_frontier_mpnet_metrics.json)
- [iclr2025_repro_multi_frontier_issue_ledger_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_multi_frontier_issue_ledger_metrics.json)
- [iclr2025_repro_multi_frontier_structured_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_multi_frontier_structured_metrics.json)

Interpretation of the mini evaluation:

The stress frontier is dominated by `partially_fixed`, so TF-IDF obtains high accuracy by predicting the majority label for every example and has zero fixed-label recovery. Structured is not yet robust on cross-year frontier examples, but it recovers some fixed cases and avoids the pure-majority behavior. This is a useful failure signal: the cross-year benchmark must be scaled and human-validated before making a method claim.

## Human Validation V1

The full `16`-row mini frontier has been packaged for blind human validation:

- blind sheet: [iclr2025_repro_human_validation_v1_blind.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_human_validation_v1_blind.tsv)
- hidden key: [iclr2025_repro_human_validation_v1_key.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_human_validation_v1_key.tsv)
- audit sheet: [iclr2025_repro_human_validation_v1_audit.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_human_validation_v1_audit.tsv)
- blind packet: [iclr2025_repro_human_validation_v1_blind_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_human_validation_v1_blind_packet.html)
- audit packet: [iclr2025_repro_human_validation_v1_audit_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_human_validation_v1_audit_packet.html)
- pending metrics: [iclr2025_repro_human_validation_v1_pending_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_human_validation_v1_pending_metrics.json)

Key distribution:

- assistant labels: `partially_fixed 12 / fixed 4`
- audit buckets: `structured_error 8 / model_disagreement 6 / model_high_conflict 2`

## Full Repro V2 Coverage

The v1 stress frontier covered the `16` model-disagreement rows. V2 adds the remaining `5` low-conflict agreement rows so that the local repro mini-pool is fully labeled:

- full prefilled sheet: [iclr2025_repro_multi_frontier_structured_v2_full_prefilled.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_multi_frontier_structured_v2_full_prefilled.tsv)
- full assistant sheet: [iclr2025_repro_multi_frontier_structured_v2_full_assistant.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_multi_frontier_structured_v2_full_assistant.tsv)
- full data: [iclr2025_repro_multi_frontier_structured_v2_full_assistant.jsonl](/data/sony/emnlp2026_revtrack/data/processed/iclr2025_repro_multi_frontier_structured_v2_full_assistant.jsonl)
- full assistant packet: [iclr2025_repro_multi_frontier_structured_v2_full_assistant_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_multi_frontier_structured_v2_full_assistant_packet.html)
- rows: `21`
- label distribution: `partially_fixed 16 / fixed 5`
- sheet audit: `0` missing labels, `21` evidence spans, no duplicate issue IDs, no invalid labels

V2 transfer metrics on all `21` repro candidates:

- `TF-IDF`: accuracy `0.762`, macro-F1 `0.216`, fixed F1 `0.000`
- `ModernBERT`: accuracy `0.524`, macro-F1 `0.238`, fixed F1 `0.286`
- `MPNet`: accuracy `0.381`, macro-F1 `0.197`, fixed F1 `0.308`
- `Issue-Ledger`: accuracy `0.333`, macro-F1 `0.140`, fixed F1 `0.000`
- `Structured`: accuracy `0.571`, macro-F1 `0.227`, fixed F1 `0.200`

V2 metric files:

- [iclr2025_repro_v2_full_tfidf_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_v2_full_tfidf_metrics.json)
- [iclr2025_repro_v2_full_modernbert_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_v2_full_modernbert_metrics.json)
- [iclr2025_repro_v2_full_mpnet_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_v2_full_mpnet_metrics.json)
- [iclr2025_repro_v2_full_issue_ledger_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_v2_full_issue_ledger_metrics.json)
- [iclr2025_repro_v2_full_structured_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_v2_full_structured_metrics.json)
- paper-ready metrics table: [iclr2025_v2_transfer_metrics.csv](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2025_v2_transfer_metrics.csv)
- paper-ready error profile: [iclr2025_v2_error_profile.csv](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2025_v2_error_profile.csv)
- null-baseline comparison: [null_baseline_comparison.csv](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/null_baseline_comparison.csv)
- claim evidence ledger: [claim_evidence_ledger.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/claim_evidence_ledger.md)

Interpretation:

V2 confirms that the ICLR 2025 mini-pool is still too small and too label-skewed for a method claim. TF-IDF has the highest accuracy only because every prediction is `partially_fixed`; it has zero fixed-label recovery. Structured avoids pure-majority behavior and recovers one fixed example, but its macro-F1 remains weak. This should be framed as cross-year brittleness evidence and used to motivate larger ICLR 2025 collection plus independent human validation.

The null-baseline comparison makes this exact: the ICLR 2025 majority-label baseline obtains accuracy `0.762` and macro-F1 `0.216`, exactly matching TF-IDF. In contrast, on ICLR 2024 clean dev v7 the majority baseline has accuracy `0.581` but macro-F1 only `0.184`, while Structured reaches accuracy `0.682` and macro-F1 `0.704`.

The claim ledger marks ICLR 2025 as `stress_evidence`, not a publishable cross-year benchmark claim. The not-ready claim is explicit: benchmark generalization across years or venues still requires a larger venue/year pool that passes quality gates and independent validation.

The paper-readiness audit [paper_readiness_audit.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/paper_readiness_audit.md) keeps this boundary enforceable: ICLR 2025 pool quality is a warning, not a blocker for in-domain claims, while independent human validation is the current hard blocker for final benchmark claims.

The label-evidence audit also confirms that ICLR 2025 v2 is internally well documented: [iclr2025_repro_v2_label_evidence_audit.md](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_v2_label_evidence_audit.md) reports structural ok and `0` evidence issues.

## Human Validation V2

The full `21`-row repro pool has also been packaged for blind validation:

- blind sheet: [iclr2025_repro_human_validation_v2_blind.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_human_validation_v2_blind.tsv)
- hidden key: [iclr2025_repro_human_validation_v2_key.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_human_validation_v2_key.tsv)
- audit sheet: [iclr2025_repro_human_validation_v2_audit.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_human_validation_v2_audit.tsv)
- blind packet: [iclr2025_repro_human_validation_v2_blind_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_human_validation_v2_blind_packet.html)
- audit packet: [iclr2025_repro_human_validation_v2_audit_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_human_validation_v2_audit_packet.html)
- pending metrics: [iclr2025_repro_human_validation_v2_pending_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_human_validation_v2_pending_metrics.json)
- packet audit: [iclr2025_repro_human_validation_v2_packet_audit.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_human_validation_v2_packet_audit.json)

The new packet audit script [audit_human_validation_packet.py](/data/sony/emnlp2026_revtrack/scripts/audit_human_validation_packet.py) verifies blind/key/audit ID alignment, checks that blind sheets do not expose assistant/model/gold labels, and checks key values against the source labeled sheet. It passes for ICLR 2025 v1 and v2, and for the sampled ICLR 2024 validation packet.

## Candidate-Pool Quality Gate

The candidate-pool audit script [audit_candidate_pool.py](/data/sony/emnlp2026_revtrack/scripts/audit_candidate_pool.py) now turns the cross-venue quality gates into a machine-readable report.

- ICLR 2025 repro audit: [iclr2025_repro_candidate_pool_quality_gate.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_candidate_pool_quality_gate.json)
- ICLR 2024 comparison audit: [iclr2024_candidate_pool_quality_gate.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2024_candidate_pool_quality_gate.json)

ICLR 2025 repro pool audit:

- candidates: `21`
- submissions: `5`
- complete-field rate: `1.000`
- multi-model disagreement rows: `16`
- high-disagreement rows: `6`
- gate status: fails publishable-size thresholds because `21 < 150` candidates and `16 < 25` disagreement rows

ICLR 2024 comparison pool audit:

- candidates: `230`
- submissions: `60`
- complete-field rate: `1.000`
- multi-model disagreement rows: `82`
- gate status: passes current pool-quality thresholds

This makes the next collection goal explicit: ICLR 2025 needs scale, not more analysis of the current five-paper repro sample.
