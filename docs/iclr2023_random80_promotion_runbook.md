# ICLR 2023 Random80 Promotion Runbook

Date: 2026-04-28
Executed: 2026-04-29

Purpose: finish the random/stratified ICLR 2023 `80`-row lane by promoting the resolved-candidate labels into the canonical blind sheet after explicit user confirmation.

## Current State

- Blind/key/audit packet exists and passes packet audit.
- Resolved-candidate sheet is prepared:
  - `experiments/day1/iclr2023_limit80_random80_resolved_adjudication_v1.tsv`
- Dry-run promotion passes:
  - `outputs/day1/iclr2023_limit80_random80_standard_validation_promotion_dry_run.json`
- Write promotion is complete:
  - `outputs/day1/iclr2023_limit80_random80_standard_validation_promotion.json`
  - `promoted_rows=80`
- Standard transfer/taxonomy assets exist and are paper-facing under standard single-user validation provenance.

## Promotion Command (write)

```bash
cd /data/sony/emnlp2026_revtrack

python scripts/promote_resolved_candidate_to_human_validation.py \
  --resolved-candidate experiments/day1/iclr2023_limit80_random80_resolved_adjudication_v1.tsv \
  --blind-sheet experiments/day1/iclr2023_limit80_random80_human_validation_v1_blind.tsv \
  --report-json outputs/day1/iclr2023_limit80_random80_standard_validation_promotion.json \
  --confirmation-note "User confirmed ICLR 2023 random80 resolved candidate labels in Codex chat on 2026-04-29." \
  --write
```

## Post-Promotion Refresh

```bash
python scripts/evaluate_human_validation.py \
  --human-sheet experiments/day1/iclr2023_limit80_random80_human_validation_v1_blind.tsv \
  --key experiments/day1/iclr2023_limit80_random80_human_validation_v1_key.tsv \
  --output-json outputs/day1/iclr2023_limit80_random80_human_validation_v1_standard_metrics.json \
  --mismatch-output outputs/day1/iclr2023_limit80_random80_human_validation_v1_standard_mismatches.tsv

python scripts/export_active_frontier_standard_transfer_metrics.py \
  --dataset-name "ICLR 2023 random80 standard slice" \
  --human-sheet experiments/day1/iclr2023_limit80_random80_human_validation_v1_blind.tsv \
  --candidates data/processed/iclr2023_limit80_issue_candidates_complete.jsonl \
  --output-jsonl data/processed/iclr2023_limit80_random80_standard_validation_v1.jsonl \
  --metrics-csv outputs/day1/paper_assets/iclr2023_limit80_random80_standard_transfer_metrics.csv \
  --metrics-md outputs/day1/paper_assets/iclr2023_limit80_random80_standard_transfer_metrics.md \
  --details-dir outputs/day1/iclr2023_limit80_random80_standard_transfer \
  --manifest outputs/day1/iclr2023_limit80_random80_standard_transfer_manifest.json \
  --sample-design random_stratified \
  --validation-status standard_single_user_confirmed \
  --prediction tfidf=outputs/day1/iclr2023_limit80_candidates_tfidf_train_iclr2024_v8_transfer_predictions.jsonl \
  --prediction issue_ledger=outputs/day1/iclr2023_limit80_candidates_issue_ledger_train_iclr2024_v8_transfer_predictions.jsonl

python scripts/export_active_frontier_failure_taxonomy.py \
  --dataset-name "ICLR 2023 random80 standard slice" \
  --label-sheet experiments/day1/iclr2023_limit80_random80_human_validation_v1_blind.tsv \
  --details-dir outputs/day1/iclr2023_limit80_random80_standard_transfer \
  --output-csv outputs/day1/paper_assets/iclr2023_limit80_random80_standard_failure_taxonomy.csv \
  --output-md outputs/day1/paper_assets/iclr2023_limit80_random80_standard_failure_taxonomy.md \
  --sample-design random_stratified \
  --validation-status standard_single_user_confirmed
```

## Boundary

- Before the `--write` promotion: use only as proxy/pre-confirmation analysis.
- After the `--write` promotion: use as standard single-user validation only, not independent IAA.
- The `--write` promotion was executed on 2026-04-29 after explicit user confirmation in Codex chat.
