# NeurIPS 2024 limit100 active frontier Adjudication Draft Audit

Status: `needs_review`

Human-validation status: `not_human_validated`

Recommendation: Do not promote automatically. Use as an assistant-adjudication draft for user review.

## Checks

### pass_1_packet_integrity (pass)

Blind/key/audit packet must have passed its packet audit before draft review.

Evidence:

```json
{
  "audit_rows": 80,
  "blind_rows": 80,
  "errors": [],
  "key_rows": 80,
  "ok": true,
  "warnings": []
}
```

### pass_2_candidate_gate (pass)

Candidate pool must pass count, completeness, duplicate-ID, and disagreement gates.

Evidence:

```json
{
  "complete_rate": 1.0,
  "disagreement_rows": 316,
  "errors": [],
  "high_disagreement_rows": 93,
  "ok": true,
  "rows": 393,
  "warnings": []
}
```

### pass_3_row_identity (pass)

Adjudication, blind, key, and source frontier rows must align exactly.

Evidence:

```json
{
  "duplicate_issue_ids": {
    "adjudication": [],
    "blind": [],
    "frontier": [],
    "key": []
  },
  "id_set_match": true,
  "row_counts": {
    "adjudication": 80,
    "blind": 80,
    "frontier": 80,
    "key": 80
  }
}
```

### pass_4_label_evidence_completeness (pass)

Every draft row must have a valid label, confidence, and evidence span.

Evidence:

```json
{
  "invalid_labels": [],
  "missing_confidence": [],
  "missing_evidence": []
}
```

### pass_5_provenance_boundary (pass)

Draft rows must remain explicitly marked as not human validation.

Evidence:

```json
{
  "bad_provenance_rows": []
}
```

### pass_6_distribution_sanity (warning)

Extreme label concentration should block promotion until a human reviews the frontier.

Evidence:

```json
{
  "label_distribution": {
    "regressed": 4,
    "unresolved": 76
  },
  "max_label": "unresolved",
  "max_rate": 0.95,
  "regressed_rate": 0.05
}
```

### pass_7_model_support_sanity (warning)

Rows with labels supported by only one model are useful for review but risky as auto labels.

Evidence:

```json
{
  "support_count_distribution": {
    "1": 43,
    "2": 32,
    "3": 5
  },
  "weak_support_examples": [
    "BRZYhVHvSg__r02",
    "BRZYhVHvSg__r03",
    "DAO2BFzMfy__r04",
    "3ZAfFoAcUI__r02",
    "3BNPUDvqMt__r01",
    "3BNPUDvqMt__r02",
    "3ZAfFoAcUI__r01",
    "9uolDxbYLm__r01",
    "9uolDxbYLm__r03",
    "IfZwSRpqHl__r04"
  ],
  "weak_support_rate": 0.5375,
  "weak_support_rows": 43
}
```

### pass_8_regression_cue_sanity (pass)

Regressed labels should be treated cautiously when explicit regression cues are absent.

Evidence:

```json
{
  "missing_cue_examples": [],
  "missing_cue_rate": 0.0,
  "regressed_rows": 4,
  "regressed_rows_without_explicit_regression_cue": 0
}
```
