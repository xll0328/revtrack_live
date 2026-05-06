# Related Work Matrix

Date: 2026-04-26

Scope: paper-facing positioning for RevTrack. This file is a compact audit trail for Section 7 and should stay aligned with [paper/sections/07_related_work.tex](/data/sony/emnlp2026_revtrack/paper/sections/07_related_work.tex).

## Positioning Summary

RevTrack is closest to peer-review corpora and evidence-grounded scientific QA, but its evaluation target is different: given an old review concern and later revision evidence, decide whether the concern is fixed, partially fixed, unresolved, or regressed. The benchmark is therefore about longitudinal issue status and issue-ledger maintenance, not acceptance prediction, review generation, or generic fact verification.

## Comparison Table

| Work | Main artifact or task | Overlap with RevTrack | RevTrack distinction | Citation key |
| --- | --- | --- | --- | --- |
| PeerRead | Paper drafts, expert reviews, decisions, and score-prediction tasks | Public scientific peer-review data | Tracks issue-level post-revision status rather than acceptance or score prediction | `kang-etal-2018-dataset` |
| NLPeer | Licensed multidomain peer-review corpus with drafts, camera-ready versions, reviews, metadata, and versioning | Reuses the idea that versioned peer-review data enables computational reviewing research | Converts versioned review context into a concern-resolution judgment with evidence spans and audits | `dycke-etal-2023-nlpeer` |
| Re2 | Full-stage OpenReview review, rebuttal, and discussion corpus | Covers rebuttal and reviewer-author interaction at large scale | Narrows the unit from whole discussion threads to one concern and one status label after revision | `zhang-etal-2025-re2` |
| PeerQA | Scientific document QA questions sourced from peer reviews, with evidence retrieval and answerability | Uses reviewer information needs as realistic scientific QA prompts | Outputs revision status rather than answers; evidence depends on author response and revision state | `baumgartner-etal-2025-peerqa` |
| FEVER | Evidence-grounded claim verification over textual sources | Shares the evidence-grounding requirement | The claim is a historical review concern whose status can become fixed, partially fixed, unresolved, or regressed after revision | `thorne-etal-2018-fever` |
| MARG | Multi-agent LLM review-feedback generation for scientific papers | Studies LLM assistance for scientific review | Evaluates whether an assistant retires stale criticism, not whether it can generate new comments | `darcy-etal-2024-marg` |
| Peer-review task inventory | Survey of peer-review tasks and datasets | Clarifies where review automation tasks differ | Positions RevTrack as issue-status tracking rather than paper-level review modeling | `staudinger-etal-2024-analysis` |
| LLM feedback for papers | Large-scale empirical analysis of LLM feedback on research papers | Shows LLM feedback can overlap with reviewer feedback | RevTrack tests whether old feedback should remain active after revision | `liang-etal-2023-can` |
| LLM-as-judge / G-Eval | Scalable model-based evaluation of open-ended outputs | Motivates prompted LLM baselines | RevTrack treats LLM judgments as stress baselines, not gold labels | `zheng-etal-2023-judging`; `liu-etal-2023-g` |
| Judge bias and judge panels | Bias analysis and multi-judge evaluation | Supports calibration and ensemble analysis | RevTrack adds label-level transfer stress and claim gating | `wang-etal-2024-large-language-models-fair`; `verga-etal-2024-replacing` |
| LLM annotation | Survey and empirical analysis of LLM annotation/annotation assistance | Motivates low-cost labeling assistance | RevTrack separates AI-assisted drafts from standard labels and claim-ready validation | `tan-etal-2024-large`; `gu-etal-2025-large` |
| Calibration under shift | Predictive calibration and uncertainty reliability under distribution shift | Supports transfer-risk interpretation beyond peer-review-specific tasks | RevTrack turns this into label-level revision-status risk (fixed/unresolved/regressed) under venue/year shift | `guo-etal-2017-calibration`; `ovadia-etal-2019-shift`; `koh-etal-2021-wilds` |

## Paper Claim Boundary

This matrix supports the novelty claim that RevTrack fills a revision-aware issue-tracking gap. It does not support claims about broad peer-review automation, acceptance prediction, or fully validated cross-year generalization. Expanded80 now has user-confirmed standard labels, but it remains a hardened active frontier rather than an independent IAA set or a natural-prevalence sample.
