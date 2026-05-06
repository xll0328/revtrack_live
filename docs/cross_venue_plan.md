# Cross-Venue Expansion Plan

## Current Local State

The local workspace now contains the original ICLR 2024 pool plus a feasibility sample for NeurIPS 2024:

- `data/raw/openreview/iclr2024_submissions.jsonl`
- `data/processed/iclr2024_issue_candidates.jsonl`
- `data/raw/openreview/neurips2024_limit100_submissions.jsonl`
- `data/processed/neurips2024_limit100_issue_candidates.jsonl`

The ICLR 2024 pool has `230` issue candidates and is exhausted for model-disagreement active sampling after train v8. The next benchmark claim needs new venue/year evidence, not more sampling from the same pool.

The NeurIPS 2024 limit100 feasibility sample was repaired after detecting that author rebuttals were being misclassified as official reviews. The repaired pool has `393` issue candidates from `100` submissions, a complete-field rate of `1.000`, and no duplicate issue identifiers. The full prediction stack yields `316` disagreement rows and `93` high-disagreement rows, and the full-stack candidate-pool gate passes. This makes NeurIPS 2024 the current primary scaling route.

## Target Order

Start with the lowest-schema-risk targets, then move to broader transfer:

- `NeurIPS.cc/2024/Conference`: primary current route after the 2026-04-27 probe; high candidate yield and true cross-venue evidence.
- `ICLR.cc/2023/Conference`: same venue family, useful year-transfer check.
- `ICLR.cc/2025/Conference`: same venue family, stronger temporal-transfer check.
- `ICML.cc/2024/Conference`: secondary cross-venue robustness target if OpenReview metadata exposes enough response text.

Before using any non-ICLR target in a paper claim, manually verify that the candidate extraction is not silently degrading because of different review or rebuttal fields.

## 2026-04-27 Probe Results

| target | working API mode | probe size | issue candidates | candidate rate | decision |
| --- | --- | ---: | ---: | ---: | --- |
| `NeurIPS.cc/2024/Conference` | `v2-notes` | 20 submissions | 157 | 1.000 | primary route |
| `ICLR.cc/2023/Conference` | `v1-notes` | 20 submissions | 74 | 1.000 | fallback route |

NeurIPS 2024 was expanded to a limit100 feasibility sample and, after extraction repair, produced `393` clean issue candidates. A priority sheet for TF-IDF versus issue-ledger disagreement lives at `experiments/day1/neurips2024_limit100_priority_sheet_issue_ledger_vs_tfidf_transfer.tsv`, with an HTML packet at `outputs/day1/neurips2024_limit100_priority_sheet_issue_ledger_vs_tfidf_transfer_packet.html`.

The full-stack multi-model frontier lives at `experiments/day1/neurips2024_limit100_multi_frontier_structured_prefilled.tsv`, with packet HTML at `outputs/day1/neurips2024_limit100_multi_frontier_structured_packet.html`. It has also been converted into a blind validation packet:

- blind sheet: `experiments/day1/neurips2024_limit100_human_validation_v1_blind.tsv`
- hidden key: `experiments/day1/neurips2024_limit100_human_validation_v1_key.tsv`
- audit sheet: `experiments/day1/neurips2024_limit100_human_validation_v1_audit.tsv`
- packet audit: `outputs/day1/neurips2024_limit100_human_validation_v1_packet_audit.json`, pass with 0 errors and 0 warnings

This packet is now promoted as a user-confirmed standard single-user active-frontier validation result.

A conservative resolved-label candidate for this frontier is archived at `experiments/day1/neurips2024_limit100_resolved_adjudication_v1.tsv`, with a candidate blind sheet at `experiments/day1/neurips2024_limit100_standard_label_candidate_blind.tsv`. Its promoted distribution is `partially_fixed=44`, `unresolved=36`, and the canonical NeurIPS limit100 standard-validation artifacts are now user-confirmed.

The promotion path is implemented in `scripts/promote_resolved_candidate_to_human_validation.py`. The executed promotion manifest is `outputs/day1/neurips2024_limit100_standard_validation_promotion.json`, and the pre-promotion dry run is `outputs/day1/neurips2024_limit100_standard_validation_promotion_dry_run.json`.

## Quality Gates

A venue/year pool is usable only if it satisfies all of these:

- at least `150` extracted issue candidates after preprocessing
- at least `70%` of candidates have non-empty review concern, author response, and revision summary fields
- at least `25` high-disagreement candidates for the first active-sampling pass, unless the transfer models already agree and a random validation pass is used instead
- no evidence of venue-specific field leakage into labels
- human validation can cover at least `40` examples or `20%` of the first adjudicated tranche, whichever is smaller

Run the candidate-pool audit as the first local gate after prediction files exist:

```bash
TARGET_SLUG=iclr2025

python scripts/audit_candidate_pool.py \
  --candidates "data/processed/${TARGET_SLUG}_issue_candidates.jsonl" \
  --prediction tfidf="outputs/day1/${TARGET_SLUG}_candidates_tfidf_train_iclr2024_v8_transfer_predictions.jsonl" \
  --prediction modernbert="outputs/day1/${TARGET_SLUG}_candidates_modernbert_train_iclr2024_v8_transfer_predictions.jsonl" \
  --prediction mpnet="outputs/day1/${TARGET_SLUG}_candidates_mpnet_train_iclr2024_v8_transfer_predictions.jsonl" \
  --prediction issue_ledger="outputs/day1/${TARGET_SLUG}_candidates_issue_ledger_train_iclr2024_v8_transfer_predictions.jsonl" \
  --prediction structured="outputs/day1/${TARGET_SLUG}_candidates_structured_train_iclr2024_v8_transfer_predictions.jsonl" \
  --output-json "outputs/day1/${TARGET_SLUG}_candidate_pool_quality_gate.json" \
  --fail-on-error
```

For exploratory mini-runs, omit `--fail-on-error` and treat failures as scope notes rather than blockers. The local ICLR 2025 repro pool has complete fields but intentionally fails publishable-size gates (`21` candidates, `16` disagreement rows), while the ICLR 2024 pool passes (`230` candidates, `82` disagreement rows).

For a publishable generalization claim, require at least one new venue/year with an independently adjudicated clean set and report both in-domain ICLR 2024 and transfer numbers.

## Collection Commands

First probe the venue and API mode. This produces a machine-readable report with submission counts, reply counts, candidate counts, and explicit network/API errors:

```bash
TARGET_SLUG=iclr2025
VENUE_ID=ICLR.cc/2025/Conference

python scripts/probe_openreview_venue.py \
  --venue-id "$VENUE_ID" \
  --limit 20 \
  --timeout 8 \
  --retries 0 \
  --output-json "outputs/day1/openreview_probe_${TARGET_SLUG}.json"
```

Then use this template after the probe confirms a working API mode:

```bash
TARGET_SLUG=iclr2025
VENUE_ID=ICLR.cc/2025/Conference

python scripts/collect_openreview.py \
  --venue-id "$VENUE_ID" \
  --output "data/raw/openreview/${TARGET_SLUG}_submissions.jsonl" \
  --limit 500 \
  --api-mode v2-notes \
  --diagnostics-json "outputs/day1/openreview_collect_${TARGET_SLUG}_diagnostics.json"

python scripts/prepare_openreview_issues.py \
  --input "data/raw/openreview/${TARGET_SLUG}_submissions.jsonl" \
  --output "data/processed/${TARGET_SLUG}_issue_candidates.jsonl"

python scripts/export_candidates_as_examples.py \
  --input "data/processed/${TARGET_SLUG}_issue_candidates.jsonl" \
  --output "data/processed/${TARGET_SLUG}_candidate_examples.jsonl"
```

## Zero-Shot Transfer Commands

Train on the frozen ICLR 2024 train v8 labels and predict the new candidate pool. The transfer scripts accept either `issue_candidates` JSONL or exported `candidate_examples` JSONL; use `issue_candidates` as the default because the structured calibrators need candidate-specific fields.

```bash
TARGET_SLUG=iclr2025

python scripts/predict_tfidf_transfer.py \
  --train-data data/processed/iclr2024_train_v8.jsonl \
  --candidate-data "data/processed/${TARGET_SLUG}_issue_candidates.jsonl" \
  --output "outputs/day1/${TARGET_SLUG}_candidates_tfidf_train_iclr2024_v8_transfer_predictions.jsonl"

python scripts/predict_encoder_transfer.py \
  --train-data data/processed/iclr2024_train_v8.jsonl \
  --candidate-data "data/processed/${TARGET_SLUG}_issue_candidates.jsonl" \
  --model /data/sony/.cache/huggingface/hub/models--answerdotai--ModernBERT-base/snapshots/8949b909ec900327062f0ebf497f51aef5e6f0c8 \
  --output "outputs/day1/${TARGET_SLUG}_candidates_modernbert_train_iclr2024_v8_transfer_predictions.jsonl" \
  --local-files-only

python scripts/predict_encoder_transfer.py \
  --train-data data/processed/iclr2024_train_v8.jsonl \
  --candidate-data "data/processed/${TARGET_SLUG}_issue_candidates.jsonl" \
  --model /data/sony/.cache/huggingface/hub/models--sentence-transformers--all-mpnet-base-v2/snapshots/9a3225965996d404b775526de6dbfe85d3368642 \
  --output "outputs/day1/${TARGET_SLUG}_candidates_mpnet_train_iclr2024_v8_transfer_predictions.jsonl" \
  --local-files-only

python scripts/predict_issue_ledger_transfer.py \
  --candidates "data/processed/${TARGET_SLUG}_issue_candidates.jsonl" \
  --base-predictions "outputs/day1/${TARGET_SLUG}_candidates_mpnet_train_iclr2024_v8_transfer_predictions.jsonl" \
  --output "outputs/day1/${TARGET_SLUG}_candidates_issue_ledger_train_iclr2024_v8_transfer_predictions.jsonl"

python scripts/predict_structured_calibrator_transfer.py \
  --train-sheet experiments/day1/iclr2024_train_v8_sheet_refreshed.tsv \
  --candidates "data/processed/${TARGET_SLUG}_issue_candidates.jsonl" \
  --tfidf-predictions "outputs/day1/${TARGET_SLUG}_candidates_tfidf_train_iclr2024_v8_transfer_predictions.jsonl" \
  --modernbert-predictions "outputs/day1/${TARGET_SLUG}_candidates_modernbert_train_iclr2024_v8_transfer_predictions.jsonl" \
  --mpnet-predictions "outputs/day1/${TARGET_SLUG}_candidates_mpnet_train_iclr2024_v8_transfer_predictions.jsonl" \
  --output "outputs/day1/${TARGET_SLUG}_candidates_structured_train_iclr2024_v8_transfer_predictions.jsonl"
```

## First Annotation Pass

Prioritize `structured` against the strongest semantic baseline and the issue-ledger model:

```bash
TARGET_SLUG=iclr2025

python scripts/make_priority_sheet.py \
  --candidates "data/processed/${TARGET_SLUG}_issue_candidates.jsonl" \
  --primary-predictions "outputs/day1/${TARGET_SLUG}_candidates_structured_train_iclr2024_v8_transfer_predictions.jsonl" \
  --secondary-predictions "outputs/day1/${TARGET_SLUG}_candidates_mpnet_train_iclr2024_v8_transfer_predictions.jsonl" \
  --primary-name structured \
  --secondary-name mpnet \
  --output "experiments/day1/${TARGET_SLUG}_priority_sheet_structured_vs_mpnet_transfer.tsv" \
  --sample-size 40 \
  --require-disagreement
```

After the first tranche is adjudicated, run a blind human-validation packet before making any transfer claim.

For a single de-duplicated frontier across several comparison models, use:

```bash
TARGET_SLUG=iclr2025

python scripts/make_multi_model_frontier_sheet.py \
  --candidates "data/processed/${TARGET_SLUG}_issue_candidates.jsonl" \
  --anchor-name structured \
  --anchor-predictions "outputs/day1/${TARGET_SLUG}_candidates_structured_train_iclr2024_v8_transfer_predictions.jsonl" \
  --comparison tfidf="outputs/day1/${TARGET_SLUG}_candidates_tfidf_train_iclr2024_v8_transfer_predictions.jsonl" \
  --comparison modernbert="outputs/day1/${TARGET_SLUG}_candidates_modernbert_train_iclr2024_v8_transfer_predictions.jsonl" \
  --comparison mpnet="outputs/day1/${TARGET_SLUG}_candidates_mpnet_train_iclr2024_v8_transfer_predictions.jsonl" \
  --comparison issue_ledger="outputs/day1/${TARGET_SLUG}_candidates_issue_ledger_train_iclr2024_v8_transfer_predictions.jsonl" \
  --output "experiments/day1/${TARGET_SLUG}_multi_frontier_structured_prefilled.tsv" \
  --sample-size 80

python scripts/render_annotation_packet.py \
  --sheet "experiments/day1/${TARGET_SLUG}_multi_frontier_structured_prefilled.tsv" \
  --output "outputs/day1/${TARGET_SLUG}_multi_frontier_structured_packet.html" \
  --title "${TARGET_SLUG} multi-model structured frontier"
```

Before sending any blind packet to a human annotator, audit the packet/key/source alignment:

```bash
python scripts/audit_human_validation_packet.py \
  --blind "experiments/day1/${TARGET_SLUG}_human_validation_v1_blind.tsv" \
  --key "experiments/day1/${TARGET_SLUG}_human_validation_v1_key.tsv" \
  --audit "experiments/day1/${TARGET_SLUG}_human_validation_v1_audit.tsv" \
  --source-sheet "experiments/day1/${TARGET_SLUG}_multi_frontier_structured_assistant.tsv" \
  --output-json "outputs/day1/${TARGET_SLUG}_human_validation_v1_packet_audit.json" \
  --fail-on-error
```

This check must pass before reporting human-validation agreement. It catches duplicate IDs, blind-sheet label leakage, key/source label mismatches, audit/key mismatches, and missing source rows.

To maintain the current independent-validation backlog, export the active work queue:

```bash
python scripts/export_human_validation_queue.py
```

The generated queue lives at [human_validation_work_queue.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/human_validation_work_queue.md) and [human_validation_work_queue.csv](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/human_validation_work_queue.csv). It is triage metadata only; completed blind-sheet labels still need an independent human annotator before they can be reported as human validation.

To split the queue into small blind review batches:

```bash
python scripts/export_human_validation_batches.py
```

The batch manifest lives at [human_validation_priority_manifest.md](/data/sony/emnlp2026_revtrack/outputs/day1/human_validation_batches/human_validation_priority_manifest.md). These batches are convenience views over the blind sheets, not hidden-key files.

To validate completed batches and prepare merged blind-sheet copies:

```bash
python scripts/merge_human_validation_batches.py
```

The ingest report lives at [human_validation_batch_ingest_report.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/human_validation_batch_ingest_report.md). The default mode is a dry run that writes merged copies under [human_validation_batch_ingest](/data/sony/emnlp2026_revtrack/outputs/day1/human_validation_batch_ingest); use `--write-canonical` only after the dry run has no errors, then rerun `evaluate_human_validation.py` and the paper-readiness audit.

The preferred one-command post-validation path is:

```bash
python scripts/run_human_validation_pipeline.py
```

This performs a dry-run batch ingest, writes preview agreement metrics, and refreshes the readiness audit without modifying canonical blind sheets. After checking the preview report, commit the completed annotations into the canonical blind sheets and refresh official artifacts with:

```bash
python scripts/run_human_validation_pipeline.py --write-canonical
```

If the goal is a fast final author signoff rather than independent blind validation, export the non-blind AI-assisted signoff sheet:

```bash
python scripts/export_ai_assisted_validation_signoff.py
```

The signoff manifest lives at [ai_assisted_validation_signoff_manifest.md](/data/sony/emnlp2026_revtrack/outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff_manifest.md). This sheet exposes assistant labels, assistant evidence, and model disagreement context; it can support final human review, but it must stay separate from independent validation evidence. Rows without a key-level assistant evidence span are filled with an explicitly prefixed context fallback from aligned response, top response, revision summary, or assistant note text.

Before using the signoff sheet, run the six-pass audit:

```bash
python scripts/audit_ai_assisted_validation_signoff.py
```

The audit report lives at [ai_assisted_validation_signoff_audit.md](/data/sony/emnlp2026_revtrack/outputs/day1/ai_assisted_validation_signoff/ai_assisted_validation_signoff_audit.md). It checks schema/identity, queue coverage, context completeness, assistant evidence, non-blind isolation, and high-risk triage order, and reports any rows using context fallback evidence spans.

After a human has reviewed and accepted the signoff rows, promote them into the canonical human-validation sheets with explicit provenance:

```bash
python scripts/promote_ai_signoff_to_human_validation.py --write
python scripts/run_human_validation_pipeline.py --write-canonical
```

This records the rows as human validation for project tracking, but the provenance remains user-reviewed AI-assisted signoff rather than independent blind relabeling. Report that distinction explicitly.

## Paper-Level Decision Rule

The cross-venue result is paper-worthy only if it shows one of these:

- structured evidence remains better than semantic baselines on macro-F1 after independent adjudication
- transfer exposes a systematic failure mode that motivates a stronger revision-aware model
- human validation shows the label rubric is reliable enough to freeze a benchmark release

If none of these hold, the result is still useful, but the paper should pivot from "benchmark plus method wins" to "benchmark exposes brittle revision tracking under venue shift."
