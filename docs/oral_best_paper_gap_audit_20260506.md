# Oral / Best Paper Gap Audit

Date: 2026-05-06  
Scope: `emnlp2026_revtrack` (ARR May cycle for EMNLP 2026)

## Bottom Line

We are in a strong submission position, but still short of reliable Oral / Best Paper confidence.

Current judgment:

| target | readiness | status |
| --- | ---: | --- |
| Main-track acceptance | 7.5 / 10 | plausible now |
| Oral | 6.0 / 10 | reachable with one more strong evidence axis + sharper narrative |
| Best paper | 4.0 / 10 | not yet; needs stronger field-level signal |

Deadline reality:

- ARR May deadline: `2026-05-25`
- Time remaining from this audit: `19` days

## Audited Facts (Refreshed 2026-05-06)

1. `scripts/export_paper_assets.py` regenerated paper-facing assets with no scope drift.
2. `scripts/audit_paper_readiness.py` reports `overall_status=ready`, `ready claims=9`, no blockers.
3. `scripts/render_progress_dashboard.py` refreshed the dashboard.
4. `make -C paper` reports no pending rebuild.
5. Targeted regression tests for readiness/asset/Figure-1 pipeline pass (`14 passed`).
6. Prompted-LLM ensemble and bootstrap assets were regenerated; transfer brittleness conclusions remain unchanged (ICLR25 prompted rows below majority, NeurIPS24 near-majority overlap).
7. A second-annotator IAA mini-slice packet is now staged for immediate execution: `experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv` + key + manifest (`60` rows; balanced across all five current standard packets).
8. Readiness audit now includes a dedicated `iaa_second_annotator_packet` check so the second-pass progress and eventual agreement metrics are surfaced in the same gate report.
9. A no-key prompted-LMM significance package is exported (`prompted_llm_significance.{md,csv,json}` + LaTeX table), confirming transfer conclusions with paired bootstrap deltas versus majority.

## What Is Already Strong

1. Quality gates and provenance are explicit and passing.
2. In-domain ICLR 2024 result still supports structured-evidence advantage.
3. Accuracy-trap claim remains clear and defensible.
4. Cross-year/cross-venue stress evidence exists with bounded claim language.
5. Human-validation queue is complete (`301/301`), with packet and evidence audits clean.

## Oral-Level Gaps (Priority Order)

1. **Independent reliability evidence gap**  
   Current labels are standard single-user; no independent IAA claim should be made.

2. **Strong prompted-LLM transfer baseline gap**  
   Infrastructure is ready, but the strongest API run is not locked as a paper-facing final baseline.

3. **External-validity breadth gap**  
   Evidence is strong but still concentrated in active-frontier and bounded slices; one more high-trust axis is needed.

4. **Narrative concentration gap**  
   The paper must center on stale-criticism failure and failure taxonomy as primary findings.

## 7-10 Day Execution Plan (2026-05-06 to 2026-05-15)

1. **P0: Lock transfer baseline package (highest ROI)**
   - Run one strong prompted-LLM baseline end-to-end on current standard packets.
   - Keep strict output audit; invalid rows must be explicit in paper text.
   - Regenerate prompted assets and summary table.

2. **P1: Lock broader-evidence package**
   - Prefer: one additional random/stratified venue slice with same audit gates.
   - Fallback: targeted second-annotator mini-slice (40-80 rows) for IAA sensitivity only.
   - Keep claim boundaries explicit (`not IAA`, `not prevalence`) unless new evidence supports expansion.
   - Current status (2026-05-06): mini-slice packet is prepared; pending step is independent second-pass labeling + agreement report export.

3. **P2: Convert narrative to oral shape**
   - Make Figure 1 + three flagship failure modes the Results spine.
   - Demote implementation detail that does not serve the central claim.
   - Keep macro-F1/per-label recovery first; accuracy second.

4. **P3: Freeze submission hardening package**
   - Re-run readiness, citation, and packet audits after paper edits.
   - Freeze artifact paths and command list for reproducibility.

## Minimal Command Backbone

```bash
python scripts/export_paper_assets.py --output-dir outputs/day1/paper_assets
python scripts/audit_paper_readiness.py \
  --output-json outputs/day1/paper_assets/paper_readiness_audit.json \
  --output-md outputs/day1/paper_assets/paper_readiness_audit.md
python scripts/render_progress_dashboard.py \
  --output outputs/day1/revtrack_progress_dashboard.html \
  --title "RevTrack Progress Dashboard"
```

## Go / No-Go

- **Go** for submission path now.
- **Go** for Oral push only if P0 + P1 are closed by `2026-05-15`.
- **Best-paper push** remains conditional on a stronger field-level reliability result beyond current bounded evidence.
