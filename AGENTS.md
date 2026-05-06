# RevTrack Automation Notes

Use OMX for long-running maintenance in this repo, with `ralplan` for claim/evidence changes and `ralph` for bounded refresh loops.

## Project North Star

RevTrack evaluates whether models can update scientific judgments after paper revision: `fixed`, `partially_fixed`, `unresolved`, or `regressed`.

## Safe Automation Targets

- Refresh paper assets, dashboards, claim ledgers, readiness audits, and packet audits.
- Prepare or inspect human-validation packets and batch-ingest reports.
- Summarize clean-dev and transfer metrics from existing outputs.
- Keep ICLR 2024 in-domain claims separate from ICLR 2025 stress evidence.

## Guardrails

- Independent human validation remains blocking until blind rows are filled by humans.
- AI-assisted signoff is useful for triage only; do not report it as independent validation.
- Do not promote `C6_publishable_cross_year_benchmark` or any broad cross-year claim until quality gates pass.
- Treat the ICLR 2025 repro pool as stress evidence unless it is expanded and validated.
- Be careful with `regressed`: current support is too sparse for broad per-label conclusions.

## Preferred Stop Conditions

Stop when the next step requires human relabeling, larger OpenReview collection, or a claim beyond the current paper-readiness audit.
