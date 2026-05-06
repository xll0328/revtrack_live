# Idea Brief

## One-Sentence Story

LLMs can criticize a paper in isolation, but they are much worse at deciding whether that criticism still holds after the paper is revised.

## Task

Given:

- a paper snapshot
- one review concern
- the author response
- a revision summary

Predict one of:

- `fixed`
- `partially_fixed`
- `unresolved`
- `regressed`

## Why This Is Better Than A Generic Review Benchmark

- the scientific action is temporal
- the model must update a prior judgment
- stale criticism is an observable failure mode
- the task is close to real research workflows

## EMNLP Oral / Best-Paper Version

At least three of these need to hold:

- strong models are far from ceiling
- errors cluster into sharp behaviors such as stale criticism or over-crediting
- the effect transfers across at least two venues or domains
- a simple issue-ledger intervention improves judgment without making the model overly lenient
- humans agree the benchmark reflects useful research-assistant behavior

## Current Evidence Snapshot

- ICLR 2024 clean dev v7 contains `148` assistant-adjudicated issue examples.
- The strict `LOO-feature` structured calibrator reaches `0.682` accuracy and `0.704` macro-F1.
- The best semantic baseline, `MPNet + LinearSVC`, reaches `0.581` accuracy and `0.389` macro-F1.
- Removing structured hard overrides drops macro-F1 to `0.424`, which supports the hypothesis that explicit revision-follow-up cues matter for minority-label recovery.
- The current 230-candidate ICLR 2024 active-sampling pool is exhausted for model-disagreement sampling after train v8.
- Standard validation labels are complete for `301 / 301` active audit rows: `40` ICLR 2024 v1, `21` ICLR 2025 repro v2, `80` ICLR 2025 expanded80, `80` NeurIPS 2024 limit100, and `80` ICLR 2023 random80.
- ICLR 2025 repro v2 remains a validated `21`-row stress sample; expanded80 adds a `322`-candidate cross-year pool with `244` model-disagreement rows; NeurIPS 2024 limit100 adds a `393`-candidate cross-venue pool with `316` model-disagreement rows; and ICLR 2023 random80 adds a user-confirmed random/stratified standard slice.

## Current Non-Negotiable Gaps

- Cross-year data scale is no longer the blocker for the current claim set; the current gap is broader non-ICLR generalization and/or an independent IAA pass.
- The paper needs a memorable running example and failure taxonomy, not just metric tables.
- `regressed` has only one clean-dev example, so per-label conclusions about regression detection are not yet defensible.

## Fatal Risks

- `MAJOR`: label boundaries between `partially_fixed` and `unresolved` may blur
- `MAJOR`: public review text varies a lot by venue, which can make preprocessing brittle
- `MINOR`: some venues expose only the final submission PDF, not a full PDF history

## Mitigations

- define label rules around concrete issue resolution, not tone
- keep the first version text-first before PDF-diff-heavy modeling
- annotate a small but diverse set before scaling
- expand to at least one additional venue or year before making generalization claims
- use the completed standard human-validation labels as the current benchmark standard
- route any new scaled transfer pool through the same signoff and audit path before freezing claims
