# RevTrack Dataset Card v0

Date: 2026-04-26

## Intended Use

RevTrack evaluates revision-aware scientific judgment: given a reviewer concern, author response, and revision evidence, the task is to decide whether the original concern is now `fixed`, `partially_fixed`, `unresolved`, or `regressed`.

The benchmark is intended for evaluating research-assistant systems and diagnostic models that must reason about changed manuscripts. It is not a general paper-quality benchmark and should not be used to infer final acceptance quality.

## Task Unit

Each row is one issue-level example extracted from OpenReview discussions. The model sees paper/context fields, the original review concern, aligned response evidence, and revision-summary evidence. The target is the post-revision status of that concern.

Primary fields:

- `issue_id`
- `paper_title`
- `review_excerpt` or `concern_text`
- `top_response_excerpt`
- `aligned_response_excerpt`
- `revision_summary`
- `gold_label` or `human_label`
- `evidence_span`
- `notes`

## Label Rubric

The label asks whether the original concern still holds after revision, not whether the author response sounds persuasive.

- `fixed`: the exact concern is addressed with concrete revision evidence.
- `partially_fixed`: the authors made real progress, but a material part of the concern remains.
- `unresolved`: the issue remains materially present or is deferred/reframed without enough evidence.
- `regressed`: the attempted fix introduces a new problem on the same axis or makes the paper less reliable.

Full rubric: [label_rubric.md](/data/sony/emnlp2026_revtrack/docs/label_rubric.md).

## Current Versions

| split or artifact | rows | status | notes |
| --- | ---: | --- | --- |
| ICLR 2024 clean dev v7 | 148 | assistant-adjudicated release candidate | label distribution: fixed 50 / partially_fixed 86 / unresolved 11 / regressed 1 |
| ICLR 2024 train v8 | 180 | training source for transfer probes | label distribution: fixed 63 / partially_fixed 104 / unresolved 12 / regressed 1 |
| ICLR 2024 candidate pool | 230 | quality gate passed | complete rate 1.000; model-disagreement rows 82 |
| ICLR 2024 human validation v1 | 40 | standard human-validation labels locked | user-reviewed AI-assisted signoff promoted on 2026-04-26 |
| ICLR 2025 repro v2 | 21 | standard human-validation stress sample locked | fixed 5 / partially_fixed 16 |
| ICLR 2025 expanded80 candidate pool | 322 | construction-ready frontier | complete rate 0.963; model-disagreement rows 244; high-disagreement rows 63 |
| ICLR 2025 expanded80 validation v1 | 80 | standard single-user validation locked | fixed 4 / partially_fixed 4 / unresolved 66 / regressed 6 |
| ICLR 2025 expanded80 assistant adjudication v1 | 80 | promoted source record | user-confirmed on 2026-04-26; keep provenance distinct from two-annotator IAA |
| NeurIPS 2024 limit100 candidate pool | 393 | quality gate passed | complete rate 1.000; model-disagreement rows 316 |
| NeurIPS 2024 limit100 validation v1 | 80 | standard single-user validation locked | partially_fixed 44 / unresolved 36; user-confirmed on 2026-04-28 |
| ICLR 2023 random80 validation v1 | 80 | standard single-user random/stratified validation locked | fixed 5 / partially_fixed 49 / unresolved 26; user-confirmed on 2026-04-29 |

## Provenance

Source data comes from public OpenReview conference discussions collected through the local OpenReview pipeline. The current standard human-validation labels cover `301 / 301` active validation rows: `61` rows after user-reviewed AI-assisted signoff promotion, `80` expanded80 rows after user-confirmed assistant-adjudication promotion on 2026-04-26, `80` NeurIPS 2024 rows after user-confirmed promotion on 2026-04-28, and `80` ICLR 2023 random80 rows after user-confirmed promotion on 2026-04-29.

This provenance supports the current standard-label claims, but it is not an independent two-annotator IAA study. A second annotator pass is required before reporting inter-annotator agreement as a paper claim.

## Quality Controls

Current gates:

- Candidate-pool gates pass for ICLR 2024, ICLR 2025 expanded80, and NeurIPS 2024 limit100.
- Blind/key/source packet audits pass for ICLR 2024 v1, ICLR 2025 v1, ICLR 2025 v2, ICLR 2025 expanded80 v1, NeurIPS 2024 limit100 v1, and ICLR 2023 random80 v1.
- Label-evidence completeness passes on the release-candidate labeled sheets, including expanded80 and ICLR 2023 random80: 329 audited rows, 0 evidence issues.
- AI-assisted signoff audit passes: 61 rows, 0 errors, 0 warnings; 41 key evidence rows and 20 explicitly marked context-fallback rows.
- Paper-readiness audit is `ready` for the current claim set; expanded80 and NeurIPS 2024 limit100 are standard single-user labeled active frontiers, while ICLR 2023 random80 is a standard single-user random/stratified slice.

Key artifacts:

- [paper_readiness_audit.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/paper_readiness_audit.md)
- [claim_evidence_ledger.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/claim_evidence_ledger.md)
- [iclr2025_expanded80_frontier_summary.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2025_expanded80_frontier_summary.md)
- [neurips2024_limit100_standard_transfer_metrics.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/neurips2024_limit100_standard_transfer_metrics.md)
- [iclr2023_limit80_random80_standard_transfer_metrics.md](/data/sony/emnlp2026_revtrack/outputs/day1/paper_assets/iclr2023_limit80_random80_standard_transfer_metrics.md)

## Reporting Boundaries

Safe current claims:

- The task is labelable with complete standard validation for the active audit set.
- In-domain ICLR 2024 experiments support the structured-evidence advantage claim.
- Accuracy can hide failures under label skew, especially on fixed-case recovery.
- The expanded ICLR 2025 pool removes the cross-year scale blocker at the active-frontier stage.
- Expanded80 standard transfer metrics support a bounded hardened cross-year active-frontier brittleness claim.
- NeurIPS 2024 standard transfer metrics support a bounded cross-venue standard single-user active-frontier claim.
- ICLR 2023 random80 standard transfer metrics support bounded random/stratified external-validity evidence within the ICLR venue family.

Do not claim yet:

- That expanded80 is an independent two-annotator IAA result.
- That expanded80, NeurIPS 2024 limit100, or ICLR 2023 random80 is an independent two-annotator IAA result.
- That active frontiers estimate natural label prevalence across all ICLR 2025 or NeurIPS 2024 review issues.
- That RevTrack broadly generalizes across all years or venues from one ICLR-family random/stratified slice.
- That the labels have measured inter-annotator reliability.
- That `regressed` performance is reliable; the current labeled pool has too few regressed examples.

## Limitations

The current strongest positive method evidence is in-domain ICLR 2024. The ICLR 2025 repro set is a validated stress sample, expanded80 and NeurIPS 2024 limit100 are standard single-user labeled active frontiers intentionally skewed toward model disagreement, and ICLR 2023 random80 is a standard single-user random/stratified slice. The label rubric depends on issue-level evidence alignment, so ambiguous review concerns and incomplete revision summaries can create boundary cases. Future releases should add a second annotator and another random or stratified venue-family slice.
