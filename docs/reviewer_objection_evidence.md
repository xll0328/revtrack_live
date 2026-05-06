# Reviewer Objection Evidence Matrix

Date: 2026-04-28

Purpose: convert likely weak-reject objections into concrete paper text, evidence artifacts, and sprint actions. This is an internal defense plan for raising RevTrack from a clean scoped submission to an oral-level paper.

## Current Position

The current scoped claim set is submission-ready: paper-readiness is `ready`, all nine claims in the claim ledger are `ready`, the citation audit passes, and the active validation set has `301 / 301` standard labels.

The remaining oral/best-paper gap is not basic correctness. It is whether reviewers see RevTrack as a new evaluation lens for AI-assisted science rather than a small peer-review classification benchmark.

## Objection Matrix

| reviewer objection | risk | current answer | evidence already available | paper location | remaining action |
| --- | --- | --- | --- | --- | --- |
| "This is just paper-review classification." | high | RevTrack is issue-level temporal update: the target is whether an old concern still holds after revision, not acceptance, score, or static critique quality. | Figure 1 stale-criticism example; related-work comparison; dataset card task unit. | `paper/sections/01_introduction.tex`; `paper/sections/02_task.tex`; `paper/sections/07_related_work.tex` | Keep Figure 1 and first two Introduction paragraphs centered on criticism retirement. Avoid leading with model wins. |
| "The benchmark is too small." | high | The publishable claim is scoped: ICLR 2024 in-domain evidence plus ICLR 2025 and NeurIPS 2024 stress/frontier evidence, with ICLR 2023 random80 as bounded random/stratified external-validity evidence. The expanded and cross-venue pools remove the immediate scale blocker, but not broad prevalence. | ICLR 2024 pool: 230 candidates; ICLR 2025 expanded pool: 322 candidates, 244 disagreement rows; NeurIPS 2024 pool: 393 candidates, 316 disagreement rows; expanded80/limit100/random80: 80+80+80 standard labels. | `paper/sections/03_dataset.tex`; `paper/sections/05_experiments.tex`; `paper/sections/08_limitations.tex` | Use exact provenance: active frontiers vs random/stratified slice. Add a second annotator before claiming IAA. |
| "Labels are subjective." | high | Labels are issue-resolution judgments with explicit evidence spans and notes; label-evidence audit covers 329 rows with 0 evidence issues. | `paper_readiness_audit.md`; label-evidence audits; dataset card rubric; 301/301 standard validation rows. | `paper/sections/02_task.tex`; `paper/sections/03_dataset.tex`; `paper/sections/08_limitations.tex` | Do not claim IAA. Add a second annotator only if reporting inter-annotator reliability. |
| "AI-assisted signoff contaminates human validation." | high | Current labels are user-confirmed standard validation with provenance disclosed. They are not reported as independent two-annotator labels. Blind validation and key/signoff artifacts remain separated. | Promotion manifests; packet audits; readiness provenance text; dataset card provenance. | `paper/sections/03_dataset.tex`; `paper/sections/08_limitations.tex`; appendix artifact manifest. | Keep exact phrase "user-confirmed standard validation" and avoid "independent human agreement." |
| "The model gains are heuristic or overfit." | medium-high | The structured model is positioned as a diagnostic intervention, not a universal SOTA model. The no-overrides ablation shows the contribution of explicit revision cues: macro-F1 drops from 0.704 to 0.424. | `clean_dev_metrics.csv`; main results table; no-overrides ablation. | `paper/sections/04_models.tex`; `paper/sections/05_experiments.tex` | Add one sentence in Results that the point is interpretability of evidence slots, not model zoo dominance. |
| "Accuracy improvements are not enough." | medium-high | The paper makes accuracy the failure case: majority and TF-IDF can look strong by accuracy while missing fixed/unresolved/regressed labels. | ICLR 2024 majority macro-F1 0.184; ICLR 2025 TF-IDF fixed F1 0.000; null baseline table. | `paper/sections/02_task.tex`; `paper/sections/05_experiments.tex`; `paper/tables/null_baselines.tex` | Keep macro-F1 and per-label recovery in every result claim. Never sell accuracy alone. |
| "Cross-year evidence is not a natural benchmark." | medium-high | Correct. The paper treats expanded80 and NeurIPS limit100 as disagreement-focused standard single-user active frontiers, and ICLR 2023 random80 as a measured random/stratified slice. These support bounded transfer and external-validity claims, not unmeasured natural prevalence. | expanded80 + NeurIPS frontier summaries; ICLR 2023 random80 standard transfer metrics; claim ledger C4/C6/C8/C9; limitations. | `paper/sections/03_dataset.tex`; `paper/sections/05_experiments.tex`; `paper/sections/08_limitations.tex` | Keep slice-design language exact; add independent annotator coverage before IAA claims. |
| "Failure taxonomy is post-hoc." | medium | The taxonomy is grounded in labeled examples and aggregate expanded80 error counts; it is used to explain why static semantic matching fails. | `failure_taxonomy.md`; Table 3; Results RQ3. | `paper/sections/05_experiments.tex`; `paper/tables/failure_taxonomy.tex` | Make taxonomy one of the paper's central findings, not a descriptive afterthought. Add one takeaway sentence after Table 3. |
| "Regressed is too rare to evaluate." | medium | The paper already does not make stable regression-performance claims. Regressed remains in the label set because it is high risk, but results are framed cautiously. | Dataset card reporting boundaries; limitations; expanded80 regressed count 6. | `paper/sections/02_task.tex`; `paper/sections/05_experiments.tex`; `paper/sections/08_limitations.tex` | State that regression detection is a release target and diagnostic category, not a solved performance result. |
| "Text-only revision evidence misses real PDF changes." | medium | Current evidence uses review text, author responses, revision summaries, and metadata. The limitation is explicit; future work adds PDF-aware diff extraction. | limitations section; dataset card limitations. | `paper/sections/08_limitations.tex` | Keep this as a limitation rather than over-engineering PDF differencing before ARR. |
| "Related work is incomplete." | medium | Current related work cites peer-review corpora, peer-review QA, fact verification, and review generation, then distinguishes issue-status tracking. Citation audit passes. | `refs.bib`; `paper_citation_audit.md`; related-work comparison table. | `paper/sections/07_related_work.tex`; appendix comparison table. | Add one document-revision/temporal-update citation only if a clearly relevant primary source is selected. |
| "Reproducibility is fragile." | low-medium | The paper ships claim ledger, dataset card, readiness audit, citation audit, packet audits, label-evidence audits, and table/figure generation scripts. | paper-readiness audit; citation audit; appendix artifact manifest. | appendix artifact manifest; dataset section. | Prepare anonymized artifact bundle and a one-command reproduction README before final submission. |
| "Why EMNLP?" | medium | The task evaluates NLP systems as research assistants: evidence tracking, review understanding, temporal update, and reliability under skew. | Introduction framing; related work; failure taxonomy. | `paper/main.tex`; `paper/sections/01_introduction.tex`; `paper/sections/07_related_work.tex` | Make the title/abstract/intro lead with AI-assisted science and revision-aware evaluation, not "new dataset." |

## Highest-Value Fixes Before ARR

1. Add prevalence-sensitive non-ICLR random/stratified evidence.

   Best option: another venue/year with at least 80 standard-labeled issue examples sampled by a random/stratified design, plus the same null, semantic, structured, and issue-ledger baselines. This directly addresses the hardest remaining oral-level objection: limited natural-distribution evidence beyond ICLR-family data.

2. Decide whether to buy IAA.

   If time permits, run an independent second-annotator pass on a targeted slice. Minimum useful target: 40 to 80 examples covering fixed, unresolved, and regressed cases. Without it, keep all language at "standard validation" and do not report agreement.

3. Turn the failure taxonomy into a main finding.

   The taxonomy should be introduced as the mechanism behind the benchmark, not just an error table. The paper should make reviewers remember stale criticism, over-crediting, fixed under-recovery, regression blindness, and partial/full boundary errors.

4. Harden the artifact story.

   Prepare an anonymized artifact index with exact regeneration commands for tables, Figure 1, readiness audit, citation audit, and label-evidence audit.

5. Prepare a rebuttal skeleton now.

   Write one 120-word answer for each high-risk objection above. The author-response window is short; the defense should be ready before reviews arrive.

## Recommended Claim Boundaries

Safe:

- RevTrack defines an issue-level revision-status tracking task for scientific review assistance.
- The current active validation set has `301 / 301` standard labels with complete evidence/audit provenance.
- Structured revision evidence improves in-domain macro-F1 on the hardened ICLR 2024 benchmark.
- Accuracy hides fixed-case and unresolved-case failures under label skew.
- Expanded80 and NeurIPS limit100 support bounded standard-labeled active-frontier transfer-brittleness claims; ICLR 2023 random80 supports bounded random/stratified external-validity evidence.

Do not claim:

- independent two-annotator agreement;
- natural ICLR 2025 label prevalence from expanded80;
- broad cross-venue generalization;
- reliable regressed-label performance;
- that heuristic structured models are the final modeling solution.

## One-Sentence Defense

RevTrack is not another peer-review classifier: it evaluates whether an AI research assistant can update an old scientific concern after the manuscript changes, and its audits, baselines, and failure taxonomy show why static semantic matching can look plausible while preserving stale criticism.
