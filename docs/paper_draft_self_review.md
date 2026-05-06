# Paper Draft Self-Review

Date: 2026-04-28

Scope: [paper/main.tex](/data/sony/emnlp2026_revtrack/paper/main.tex) and [paper/main.pdf](/data/sony/emnlp2026_revtrack/paper/main.pdf).

## Summary Counts

- `CRITICAL`: 1
- `MAJOR`: 4
- `MINOR`: 3

## Critical Finding

1. **Oral/Best-paper evidence bar is not met yet.**
   - Current standard labels are high quality for the scoped claim set (`301 / 301`), and now include one broader ICLR 2023 random/stratified standard slice.
   - Missing for oral-level confidence: independent second-annotator coverage and/or another non-ICLR random/stratified venue slice.
   - Current status should remain: main-track plausible, oral uncertain, best-paper not ready.

## Major Findings

1. **Visualization depth improved but the narrative anchor is still incomplete.**
   - Figure 1 and transfer diagnostics are strong, but the construction/governance pipeline must remain visible in the main story, not only as a side artifact.
   - Action: keep the pipeline overview figure in the paper body and tie each claim to one figure/table anchor in Results.

2. **Experiment breadth is still narrow for top-tier oral expectations.**
   - Strong: in-domain ICLR 2024, two standard-labeled active frontiers (ICLR 2025 expanded80, NeurIPS 2024 limit100), and one standard-labeled ICLR 2023 random/stratified slice.
   - Weak: the random/stratified slice is still ICLR-family and single-user; it does not provide IAA or full cross-venue natural-prevalence evidence.
   - Progress: ICLR 2023 random80 random/stratified slice is now promoted and paper-facing with standard transfer/taxonomy assets.
   - Action: decide whether the next evidence sprint should be second annotator coverage or a non-ICLR random/stratified slice.

3. **Reference coverage is structurally thin for this claim scope.**
   - Citation audit passes mechanically, but breadth is still limited (`26` BibTeX entries for a paper spanning peer review, revision tracking, evidence QA, and reliability).
   - Action: expand related-work coverage with additional primary sources on revision-aware evaluation and temporal evidence updates.

4. **Transfer claims need uncertainty reporting beyond one in-domain split.**
   - In-domain significance is present, but transfer uncertainty must be explicitly quantified.
   - Action: add cross-split significance/CI assets for ICLR 2024, expanded80, and NeurIPS 2024 (now integrated into appendix assets).

## Minor Findings

1. Several sections still read as artifact-heavy before delivering the main scientific punchline; trim operational detail in the main text where possible.
2. Table labels and caveat text are accurate but repeated; reduce redundancy to free space for stronger qualitative examples.
3. Some layout quality warnings should be cleaned before final submission pass (box warnings and line-break polish during final camera-ready shaping).

## Recommendation

Proceed with sprint mode, but keep claim discipline strict:

1. Do not claim broad venue/year prevalence yet.
2. Prioritize one broader labeled slice plus targeted reference expansion.
3. Keep uncertainty and provenance visible in paper-facing tables/appendix.
