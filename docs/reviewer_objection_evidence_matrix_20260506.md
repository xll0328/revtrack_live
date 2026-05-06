# RevTrack Reviewer Objection -> Evidence Matrix (2026-05-06)

Scope: `emnlp2026_revtrack`  
Cycle: ARR May 2026 -> EMNLP 2026

Use this matrix to keep claim boundaries strict and response evidence concrete.

## O1: "This is just another static review benchmark."

- Response spine:
  - RevTrack evaluates temporal judgment after revision, not static plausibility.
  - Four-way issue outcome labels (`fixed`, `partially_fixed`, `unresolved`, `regressed`) expose failure modes hidden by static tasks.
- Evidence artifacts:
  - `paper/sections/01_introduction.tex`
  - `paper/sections/02_task.tex`
  - `paper/figures/revtrack_running_example.tex`
- Status: `ready`

## O2: "Accuracy gains are not meaningful under skew."

- Response spine:
  - We report macro-F1 and per-label recovery as primary metrics.
  - Accuracy-trap behavior is explicit on transfer stress sets.
- Evidence artifacts:
  - `outputs/day1/paper_assets/oral_evidence_panel.md`
  - `outputs/day1/paper_assets/oral_casebook.md`
  - `outputs/day1/paper_assets/clean_dev_summary.md`
  - `outputs/day1/paper_assets/transfer_summary.md`
  - `paper/sections/05_experiments.tex`
  - `paper/tables/prompted_llm_significance.tex`
- Status: `ready`

## O3: "Transfer claims are weak / not statistically grounded."

- Response spine:
  - Cross-year transfer is explicitly framed as bounded stress evidence.
  - Prompted baseline deltas vs majority are backed by paired bootstrap export.
- Evidence artifacts:
  - `outputs/day1/paper_assets/oral_evidence_panel.md`
  - `outputs/day1/paper_assets/oral_casebook.md`
  - `outputs/day1/paper_assets/prompted_llm_significance.md`
  - `outputs/day1/paper_assets/bootstrap_transfer_summary.md`
  - `docs/oral_best_paper_gap_audit_20260506.md`
- Status: `ready (bounded claim only)`

## O4: "No independent annotation reliability (IAA)."

- Response spine:
  - Main benchmark labels remain standard single-user confirmation for scope control.
  - A bounded independent second-pass mini60 is completed.
  - A broader boundary160 second-pass packet is also complete after explicit user confirmation of all rows.
- Evidence artifacts:
  - `experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv`
  - `outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_manifest.md`
  - `outputs/day1/paper_assets/iaa_second_annotator_mini60_batches.md`
  - `outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_metrics.json`
  - `experiments/day1/iaa_second_annotator_boundary160_v1_blind.tsv`
  - `outputs/day1/paper_assets/iaa_second_annotator_boundary160_v1_manifest.md`
  - `outputs/day1/paper_assets/iaa_second_annotator_boundary160_v1_metrics.json`
  - `outputs/day1/paper_assets/iaa_second_annotator_boundary160_v1_user_confirmation.md`
  - `outputs/day1/paper_assets/paper_readiness_audit.md` (`iaa_second_annotator_packet`)
- Boundary:
  - Treat this as bounded reliability evidence, not full-scale two-annotator prevalence evidence.
  - boundary160 is prelabel-assisted before user confirmation, so it should not be described as blind-independent IAA.
- Status: `ready (bounded reliability packet evidence with explicit claim boundary)`

## O5: "Possible leakage or packet misalignment."

- Response spine:
  - Blind/key/audit packet integrity checks and key alignment are script-audited.
  - Label-evidence completeness is tracked in readiness.
- Evidence artifacts:
  - `outputs/day1/paper_assets/paper_readiness_audit.md`
  - `outputs/day1/paper_assets/label_evidence_audit_summary.md`
  - `scripts/audit_human_validation_packet.py`
- Status: `ready`

## O6: "Regression label is too sparse to conclude much."

- Response spine:
  - We explicitly treat regression evidence as sparse and avoid broad per-label prevalence claims.
  - Regression is reported as a risk signal, not a large-scale rate estimate.
- Evidence artifacts:
  - `docs/oral_best_paper_gap_audit_20260506.md`
  - `paper/sections/06_discussion.tex`
- Status: `ready (bounded wording required)`

## O7: "Reproducibility is not complete."

- Response spine:
  - Paper assets, readiness audit, citation audit, and dashboard are script-regenerated.
  - Core targeted tests pass for packet/readiness/figure and IAA split pipeline.
- Evidence artifacts:
  - `scripts/export_paper_assets.py`
  - `scripts/audit_paper_readiness.py`
  - `scripts/render_progress_dashboard.py`
  - `tests/test_audit_paper_readiness.py`
  - `tests/test_split_second_annotator_packet.py`
- Status: `ready`

## Execution Priority (for Oral Push)

1. Keep O3 bounded and statistically explicit in main text.
2. Keep O2/O6 wording tight: macro-F1 first, no overclaim on sparse labels.
3. Use O4 reliability packets (mini60 + boundary160) as support, but keep the blind-independence boundary explicit.
