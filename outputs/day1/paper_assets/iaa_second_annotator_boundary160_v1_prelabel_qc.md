# Prelabel QC Report (Strict Recheck)

- Date: `2026-05-06`
- Scope: `experiments/day1/iaa_second_annotator_boundary160_v1_blind.tsv`
- Verdict: `PASS (with methodological caveat)`

## 1) Structural integrity

- Rows: `160`
- Unique `issue_id`: `160` (duplicates `0`)
- Invalid labels: `0`
- Missing fields:
  - `human_confidence`: `0`
  - `evidence_span`: `0`
  - `notes`: `0`
- Blind-sheet leakage fields present: `none`

## 2) Copy/prelabel correctness vs key sheet

- Label source in notes:
  - `source=assistant_label`: `160`
  - `source=first_pass_label`: `0`
- Mismatch vs key logic:
  - Label mismatch rows: `0`
  - Confidence mismatch rows: `0`
  - Evidence mismatch rows: `0`

## 3) Agreement/audit checks

- `evaluate_human_validation.py` recheck:
  - Agreement: `1.0`
  - Cohen’s kappa: `1.0`
  - Mismatches: `0`
- `audit_label_evidence.py` recheck:
  - `ok=true`
  - `structural_errors=0`
  - `evidence_issue_count=0`

## 4) Batch consistency

- Batch files: `4`
- Total batch rows: `160`
- Duplicates across batches: `0`
- Missing-from-batches: `0`
- Extra-in-batches: `0`
- Annotation mismatch vs master blind: `0`

## 5) Text quality sanity checks

- Label distribution:
  - `fixed=27`, `partially_fixed=60`, `unresolved=66`, `regressed=7`
- Evidence length:
  - min `51`, median `418`, p95 `422`, max `422`
  - `<100 chars`: `13`
  - `>=418 chars`: `86`
  - `==422 chars`: `25`
- Notes template:
  - unique template count: `1`
- Placeholder regex scan:
  - hits: `1` (issue `eHzIwAhj06__r03`)
  - manual read: lexical usage (“unknown nuances”), not placeholder annotation.

## 6) Caveat (important)

This sheet is an **AI prelabel draft** and is **not** independent second-annotator evidence.  
IAA claim promotion should use your human-reviewed final labels (after you accept/modify each row).
