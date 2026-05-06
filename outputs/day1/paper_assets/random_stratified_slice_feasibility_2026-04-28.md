# Random/Stratified Slice Feasibility Snapshot

Date: 2026-04-28

## Objective

Find the next broader venue/year slice beyond disagreement-focused active frontiers.

## Probe Results

### ICML 2024 (`ICML.cc/2024/Conference`, limit 40)

- Probe report: `outputs/day1/openreview_probe_icml2024_limit40_20260428.json`
- Retry report: `outputs/day1/openreview_probe_icml2024_limit40_timeout20_20260428.json`
- Outcome: not usable as-is for this pipeline.
  - `v2-notes`: submissions appear, but `issue_candidates=0`.
  - `v2-search`: API returns `400`.
  - `v1-notes`: `submissions=0`.

### ICLR 2023 (`ICLR.cc/2023/Conference`, limit 40 probe)

- Probe report: `outputs/day1/openreview_probe_iclr2023_limit40_timeout20_20260428.json`
- Outcome: feasible fallback.
  - `v1-notes`: `submissions=40`, `issue_candidates=147`, `candidate_rate=1.0`.

## Collection + Extraction (ICLR 2023 limit80)

- Raw submissions: `data/raw/openreview/iclr2023_limit80_submissions.jsonl` (`80` rows)
- Collection diagnostics: `outputs/day1/iclr2023_limit80_collect_diagnostics_20260428.json`
- Extracted candidates: `data/processed/iclr2023_limit80_issue_candidates.jsonl` (`294` issue candidates)

## Candidate-Gate Status

### Raw pool gate

- Report: `outputs/day1/iclr2023_limit80_candidate_pool_quality_gate.json`
- Result: `ok=false`
- Reason: complete-field rate `0.820 < 0.950`.

### Complete-field subpool gate

- Filtered pool: `data/processed/iclr2023_limit80_issue_candidates_complete.jsonl` (`241` rows)
- Report: `outputs/day1/iclr2023_limit80_candidate_pool_quality_gate_complete.json`
- Result: `ok=true` under current pre-disagreement feasibility thresholds.
- Caveat (resolved below): disagreement gate required prediction files.

## Disagreement Gate (TF-IDF + Issue-Ledger)

- TF-IDF predictions: `outputs/day1/iclr2023_limit80_candidates_tfidf_train_iclr2024_v8_transfer_predictions.jsonl`
- Issue-ledger predictions: `outputs/day1/iclr2023_limit80_candidates_issue_ledger_train_iclr2024_v8_transfer_predictions.jsonl`
- Gate report: `outputs/day1/iclr2023_limit80_candidate_pool_quality_gate_complete_with_tfidf_issue_ledger.json`
- Result: `ok=true` with `241` comparable rows and `83` disagreement rows.
- Label-combo concentration:
  - `issue_ledger=partially_fixed; tfidf=partially_fixed`: `153`
  - `issue_ledger=unresolved; tfidf=partially_fixed`: `78`

## Current Status

The complete-field ICLR2023 slice is now promoted from packet-ready to standard-labeled random/stratified evidence on the existing `80`-row packet, with provenance kept distinct from active-frontier packets.

## Initial Packet Build (completed)

- Seed sheet (`80` sampled rows): `experiments/day1/iclr2023_limit80_random_stratified_seed80.tsv`
- Seed summary: `outputs/day1/iclr2023_limit80_random_stratified_seed80_summary.json`
- Blind sheet: `experiments/day1/iclr2023_limit80_random80_human_validation_v1_blind.tsv`
- Hidden key: `experiments/day1/iclr2023_limit80_random80_human_validation_v1_key.tsv`
- Audit sheet: `experiments/day1/iclr2023_limit80_random80_human_validation_v1_audit.tsv`
- Packet HTML: `outputs/day1/iclr2023_limit80_random80_human_validation_v1_blind_packet.html`
- Packet audit: `outputs/day1/iclr2023_limit80_random80_human_validation_v1_packet_audit.json` (`ok=true`, `errors=0`, `warnings=0`)
- Standard validation metrics: `outputs/day1/iclr2023_limit80_random80_human_validation_v1_standard_metrics.json` (`labeled_rows=80`, `unlabeled_rows=0`)

## Resolved-Candidate Prep (completed)

- Assistant adjudication draft: `experiments/day1/iclr2023_limit80_random80_assistant_adjudication_v1.tsv`
- Resolved candidate sheet: `experiments/day1/iclr2023_limit80_random80_resolved_adjudication_v1.tsv`
- Human-review candidate blind copy: `experiments/day1/iclr2023_limit80_random80_resolved_label_candidate_for_human_review.tsv`
- Promotion dry run: `outputs/day1/iclr2023_limit80_random80_standard_validation_promotion_dry_run.json` (`status=ok`, `promotable_rows=80`)
- Promotion write report: `outputs/day1/iclr2023_limit80_random80_standard_validation_promotion.json` (`status=ok`, `promoted_rows=80`)
- Standard transfer metrics: `outputs/day1/paper_assets/iclr2023_limit80_random80_standard_transfer_metrics.md`
- Standard failure taxonomy: `outputs/day1/paper_assets/iclr2023_limit80_random80_standard_failure_taxonomy.md`
- Historical pre-confirmation transfer metrics: `outputs/day1/paper_assets/iclr2023_limit80_random80_resolved_candidate_transfer_metrics.md`
- Historical pre-confirmation failure taxonomy: `outputs/day1/paper_assets/iclr2023_limit80_random80_resolved_candidate_failure_taxonomy.md`

Boundary: report the promoted sheet as standard single-user validation only. It is not an independent two-annotator IAA result and should be described by the measured random/stratified slice design rather than as unmeasured natural venue prevalence.
