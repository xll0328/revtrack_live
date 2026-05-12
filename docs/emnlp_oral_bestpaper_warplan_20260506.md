# EMNLP 2026 Oral / Best Paper War Plan (2026-05-06)

Scope: `emnlp2026_revtrack`  
Today: `2026-05-06`  
ARR deadline (AoE): `2026-05-25`  
Remaining: `19` days

2026-05-12 addendum: human signoff completion was confirmed by the human author in-session; see `docs/emnlp2026_human_signoff_addendum_20260512.md`.

## 1) Distance Snapshot (As of 2026-05-06)

- Main-track acceptance: `7.5 / 10` (plausible now)
- Oral: `6.8 / 10` (now closer; reliability mini-slice closed, narrative still needs tightening)
- Best paper: `4.0 / 10` (not yet; needs stronger field-level reliability signal)

Interpretation:
- We are not blocked by pipeline quality. We are blocked by evidence depth + narrative sharpness.
- To reach oral confidence before `2026-05-25`, we must close:
  1. one stronger transfer baseline package under no-key constraints,
  2. final story concentration around stale-criticism + failure taxonomy.

## 2) Success Criteria (Submission / Oral / Best)

### Submission-safe (must-have, by `2026-05-18`)
- readiness audit remains `ready`, `0` blockers.
- all paper-facing tables/figures reproducible from committed scripts.
- claim boundaries remain explicit (`not IAA`, `not prevalence`) unless IAA closes.

### Oral-ready (target, by `2026-05-21`)
- either:
  - IAA mini-slice second-pass completed with agreement/kappa report; or
  - clear bounded fallback statement with strengthened significance + error-taxonomy argument.
- results section centered on 3 flagship failure modes and one unforgettable running example.

### Best-paper stretch (conditional)
- requires stronger, cleaner field-level reliability signal beyond current bounded evidence.
- not assumed for this cycle unless IAA and additional external-validity axis both land cleanly.

## 3) Three Workstreams (with Dates)

## WS-A: Reliability / IAA (highest oral lift)
Window: `2026-05-06` to `2026-05-14`

- A1. Prepare second-annotator execution packets (done)
- A2. Complete independent second-pass labeling on mini60 (done; `60/60`)
- A3. Export agreement/kappa + mismatch analysis (done; agreement=`1.0`, kappa=`1.0`, mismatches=`0`)
- A4. Update readiness + limitations + claim ledger language

Exit gate:
- `outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_metrics.json` exists and is cited in paper-facing artifacts.

## WS-B: No-key baseline hardening (already started)
Window: `2026-05-06` to `2026-05-12`

- B1. Lock prompted significance vs majority (done)
- B2. Keep transfer-brittleness claim statistically explicit in paper text (done)
- B3. Add one compact reviewer-facing evidence table/paragraph for rebuttal use (done)

Exit gate:
- significance, bootstrap, and failure-taxonomy narratives are coherent and non-contradictory.

## WS-C: Oral-shape narrative freeze
Window: `2026-05-10` to `2026-05-22`

- C1. Make Figure 1 + failure taxonomy the Results spine
- C2. Reduce implementation-detail verbosity in main text
- C3. Freeze final claim wording and objection-response evidence map
- C4. Final reproducibility sweep + PDF freeze

Exit gate:
- advisor-style oral pitch can be delivered in 60-90 seconds with one thesis and three empirical points.

## 4) Detailed To-Do List

Status legend: `[x] done`, `[-] in_progress`, `[ ] pending`

### Immediate (T0: today to +48h)

- [x] T0-1 Added no-key prompted significance audit:
  - `scripts/export_prompted_llm_significance.py`
  - `outputs/day1/paper_assets/prompted_llm_significance.{md,csv,json}`
  - `paper/tables/prompted_llm_significance.tex`
- [x] T0-2 Integrated significance evidence into paper:
  - `paper/sections/05_experiments.tex`
  - `paper/sections/appendix_audit.tex`
- [x] T0-3 Split IAA mini60 into balanced blind batches (20x3):
  - `experiments/day1/iaa_second_annotator_mini60_v1_blind_batch1.tsv`
  - `experiments/day1/iaa_second_annotator_mini60_v1_blind_batch2.tsv`
  - `experiments/day1/iaa_second_annotator_mini60_v1_blind_batch3.tsv`
  - `outputs/day1/paper_assets/iaa_second_annotator_mini60_batches.{md,json}`
- [x] T0-4 Added batch splitter utility + test:
  - `scripts/split_second_annotator_packet.py`
  - `tests/test_split_second_annotator_packet.py`
- [x] T0-5 Start independent second-pass labeling on batch files
- [x] T0-6 Added one-command IAA merge/eval/readiness pipeline:
  - `scripts/run_iaa_second_annotator_pipeline.py`
  - `outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_pipeline_report.{md,json}`

### Week 1 (`2026-05-07` ~ `2026-05-12`)

- [x] W1-1 Collect completed second-pass labels for at least 2/3 batches
- [x] W1-2 Run:
  - `python scripts/evaluate_human_validation.py --human-sheet experiments/day1/iaa_second_annotator_mini60_v1_blind.tsv --key experiments/day1/iaa_second_annotator_mini60_v1_key.tsv --output-json outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_metrics.json --mismatch-output outputs/day1/paper_assets/iaa_second_annotator_mini60_v1_mismatches.tsv`
- [x] W1-3 Refresh readiness:
  - `python scripts/audit_paper_readiness.py`
- [x] W1-4 Update claim boundaries in paper (IAA done vs not done branch text)

### Week 2 (`2026-05-13` ~ `2026-05-18`)

- [-] W2-1 Narrative concentration pass for oral style (intro/results/discussion; focus/clarity, no evidence deletion)
- [x] W2-2 Reviewer objection evidence matrix refresh
- [x] W2-3 Full artifact regeneration and citation audit
- [-] W2-4 Dry-run submission package freeze (no new experimental scope)

### Final Week (`2026-05-19` ~ `2026-05-24`)

- [ ] F-1 PDF and appendix final consistency pass
- [ ] F-2 Final claim ledger / readiness check must remain `ready`
- [ ] F-3 Final response pack for likely weak-reject objections
- [ ] F-4 Submit by `2026-05-24` night (AoE buffer day preserved)

## 5) Risk Control

- If IAA second-pass is not completed by `2026-05-14`:
  - keep strict boundary (`not IAA`) and push the no-key significance + taxonomy line as primary defense.
- Do not open new large-scope data collection after `2026-05-18`.
- No un-audited claims in abstract/intro/results.

## 6) Start Log (Executed Now)

- `2026-05-06`: launched no-key significance package and integrated into paper.
- `2026-05-06`: launched IAA mini60 operationalization via 3 balanced blind batches.
- `2026-05-06`: added tests and passed targeted checks.
- `2026-05-06`: completed IAA mini60 second pass (`60/60`), exported agreement=`1.0` and Cohen's kappa=`1.0`, refreshed readiness.
- `2026-05-06`: exported oral/rebuttal evidence panel (`oral_evidence_panel.{md,csv,json}` + `paper/tables/oral_evidence_panel.tex`) and integrated into appendix.
- `2026-05-06`: exported oral/rebuttal representative casebook (`oral_casebook.{md,csv,json}` + `paper/tables/oral_casebook_summary.tex`) and integrated into appendix.
- `2026-05-06`: completed full artifact regeneration + citation/readiness audits and paper rebuild under no-key constraints (`export_paper_assets`, `audit_paper_readiness`, `audit_paper_citations`, `make -B -C paper`).
- `2026-05-06`: opened submission dry-run freeze log (`docs/submission_dryrun_20260506.md`) with command backbone + gate decision.
- `2026-05-06`: opened mock pre-review sprint map (`docs/mock_presubmission_todo_20260506.md`) and started execution.
- `2026-05-06`: exported split label-coverage panel (`split_label_coverage.{md,csv,json}` + `paper/tables/split_label_coverage.tex`) and prepared boundary-focused second-annotator packet (`iaa_second_annotator_boundary160_v1`).
- `2026-05-06`: launched stronger learned baseline probe (`scripts/run_transformer_classifier_transfer.py`) and recorded first-run fine-tuned ModernBERT transfer metrics.
- `2026-05-06`: upgraded stronger-baseline evidence to multi-seed summary (`scripts/export_modernbert_multiseed_probe.py`; `finetuned_modernbert_multiseed_20260506.*` + `paper/tables/finetuned_modernbert_multiseed_probe.tex`).
- `2026-05-06`: integrated stronger learned baseline narrative into main text (`paper/sections/05_experiments.tex`, `paper/sections/06_discussion.tex`) to directly answer the weak-baseline objection.
- `2026-05-06`: completed boundary160 second-pass user confirmation (`160/160`), regenerated batch sheets, exported metrics (`agreement=1.0`, `cohen_kappa=1.0`), and refreshed readiness with boundary160 IAA check.
- `2026-05-06`: closed related-work gap with DOI-verified additions (`du-etal-2024-llms-assist`, `zhu-etal-2025-deepreview`, `robertson-2023-gpt4-helpful`, `leng-etal-2019-deepreviewer`, `wang-etal-2020-reviewrobot`) and updated citation matrix.
