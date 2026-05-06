# EMNLP 2026 Oral / Best Paper Sprint Plan

Working target: EMNLP 2026 long paper, oral-level bar, best-paper upside.

Official schedule anchor: EMNLP 2026 main conference papers use ARR. The May ARR submission deadline is `2026-05-25`, author response is `2026-07-07` to `2026-07-13`, EMNLP commitment is `2026-08-02`, notification is `2026-08-20`, and the main conference is `2026-10-24` to `2026-10-29`.

## North Star

RevTrack should not read like "we made another benchmark." It should read like:

> Modern LLM research assistants can critique scientific papers, but they fail at a harder and more realistic operation: updating a criticism after the paper changes. RevTrack turns this failure into a measurable revision-tracking task, a human-validated benchmark, and a diagnostic suite showing why static semantic matching is not enough.

The oral/best-paper bet is that this is a new evaluation lens for AI-assisted science, not just an incremental classifier result.

## Current Locked State

- Standard validation labels are complete for the active audit set: `301 / 301` across ICLR 2024, ICLR 2025 repro v2, ICLR 2025 expanded80, NeurIPS 2024 limit100, and ICLR 2023 random80.
- ICLR 2024 in-domain result is strong: Structured `0.682` accuracy / `0.704` macro-F1 versus MPNet `0.581` / `0.389`.
- Accuracy-trap evidence is strong: ICLR 2025 TF-IDF matches the majority baseline while failing fixed-case recovery.
- Candidate machinery is reproducible: packet audits, leakage checks, label-evidence audits, signoff audits, and pipeline tests pass.
- Current paper-readiness is `ready` for the current claim set, including citation audit status `pass`.
- Current paper self-review has `0` critical, `0` major, and `0` minor blockers for the scoped claim set.
- The paper builds as an 8-page PDF, and the full Python test suite passes (`106` tests).
- Oral/best-paper gap audit is tracked at `outputs/day1/top_conference_quality_audit_2026-04-28.md`; current estimate is top-conference plausible, oral not yet secure, best-paper not yet.

What is not yet oral-level:

- Cross-year/cross-venue evidence now has scaled ICLR 2025 (`322` candidates, `244` disagreements) and NeurIPS 2024 (`393` candidates, `316` disagreements) pools plus two `80`-row user-confirmed standard-validation packets; these support bounded active-frontier claims, not broad natural-prevalence or IAA claims.
- The "why models fail" taxonomy exists, but it still needs to become a flagship narrative point rather than only a support table.
- Figure 1 now exists, but the paper story still needs to make the running example and error taxonomy the center of the narrative.
- The method is useful but not enough by itself for best-paper energy; the contribution must be framed as a new evaluation problem plus sharp empirical findings.

## Five-Pillar Benchmark Paper Target

| pillar | current state | oral-level requirement | sprint action |
| --- | --- | --- | --- |
| Research gap | Good: static critique benchmarks miss revision updates | Make the gap unforgettable with one running example where a stale critique becomes wrong after revision | Build Figure 1 and Introduction around stale-criticism failure |
| Construction pipeline | Good: OpenReview issue extraction, active sampling, signoff, audits, citation gate | Show reproducibility, leakage control, and label quality as first-class contributions | Keep dataset card, audit table, and standard-label record synchronized |
| Evaluation framework | Good: four labels, structured evidence model, and failure taxonomy | Make difficulty/failure dimensions central: stale criticism, over-crediting, partial-fix ambiguity, regression detection | Move taxonomy from support artifact into the main empirical argument |
| Empirical findings | Strong in-domain, validated cross-year stress set, and standard-labeled expanded80 + NeurIPS frontiers | Need random/stratified venue evidence and/or independent IAA for broad generalization | Use frontier errors as flagship analysis; then add random/stratified slices and targeted second-annotator pass |
| Companion method | Structured calibrator beats semantic baselines in-domain | Position as diagnostic intervention, not SOTA chasing | Keep method simple; emphasize evidence slots and minority-label recovery |

## Main Claim Stack

Use these as the paper's claim hierarchy.

1. Problem claim:
   Scientific review assistance requires temporal judgment: deciding whether a criticism still holds after revision.

2. Benchmark claim:
   RevTrack provides a human-validated issue-level benchmark for revision-status tracking with reproducible leakage/key-alignment audits.

3. Empirical claim:
   Static semantic baselines can look competent by accuracy while failing label-level recovery under skew.

4. Method/diagnostic claim:
   Structured revision evidence slots and follow-up cues recover minority labels better than pure semantic matching on the hardened ICLR 2024 benchmark.

5. Stress/frontier claim:
   Cross-year transfer exposes brittleness on a validated stress set and a standard-labeled active frontier; it is strong diagnostic evidence but not yet a broad natural-prevalence generalization claim.

Do not lead with "our model wins." Lead with "the community is measuring the wrong thing for AI research assistants."

## Introduction Chain

1. Background and running example:
   LLMs are increasingly used as research assistants for critique, rebuttal analysis, and paper revision. The real workflow is temporal: a reviewer raises a concern, authors revise, and the assistant must decide whether the concern remains valid.

2. Existing limitation:
   Current review/critique benchmarks mostly judge static comments or static paper quality. They do not test whether a model updates a prior criticism after new evidence appears.

3. Research questions:
   Can models reliably classify issue outcomes as fixed, partially fixed, unresolved, or regressed? Do semantic baselines fail under label skew? Does structured revision evidence help? Does the behavior transfer across years?

4. Design considerations:
   The task must isolate one issue at a time, align review concerns with author responses/revision summaries, control leakage between blind sheets and keys, and evaluate minority-label recovery rather than accuracy alone.

5. Proposal:
   RevTrack builds issue-level revision-status examples from public OpenReview data, validates labels through a standard human signoff process, and evaluates semantic baselines against structured evidence models and null baselines.

6. Contributions:
   A new revision-tracking benchmark and rubric; a reproducible construction/audit pipeline; evidence that accuracy hides stale-criticism failures; a structured diagnostic model that improves macro-F1; and a cross-year stress test showing brittleness.

## Paper Skeleton

### 1. Introduction

Purpose: sell revision tracking as a missing capability for AI-assisted science.

Must contain:

- one vivid stale-criticism running example
- why static paper review benchmarks miss this
- the four-label task
- headline results and accuracy trap
- contribution bullets with exact artifacts

### 2. Task: Revision-Status Tracking

Purpose: define the benchmark.

Subsections:

- Input and output format
- Label rubric: fixed, partially fixed, unresolved, regressed
- Why issue-level labels are better than paper-level deltas
- Evaluation metrics: macro-F1 first, accuracy second, per-label recovery mandatory

### 3. Dataset Construction and Validation

Purpose: make reviewers trust the data.

Subsections:

- OpenReview collection and issue extraction
- Response/revision alignment
- Active sampling and disagreement frontier
- Standard human-validation signoff
- Leakage, key-alignment, and label-evidence audits

Critical table:

- rows, submissions, labels, validation rows, audit status, leakage status

### 4. Models and Diagnostic Baselines

Purpose: make the comparison clean and interpretable.

Subsections:

- Majority/null baselines
- TF-IDF, ModernBERT, MPNet
- Issue-ledger model
- Structured calibrator and no-overrides ablation
- Strict LOO-feature protocol

### 5. Results

Purpose: deliver the empirical story in research-question order.

RQ1: Is revision tracking hard under label skew?

- majority/null baseline
- macro-F1 vs accuracy

RQ2: Does structured revision evidence help in-domain?

- ICLR 2024 clean-dev table
- no-overrides ablation
- per-label recovery

RQ3: What failure modes dominate?

- stale criticism
- over-crediting superficial replies
- partial-fix ambiguity
- regression scarcity

RQ4: Does it transfer across years?

- ICLR 2025 stress test
- expanded ICLR 2025 candidate pool passes data-quality gates and has `80 / 80` standard labels
- do not overclaim beyond a hardened active-frontier setting without another venue/year or independent IAA

### 6. Discussion

Purpose: make the paper bigger than this dataset.

Subsections:

- Why AI research assistants need revision-aware evaluation
- When accuracy is the wrong metric
- What a good scientific assistant should track
- Limitations: label boundaries, venue style, cross-year scale
- Release plan and reproducibility

### 7. Related Work

Purpose: position cleanly.

Buckets:

- peer review and scientific critique benchmarks
- LLMs for paper review/research assistance
- document revision and temporal update evaluation
- benchmark construction and active sampling
- reliability and calibration under label skew

## Figure / Table Plan

Figure 1: Running example plus task definition.

- left: reviewer concern
- middle: author response/revision evidence
- right: old static critique vs updated revision-status label
- message: "the target is not whether the criticism sounds plausible; it is whether it still holds."

Figure 2: Construction and validation pipeline.

- OpenReview notes -> issue extraction -> model frontier -> human signoff -> audited benchmark -> evaluation

Figure 3: Main in-domain results.

- macro-F1 and accuracy side by side
- include majority baseline and semantic baselines
- highlight structured vs no-overrides

Figure 4: Accuracy trap / cross-year stress.

- ICLR 2025 majority/TF-IDF collapse
- fixed F1 = 0 for majority-like model
- structured and encoders still weak

Table 1: Dataset and audit summary.

Table 2: Main results.

Table 3: Failure taxonomy with examples.

Table 4: Cross-year stress test.

## Sprint Calendar

### Current Checkpoint: 2026-05-06 (T-19 to ARR May deadline)

Deadline anchor:

- ARR May deadline: `2026-05-25` (19 days left)
- Target: submit by `2026-05-24` night with no deadline-day experiments

Verified today:

- Paper assets were regenerated (`scripts/export_paper_assets.py`) with no claim-scope drift.
- Readiness audit remains `ready` with `9` ready claims and no blockers (`scripts/audit_paper_readiness.py`).
- Progress dashboard refreshed (`scripts/render_progress_dashboard.py`).
- Paper build command reports clean state (`make -C paper` -> no pending rebuild).
- Figure-1 rendering text and regression tests are aligned (`14` targeted tests pass).
- A second-annotator IAA mini-slice packet is now prepared with balanced per-packet coverage (`60` rows; label mix `regressed 6 / fixed 12 / unresolved 30 / partially_fixed 12`) at `experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv`, with key and manifest in `outputs/day1/paper_assets/`.
- Readiness audit now tracks the second-annotator packet explicitly (`iaa_second_annotator_packet`) with target rows, labeling progress, and optional agreement/kappa once second-pass labels are filled.
- A no-key prompted significance audit is now added: paired stratified-bootstrap deltas versus majority for ICLR24 / ICLR25 expanded80 / NeurIPS24, exported to `outputs/day1/paper_assets/prompted_llm_significance.md` and Appendix Table `tab:prompted-llm-significance`.

What still blocks oral/best-paper confidence:

- No independent IAA evidence yet (current validation is standard single-user).
- No strong frontier prompted-LLM rerun is finalized under the current runtime (GPT-5.5 path still pending key/runtime run in this shell).
- External-validity framing is stronger than April, but still requires one more high-trust axis (non-frontier random/stratified venue slice and/or targeted IAA mini-slice).
- The manuscript story must keep failure taxonomy and stale-criticism narrative as the center, not auxiliary analysis.

Next gate (2026-05-15):

- lock one stronger transfer baseline package,
- lock one broader-evidence package (or explicit constrained fallback),
- freeze paper-facing narrative around three flagship failure modes.

### Current Checkpoint: 2026-04-27

Goal: enter the next sprint with a clean scoped draft rather than unresolved core blockers.

Completed:

- `301 / 301` active validation labels are locked as user-confirmed standard validation.
- expanded80 standard transfer metrics and failure taxonomy are paper-facing artifacts.
- citation audit is automated and included in paper-readiness.
- reviewer-objection evidence matrix is drafted at `docs/reviewer_objection_evidence.md`.
- NeurIPS 2024 is selected as the primary second scaling axis after an extraction repair produced 393 clean issue candidates from 100 submissions with complete response/revision context.
- The full NeurIPS 2024 prediction stack is complete for limit100: TF-IDF, ModernBERT, MPNet, issue-ledger, and structured transfer. The repaired full-stack candidate gate passes with 316 disagreement rows and 93 high-disagreement rows.
- A NeurIPS 2024 limit100 blind/key/audit validation packet is generated and passes packet audit with 0 errors and 0 warnings.
- NeurIPS 2024 standard-label promotion is completed (`80 / 80` rows), with user-confirmed provenance and packet audits still passing (`0` errors, `0` warnings).
- NeurIPS 2024 standard transfer metrics and standard failure taxonomy are regenerated as paper-facing artifacts under standard single-user active-frontier provenance.
- Prompted-LLM baseline infrastructure is implemented for ICLR 2024, ICLR 2025 expanded80, and NeurIPS candidate packets. A local Qwen2.5-1.5B smoke run on ICLR 2025 expanded80 is evaluated: accuracy `0.113`, macro-F1 `0.062`, with severe over-crediting toward `fixed`.
- AIHubMix/OpenAI-compatible GPT-5.5 runner and runbook are implemented; the current shell lacks `AIHUBMIX_API_KEY`, so no GPT-5.5 result has been executed yet.
- A NeurIPS 2024 risk-ranked review queue is regenerated on the repaired pool; no rows are missing response/revision context.
- A NeurIPS 2024 regression verification packet is regenerated; it gates 4 provisional `regressed` rows, with 3 requiring manual same-axis confirmation and 1 candidate to keep after final review.
- A rebuttal skeleton for high-risk reviewer objections is drafted at `docs/rebuttal_skeleton.md`.
- ICLR 2023 random/stratified fallback is now promoted as an `80 / 80` standard single-user validation slice, with standard transfer metrics and standard failure taxonomy regenerated as paper-facing assets.
- self-review now tracks oral-level blockers explicitly (`1` critical, `4` major, `3` minor) rather than reporting a scoped-claim all-clear.
- full Python tests pass (`106 passed`), readiness is `ready`, and the paper builds as an 8-page PDF.

Next gate:

- upgrade the draft from "submission-ready for scoped claims" to "oral-level story": make the failure taxonomy and running example unforgettable, and decide whether the next evidence sprint is second annotator, another venue/year, or both.

### Phase 0: Completed 2026-04-26

Goal: lock the paper target and remove stale blockers.

- Treat current `301/301` labels as standard validation.
- Update claim ledger and readiness assets.
- Create this oral/best-paper sprint plan.
- Freeze one-sentence thesis and claim stack.

Exit gate:

- all tests pass
- claim ledger no longer says human validation is pending
- README points to this plan

### Phase 1: 2026-04-27 to 2026-04-30

Goal: make the paper story reviewer-proof.

- Draft Figure 1 running example.
- Draft Introduction as six paragraphs.
- Build a "reviewer objection -> evidence" table.
- Decide whether this is submitted to main track or theme framing around AI in research.

Exit gate:

- 1-page paper pitch exists
- advisor can explain the contribution in one sentence
- Figure 1 can be understood without reading the paper

### Phase 2: 2026-05-01 to 2026-05-07

Goal: attempt oral-level scale improvement.

Primary route:

- add a second scaling axis beyond expanded80: another venue/year, or an independent second-annotator pass
- target at least `80` additional issue labels if choosing another venue/year
- run the same structured/semantic/null baselines
- route the selected scaled frontier through the same signoff, evidence, and readiness audits

Fallback route:

- add one additional venue/year with reliable OpenReview fields
- keep it as a transfer stress test if scale is limited
- do not dilute the main claim with weak data

Exit gate:

- either the broader transfer axis is standard-labeled, or the paper explicitly frames expanded80 as a hardened active-frontier result rather than broad generalization

### Phase 3: 2026-05-08 to 2026-05-12

Goal: convert experiments into findings.

- Generate final result tables.
- Generate failure taxonomy.
- Audit every claim against an artifact.
- Add ablations that directly answer reviewer questions, not decorative ablations.

Minimum ablations:

- structured vs no-overrides
- semantic-only vs evidence-slot model
- majority/null baseline
- per-label recovery, especially fixed/unresolved

Exit gate:

- every result table answers one RQ
- no table exists only because it was easy to compute

### Phase 4: 2026-05-13 to 2026-05-18

Goal: write the full 8-page ARR draft.

Daily target:

- May 13: Introduction and task
- May 14: dataset construction and validation
- May 15: models and evaluation
- May 16: results and analysis
- May 17: discussion, limitations, ethics
- May 18: related work and abstract

Exit gate:

- complete PDF
- all figures placed
- no "TODO" in main paper

### Phase 5: 2026-05-19 to 2026-05-24

Goal: harden for ARR.

- pre-submission review pass
- citation check
- reproducibility checklist
- limitations and ethics
- anonymous artifact cleanup
- adversarial reviewer simulation
- final PDF audit

Exit gate:

- submit-ready package by 2026-05-24 night
- no dependency on last-day experiments

### Phase 6: 2026-05-25

Goal: submit to ARR May cycle with EMNLP 2026 selected.

No new experiments on deadline day.

## Best-Paper Stretch Goals

These are the only stretch tasks worth taking on.

1. A second scaling axis beyond the current active frontier: another venue/year, an independent second-annotator pass, or both.
2. A crisp failure taxonomy with examples that changes how people think about AI peer-review assistants.
3. A release-quality dataset card and audit pipeline that reviewers trust.
4. A Figure 1 that makes the problem obvious in 15 seconds.
5. A writing frame tied to EMNLP 2026's "New Missions for NLP Research" theme: evaluation for LLMs as research tools.

Do not chase:

- a larger model zoo without a claim
- small accuracy gains without macro-F1 or minority-label recovery
- unvalidated cross-year claims
- extra visualizations that do not support a reviewer-facing argument

## Reviewer Objection Matrix

| likely objection | answer we need |
| --- | --- |
| "This is just paper-review classification." | No: the core operation is temporal update after revision; static critique is insufficient. |
| "Labels are subjective." | Label rubric is issue-resolution based; evidence spans and signoff are complete; leakage/key audits pass. |
| "Accuracy gains are small." | Accuracy is the wrong metric under skew; macro-F1 and fixed/unresolved recovery reveal the real failure. |
| "Cross-year evidence is too small." | The current expanded80 result is a standard-labeled active frontier, not a natural-prevalence claim; add another venue/year before broad generalization. |
| "Structured model is heuristic." | That is the point: explicit revision evidence slots diagnose what semantic matching misses. |
| "Why EMNLP?" | It directly evaluates LLMs as research tools and asks what scientific NLP systems should track over time. |

## Immediate Sprint Tasks

1. Tighten Figure 1 and the Introduction around one stale-criticism running example.
2. Add a random/stratified venue-slice plan (and minimal pilot) to support broader generalization beyond active frontiers: `docs/random_stratified_slice_plan_20260428.md`.
3. Define a targeted second-annotator pass (40-80 rows across fixed/unresolved/regressed) only if IAA claim is needed.
4. Prepare the anonymized artifact bundle and final reproducibility checklist.
5. Add one cheap-model prompt ablation pass focused on uncertainty/refusal behavior under transfer.

## Working Principle

We are optimizing for a memorable, defensible paper, not a perfect internal pipeline. Internal audits exist to protect the story; they should not become the story.
