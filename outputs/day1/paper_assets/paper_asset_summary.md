# Paper Asset Summary

Generated from local RevTrack outputs.

## Main Clean-Dev Claim

- Latest benchmark: clean dev v7, `148` assistant-adjudicated issue examples.
- `Structured`: accuracy `0.682`, macro-F1 `0.704`.
- Best semantic baseline (`MPNet + LinearSVC`): accuracy `0.581`, macro-F1 `0.389`.
- No-overrides ablation: accuracy `0.655`, macro-F1 `0.424`.

## Active-Sampling Status

- Train v8 covers `180` labeled or high-confidence examples.
- Remaining unlabeled model-disagreement frontier in the current 230-candidate ICLR 2024 pool: `0`.

## Cross-Year Transfer Sanity Check

- ICLR 2025 repro v2 covers all `21` local issue candidates with label distribution `partially_fixed 16 / fixed 5`.
- `TF-IDF + LinearSVC`: accuracy `0.762`, macro-F1 `0.216`, fixed F1 `0.000`.
- `Structured`: accuracy `0.571`, macro-F1 `0.227`, fixed F1 `0.200`.
- Best macro-F1 on this tiny transfer set is `ModernBERT + LinearSVC` at `0.238`; this is still weak and not a method-win result.
- The important signal is negative evidence: high accuracy can come from predicting only the majority `partially_fixed` label.

## Null-Baseline Check

- ICLR 2024 clean dev v7 majority baseline: accuracy `0.581`, macro-F1 `0.184`.
- ICLR 2025 repro v2 majority baseline: accuracy `0.762`, macro-F1 `0.216`.
- On ICLR 2025 v2, TF-IDF matches the majority-label baseline exactly in accuracy and macro-F1 because it predicts only `partially_fixed`.

## Scaled Cross-Year Frontier

- ICLR 2025 expanded80 passes candidate-pool quality gates with `322` candidates and `244` model-disagreement rows.
- The expanded80 frontier summary is [iclr2025_expanded80_frontier_summary.md](iclr2025_expanded80_frontier_summary.md).
- The expanded80 blind validation packet has `80` standard single-user labels and an audited hidden assistant/model key.
- Standard expanded80 transfer metrics are available at [iclr2025_expanded80_standard_transfer_metrics.md](iclr2025_expanded80_standard_transfer_metrics.md).

## Standard-Labeled Expanded80 Frontier

- Expanded80 has `80` user-confirmed standard labels with complete evidence spans.
- Best expanded80 model by macro-F1: `issue_ledger` with accuracy `0.850`, macro-F1 `0.469`, fixed F1 `0.429`.
- Reporting boundary: expanded80 is a hardened standard single-user active frontier, not an independent two-annotator IAA set or natural-prevalence estimate.


## Standard-Labeled ICLR 2023 Random/Stratified Slice

- ICLR 2023 random80 has `80` user-confirmed standard labels and complete evidence spans.
- Best random80 transfer row by macro-F1: `issue_ledger` with accuracy `1.000`, macro-F1 `0.750`.
- Reporting boundary: this is standard single-user validation from user-confirmed resolved candidates; it is not independent IAA and should be reported by measured slice design, not as natural venue prevalence.


## Failure Taxonomy

- Failure taxonomy rows: `9` total, `4` from expanded80 standard validation.
- Paper table: [failure_taxonomy.md](failure_taxonomy.md) and `paper/tables/failure_taxonomy.tex`.
- Main diagnostic modes: stale criticism, over-crediting unresolved issues, fixed under-recovery, regression blindness, and partial/full-boundary errors.


## Claim Ledger

- Ready claims: `9`
- Integrity-ready claims: `0`
- Stress-evidence claims: `0`
- Not-ready claims: `0`
- Full ledger: [claim_evidence_ledger.md](claim_evidence_ledger.md)


## Paper Interpretation

The strongest current claim is not that the task is solved. It is that revision-aware structured evidence slots plus selective follow-up overrides beat pure semantic matching on a deliberately hardened, active-sampled revision benchmark, especially in macro-F1 and minority-label recovery. The 21-row ICLR 2025 repro result remains a reliability stress test; expanded80 and NeurIPS limit100 add standard-labeled hardened active-frontier evidence, and ICLR 2023 random80 adds bounded random/stratified external-validity evidence while preserving the boundary that none of these single-user packets are IAA results.
