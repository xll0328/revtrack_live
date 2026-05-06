# Top-conference readiness audit

Date: 2026-04-28
Project: RevTrack
Target bar: top NLP main track; stretch target: Oral / Best Paper

## Bottom line

Current status: main-track plausible, not yet Oral / Best Paper caliber.

The evidence base is materially stronger than before: `301 / 301` standard labels are complete, claim/readiness audits are clean, cross-venue transfer includes a user-confirmed NeurIPS 2024 limit100 frontier, and external-validity evidence now includes an ICLR 2023 random/stratified standard slice. The remaining gap is not basic correctness. It is whether the paper demonstrates broad reliability beyond single-user labels and ICLR-family random/stratified evidence.

## Locked strengths

1. Quality gates are in place and passing.
   - Candidate-pool gates pass for ICLR 2024, ICLR 2025 expanded80, and NeurIPS 2024 limit100.
   - Blind/key/source packet audits pass for five packets (ICLR 2024 v1, ICLR 2025 v1/v2, expanded80 v1, NeurIPS limit100 v1).
   - Paper-readiness is `ready` with `8` ready claims.

2. Validation provenance is explicit.
   - Standard labels cover `301 / 301` active rows.
   - Expanded80 and NeurIPS limit100 are framed as standard single-user active frontiers; ICLR 2023 random80 is framed as a standard single-user random/stratified slice.
   - Boundaries are explicit: not independent IAA, not natural-prevalence estimates.

3. The core empirical story is defensible.
   - In-domain ICLR 2024 still shows a clear structured-evidence advantage.
   - Cross-year and cross-venue transfer remain brittle, which is a meaningful diagnostic contribution.
   - Stratified-bootstrap uncertainty summaries are now available across ICLR 2024, expanded80, and NeurIPS 2024 standard splits.

## Oral-level blockers

1. External-validity blocker (highest priority).
   - Current frontier splits are disagreement-focused by design.
   - Missing: independent second annotator and/or a non-ICLR random/stratified venue slice.
   - Progress: ICLR 2023 random80 packet is promoted with standard transfer diagnostics and failure taxonomy; it can now be used as bounded random/stratified evidence.

2. Transfer narrative is still mostly negative evidence.
   - This can be a strength, but the framing must make the failure signal the main scientific contribution.
   - The manuscript still risks being read as "small benchmark + weak transfer gains."

3. Figure/story memorability gap.
   - Figure 1 and the taxonomy need to become the paper’s anchor, not supporting material.
   - The current text still spreads attention across too many implementation details.

4. Reference breadth gap.
   - Citation integrity passes, but coverage breadth is still thin for an oral-level positioning across peer-review NLP, revision-aware evaluation, and reliability.
   - Add targeted primary-source citations instead of adding volume-only references.

5. Reproducibility packaging gap.
   - Internal audits are strong, but the anonymized external artifact package and one-command reproduction story need final hardening.

## High-impact next work

1. Add one broader slice beyond active frontiers.
   - Preferred: random/stratified venue slice with standard labels.
   - Fallback: targeted second-annotator pass (40-80 rows across fixed/unresolved/regressed) if IAA is needed.

2. Tighten the paper’s central message.
   - Lead with revision-status tracking as a missing AI-assistant capability.
   - Keep transfer brittleness as a bounded reliability result, not a generalized prevalence claim.

3. Ship the final artifact package.
   - Include exact regeneration commands for readiness, claim ledger, transfer tables, and figures.
   - Keep provenance labels explicit in all paper-facing tables.

4. Run one low-cost prompt ablation sweep.
   - Focus on uncertainty/refusal behavior and calibration under transfer.
   - Use this to strengthen the "reliability under shift" argument.

## Stop/go assessment

Go for continued development. Do not position the current draft as Oral / Best Paper ready yet.

Fastest credible path:

1. Lock Figure 1 + taxonomy-centered narrative.
2. Add broader-evidence slice (or targeted IAA pass).
3. Finalize anonymized reproducibility bundle.
4. Add one transfer-focused prompt calibration ablation.
