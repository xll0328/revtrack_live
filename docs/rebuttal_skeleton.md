# Rebuttal Skeleton

Date: 2026-04-29

Purpose: short, evidence-grounded responses for likely reviewer objections. These are not final author responses; they are reusable building blocks for revision, rebuttal, and advisor discussion.

## R1: "This is just another peer-review classification benchmark."

RevTrack is not a paper-level review classification task. The unit is one concrete reviewer concern, and the target is whether that concern still holds after author response and revision evidence. This temporal update step is exactly what static review generation, score prediction, and acceptance prediction do not test. A model can produce a plausible criticism while failing to retire a stale concern after the paper changes. The benchmark therefore evaluates issue-status tracking: fixed, partially fixed, unresolved, or regressed. We make this distinction explicit in the task definition, Figure 1, and Related Work, where RevTrack is positioned as an issue ledger rather than a static peer-review corpus.

## R2: "The dataset is too small for a strong benchmark claim."

We intentionally separate scoped benchmark claims from broad prevalence claims. The current paper-ready evidence includes a hardened ICLR 2024 benchmark slice, a validated ICLR 2025 stress set, 80-row standard-labeled active frontiers for ICLR 2025 and NeurIPS 2024, and an 80-row ICLR 2023 random/stratified standard slice. These support in-domain behavior, accuracy-trap analysis, hardened transfer brittleness, and bounded external-validity evidence by measured slice design. We do not claim natural ICLR 2025 prevalence, full natural venue prevalence, or broad cross-venue generalization from these artifacts.

## R3: "The labels are subjective."

The label is not whether an author response sounds persuasive; it is whether the original concern is resolved by concrete response or revision evidence. Each release-quality row is required to carry evidence spans and notes, and the label-evidence audit covers 329 rows with zero evidence issues. The paper also discloses the hardest boundary cases: partial fixes, regression scarcity, and cases where added evidence narrows but does not eliminate a concern. We do not overclaim independent inter-annotator reliability. Current labels are user-confirmed standard validation, and we state that a separate second-annotator pass is required before reporting IAA.

## R4: "AI-assisted signoff contaminates the human validation."

The validation provenance is explicitly separated. Blind sheets, hidden keys, audit sheets, assistant signoff, and promoted standard labels are stored as distinct artifacts and audited before use. The paper reports the current labels as user-confirmed standard validation, not independent two-annotator agreement. This is why the dataset card, limitations, and readiness audit all state that the labels support the current standard-label claims but not IAA. The packet audit checks row identity, forbidden label leakage into blind files, key/source consistency, duplicate issue IDs, model snapshot fields, and evidence completeness before a packet can support a paper claim.

## R5: "The structured model is heuristic."

We agree that the structured model should not be read as the final modeling solution. It is a diagnostic intervention that tests whether explicit revision-evidence slots and follow-up cues recover behavior that semantic matching misses. This is why we include TF-IDF, ModernBERT, MPNet, issue-ledger rules, majority/null baselines, and a no-overrides ablation. On ICLR 2024, removing structured hard overrides drops macro-F1 from 0.704 to 0.424, showing that revision-specific cues matter for minority-label recovery. The main claim is not model zoo dominance; it is that revision-aware evidence tracking exposes failures hidden by static semantic similarity.

## R6: "Accuracy gains are not convincing."

Accuracy is deliberately treated as an unreliable metric in this task. Under label skew, a model can achieve high accuracy by predicting the majority outcome while failing the cases that matter most for review support. On ICLR 2025, TF-IDF matches the majority baseline while assigning fixed-case F1 of 0.000. On ICLR 2024, the majority baseline reaches the same accuracy as the strongest semantic baseline but has zero F1 for fixed, unresolved, and regressed cases. RevTrack therefore makes macro-F1, fixed-case recovery, unresolved-case recovery, and regression analysis part of the task definition rather than secondary diagnostics.

## R7: "Expanded80 is not a natural benchmark."

Correct. Expanded80 is an active, model-disagreement-heavy frontier and is framed as such throughout the paper. It supports a hardened cross-year brittleness claim, not a natural-prevalence estimate for all ICLR 2025 issues. The same boundary applies to the NeurIPS 2024 active frontier, while the ICLR 2023 random80 slice is reported separately as bounded random/stratified evidence by measured slice design. These boundaries are stated in the dataset section, limitations, tables, claim ledger, and dataset card. For broad natural-distribution or IAA claims, the next additions would be a non-ICLR random/stratified slice and/or an independent second-annotator pass.

## R8: "The failure taxonomy is post-hoc."

The taxonomy is not used as an unsupported story after the fact. It is grounded in specific labeled examples and aggregate error counts from the standard-labeled active frontier. It explains why aggregate metrics fail to capture the practical risk: stale criticism, over-crediting unresolved issues, fixed under-recovery, regression blindness, and partial/full boundary errors. These modes connect the running example, the label rubric, the null-baseline analysis, and the cross-year frontier. The goal is to make the benchmark diagnostic, not just comparative. A useful review assistant must know when to retire a criticism, when not to over-credit a response, and when a revision introduces a new problem.

## R9: "Regressed is too rare to evaluate."

We do not claim stable regressed-label performance. The regressed label is retained because it captures a high-risk outcome in revision workflows: a change can introduce or worsen a problem even if it appears responsive. The current labeled pool has too few regressed examples for a strong performance claim, and the limitations section states this explicitly. In the current paper, regressed is a necessary diagnostic category, not a solved benchmark slice.

## R10: "The pipeline misses PDF-level changes."

The current pipeline is text-first: it uses public OpenReview reviews, author responses, revision summaries, and available metadata. This is a deliberate first release because it preserves issue-level provenance and makes evidence spans auditable. We agree that future versions should add PDF-aware differencing and direct manuscript-change extraction. The limitation is already stated in the paper, and we avoid claiming that RevTrack exhaustively captures all revision evidence. The present contribution is the issue-status task, validation/audit pipeline, and diagnostic findings about stale criticism and over-crediting. PDF-aware extraction is a natural extension, not a prerequisite for the current scoped claims.

## R11: "Why is this an EMNLP paper?"

RevTrack evaluates a concrete NLP capability needed by LLM research assistants: tracking how scientific claims, concerns, and evidence change over time. This connects peer-review understanding, evidence grounding, document revision, temporal update, calibration under label skew, and trustworthy AI-assisted science. The task is language-centric and system-facing: the model must read a review concern, author response, and revision evidence, then produce a calibrated issue-status label. The broader message is that evaluating research assistants by static critique quality is insufficient. Scientific NLP systems need to know when old language remains valid and when it has become stale.

## R12: "What would make this stronger before acceptance?"

The strongest remaining additions are a non-ICLR random/stratified slice and a targeted independent second-annotator pass. The former would test whether the random/stratified evidence now available for ICLR 2023 also holds outside the ICLR venue family; the latter would enable an explicit IAA claim. These additions are orthogonal: a new slice improves prevalence-sensitive venue scope, while a second annotator improves label-reliability claims. The current paper is already scoped conservatively so that neither is overclaimed before completion.
