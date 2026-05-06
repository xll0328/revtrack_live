# Random/Stratified Slice Feasibility Snapshot

Date: 2026-05-06

## Objective

Refresh feasibility for a non-ICLR broader slice that can support oral-level external-validity claims beyond active-frontier evidence.

## Probe Runs (2026-05-06)

### Control checks (known working venues)

- ICLR 2024 probe (limit 20): `outputs/day1/openreview_probe_iclr2024_refresh_20260506.json`
  - `v2-notes`: `submissions=20`, `submissions_with_candidates=20`, `issue_candidates=79`.
- NeurIPS 2024 probe (limit 20): `outputs/day1/openreview_probe_neurips2024_refresh_20260506.json`
  - `v2-notes`: `submissions=20`, `submissions_with_candidates=20`, `issue_candidates=79`.

Interpretation: pipeline connectivity and core extraction path are healthy.

### Non-ICLR candidates

- ICML 2024 probes:
  - `outputs/day1/openreview_probe_icml2024_20260506.json` (fast timeout run)
  - `outputs/day1/openreview_probe_icml2024_retry_20260506.json` (timeout/retry run)
  - Outcome: still not usable as-is.
    - `v2-notes`: submissions may appear, but `issue_candidates=0`.
    - `v2-search`: API returns `400`.
    - `v1-notes`: no usable submissions.

- NeurIPS 2023 probe:
  - `outputs/day1/openreview_probe_neurips2023_20260506.json`
  - Outcome: currently blocked by repeated read timeouts on `v2` paths; no usable fallback rows from `v1`.

- ICML 2023 probe:
  - `outputs/day1/openreview_probe_icml2023_20260506.json`
  - Outcome: currently blocked (`v2-notes` timeout, `v2-search` 400, `v1` empty).

## Current Feasibility Verdict

1. Existing RevTrack extraction remains healthy for ICLR/NeurIPS 2024 controls.
2. Non-ICLR broad-slice acquisition remains blocked in the current OpenReview path:
   - ICML schema/path mismatch (`issue_candidates=0` despite submissions),
   - or unstable/timeout behavior for older venue-year endpoints.
3. The current external-validity evidence stack should continue to be reported as:
   - standard single-user active frontiers (expanded80, NeurIPS2024 limit100),
   - plus bounded random/stratified ICLR2023 slice evidence,
   - not independent IAA and not natural-prevalence estimates.

## Next Action (bounded)

- Keep oral-level P1 on two parallel tracks:
  1. non-ICLR ingestion repair (ICML/NeurIPS2023 schema/timeouts), and
  2. targeted second-annotator mini-slice fallback (40-80 rows) if non-ICLR ingestion remains blocked.

- Do not expand claim scope until one of the two tracks produces auditable standard evidence.
