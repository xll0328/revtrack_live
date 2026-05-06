# RevTrack Virtual Pre-Review Action Plan (v2)

Date: `2026-05-06`  
Scope: address the latest virtual pre-review (borderline 2.5) with auditable, submission-facing upgrades.

Status legend: `[x] done`, `[-] in progress`, `[ ] pending`

## A. Highest-impact fixes (review-score critical)

- [-] **A1. Reliability claim hardening (without overclaim)**
  - Reviewer issue: reliability evidence too narrow for benchmark maturity.
  - Actions:
    - keep explicit boundary: `mini60` is blind-independent bounded check; `boundary160` is user-confirmed prelabel-assisted packet.
    - ensure Abstract/Intro/Dataset/Discussion/Limitations use one consistent wording.
    - keep claim as bounded reliability support, not full-dataset IAA.
  - Artifacts:
    - `paper/sections/{01_introduction,03_dataset,06_discussion,08_limitations,appendix_audit}.tex`
    - `outputs/day1/paper_assets/paper_readiness_audit.{json,md}`
  - Exit gate:
    - no section still implies full independent two-annotator IAA.

- [ ] **A2. Annotation rubric operationalization in main text**
  - Reviewer issue: fixed/partial/unresolved boundary not operational enough.
  - Actions:
    - add explicit adjudication protocol (axis match, materiality threshold, evidence sufficiency) in Section 2.
    - add concise worked boundary examples in main text (not only appendix pointer).
  - Artifacts:
    - `paper/sections/02_task.tex`
    - `paper/tables/worked_issue_examples.tex` (main-text pointer update)
  - Exit gate:
    - reviewer can reproduce label decision logic from main text alone.

- [ ] **A3. Stronger baseline suite expansion (NLI-style + evidence-grounded)**
  - Reviewer issue: baseline suite lacks explicit entailment-style formulation.
  - Actions:
    - add an NLI-style hypothesis baseline (concern + response + revision -> label hypotheses).
    - report on clean-dev + cross-year + cross-venue standard splits.
  - Artifacts:
    - `scripts/run_nli_hypothesis_baseline.py`
    - `outputs/day1/paper_assets/nli_hypothesis_transfer_20260506.{csv,json,md}`
    - optional table: `paper/tables/nli_hypothesis_transfer.tex`
  - Exit gate:
    - reproducible command + auditable metrics exported.

- [ ] **A4. Transfer-claim boundary tightening**
  - Reviewer issue: abstract/intro can still be read as broader than stress-sampled evidence.
  - Actions:
    - tighten abstract and intro phrasing to “stress-oriented transfer evidence”.
    - explicitly separate diagnostic brittleness vs prevalence/generalization.
  - Artifacts:
    - `paper/main.tex`
    - `paper/sections/01_introduction.tex`
    - `paper/sections/05_experiments.tex`
  - Exit gate:
    - no sentence implies venue-wide prevalence inference from active frontiers.

## B. Medium-impact upgrades (robustness & readability)

- [ ] **B1. Label-sparsity-aware reporting panel**
  - Actions:
    - add collapsed evaluation panel (4-way primary + boundary-aware notes) to reduce over-interpretation under missing labels.
    - add per-split “interpretable labels present/absent” callout next to transfer tables.
  - Artifacts:
    - `outputs/day1/paper_assets/split_label_coverage.{md,csv,json}`
    - `paper/sections/05_experiments.tex`
    - `paper/tables/split_label_coverage.tex`

- [ ] **B2. Main-text qualitative example strengthening**
  - Actions:
    - ensure 3-5 compact, concrete cases with concern/evidence/rationale are visible from main narrative.
  - Artifacts:
    - `paper/sections/05_experiments.tex`
    - `paper/sections/appendix_audit.tex`
    - `outputs/day1/paper_assets/oral_casebook.md`

- [ ] **B3. Presentation polish from reviewer notes**
  - Actions:
    - standardize `in-domain` spelling.
    - shorten long table captions where possible.
    - fix malformed citation style snippets.
  - Artifacts:
    - paper sections + affected tables.

## C. Final freeze + rebuttal packet

- [ ] **C1. Full no-key reproducibility sweep**
  - Commands:
    - `python scripts/export_paper_assets.py --output-dir outputs/day1/paper_assets`
    - `python scripts/audit_paper_readiness.py --output-json ... --output-md ...`
    - `python scripts/audit_paper_citations.py`
    - `make -B -C paper`
    - targeted `pytest` for modified scripts.
  - Exit gate:
    - readiness `ready`, citations `pass`, paper builds.

- [ ] **C2. Rebuttal-ready objection matrix refresh**
  - Actions:
    - map each major criticism to exact artifact paths and one-line rebuttal claims.
  - Artifact:
    - `docs/reviewer_objection_evidence_matrix_20260506.md`

---

## Immediate execution order (now)

1. `A2` Task-label operationalization patch in Section 2.  
2. `A3` Implement and run NLI-style baseline export on canonical splits.  
3. `A4` Tighten abstract/intro transfer-boundary wording.  
4. `C1` Rebuild + audits + updated freeze manifest.
