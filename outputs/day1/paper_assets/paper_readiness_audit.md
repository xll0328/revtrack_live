# Paper Readiness Audit

Overall status: `ready`

## Claim Counts

- `ready`: `9`

## Checks

### claims_ready (pass)

Core paper claims are separated into ready/stress/not-ready buckets.

Evidence: ready=9, integrity_ready=0, stress=0, not_ready=0

Next action: Keep the claim ledger updated after every new experiment.

### iclr2024_pool_quality (pass)

ICLR 2024 in-domain pool passes candidate quality gates.

Evidence: ok=True, rows=230, complete_rate=1.0, disagreements=82

Next action: Freeze exact split/version metadata for the eventual benchmark release.

### iclr2025_pool_quality (pass)

ICLR 2025 scaled pool passes candidate quality gates.

Evidence: ok=True, rows=322, complete_rate=0.9627329192546584, disagreements=244

Next action: Use the scaled ICLR 2025 frontier as hardened cross-year evidence; add another venue/year before broad generalization claims.

### packet_integrity (pass)

Blind/key/audit validation packet integrity checks pass.

Evidence: packet_audits=6, failures=0

Next action: Run packet audit before every human-validation release.

### label_evidence_complete (pass)

Labeled sheets should have explicit evidence spans and notes for release-quality auditing.

Evidence: audited_rows=329, evidence_issues=0

Next action: Fill missing evidence_span values before freezing the benchmark release.

### human_validation_completed (pass)

Human validation labels are required before final benchmark claims.

Evidence: labeled_rows=301, total_rows=301, provenance=canonical blind-sheet labels | standard human-validation signoff; promoted_rows=61; second annotator only needed for inter-annotator reliability claims | expanded80 user-confirmed standard validation; promoted_rows=80; not an independent two-annotator IAA pass | NeurIPS2024 user-confirmed standard validation; promoted_rows=80; not an independent two-annotator IAA pass | ICLR2023 random80 user-confirmed standard validation; promoted_rows=80; transfer_status=standard_single_user_confirmed; not an independent two-annotator IAA pass

Next action: Use these standard human-validation labels for current claims; add a second annotator only for inter-annotator reliability claims.

### human_validation_queue_ready (pass)

A prioritized human-validation work queue points to the active blind sheets.

Evidence: queue_rows=301, pending=0, done=301, packets=['ICLR 2023 random80 v1', 'ICLR 2024 v1', 'ICLR 2025 expanded80 v1', 'ICLR 2025 repro v2', 'NeurIPS 2024 limit100 v1']

Next action: Regenerate outputs/day1/paper_assets/human_validation_work_queue.csv after packet or label updates.

### human_validation_batches_ready (pass)

Blind human-validation batches cover the active pending queue.

Evidence: batches=0, batch_rows=0, expected_pending_rows=0

Next action: Regenerate outputs/day1/human_validation_batches after queue or blind-sheet updates.

### human_validation_batch_ingest_ready (pass)

Completed batch annotations can be mapped back to the canonical blind sheets.

Evidence: status=ok, batch_rows=0, completed_batch_rows=0, merged_rows=0, errors=0

Next action: Rerun merge_human_validation_batches.py after batch edits; write canonical sheets only after an error-free dry run.

### paper_citations_ready (pass)

Paper citations resolve against the BibTeX file and the final LaTeX log.

Evidence: status=pass, cited_keys=31, bib_entries=31, problems=0

Next action: Rerun audit_paper_citations.py after related-work or BibTeX edits.

### iaa_second_annotator_packet (pass)

Second-annotator IAA mini-slice status is tracked separately from canonical first-pass labels.

Evidence: target_rows=160, blind_rows=160, labeled_rows=160, metrics_labeled_rows=160, agreement=1.0, cohen_kappa=1.0

Next action: IAA mini-slice metrics are complete; keep this as bounded reliability evidence and avoid broad prevalence claims.

### not_ready_claims_blocked (pass)

Not-ready claims are explicitly blocked from paper claims.

Evidence: not_ready_claims=[]

Next action: Keep not-ready claims out of the main claim set until gates pass.

## Immediate Next Actions

