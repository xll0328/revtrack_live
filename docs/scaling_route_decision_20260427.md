# Scaling Route Decision

Date: 2026-04-27

Purpose: choose the next evidence sprint for moving RevTrack from a clean scoped submission toward an oral-level EMNLP 2026 paper.

## Decision

Primary route: **NeurIPS 2024 cross-venue active frontier**.

Fallback route: **ICLR 2023 year-transfer frontier**.

IAA route: defer unless the paper will explicitly claim inter-annotator agreement. If time allows, run a targeted second-annotator pass after the NeurIPS frontier is selected, prioritizing fixed, unresolved, and regressed examples.

## Why NeurIPS 2024 First

The strongest remaining reviewer objection is limited generalization: current evidence is ICLR-heavy and expanded80 is an active frontier, not a natural-prevalence sample. A NeurIPS 2024 frontier directly adds a second venue family and is therefore higher value than another ICLR-only pass.

The local probe and sample collection are encouraging:

| artifact | result |
| --- | --- |
| Probe file | `outputs/day1/openreview_probe_neurips2024_limit20_20260427.json` |
| Probe API mode | `v2-notes` works |
| Probe sample | 20 submissions |
| Probe candidate yield | 157 issue candidates |
| Limit100 raw collection | `data/raw/openreview/neurips2024_limit100_submissions.jsonl` |
| Limit100 candidate file | `data/processed/neurips2024_limit100_issue_candidates.jsonl` |
| Limit100 rows | 393 repaired issue candidates |
| Candidate completeness | 393/393 rows complete, rate 1.000 |
| Duplicate issue IDs | 0 |
| TF-IDF predictions | `outputs/day1/neurips2024_limit100_candidates_tfidf_train_iclr2024_v8_transfer_predictions.jsonl` |
| ModernBERT predictions | `outputs/day1/neurips2024_limit100_candidates_modernbert_train_iclr2024_v8_transfer_predictions.jsonl` |
| MPNet predictions | `outputs/day1/neurips2024_limit100_candidates_mpnet_train_iclr2024_v8_transfer_predictions.jsonl` |
| Issue-ledger predictions | `outputs/day1/neurips2024_limit100_candidates_issue_ledger_train_iclr2024_v8_transfer_predictions.jsonl` |
| Structured predictions | `outputs/day1/neurips2024_limit100_candidates_structured_train_iclr2024_v8_transfer_predictions.jsonl` |
| Full-stack prediction disagreement | 316/393 comparable rows |
| Full-stack high-disagreement rows | 93 |
| Candidate gate with predictions | pass |
| Two-model priority sheet | `experiments/day1/neurips2024_limit100_priority_sheet_issue_ledger_vs_tfidf_transfer.tsv` |
| Two-model annotation packet | `outputs/day1/neurips2024_limit100_priority_sheet_issue_ledger_vs_tfidf_transfer_packet.html` |
| Multi-model frontier sheet | `experiments/day1/neurips2024_limit100_multi_frontier_structured_prefilled.tsv` |
| Multi-model packet | `outputs/day1/neurips2024_limit100_multi_frontier_structured_packet.html` |
| Blind validation sheet | `experiments/day1/neurips2024_limit100_human_validation_v1_blind.tsv` |
| Hidden key sheet | `experiments/day1/neurips2024_limit100_human_validation_v1_key.tsv` |
| Audit sheet | `experiments/day1/neurips2024_limit100_human_validation_v1_audit.tsv` |
| Packet audit | `outputs/day1/neurips2024_limit100_human_validation_v1_packet_audit.json`, pass |

The 80-row priority sheet is intentionally sharp: issue-ledger predicts `unresolved` for 59 rows, `fixed` for 18, and `regressed` for 3, while TF-IDF predicts `partially_fixed` for all 80. This is not a natural sample. It is a targeted over-crediting frontier and should be labeled as such until a broader validation set is built.

The repaired full-stack 80-row frontier is risk-focused: the hidden assistant/key labels are `unresolved=76` and `regressed=4`, with TF-IDF mostly predicting `partially_fixed`, semantic encoders split across `fixed`, `partially_fixed`, and `unresolved`, and issue-ledger/MPNet providing the strongest minority-label support. This packet is valuable for stress-testing over-crediting and regression blindness, but it must not be described as natural NeurIPS prevalence.

## Comparison Against Other Routes

| route | upside | risk | current evidence | recommendation |
| --- | --- | --- | --- | --- |
| NeurIPS 2024 cross-venue frontier | Directly addresses cross-venue generalization and raises oral-level novelty | Different OpenReview schema and venue norms required extractor repair | 100 submissions yield 393 clean candidates, complete rate 1.000, 316 full-stack disagreements | Primary route |
| ICLR 2023 year-transfer frontier | Low schema risk, same venue family, useful temporal replication | Less exciting than cross-venue; still ICLR-only | Probe limit20 yields 74 candidates using `v1-notes` | Fallback route |
| Independent second annotator | Addresses label subjectivity and enables IAA claim | Does not solve venue generalization; requires human time | Current labels are standard validation but not IAA | Targeted stretch |
| Larger model zoo | Easy to run if models are cached | Weak paper value unless tied to a claim | Current model set already supports accuracy-trap and structured-evidence claims | Do not prioritize |

## Required Next Steps

1. Label at least 80 NeurIPS rows as standard validation.

   Minimum paper-useful target: 80 standard labels with evidence spans. Best oral-level target: 80 standard labels plus a targeted second-annotator pass on 40 rows.

2. Rerun transfer metrics and failure taxonomy.

   The key paper question is whether over-crediting, fixed under-recovery, and regression blindness repeat outside ICLR.

3. Decide whether to broaden the NeurIPS sample beyond the high-risk frontier.

   The current blind packet is deliberately high-conflict and high-risk. For a natural-prevalence or broader performance claim, add a random or stratified NeurIPS validation slice.

4. Add a targeted second-annotator pass only if reporting IAA.

   The first NeurIPS packet can support standard validation after user review. IAA still requires an independent second pass.

## Claim Boundary Before Labels

Safe now:

- NeurIPS 2024 is feasible as a cross-venue candidate source.
- A 100-submission NeurIPS sample passes candidate count and completeness gates.
- TF-IDF vs issue-ledger disagreement creates a plausible 80-row active frontier.
- The repaired full-stack NeurIPS candidate gate passes with 316 disagreement rows and 93 high-disagreement rows.
- A blind/key/audit validation packet exists and passes packet audit.

Not safe yet:

- NeurIPS transfer performance;
- NeurIPS standard human-validation results;
- cross-venue generalization;
- natural prevalence;
- IAA.

## One-Sentence Sprint Goal

Turn NeurIPS 2024 from a promising candidate source into a standard-labeled cross-venue active frontier that tests whether RevTrack's stale-criticism and over-crediting failure modes survive outside ICLR.
