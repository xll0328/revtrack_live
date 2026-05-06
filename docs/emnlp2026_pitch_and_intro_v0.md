# EMNLP 2026 Pitch and Introduction v0

Status: working draft for an EMNLP 2026 long paper targeting oral-level clarity.

## One-Page Pitch

### Title Candidates

1. `RevTrack: Evaluating Whether Research Assistants Update Scientific Critiques After Revision`
2. `Do LLM Reviewers Know When a Criticism Has Been Fixed?`
3. `From Static Critique to Revision Tracking: A Benchmark for Scientific Judgment Updates`

Recommended working title: `RevTrack: Evaluating Whether Research Assistants Update Scientific Critiques After Revision`.

### One-Sentence Thesis

LLM research assistants can generate plausible paper critiques, but they are much less reliable at the temporal judgment that real reviewing requires: deciding whether a specific criticism still holds after authors revise the paper.

### Why This Is an EMNLP Paper

The NLP contribution is an evaluation problem for language agents in scientific workflows. The task is not generic paper scoring; it is issue-level state tracking over review text, author response, and revision evidence. It probes whether models can update a prior natural-language judgment when new scientific evidence appears.

### Main Research Questions

1. Can current text and embedding baselines classify whether a reviewer concern was fixed, partially fixed, unresolved, or regressed?
2. Does accuracy hide failures under the natural label skew of revision outcomes?
3. Do explicit revision-evidence slots improve minority-label recovery over semantic matching?
4. Does the behavior remain stable under cross-year transfer?

### Current Headline Result

On the hardened ICLR 2024 clean-dev benchmark, the structured revision-evidence model reaches `0.704` macro-F1 versus `0.389` for the best semantic baseline, while majority and TF-IDF-style baselines can look strong by accuracy but collapse on minority-label recovery.

### Best-Paper Bet

The paper should make reviewers remember one idea: static critique is the wrong evaluation target for AI research assistants. The relevant capability is revision-aware scientific judgment.

## Paper Type

New problem / benchmark paper with a lightweight diagnostic method.

The paper should not be framed as a pure technique paper. The strongest contribution is the task definition plus empirical evidence that common semantic baselines fail in a way that matters for AI-assisted science.

## Six-Paragraph Introduction Outline

### Paragraph 1: Background and Running Example

Purpose: make the problem concrete before naming the benchmark.

Writing points:

- LLMs are increasingly used to review papers, summarize rebuttals, and assist scientific revision.
- The real workflow is temporal: a reviewer raises a concern, authors revise, and someone must decide whether the concern remains valid.
- Running example: a reviewer asks a paper to address computational cost because efficiency is part of its motivation; after revision, the authors add error/cost comparisons in Figure 6 and Lines 510-530.
- A static critique model can still repeat the old concern because the concern remains plausible in isolation.
- The correct judgment is `fixed`: the issue was directly addressed by revision evidence.

Draft paragraph:

Large language models are increasingly used as research assistants: they summarize reviews, draft rebuttals, critique manuscripts, and help authors decide what to revise. Yet the core operation in peer review is not static criticism. A reviewer may ask a paper to address computational cost; after revision, the authors may add an explicit error and cost comparison. At that point, a useful assistant must not merely decide whether the original criticism sounds plausible. It must decide whether that criticism still holds. This temporal judgment is easy to overlook but central to scientific revision: the target is not critique generation, but critique updating.

Gap severity: none.

### Paragraph 2: Limitation of Existing Evaluation

Purpose: explain why existing review benchmarks do not solve this.

Writing points:

- Existing paper-review benchmarks usually evaluate static review generation, quality assessment, or consistency with acceptance decisions.
- Static paper critique benchmarks do not represent the post-revision state.
- Rebuttal summarization and response generation are adjacent but do not require issue-level resolution labels.
- A model can sound critical and useful while preserving stale criticisms.

Draft paragraph:

Existing evaluations of LLMs for scientific reviewing mostly ask whether a model can produce a plausible review, assess paper quality, or summarize reviewer-author exchanges. These settings miss a distinct capability needed in real revision workflows. After authors respond and update a manuscript, the assistant must track the status of each concrete issue: fixed, partially fixed, unresolved, or regressed. Without this issue-level update step, a model can appear helpful by restating reasonable criticisms while failing the actual decision authors and area chairs need to make.

Gap severity: none. The paper now cites PeerRead, NLPeer, Re2, PeerQA, FEVER, and MARG, and the citation audit passes for the current related-work scope.

### Paragraph 3: Problem Essence and Goal

Purpose: state the task and why macro-F1/per-label recovery matter.

Writing points:

- Define revision-status tracking.
- Inputs: review concern, response/revision context, optionally paper metadata.
- Output: four labels.
- Natural skew makes accuracy dangerous.
- Goal is benchmark plus diagnostic evaluation, not just a classifier.

Draft paragraph:

We formalize this missing capability as revision-status tracking. Given a paper, one reviewer concern, the author response, and aligned revision evidence, the system predicts whether the issue is fixed, partially fixed, unresolved, or regressed. This formulation intentionally operates at the issue level rather than the paper level: a single paper may fix some criticisms while leaving others open. It also requires label-level evaluation. In our data, most issues are at least partially addressed, so a model can obtain high accuracy by predicting the majority outcome while failing to recover fixed or unresolved cases.

Gap severity: none.

### Paragraph 4: Key Challenges

Purpose: make the benchmark construction and evaluation feel nontrivial.

Writing points:

- Challenge 1: extract concrete issue units from natural reviews.
- Challenge 2: align concerns with responses/revisions without leaking labels.
- Challenge 3: evaluate under skew and distinguish partial fixes from superficial replies.
- Mention standard human validation and audits.

Draft paragraph:

Building such an evaluation is challenging for three reasons. First, peer reviews mix summaries, questions, weaknesses, and broad opinions, so the benchmark must isolate concrete issue units. Second, revision evidence is distributed across author responses and manuscript changes, making naive semantic matching unreliable. Third, the label space is asymmetric: partial fixes are common, regressions are rare, and unresolved concerns may be hidden behind long persuasive responses. We therefore build RevTrack with explicit issue extraction, response/revision alignment, standard human-validation signoff, and leakage/key-alignment audits.

Gap severity: `MINOR`: specify whether final dataset release uses paper revision summaries, author responses, or both.

### Paragraph 5: RevTrack and Diagnostic Models

Purpose: map challenges to modules.

Writing points:

- Dataset pipeline: OpenReview -> issue candidates -> active frontier -> human validation -> audited benchmark.
- Baselines: majority/null, TF-IDF, ModernBERT, MPNet.
- Diagnostic methods: issue-ledger and structured revision evidence slots.
- Strict LOO-feature protocol.

Draft paragraph:

RevTrack combines a benchmark and a diagnostic suite. We collect public OpenReview discussions, extract issue-level examples, prioritize hard cases through model disagreement, and validate the active audit set with standard human signoff. We compare majority and semantic baselines against models that explicitly represent revision evidence, including an issue-ledger baseline and a structured calibrator with follow-up cues. To avoid inflated numbers from reusing full-training predictions, we report strict leave-one-out feature evaluations on the clean ICLR 2024 development set and separate cross-year transfer as a stress test.

Gap severity: none.

### Paragraph 6: Contributions and Results

Purpose: state exact claims without overclaiming cross-year transfer.

Writing points:

- Contribution 1: task and benchmark.
- Contribution 2: audited construction/validation pipeline.
- Contribution 3: empirical accuracy-trap finding.
- Contribution 4: structured evidence improves macro-F1 in-domain.
- Contribution 5: cross-year stress exposes brittleness.

Draft paragraph:

Our results show that revision tracking exposes failure modes hidden by static evaluation. On the hardened ICLR 2024 benchmark, structured revision evidence reaches `0.704` macro-F1, substantially above the best semantic baseline at `0.389`, while removing structured overrides drops macro-F1 to `0.424`. Null-baseline analysis shows why accuracy alone is misleading: on the ICLR 2025 stress set, a TF-IDF model matches the majority baseline while assigning zero F1 to fixed cases. We release the task formulation, label rubric, audited construction pipeline, standard human-validation labels, and diagnostic results as a foundation for evaluating revision-aware scientific assistants.

Gap severity: `MAJOR`: the ICLR 2025 pool is now scaled, but it must remain a construction/frontier claim until the expanded blind packet has standard human labels and rerun transfer metrics.

## Contribution Alignment Check

| contribution | challenge addressed | evidence/artifact | section |
| --- | --- | --- | --- |
| Revision-status tracking task | static critique does not test temporal update | task definition and label rubric | Section 2 |
| Audited benchmark construction | issue extraction and leakage risk | packet audits, label-evidence audits, human signoff | Section 3 |
| Accuracy-trap analysis | label skew hides failures | null-baseline comparison, ICLR 2025 stress set | Section 5.1 |
| Structured evidence model | semantic matching misses issue resolution | clean-dev macro-F1, no-overrides ablation | Section 5.2 |
| Cross-year stress test and scaled frontier | transfer robustness | ICLR 2025 v2 transfer table; expanded80 standard validation and transfer metrics | Section 5.4 |

## Flow Consistency Report

- Running example -> solution overview: pass. The computational-cost example motivates checking revision evidence.
- Limitations -> challenges: pass. Static benchmarks motivate issue extraction, evidence alignment, and skew-aware evaluation.
- Goal -> contribution 1: pass. The task directly instantiates the goal.
- Challenges -> modules: pass. Each construction/evaluation module answers a challenge.
- Contributions -> sections: pass, with one caveat: expanded80 supports a hardened active-frontier claim, not broad natural-prevalence generalization or IAA.

## Top Three Actions

1. Turn the Paragraph 1 running example into Figure 1 v1.
2. Keep the related-work citations synchronized with any new positioning edits by rerunning `audit_paper_citations.py`.
3. Use the expanded80 error taxonomy to guide the next scaling route: second annotator for IAA, or another venue/year for broader transfer.
