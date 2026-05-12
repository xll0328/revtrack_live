# EMNLP 2026 ARR Submission Tracker (2026-05-12)

Scope: `emnlp2026_revtrack`

Status: `READY_FOR_UPLOAD_NOT_SUBMITTED`

## Official Venue Constraint

- ARR cycle: `2026 May`
- Intended venue: `EMNLP 2026`
- Required submission-form choice: `Preferred venue: EMNLP 2026`
- Source checked: `https://2026.emnlp.org/calls/main_conference_papers/`
- Interpretation: for ARR 2026 May, failing to select `EMNLP 2026` blocks later
  commitment to EMNLP 2026.

## Local Gate Evidence

- Human signoff addendum: `docs/emnlp2026_human_signoff_addendum_20260512.md`
- Readiness audit: `outputs/day1/paper_assets/paper_readiness_audit.md`
- Readiness result: `overall_status=ready`
- Citation audit: `outputs/day1/paper_assets/paper_citation_audit.json`
- Citation result: `status=pass`, `problems=0`
- Build command: `make -B -C paper`
- Build result: pass; `paper/main.pdf` rebuilt
- Page count: `19`
- Automated PDF metadata check: title/author empty via local PyPDF check

## Locked Upload Artifact

- Paper PDF: `paper/main.pdf`
- Paper PDF SHA-256: `e480c8262d3ffbbedbe92da5015b27ba07025deb15ae21217e19ebef2d776113`
- Current repo state when checked: clean

## Submission Backfill

- ARR submission ID:
- OpenReview URL:
- Upload timestamp UTC:
- Preferred venue selected: EMNLP 2026
- Upload operator:
- Uploaded paper PDF:
- Uploaded paper PDF SHA-256:
- Supplement/source uploaded, if any:
- Post-upload preview verified by:
- Post-upload preview timestamp UTC:

## Stop Rules

- Stop if the OpenReview preview does not match `paper/main.pdf`.
- Stop if `Preferred venue` is anything other than `EMNLP 2026`.
- Stop if citation audit changes from `pass` or readiness changes from `ready`.

