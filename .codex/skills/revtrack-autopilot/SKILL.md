---
name: revtrack-autopilot
description: Continue the /data/sony/emnlp2026_revtrack RevTrack project toward an EMNLP 2026 oral/best-paper submission. Use when the user says to continue RevTrack, keep going, do not stop, push toward EMNLP 2026, oral, best paper, victory, or asks Codex to autonomously advance the project after prior work.
---

# RevTrack Autopilot

## Boundary

Do not claim that Codex can self-wake after a final answer, run forever, or trigger a new turn without user input. Within the active turn, keep working until one useful end-to-end project increment is complete: artifact, validation, and project record.

## Project Root

Work in `/data/sony/emnlp2026_revtrack`.

Treat this project as an EMNLP 2026 benchmark/method paper effort on revision-aware scientific judgment. Preserve the central discipline: strong claims need reproducible artifacts, quality gates, human-validation readiness, and honest failure analysis.

## Autopilot Loop

1. Orient quickly:
   - Read `README.md`, `experiments/day1/summary_2026-04-24.md`, and `outputs/day1/paper_assets/paper_asset_summary.md` if needed.
   - Inspect current scripts/tests before adding new abstractions.
   - Prefer `rg`, `find`, `sed`, and existing project scripts.

2. Choose the next highest-value gap from this priority order:
   - Data/validation integrity: candidate-pool gates, blind/key/audit packet checks, duplicate/leakage/missing-label audits.
   - Paper assets: tables, figures, error profiles, null baselines, claim summaries that make evidence directly citable.
   - Cross-year or cross-venue readiness: collection probes, scalable commands, quality-gate reports, transfer-pool diagnostics.
   - Benchmark/model evidence: focused evaluations, ablations, stress tests, label-level analysis, confusion/error reports.
   - Documentation: update README, day summaries, cross-venue plan, and repro summaries with exact artifact links and metrics.

3. Implement, do not stop at a plan:
   - Add or edit narrowly scoped scripts/tests/docs.
   - Reuse existing project formats and paths.
   - Do not invent positive paper claims from tiny or failed gates.
   - If a result is negative, make it useful: characterize the failure, write it into paper assets, and identify the next gate.

4. Validate:
   - Run the smallest relevant tests first.
   - Run `pytest -q` before final response when feasible.
   - Run new audit/export scripts on real local artifacts, not only toy tests.

5. Record:
   - Update the relevant summary/docs with exact paths and numbers.
   - If a candidate pool is below publishable thresholds, say that explicitly.
   - Keep the final answer concise: changed artifacts, key metric/result, validation command.

## Stop Condition For A Turn

End the turn only after at least one of these is true:

- A new reproducible artifact exists and is linked from project docs.
- A quality gate or audit has been added and run on real project data.
- A paper-ready table/figure/summary has been regenerated and verified.
- A concrete blocker is documented with the exact command, error, and next feasible action.

## Claim Discipline

Use this framing unless later evidence changes it:

- ICLR 2024 clean dev is the current in-domain benchmark evidence.
- ICLR 2025 repro is a cross-year stress sample until it passes the candidate-pool quality gate.
- High accuracy on skewed revision labels is not sufficient; report macro-F1 and label-level recovery.
- Majority/constant-label baselines are mandatory whenever label skew can explain performance.
