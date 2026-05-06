# RevTrack Mock Pre-Review Sprint ToDo (2026-05-06)

Scope: `emnlp2026_revtrack`  
Target: EMNLP 2026 ARR May cycle (`2026-05-25` AoE)  
Input: virtual pre-review (borderline; strongest blockers = reliability, representativeness, stronger baselines)

## 0) Sprint Objective

Turn the current draft from "scoped-ready" to "reviewer-resistant" by closing the highest-risk objections with auditable evidence:

1. reliability breadth (beyond mini60),
2. stronger learned baselines,
3. representativeness diagnostics for non-frontier slices,
4. clearer wording on what is stress-suite evidence vs benchmark-general evidence.

---

## 1) Priority Stack

Status legend: `[x] done`, `[-] in progress`, `[ ] pending`

### P0 (must close first; highest score impact)

- [x] **R1 Reliability breadth upgrade (mini60 -> boundary-focused larger second-pass packet)**
  - Goal: produce a larger independent second-pass packet focused on hard boundaries (`fixed` vs `partially_fixed`, `partially_fixed` vs `unresolved`, regression candidates).
  - Deliverables:
    - `experiments/day1/iaa_second_annotator_boundary160_v1_blind.tsv`
    - `experiments/day1/iaa_second_annotator_boundary160_v1_key.tsv`
    - `outputs/day1/paper_assets/iaa_second_annotator_boundary160_v1_manifest.{md,json}`
    - `outputs/day1/paper_assets/iaa_second_annotator_boundary160_v1_metrics.{md,json}`
    - `outputs/day1/paper_assets/iaa_second_annotator_boundary160_v1_user_confirmation.{md,json}`
  - Exit gate:
    - packet built with explicit quota by boundary + venue packet;
    - metrics script supports per-label and boundary-pair agreement reporting.
  - Completed:
    - packet and manifest exported;
    - user confirmed all `160/160` rows in boundary160 blind sheet;
    - canonical boundary160 metrics exported (`agreement=1.0`, `cohen_kappa=1.0`, `mismatches=0`);
    - readiness audit refreshed with boundary160 IAA status (`target_rows=160`, `labeled_rows=160`).

- [x] **R2 Stronger learned baseline (beyond frozen encoder + linear head)**
  - Goal: add a fine-tuned transformer classifier baseline trained on `iclr2024_train_v8`.
  - Deliverables:
    - `scripts/run_transformer_classifier_transfer.py`
    - outputs on at least:
      - `iclr2024_clean_dev_assistant_v7`
      - `iclr2025_expanded80_standard_validation_v1`
      - `neurips2024_limit100_standard_validation_v1`
      - `iclr2023_limit80_random80_standard_validation_v1`
    - paper-facing summary table under `outputs/day1/paper_assets/`.
  - Exit gate:
    - reproducible command log + metrics JSON + confusion/error profile per split.
  - Completed:
    - single-seed transfer runs completed;
    - multi-seed summary exported:
      - `outputs/day1/paper_assets/finetuned_modernbert_multiseed_20260506.{md,csv,json}`
      - `paper/tables/finetuned_modernbert_multiseed_probe.tex`
    - paper text updated to report stronger baseline behavior in-domain vs transfer.

### P1 (must close for oral robustness)

- [x] **R3 Representativeness/coverage diagnostics panel**
  - Goal: make missing-label coverage explicit and auditable for each split.
  - Deliverables:
    - `outputs/day1/paper_assets/split_label_coverage.{md,csv,json}`
    - appendix table: split size, label counts, absent labels, sample design tag.
  - Exit gate:
    - every transfer claim in paper points to this panel.

- [x] **R4 Hard-rule dependence transparency**
  - Goal: separate "learned signal" vs "hard override" contribution more explicitly.
  - Deliverables:
    - ablation note/table updates from existing outputs (`structured` vs `structured_no_overrides`);
    - explicit text in Methods/Experiments on portability caveats and where rules are used.
  - Exit gate:
    - reviewer can tell exactly what fraction of gain depends on overrides.

- [x] **R5 Main-text qualitative examples (3-5 cases)**
  - Goal: include concrete issue-level adjudication examples for trust.
  - Deliverables:
    - `outputs/day1/paper_assets/oral_casebook.{md,csv,json}` (issue-level worked examples)
    - paper insertion (main or appendix with main-text pointer).
  - Exit gate:
    - examples cover at least `fixed`, `partially_fixed`, `unresolved`, and one regression-risk case.

### P2 (rebuttal and polish)

- [x] **R6 Related-work gap closure**
  - Goal: verify and integrate missing adjacent work (peer-review LLM assistance, response assistance).
  - Deliverables:
    - updated `docs/related_work_matrix.md`
    - `paper/sections/07_related_work.tex`
    - `paper/refs.bib` updates (only verified references).
  - Exit gate:
    - citation audit passes and no unverifiable references are added.
  - Completed:
    - verified and integrated additional peer-review assistance references with DOI-backed entries;
    - excluded unverified candidate items from paper citations.

- [x] **R7 Ethics + misuse risk expansion**
  - Goal: explicitly discuss disciplinary bias, venue-style dependence, and semi-automated editorial misuse risks.
  - Deliverables:
    - updated `paper/sections/09_ethics.tex`
    - updated `paper/sections/08_limitations.tex`.
  - Exit gate:
    - risk statements are concrete and tied to known failure modes.

- [x] **R8 Terminology simplification pass**
  - Goal: reduce internal tooling jargon in core narrative.
  - Deliverables:
    - intro/dataset/discussion wording pass (`claim-readiness gate` etc. simplified or contextualized).
  - Exit gate:
    - one-pass readability improvement without changing claim scope.

---

## 2) Execution Backbone (No-Key Safe)

```bash
python scripts/export_paper_assets.py --output-dir outputs/day1/paper_assets
python scripts/audit_paper_readiness.py \
  --output-json outputs/day1/paper_assets/paper_readiness_audit.json \
  --output-md outputs/day1/paper_assets/paper_readiness_audit.md
python scripts/audit_paper_citations.py
make -C paper
pytest -q
```

---

## 3) Immediate Next 48h (Concrete)

1. Integrate boundary160 reliability readout into paper wording (Methods/Limitations/Appendix pointers) without overclaiming independence.
2. Run one final pre-submission artifact sweep (readiness + citation + paper build) and freeze hash list for submission.
3. Prioritize rebuttal-ready qualitative cases for fixed/partial/unresolved boundary disputes.
4. Keep live sync in `revtrack_live` with updated evidence manifest.

---

## 4) Claim Discipline During Sprint

- Keep current boundaries unless new evidence lands:
  - frontier results are stress evidence, not natural-prevalence estimates;
  - mini-slice or boundary-slice IAA is reliability support, not full two-annotator coverage of all packets;
  - sparse `regressed` counts cannot support broad per-label performance claims.
