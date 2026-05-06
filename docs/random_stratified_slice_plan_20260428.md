# Random/Stratified Venue Slice Plan

Date: 2026-04-28
Scope: post-NeurIPS-standardization expansion step for oral-level external-validity evidence.

## Goal

Add one broader venue/year slice that is **not** disagreement-focused active-frontier sampling, while preserving existing packet, evidence, and readiness gates.

## Why This Slice

- Current standard evidence is strong but bounded: expanded80 and NeurIPS limit100 are standard single-user active frontiers.
- The previous external-validity blocker was lack of random/stratified venue evidence; ICLR 2023 random80 now addresses this within the ICLR venue family, while non-ICLR random/stratified evidence remains a stretch target.
- This slice is intended to support broader transfer conclusions without claiming natural prevalence beyond measured strata.

## Candidate Targets

1. `ICML.cc/2024/Conference` (preferred cross-venue)
2. `ICLR.cc/2023/Conference` (lower schema risk fallback)

Selection rule:
- choose the first venue where probe + extraction pass minimum gates with acceptable response/revision coverage.

Current execution snapshot (2026-04-28):
- ICML 2024 probe is not currently usable in this pipeline.
- ICLR 2023 fallback reaches a complete-field subpool of `241` rows with `83` TF-IDF vs issue-ledger disagreement rows (`outputs/day1/iclr2023_limit80_candidate_pool_quality_gate_complete_with_tfidf_issue_ledger.json`).
- An initial random/stratified `80`-row blind/key/audit packet is now built and passes packet audit (`outputs/day1/iclr2023_limit80_random80_human_validation_v1_packet_audit.json`).
- The resolved-candidate sheet was user-confirmed and promoted into the canonical blind sheet on 2026-04-29 (`outputs/day1/iclr2023_limit80_random80_standard_validation_promotion.json`, `promoted_rows=80`).
- Standard transfer and failure-taxonomy assets now exist for the same `80` rows (`outputs/day1/paper_assets/iclr2023_limit80_random80_standard_transfer_metrics.md`; `outputs/day1/paper_assets/iclr2023_limit80_random80_standard_failure_taxonomy.md`).

## Sampling Policy

- Base pool: all extracted issue candidates from the selected venue slice.
- Sampling mode: stratified over `predicted label bucket` and `model disagreement bucket`.
- Target labeled rows: `80` minimum for parity with existing frontiers; `120` preferred if quality gates remain clean.
- Keep a separate provenance tag for this slice (do not merge wording with active-frontier provenance).

## Gate Sequence

1. Probe venue accessibility.
2. Collect raw OpenReview submissions.
3. Extract issue candidates.
4. Run candidate-pool quality gate.
5. Build blind/key/audit packet and run packet audit.
6. Complete standard single-user validation.
7. Evaluate transfer metrics + failure taxonomy.
8. Refresh claim ledger and paper-readiness audit.

Current gate status for ICLR 2023 random80:
- Steps 1-7: completed.
- Step 6: user-confirmed write-back completed on 2026-04-29.
- Step 7: standard-label transfer metrics and failure taxonomy completed.
- Runbook: `docs/iclr2023_random80_promotion_runbook.md`.

## Command Skeleton

```bash
cd /data/sony/emnlp2026_revtrack

# 1) probe
python scripts/probe_openreview_venue.py \
  --venue-id <VENUE_ID> \
  --limit 40 \
  --output-json outputs/day1/openreview_probe_<SLICE>.json

# 2) collect
python scripts/collect_openreview.py \
  --venue-id <VENUE_ID> \
  --limit <LIMIT> \
  --output data/raw/openreview/<SLICE>_submissions.jsonl \
  --diagnostics-json outputs/day1/<SLICE>_collect_diagnostics.json

# 3) extract
python scripts/prepare_openreview_issues.py \
  --input data/raw/openreview/<SLICE>_submissions.jsonl \
  --output data/processed/<SLICE>_issue_candidates.jsonl

# 4) candidate gate
python scripts/audit_candidate_pool.py \
  --candidates data/processed/<SLICE>_issue_candidates.jsonl \
  --output-json outputs/day1/<SLICE>_candidate_pool_quality_gate.json
```

Packet, validation, and refresh should reuse the same path as existing frontiers:

- `scripts/make_human_validation_sheet.py`
- `scripts/render_annotation_packet.py`
- `scripts/audit_human_validation_packet.py`
- `scripts/evaluate_human_validation.py`
- `scripts/export_active_frontier_standard_transfer_metrics.py`
- `scripts/export_active_frontier_failure_taxonomy.py`
- `scripts/export_paper_assets.py`
- `scripts/audit_paper_readiness.py`

## Reporting Boundaries

Keep all paper-facing wording aligned to:

- standard single-user validation (unless independent IAA is added),
- bounded claim scope per measured strata,
- no natural-prevalence claim without explicit random design and coverage checks.

## Stop Conditions

Stop and report immediately if:

- venue probe fails repeatedly;
- extracted pool cannot pass minimum complete-rate or disagreement gates;
- packet audit has leakage/key/source errors;
- next step would require independent IAA or larger scope not yet approved.
