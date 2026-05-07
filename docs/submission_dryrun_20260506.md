# Submission Dry-Run Freeze (2026-05-06)

Scope: `emnlp2026_revtrack`  
Branch: `main`  
Checkpoint commit: `1e498c8`

Purpose: run a no-key, reproducible pre-freeze check so we can decide whether the paper package is submission-safe for the current claim scope.

## Commands Executed

```bash
python scripts/export_paper_assets.py --output-dir outputs/day1/paper_assets
python scripts/audit_paper_readiness.py \
  --output-json outputs/day1/paper_assets/paper_readiness_audit.json \
  --output-md outputs/day1/paper_assets/paper_readiness_audit.md
python scripts/audit_paper_citations.py
make -B -C paper
pytest -q tests/test_audit_paper_readiness.py \
  tests/test_export_oral_evidence_panel.py \
  tests/test_export_oral_casebook.py \
  tests/test_split_second_annotator_packet.py \
  tests/test_render_figure1_revision_tracking.py
```

## Results

- Readiness audit: `overall_status=ready`, `ready_claims=9`, `blockers=0`, `warnings=0`.
- Citation audit: `pass`, `cited_keys=26`, `problems=0`.
- Paper build: `pass` (`paper/main.pdf` rebuilt).
- Targeted regression tests: `16 passed`.

## Current Gate Decision

- Submission-safe for current bounded claim scope: **Go**.
- Oral push status: **Go (in progress)** with remaining focus on final response-pack polish.
- Best-paper push status: **Conditional**; still depends on stronger field-level reliability signal beyond current bounded evidence.

## Remaining High-Priority Items

1. Final-week consistency and rebuttal response pack.

## Refresh Checkpoint (Boundary160 Integrated)

Refresh time: `2026-05-06` (UTC)  
Checkpoint commit: `838b422`

Commands executed:

```bash
python scripts/export_oral_evidence_panel.py
python scripts/audit_paper_readiness.py \
  --output-json outputs/day1/paper_assets/paper_readiness_audit.json \
  --output-md outputs/day1/paper_assets/paper_readiness_audit.md
python scripts/audit_paper_citations.py > outputs/day1/paper_assets/paper_citation_audit.json
make -B -C paper
```

Refresh results:

- Readiness audit: `overall_status=ready`, `ready_claims=9`, `blockers=0`, `warnings=0`.
- Citation audit: `pass`, `cited_keys=31`, `problems=0`.
- Boundary160 packet status: `labeled_rows=160`, `agreement=1.0`, `cohen_kappa=1.0`, `mismatches=0`.
- Paper build: `pass` (`paper/main.pdf` rebuilt; 18 pages).

Freeze artifact hashes:

- `outputs/day1/paper_assets/submission_artifact_manifest_20260506_1213.md`

## Refresh Checkpoint (2026-05-07 Final Sweep)

Refresh time: `2026-05-07` (UTC)

Commands executed:

```bash
python scripts/export_paper_assets.py --output-dir outputs/day1/paper_assets
python scripts/audit_paper_readiness.py \
  --output-json outputs/day1/paper_assets/paper_readiness_audit.json \
  --output-md outputs/day1/paper_assets/paper_readiness_audit.md
python scripts/audit_paper_citations.py > outputs/day1/paper_assets/paper_citation_audit.json
make -B -C paper
pytest -q tests/test_audit_paper_readiness.py \
  tests/test_export_oral_evidence_panel.py \
  tests/test_export_oral_casebook.py \
  tests/test_split_second_annotator_packet.py \
  tests/test_render_figure1_revision_tracking.py
```

Refresh results:

- Readiness audit: `overall_status=ready`, `ready_claims=9`, `blockers=0`, `warnings=0`.
- Citation audit: `pass`, `cited_keys=31`, `problems=0`.
- Paper build: `pass` (`paper/main.pdf` rebuilt; 19 pages).
- Targeted regression tests: `16 passed`.
- Narrative concentration pass: completed on `2026-05-07` for Introduction/Experiments/Discussion with claim boundaries unchanged.
- Updated freeze artifact manifest: `outputs/day1/paper_assets/submission_artifact_manifest_20260507_0227.md`.
