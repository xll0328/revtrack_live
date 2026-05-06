# Oral / Best Paper Gap Audit

Date: 2026-04-28

Target: EMNLP 2026 long paper, oral-level bar, best-paper upside.

## Bottom Line

The project is now strong enough for a credible top-conference submission under a careful claim scope. It is not yet strong enough to confidently expect oral, and it is not yet in best-paper territory.

Current estimated position:

| target | current readiness | judgment |
| --- | ---: | --- |
| Main-conference acceptance | 7.0 / 10 | plausible if story and limitations stay disciplined |
| Oral | 5.5 / 10 | possible only after one more strong evidence axis |
| Best paper | 3.5 / 10 | not yet; needs a field-shaping insight plus stronger validation |

This is a good place to be one month before ARR: the core system is not blocked, but the paper still needs a sharper empirical punch.

## Current Evidence Inventory

What is already strong:

- Standard validated active-audit labels are complete for `301 / 301` rows across ICLR 2024, ICLR 2025, NeurIPS 2024, and ICLR 2023 random80 packets.
- ICLR 2024 in-domain result is strong: Structured reaches `0.704` macro-F1 versus MPNet `0.389`.
- The accuracy-trap result is clear: on ICLR 2025 repro v2, TF-IDF matches the majority baseline while fixed F1 is `0.000`.
- ICLR 2025 expanded80 is now a standard-labeled active frontier with `80 / 80` labels and best macro-F1 `0.469`.
- NeurIPS 2024 extraction is repaired and produces a clean cross-venue pool: `393` candidates, `1.000` complete-field rate, `316` disagreement rows, `93` high-disagreement rows.
- NeurIPS 2024 now has an 80-row promoted standard-validation set: `partially_fixed=44`, `unresolved=36`, with user-confirmed single-user provenance.
- NeurIPS 2024 standard transfer metrics and failure taxonomy are regenerated as paper-facing assets under standard-validation provenance.
- Packet audits, label-evidence audits, citation audit, readiness audit, and the full Python test suite pass.

What is still not enough for oral/best-paper confidence:

- Cross-venue evidence is still disagreement-focused active-frontier evidence rather than random/stratified venue evidence.
- There is no independent second-annotator agreement pass, so IAA must not be claimed.
- The paper does not yet include a strong frontier-LLM baseline; reviewers may ask whether the result only beats shallow baselines.
- The prompted-LLM baseline interface now exists, and a local Qwen2.5-1.5B smoke run has been evaluated on ICLR 2025 expanded80. This is useful sanity evidence, not the final strong LLM baseline.
- Regression remains sparse, so the `regressed` label is justified as a task category but not as a stable performance claim.
- The empirical narrative is credible, but the best-paper-level thesis still needs a more memorable result than "structured rules beat encoders in domain."

## ScholarEval Scorecard

| dimension | score | rationale | next lift |
| --- | ---: | --- | --- |
| Problem formulation | 4.5 / 5 | Revision-aware scientific assistance is a real gap and the task is crisp. | Make the running example unavoidable in the abstract/intro/results. |
| Novelty | 4.0 / 5 | Issue-level revision-status tracking is distinctive. | Position harder against static peer-review and critique-generation benchmarks. |
| Data and validation rigor | 3.8 / 5 | Strong packet and evidence audits; standard labels exist across two venue families. | Add random/stratified venue slices and a small IAA slice if needed. |
| Experimental depth | 3.3 / 5 | Solid in-domain and cross-year active-frontier evidence. | Add one more venue-confirmed standard set and a stronger LLM baseline. |
| Analysis depth | 3.5 / 5 | Failure taxonomy is useful and paper-facing. | Convert taxonomy into the main result, not just supporting analysis. |
| Reproducibility | 4.4 / 5 | Scripts, manifests, gates, and readiness checks are unusually strong. | Freeze release manifest and dataset card. |
| Writing/story | 3.6 / 5 | Thesis is clear, but the paper still reads more "benchmark + classifier" than "new evaluation lens." | Make "stale criticism" the headline throughout. |

## Acceptance-Level Claim Set

This claim set is currently defensible:

1. Scientific assistants need revision-aware evaluation, not only static critique generation.
2. RevTrack defines an auditable issue-level task with four evidence-grounded labels.
3. On ICLR 2024, structured revision evidence substantially improves macro-F1 over semantic baselines.
4. Accuracy alone hides failure under label skew.
5. Cross-year active-frontier transfer remains brittle even when the data pipeline is clean and labels are standard-confirmed.

This is enough for a serious EMNLP submission if the writing is tight.

## Oral-Level Gap

To look oral-level, the paper needs at least one of these:

1. Broader venue evidence beyond disagreement-focused active frontiers, ideally through random/stratified venue slices.
2. A strong LLM baseline showing that the problem is not solved by prompting a modern research assistant.
3. A sharper analysis result: for example, models systematically confuse "acknowledgment" with "resolution", and this persists across venues.

The fastest route is:

- keep NeurIPS 2024 as standard single-user active-frontier evidence with explicit boundaries,
- add one random/stratified venue slice to reduce external-validity risk,
- add a compact LLM-prompt baseline on the 80-row active frontiers,
- rewrite Results around three memorable failure modes.

## Best-Paper Gap

Best paper usually requires the reviewer to feel that the paper changes how the community evaluates a capability. Current RevTrack is close to that framing but not yet fully there.

The missing best-paper ingredients are:

- A result that survives strong baselines and feels surprising.
- A cross-venue validation story that looks broad enough to matter beyond one community.
- A figure/table that makes the key failure instantly clear.
- A stronger release story: benchmark, audit suite, and failure taxonomy as a reusable evaluation protocol.

The best-paper version of the thesis should be:

> Scientific assistants fail not because they cannot critique papers, but because they cannot retire, revise, and audit critiques after evidence changes.

Everything in the paper should serve that sentence.

## Sprint Priority

### P0: Broaden Beyond Active Frontiers

Goal: keep NeurIPS/expanded80 as bounded standard single-user active-frontier evidence, and add one broader venue slice.

Actions:

- Define a random or stratified sampling policy for one additional venue/year slice.
- Produce a packet with the same blind/key/source audit gates and label-evidence completeness checks.
- Keep reporting boundaries explicit: standard single-user active frontier, not independent IAA, not natural prevalence.
- Rerun transfer metrics and failure taxonomy after the broader slice is labeled.
- Update claim ledger wording from "frontier-only" to "frontier + broader slice" only after gates pass.

Expected impact: biggest single lift for oral readiness and external-validity confidence.

### P1: Add A Strong Prompted-LLM Baseline

Goal: preempt the obvious reviewer objection: "Would a modern LLM just solve this with the full context?"

Actions:

- Use the same input fields and label rubric.
- Require evidence span and rationale in the output.
- Run on ICLR 2024 clean dev, ICLR 2025 expanded80, and NeurIPS candidate/standard set.
- Score exact labels and audit invalid outputs.

Current implementation:

- Prompt exporter: `scripts/export_prompted_llm_baseline_packet.py`
- Output evaluator: `scripts/evaluate_prompted_llm_baseline.py`
- Local runner: `scripts/run_local_prompted_llm_baseline.py`
- AIHubMix/OpenAI-compatible runner: `scripts/run_aihubmix_prompted_llm_baseline.py`
- ICLR 2024 packet: `outputs/day1/prompted_llm_baselines/iclr2024_clean_dev_v7_prompt_packet.jsonl`
- ICLR 2025 expanded80 packet: `outputs/day1/prompted_llm_baselines/iclr2025_expanded80_prompt_packet.jsonl`
- NeurIPS packet: `outputs/day1/prompted_llm_baselines/neurips2024_limit100_resolved_candidate_prompt_packet.jsonl`
- Leakage check: prompt messages contain `0` `gold_label` string hits across all three packets.
- Local Qwen2.5-1.5B expanded80 smoke result: accuracy `0.113`, macro-F1 `0.062`, predictions `fixed=66`, `unresolved=8`, `invalid=6`; output audit flags invalid rows, so this should be reported only as a smoke/sanity baseline.
- Smoke metrics: `outputs/day1/paper_assets/iclr2025_expanded80_qwen25_1p5b_metrics.md`
- GPT-5.5 runbook: `outputs/day1/paper_assets/aihubmix_gpt55_baseline_runbook.md`
- Current shell status: `AIHUBMIX_API_KEY` is not set, so GPT-5.5 has not yet been executed.

Expected impact: if LLMs still over-credit or miss partial fixes, the paper becomes much stronger.

### P2: Make Failure Taxonomy The Flagship Result

Goal: make the paper memorable.

Actions:

- Pick one high-quality example each for stale criticism, over-crediting, partial/full boundary, and regression risk.
- Add a compact table with issue, evidence cue, wrong model behavior, and correct label.
- Move this analysis earlier in Results so it explains the metrics rather than follows them.

Expected impact: changes reviewer perception from "small benchmark" to "new diagnostic lens."

### P3: Optional IAA Slice

Goal: unlock stronger data-quality claims without needing full second annotation.

Actions:

- Sample 30 high-risk rows across ICLR 2025 expanded80 and NeurIPS.
- Get independent second labels only for IAA, not for changing the canonical labels.
- Report agreement and adjudication policy if acceptable.

Expected impact: improves trust, but it is secondary to NeurIPS promotion and LLM baseline.

## Decision

Current work and experiment volume are enough for a scoped top-conference submission.

They are not enough to honestly say "this is already oral/best-paper level." The most efficient path to that level is not more random experiments. It is one more validated cross-venue axis, one stronger baseline, and a sharper failure-mode story.
