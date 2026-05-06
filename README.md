# RevTrack

`RevTrack` is a new EMNLP 2026 project scaffold for studying whether LLMs can update their scientific judgments after paper revision.

Core task:

- input: a paper snapshot, one review concern, the author response, and a revision summary
- output: one issue status label
  - `fixed`
  - `partially_fixed`
  - `unresolved`
  - `regressed`

The current thesis is simple:

> LLMs that look competent on static paper critique often fail once the paper changes and the model must decide whether an issue was actually fixed.

This repo is designed for day-0 and day-1 work:

- collect public OpenReview submissions and replies
- create annotation sheets for issue tracking
- run zero-training baselines on a smoke set
- render an animated issue-flow visualization for Figure 1 style demos

## Project Shape

- [docs/idea_brief.md](/data/sony/emnlp2026_revtrack/docs/idea_brief.md): scientific framing and novelty guardrails
- [docs/day0_plan.md](/data/sony/emnlp2026_revtrack/docs/day0_plan.md): what to do today
- [docs/label_rubric.md](/data/sony/emnlp2026_revtrack/docs/label_rubric.md): first-pass annotation boundaries
- [docs/annotation_quickstart.md](/data/sony/emnlp2026_revtrack/docs/annotation_quickstart.md): fastest path to the first clean dev set
- [docs/figure_storyboard.md](/data/sony/emnlp2026_revtrack/docs/figure_storyboard.md): dynamic visualization plan
- [docs/figure1_running_examples.md](/data/sony/emnlp2026_revtrack/docs/figure1_running_examples.md): recommended Figure 1 running examples
- [docs/cross_venue_plan.md](/data/sony/emnlp2026_revtrack/docs/cross_venue_plan.md): next venue/year expansion protocol
- [docs/revtrack_dataset_card_v0.md](/data/sony/emnlp2026_revtrack/docs/revtrack_dataset_card_v0.md): dataset card, provenance, reporting boundaries, and quality gates
- [docs/related_work_matrix.md](/data/sony/emnlp2026_revtrack/docs/related_work_matrix.md): paper-facing comparison against peer-review corpora, evidence QA, fact verification, and review-generation work
- [docs/emnlp_oral_best_paper_sprint_plan.md](/data/sony/emnlp2026_revtrack/docs/emnlp_oral_best_paper_sprint_plan.md): EMNLP 2026 oral/best-paper sprint plan
- [docs/emnlp_oral_bestpaper_warplan_20260506.md](/data/sony/emnlp2026_revtrack/docs/emnlp_oral_bestpaper_warplan_20260506.md): dated oral/best-paper execution plan + todo checklist
- [docs/emnlp2026_pitch_and_intro_v0.md](/data/sony/emnlp2026_revtrack/docs/emnlp2026_pitch_and_intro_v0.md): one-page pitch and Introduction v0
- [docs/paper_draft_self_review.md](/data/sony/emnlp2026_revtrack/docs/paper_draft_self_review.md): severity-ranked self-review of the current paper draft
- [paper/main.tex](/data/sony/emnlp2026_revtrack/paper/main.tex): compiled ACL/ARR-style paper draft
- [paper/main.pdf](/data/sony/emnlp2026_revtrack/paper/main.pdf): current compiled PDF draft

## Current Checkpoint

Latest assistant-adjudicated benchmark assets:

- summary: [summary_2026-04-24.md](/data/sony/emnlp2026_revtrack/experiments/day1/summary_2026-04-24.md)
- progress dashboard: [revtrack_progress_dashboard.html](/data/sony/emnlp2026_revtrack/outputs/day1/revtrack_progress_dashboard.html)
- paper asset summary: [paper_asset_summary.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/paper_asset_summary.md)
- paper-ready tables and SVGs: [paper_assets](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets)
- Figure 1 v1 schematic: [figure1_revision_tracking.svg](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/figure1_revision_tracking.svg)
- Figure 1 paper PDF: [figure1_revision_tracking.pdf](/data/sony/emnlp2026_revtrack/paper/figures/figure1_revision_tracking.pdf)
- failure taxonomy v0: [failure_taxonomy.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/failure_taxonomy.md)
- pipeline overview figure (new): [figure_pipeline_overview.pdf](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/figure_pipeline_overview.pdf)
- ICLR 2025 v2 transfer table: [iclr2025_v2_transfer_metrics.csv](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2025_v2_transfer_metrics.csv)
- ICLR 2025 v2 error profile: [iclr2025_v2_error_profile.csv](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2025_v2_error_profile.csv)
- ICLR 2024 significance audit: [iclr2024_main_results_significance.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2024_main_results_significance.md)
- cross-split significance audit: [cross_split_significance.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/cross_split_significance.md)
- NeurIPS 2024 standard transfer metrics: [neurips2024_limit100_standard_transfer_metrics.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/neurips2024_limit100_standard_transfer_metrics.md)
- NeurIPS 2024 standard failure taxonomy: [neurips2024_limit100_standard_failure_taxonomy.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/neurips2024_limit100_standard_failure_taxonomy.md)
- null-baseline comparison: [null_baseline_comparison.csv](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/null_baseline_comparison.csv)
- claim evidence ledger: [claim_evidence_ledger.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/claim_evidence_ledger.md)
- claim evidence table: [claim_evidence_ledger.csv](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/claim_evidence_ledger.csv)
- paper readiness audit: [paper_readiness_audit.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/paper_readiness_audit.md)
- paper readiness JSON: [paper_readiness_audit.json](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/paper_readiness_audit.json)
- top-conference gap audit: [top_conference_quality_audit_2026-04-28.md](/data/sony/emnlp2026_revtrack/outputs/day1/top_conference_quality_audit_2026-04-28.md)
- oral/best-paper gap audit (2026-05-06): [oral_best_paper_gap_audit_20260506.md](/data/sony/emnlp2026_revtrack/docs/oral_best_paper_gap_audit_20260506.md)
- second-annotator IAA mini-slice manifest (2026-05-06): [iaa_second_annotator_mini60_v1_manifest.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_manifest.md)
- second-annotator IAA mini-slice blind packet: [iaa_second_annotator_mini60_v1_blind_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iaa_second_annotator_mini60_v1_blind_packet.html)
- second-annotator IAA mini-slice batch plan: [iaa_second_annotator_mini60_batches.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iaa_second_annotator_mini60_batches.md)
- random/stratified next-slice plan: [random_stratified_slice_plan_20260428.md](/data/sony/emnlp2026_revtrack/docs/random_stratified_slice_plan_20260428.md)
- random/stratified feasibility snapshot: [random_stratified_slice_feasibility_2026-04-28.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/random_stratified_slice_feasibility_2026-04-28.md)
- random/stratified feasibility refresh (2026-05-06): [random_stratified_slice_feasibility_2026-05-06.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/random_stratified_slice_feasibility_2026-05-06.md)
- ICLR 2023 random/stratified seed summary: [iclr2023_limit80_random_stratified_seed80_summary.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2023_limit80_random_stratified_seed80_summary.json)
- ICLR 2023 random/stratified blind packet: [iclr2023_limit80_random80_human_validation_v1_blind_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2023_limit80_random80_human_validation_v1_blind_packet.html)
- ICLR 2023 random/stratified packet audit: [iclr2023_limit80_random80_human_validation_v1_packet_audit.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2023_limit80_random80_human_validation_v1_packet_audit.json)
- ICLR 2023 random/stratified resolved-candidate report: [iclr2023_limit80_random80_resolved_candidate_report.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2023_limit80_random80_resolved_candidate_report.md)
- ICLR 2023 random/stratified standard promotion report: [iclr2023_limit80_random80_standard_validation_promotion.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2023_limit80_random80_standard_validation_promotion.json)
- ICLR 2023 random/stratified standard validation metrics: [iclr2023_limit80_random80_human_validation_v1_standard_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2023_limit80_random80_human_validation_v1_standard_metrics.json)
- ICLR 2023 random/stratified standard transfer metrics: [iclr2023_limit80_random80_standard_transfer_metrics.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2023_limit80_random80_standard_transfer_metrics.md)
- ICLR 2023 random/stratified standard failure taxonomy: [iclr2023_limit80_random80_standard_failure_taxonomy.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2023_limit80_random80_standard_failure_taxonomy.md)
- ICLR 2023 random/stratified label-evidence audit: [iclr2023_limit80_random80_standard_label_evidence_audit.md](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2023_limit80_random80_standard_label_evidence_audit.md)
- ICLR 2023 random/stratified promotion dry run: [iclr2023_limit80_random80_standard_validation_promotion_dry_run.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2023_limit80_random80_standard_validation_promotion_dry_run.json)
- ICLR 2023 random/stratified historical pre-confirmation transfer metrics: [iclr2023_limit80_random80_resolved_candidate_transfer_metrics.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2023_limit80_random80_resolved_candidate_transfer_metrics.md)
- ICLR 2023 random/stratified historical pre-confirmation failure taxonomy: [iclr2023_limit80_random80_resolved_candidate_failure_taxonomy.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2023_limit80_random80_resolved_candidate_failure_taxonomy.md)
- ICLR 2023 random/stratified promotion runbook: [iclr2023_random80_promotion_runbook.md](/data/sony/emnlp2026_revtrack/docs/iclr2023_random80_promotion_runbook.md)
- prompted LLM bootstrap intervals: [prompted_llm_bootstrap_intervals.md](/data/sony/emnlp2026_revtrack/outputs/day1/prompted_llm_baselines/prompted_llm_bootstrap_intervals.md)
- prompted LLM significance vs majority: [prompted_llm_significance.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/prompted_llm_significance.md)
- related-work matrix: [related_work_matrix.md](/data/sony/emnlp2026_revtrack/docs/related_work_matrix.md)
- human-validation work queue: [human_validation_work_queue.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/human_validation_work_queue.md)
- human-validation queue table: [human_validation_work_queue.csv](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/human_validation_work_queue.csv)
- human-validation batch manifest: [human_validation_priority_manifest.md](/data/sony/emnlp2026_revtrack/outputs/day1/human_validation_batches/human_validation_priority_manifest.md)
- human-validation batch directory: [human_validation_batches](/data/sony/emnlp2026_revtrack/outputs/day1/human_validation_batches)
- human-validation batch ingest report: [human_validation_batch_ingest_report.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/human_validation_batch_ingest_report.md)
- human-validation pipeline report: [human_validation_pipeline_report.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/human_validation_pipeline_report.md)
- AI-assisted validation signoff manifest: [ai_assisted_validation_signoff_manifest.md](/data/sony/emnlp2026_revtrack/outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff_manifest.md)
- AI-assisted validation signoff audit: [ai_assisted_validation_signoff_audit.md](/data/sony/emnlp2026_revtrack/outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff_audit.md)
- AI-assisted signoff to human-validation promotion report: [ai_signoff_human_validation_promotion.json](/data/sony/emnlp2026_revtrack/outputs/day1/ai_assisted_validation_signoff/ai_signoff_human_validation_promotion.json)
- ICLR 2024 label-evidence audit: [iclr2024_clean_dev_v7_label_evidence_audit.md](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2024_clean_dev_v7_label_evidence_audit.md)
- ICLR 2024 assistant evidence-filled sheet: [iclr2024_clean_dev_assistant_v7_sheet_evidence_filled.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2024_clean_dev_assistant_v7_sheet_evidence_filled.tsv)
- ICLR 2024 assistant evidence-filled data: [iclr2024_clean_dev_assistant_v7_evidence_filled.jsonl](/data/sony/emnlp2026_revtrack/data/processed/iclr2024_clean_dev_assistant_v7_evidence_filled.jsonl)
- ICLR 2024 evidence-filled audit: [iclr2024_clean_dev_v7_evidence_filled_label_evidence_audit.md](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2024_clean_dev_v7_evidence_filled_label_evidence_audit.md)
- ICLR 2025 label-evidence audit: [iclr2025_repro_v2_label_evidence_audit.md](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_v2_label_evidence_audit.md)
- blind human-validation packet: [iclr2024_human_validation_v1_blind_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2024_human_validation_v1_blind_packet.html)
- ICLR 2025 mini-transfer summary: [iclr2025_repro_summary_2026-04-24.md](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_summary_2026-04-24.md)

Current best checkpoint:

- clean dev v7 has `148` assistant-adjudicated rows with label distribution `fixed 50 / partially_fixed 86 / unresolved 11 / regressed 1`
- strict `LOO-feature` evaluation is the default for `issue-ledger` and `structured`, so clean-dev numbers do not reuse full-train transfer predictions
- `Structured Calibrator` reaches `0.682` accuracy and `0.704` macro-F1 on clean dev v7
- the best semantic baseline, `MPNet + LinearSVC`, reaches `0.581` accuracy and `0.389` macro-F1
- removing hard overrides gives `0.655` accuracy and `0.424` macro-F1, showing that explicit follow-up cues still drive most minority-label recovery

Latest clean-dev assets:

- clean dev v7 sheet: [iclr2024_clean_dev_assistant_v7_sheet_refreshed.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2024_clean_dev_assistant_v7_sheet_refreshed.tsv)
- clean dev v7 data: [iclr2024_clean_dev_assistant_v7.jsonl](/data/sony/emnlp2026_revtrack/data/processed/iclr2024_clean_dev_assistant_v7.jsonl)
- clean dev v7 packet: [iclr2024_clean_dev_assistant_v7_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2024_clean_dev_assistant_v7_packet.html)
- clean dev v7 dashboard: [iclr2024_clean_dev_v7_dashboard.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2024_clean_dev_v7_dashboard.html)
- structured v7 metrics: [iclr2024_clean_dev_assistant_v7_structured_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2024_clean_dev_assistant_v7_structured_metrics.json)

Latest transfer-time assets:

- merged train v8 data: [iclr2024_train_v8.jsonl](/data/sony/emnlp2026_revtrack/data/processed/iclr2024_train_v8.jsonl)
- merged train v8 sheet: [iclr2024_train_v8_sheet_refreshed.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2024_train_v8_sheet_refreshed.tsv)
- structured transfer predictions: [iclr2024_candidates_structured_train_v8_transfer_predictions.jsonl](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2024_candidates_structured_train_v8_transfer_predictions.jsonl)

Current transfer takeaway:

- `train_v8` has `180` rows with label distribution `fixed 63 / partially_fixed 104 / unresolved 12 / regressed 1`
- full-candidate `structured_v8` predictions are `fixed 74 / partially_fixed 141 / unresolved 14 / regressed 1`
- the current 230-candidate ICLR 2024 pool has no remaining unlabeled model-disagreement frontier under `structured` vs `tfidf`, `modernbert`, or `issue_ledger`
- the next scientific bottleneck is not more active sampling from this pool; it is extending beyond the hardened ICLR 2025 expanded80 frontier to another venue/year or to an independent IAA pass

Human-validation v1:

- blind sheet for independent relabeling: [iclr2024_human_validation_v1_blind.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2024_human_validation_v1_blind.tsv)
- hidden key with assistant/model labels: [iclr2024_human_validation_v1_key.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2024_human_validation_v1_key.tsv)
- audit sheet with assistant/model labels visible: [iclr2024_human_validation_v1_audit.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2024_human_validation_v1_audit.tsv)
- blind packet: [iclr2024_human_validation_v1_blind_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2024_human_validation_v1_blind_packet.html)
- audit packet: [iclr2024_human_validation_v1_audit_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2024_human_validation_v1_audit_packet.html)
- pending validation metrics: [iclr2024_human_validation_v1_pending_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2024_human_validation_v1_pending_metrics.json)
- evaluator: [evaluate_human_validation.py](/data/sony/emnlp2026_revtrack/scripts/evaluate_human_validation.py)
- OpenReview venue probe: [probe_openreview_venue.py](/data/sony/emnlp2026_revtrack/scripts/probe_openreview_venue.py)
- successful ICLR 2025 probe report: [openreview_probe_iclr2025_current_env_rerun_20260424.json](/data/sony/emnlp2026_revtrack/outputs/day1/openreview_probe_iclr2025_current_env_rerun_20260424.json)
- sample composition from the hidden key: `fixed 13 / partially_fixed 19 / unresolved 7 / regressed 1`

ICLR 2025 mini-transfer:

- raw repro data: [iclr2025_repro.jsonl](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro.jsonl)
- extracted candidates: [iclr2025_repro_issue_candidates.jsonl](/data/sony/emnlp2026_revtrack/data/processed/iclr2025_repro_issue_candidates.jsonl)
- structured predictions: [iclr2025_repro_candidates_structured_train_iclr2024_v8_transfer_predictions.jsonl](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_candidates_structured_train_iclr2024_v8_transfer_predictions.jsonl)
- multi-model structured frontier packet: [iclr2025_repro_multi_frontier_structured_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_multi_frontier_structured_packet.html)
- assistant-labeled mini frontier: [iclr2025_repro_multi_frontier_structured_assistant.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_multi_frontier_structured_assistant.tsv)
- mini frontier structured metrics: [iclr2025_repro_multi_frontier_structured_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_multi_frontier_structured_metrics.json)
- full 21-row v2 assistant sheet: [iclr2025_repro_multi_frontier_structured_v2_full_assistant.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_repro_multi_frontier_structured_v2_full_assistant.tsv)
- full 21-row v2 data: [iclr2025_repro_multi_frontier_structured_v2_full_assistant.jsonl](/data/sony/emnlp2026_revtrack/data/processed/iclr2025_repro_multi_frontier_structured_v2_full_assistant.jsonl)
- full 21-row v2 structured metrics: [iclr2025_repro_v2_full_structured_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_v2_full_structured_metrics.json)
- ICLR 2025 v2 blind human-validation packet: [iclr2025_repro_human_validation_v2_blind_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_human_validation_v2_blind_packet.html)
- ICLR 2025 v2 packet audit: [iclr2025_repro_human_validation_v2_packet_audit.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_human_validation_v2_packet_audit.json)
- structured-vs-MPNet packet: [iclr2025_repro_priority_packet_structured_vs_mpnet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_priority_packet_structured_vs_mpnet.html)
- structured-vs-issue-ledger packet: [iclr2025_repro_priority_packet_structured_vs_issue_ledger.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_repro_priority_packet_structured_vs_issue_ledger.html)
- scaled ICLR 2025 raw data: [iclr2025_expanded80.jsonl](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_expanded80.jsonl)
- scaled ICLR 2025 candidates: [iclr2025_expanded80_issue_candidates.jsonl](/data/sony/emnlp2026_revtrack/data/processed/iclr2025_expanded80_issue_candidates.jsonl)
- scaled ICLR 2025 candidate-pool gate: [iclr2025_expanded80_candidate_pool_quality_gate.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_expanded80_candidate_pool_quality_gate.json)
- scaled ICLR 2025 frontier summary: [iclr2025_expanded80_frontier_summary.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2025_expanded80_frontier_summary.md)
- scaled ICLR 2025 multi-model frontier: [iclr2025_expanded80_multi_frontier_structured_prefilled.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_expanded80_multi_frontier_structured_prefilled.tsv)
- scaled ICLR 2025 blind validation packet: [iclr2025_expanded80_human_validation_v1_blind_packet.html](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_expanded80_human_validation_v1_blind_packet.html)
- scaled ICLR 2025 packet audit: [iclr2025_expanded80_human_validation_v1_packet_audit.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_expanded80_human_validation_v1_packet_audit.json)
- scaled ICLR 2025 standard validation metrics: [iclr2025_expanded80_human_validation_v1_standard_metrics.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_expanded80_human_validation_v1_standard_metrics.json)
- scaled ICLR 2025 standard transfer metrics: [iclr2025_expanded80_standard_transfer_metrics.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2025_expanded80_standard_transfer_metrics.md)
- scaled ICLR 2025 source adjudication record: [iclr2025_expanded80_assistant_adjudication_v1.tsv](/data/sony/emnlp2026_revtrack/experiments/day1/iclr2025_expanded80_assistant_adjudication_v1.tsv)
- scaled ICLR 2025 historical provisional transfer metrics: [iclr2025_expanded80_provisional_transfer_metrics.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2025_expanded80_provisional_transfer_metrics.md)

ICLR 2025 v2 full-pool sanity check:

- v2 covers all `21 / 21` repro issue candidates with label distribution `partially_fixed 16 / fixed 5`
- `TF-IDF` still wins accuracy (`0.762`) by predicting only `partially_fixed`, with fixed-label F1 `0.000`
- `Structured` reaches accuracy `0.571` and macro-F1 `0.227`, recovering one fixed case while still overpredicting partial fixes
- the majority-label baseline on ICLR 2025 v2 has the same accuracy and macro-F1 as TF-IDF (`0.762` / `0.216`), proving the accuracy result is not meaningful without label-level recovery
- the packet audit tool [audit_human_validation_packet.py](/data/sony/emnlp2026_revtrack/scripts/audit_human_validation_packet.py) passes on ICLR 2024 v1, ICLR 2025 v1, ICLR 2025 v2, ICLR 2025 expanded80 v1, NeurIPS 2024 limit100 v1, and ICLR 2023 random80 v1
- candidate-pool quality gates: ICLR 2024 passes ([iclr2024_candidate_pool_quality_gate.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2024_candidate_pool_quality_gate.json)); ICLR 2025 expanded80 passes with `322` candidates, `0.963` complete-field rate, and `244` disagreement rows ([iclr2025_expanded80_candidate_pool_quality_gate.json](/data/sony/emnlp2026_revtrack/outputs/day1/iclr2025_expanded80_candidate_pool_quality_gate.json)); NeurIPS 2024 limit100 passes with `393` candidates, `1.000` complete-field rate, and `316` disagreement rows ([neurips2024_limit100_candidate_pool_quality_gate.json](/data/sony/emnlp2026_revtrack/outputs/day1/neurips2024_limit100_candidate_pool_quality_gate.json)); the older ICLR 2025 repro remains a validated 21-row stress sample

Current claim ledger:

- ready: `C1_in_domain_structured_advantage`, `C2_accuracy_trap`, `C3_iclr2024_pool_quality`, `C4_cross_year_brittleness`, `C5_human_validation_complete`, `C6_publishable_cross_year_benchmark`, `C7_prompted_llm_transfer_stress`, `C8_neurips_cross_venue_frontier`, `C9_iclr2023_random_stratified_slice`
- caveat: expanded80 and NeurIPS 2024 limit100 are standard single-user active frontiers; ICLR 2023 random80 is standard single-user random/stratified slice evidence; none is an independent IAA result or natural-prevalence estimate

Current paper-readiness gate:

- overall status: `ready` for the current claim set
- ready claims in the current audit: `9`
- human validation now has `301 / 301` rows filled: `40` ICLR 2024 v1, `21` ICLR 2025 repro v2, `80` ICLR 2025 expanded80, `80` NeurIPS 2024 limit100, and `80` ICLR 2023 random80
- standard human-validation labels are locked; a second annotator is only needed if we decide to claim inter-annotator reliability
- packet audits pass for ICLR 2024 v1, ICLR 2025 v1, ICLR 2025 v2, ICLR 2025 expanded80 v1, NeurIPS 2024 limit100 v1, and ICLR 2023 random80 v1
- active work queue: [human_validation_work_queue.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/human_validation_work_queue.md), with `0` pending rows and `301` done rows
- batch readiness check passes with `0` pending rows and `0` exported batches
- batch ingest check passes with `0` merge errors on the empty pending queue
- one-command pipeline dry-run passes via [run_human_validation_pipeline.py](/data/sony/emnlp2026_revtrack/scripts/run_human_validation_pipeline.py) with `0` pending rows, `0` ingest errors, and refreshed preview evaluations for all five active packets
- AI-assisted signoff sheet remains non-blind and must not be reported as independent validation
- six-pass AI-assisted signoff audit passes with `0` errors and `0` warnings; all `61` assistant evidence spans are inspectable (`41` key evidence rows, `20` explicitly marked context fallback rows)
- caveats: ICLR 2025 repro remains a stress sample; expanded80 and NeurIPS 2024 limit100 are disagreement-focused standard single-user active frontiers; ICLR 2023 random80 is a standard single-user random/stratified slice; none supports IAA or unmeasured natural-prevalence claims
- label-evidence completeness now passes on the assistant evidence-filled release-candidate sheets plus expanded80 and ICLR 2023 random80 standard validation (`329` audited rows, `0` evidence issues)

## Quickstart

Create the smoke data if you want to regenerate it:

```bash
cd /data/sony/emnlp2026_revtrack
python scripts/make_smoke_data.py
```

Run the heuristic baseline:

```bash
python scripts/run_baseline.py \
  --backend heuristic \
  --data data/samples/smoke.jsonl \
  --output outputs/day0/heuristic_predictions.jsonl \
  --eval-json outputs/day0/heuristic_metrics.json
```

Run a local Hugging Face model:

```bash
python scripts/run_baseline.py \
  --backend transformers \
  --model Qwen/Qwen2.5-7B-Instruct \
  --data data/samples/smoke.jsonl \
  --output outputs/day0/qwen25_7b_predictions.jsonl \
  --eval-json outputs/day0/qwen25_7b_metrics.json \
  --max-new-tokens 128 \
  --temperature 0.0
```

Run a lightweight learned baseline without external weights:

```bash
python scripts/run_tfidf_baseline.py \
  --data data/processed/iclr2024_silver_dev.jsonl \
  --output outputs/day0/iclr2024_silver_tfidf_predictions.jsonl \
  --eval-json outputs/day0/iclr2024_silver_tfidf_metrics.json
```

Run a local encoder baseline:

```bash
python scripts/run_encoder_baseline.py \
  --data data/processed/iclr2024_silver_dev.jsonl \
  --model /data/sony/.cache/huggingface/hub/models--answerdotai--ModernBERT-base/snapshots/8949b909ec900327062f0ebf497f51aef5e6f0c8 \
  --output outputs/day0/iclr2024_silver_modernbert_predictions.jsonl \
  --eval-json outputs/day0/iclr2024_silver_modernbert_metrics.json \
  --local-files-only
```

Collect public OpenReview data:

```bash
python scripts/collect_openreview.py \
  --venue-id ICLR.cc/2024/Conference \
  --output data/raw/openreview/iclr2024_submissions.jsonl \
  --limit 50 \
  --api-mode v2-notes
```

Convert raw submissions into issue candidates:

```bash
python scripts/prepare_openreview_issues.py \
  --input data/raw/openreview/iclr2024_submissions.jsonl \
  --output data/processed/iclr2024_issue_candidates.jsonl
```

Prepare a manual annotation sheet:

```bash
python scripts/prepare_issue_sheet.py \
  --data data/processed/iclr2024_issue_candidates.jsonl \
  --output experiments/day0/iclr2024_issue_sheet.tsv \
  --sample-size 25 \
  --seed 42
```

Turn the filled sheet into a labeled JSONL dataset:

```bash
python scripts/build_labeled_dataset.py \
  --candidates data/processed/iclr2024_issue_candidates.jsonl \
  --sheet experiments/day0/iclr2024_issue_sheet.tsv \
  --output data/processed/iclr2024_labeled_dev.jsonl
```

Create a disagreement-prioritized annotation sheet:

```bash
python scripts/make_priority_sheet.py \
  --candidates data/processed/iclr2024_issue_candidates.jsonl \
  --primary-predictions outputs/day0/iclr2024_candidates_heuristic_predictions.jsonl \
  --secondary-predictions outputs/day0/iclr2024_candidates_mpnet_transfer_predictions.jsonl \
  --primary-name heuristic \
  --secondary-name mpnet \
  --output experiments/day0/iclr2024_priority_sheet.tsv \
  --sample-size 30 \
  --require-disagreement \
  --balance-by secondary_label
```

Create a prefilled labeling sheet with model suggestions:

```bash
python scripts/make_prefilled_sheet.py \
  --priority-sheet experiments/day0/iclr2024_priority_sheet_mpnet_balanced.tsv \
  --candidates data/processed/iclr2024_issue_candidates.jsonl \
  --silver-data data/processed/iclr2024_silver_dev.jsonl \
  --heuristic-predictions outputs/day0/iclr2024_candidates_heuristic_predictions.jsonl \
  --tfidf-predictions outputs/day0/iclr2024_candidates_tfidf_transfer_predictions.jsonl \
  --modernbert-predictions outputs/day0/iclr2024_candidates_modernbert_transfer_predictions.jsonl \
  --mpnet-predictions outputs/day0/iclr2024_candidates_mpnet_transfer_predictions.jsonl \
  --output experiments/day0/iclr2024_priority_sheet_mpnet_prefilled.tsv
```

Render a browsable HTML packet for faster labeling:

```bash
python scripts/render_annotation_packet.py \
  --sheet experiments/day0/iclr2024_priority_sheet_mpnet_prefilled.tsv \
  --output outputs/day0/iclr2024_priority_packet.html \
  --title "ICLR 2024 priority packet"
```

Run the issue-ledger calibration layer on a labeled sheet:

```bash
python scripts/run_issue_ledger_calibrator.py \
  --sheet experiments/day0/iclr2024_priority_sheet_mpnet_assistant.tsv \
  --data data/processed/iclr2024_clean_dev_assistant_v1.jsonl \
  --output outputs/day1/iclr2024_clean_dev_assistant_issue_ledger_predictions.jsonl \
  --eval-json outputs/day1/iclr2024_clean_dev_assistant_issue_ledger_metrics.json \
  --base-field mpnet_label
```

Render the clean-dev results dashboard:

```bash
python scripts/render_clean_dev_dashboard.py \
  --metrics "Heuristic=outputs/day1/iclr2024_clean_dev_assistant_heuristic_metrics.json" \
  --metrics "TF-IDF + LinearSVC=outputs/day1/iclr2024_clean_dev_assistant_tfidf_metrics.json" \
  --metrics "ModernBERT + LinearSVC=outputs/day1/iclr2024_clean_dev_assistant_modernbert_metrics.json" \
  --metrics "all-mpnet-base-v2 + LinearSVC=outputs/day1/iclr2024_clean_dev_assistant_mpnet_metrics.json" \
  --metrics "Issue-Ledger Calibrator=outputs/day1/iclr2024_clean_dev_assistant_issue_ledger_metrics.json" \
  --output outputs/day1/iclr2024_clean_dev_dashboard.html \
  --title "RevTrack clean-dev dashboard"
```

Build a high-confidence bootstrap dataset from a prefilled sheet:

```bash
python scripts/build_bootstrap_dataset.py \
  --candidates data/processed/iclr2024_issue_candidates.jsonl \
  --sheet experiments/day1/iclr2024_priority_sheet_issue_ledger_next50_prefilled.tsv \
  --output data/processed/iclr2024_bootstrap_train_v1.jsonl \
  --output-sheet experiments/day1/iclr2024_priority_sheet_issue_ledger_next50_bootstrap.tsv
```

Apply the issue-ledger logic to all candidates:

```bash
python scripts/predict_issue_ledger_transfer.py \
  --candidates data/processed/iclr2024_issue_candidates.jsonl \
  --base-predictions outputs/day1/iclr2024_candidates_mpnet_train_v2_transfer_predictions.jsonl \
  --silver-data data/processed/iclr2024_silver_dev.jsonl \
  --output outputs/day1/iclr2024_candidates_issue_ledger_train_v2_transfer_predictions.jsonl \
  --base-field mpnet_label
```

Audit a labeled sheet:

```bash
python scripts/audit_annotation_sheet.py \
  --sheet experiments/day0/iclr2024_priority_sheet_mpnet_prefilled.tsv
```

Render the animated issue ledger:

```bash
python scripts/render_issue_timeline.py \
  --data data/samples/smoke.jsonl \
  --predictions outputs/day0/heuristic_predictions.jsonl \
  --output outputs/day0/revtrack_issue_timeline.html
```

## Minimal Roadmap

1. Validate that the issue-status task is labelable.
2. Build a first adjudicated set from public OpenReview forums.
3. Compare a few strong open-source models on issue updating.
4. Add a lightweight `issue-ledger` intervention only after a clear failure pattern appears.

## Why This Can Be EMNLP-Shaped

- It targets research-assistant behavior instead of generic QA.
- It is dynamic rather than static.
- It supports crisp visualizations.
- It does not require expensive training to reach a first publishable signal.
