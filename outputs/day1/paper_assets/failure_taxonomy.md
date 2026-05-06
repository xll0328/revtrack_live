# RevTrack Failure Taxonomy v0

This table is a paper-facing qualitative analysis seed. It turns model errors and label-boundary examples into reusable claims for Figure 1, the task definition, and the results analysis. Expanded80 rows use user-confirmed standard validation, not independent IAA.

| failure mode | split | model | n | issue | gold | TF-IDF | structured | paper use | claim |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- |
| stale_criticism | iclr2024_signoff | - | - | `w7P92BEsb2__r01` | fixed | partially_fixed | partially_fixed | Figure 1 / task motivation | A static critique can preserve an old concern even after revision evidence directly fixes it. |
| over_crediting_long_response | iclr2024_signoff | - | - | `My7lkRNnL9__r01` | unresolved | - | - | Failure taxonomy | A long response can acknowledge a limitation without resolving it. |
| partial_fix_ambiguity | iclr2024_signoff | - | - | `9k0krNzvlV__r02` | partially_fixed | - | - | Label rubric | Some revisions add experiments and framing but leave part of the value proposition unresolved. |
| evidence_quality_fix | iclr2024_signoff | - | - | `kmn0BhQk7p__r04` | fixed | - | - | Dataset validation example | Concrete added evidence, such as cross-labeling, can fully resolve a reviewer concern. |
| accuracy_trap_fixed_cases | iclr2025_repro_v2 | TF-IDF | 5 | `w7P92BEsb2__r01` | fixed | partially_fixed | partially_fixed | Results / accuracy trap | A majority-like model can score well by predicting partially_fixed while missing fixed cases. |
| over_crediting_unresolved | iclr2025_expanded80_standard | Structured | 66 | `1qP3lsatCR__r01` | unresolved | partially_fixed | fixed | Expanded80 failure taxonomy | Transfer models often treat a response or local edit as resolution even when the original concern remains open. Observed 66 times for Structured on expanded80. |
| fixed_under_recovery | iclr2025_expanded80_standard | TF-IDF | 4 | `Kak2ZH5Itp__r02` | fixed | partially_fixed | fixed | Expanded80 failure taxonomy | Semantic baselines can miss direct fixes when the old criticism remains lexically salient. Observed 4 times for TF-IDF on expanded80. |
| regression_blindness | iclr2025_expanded80_standard | TF-IDF | 6 | `VNMJfBBUd5__r04` | regressed | partially_fixed | fixed | Expanded80 failure taxonomy | Regression cases are rare but high-risk: several baselines smooth them into non-regression labels. Observed 6 times for TF-IDF on expanded80. |
| partial_vs_fixed_boundary | iclr2025_expanded80_standard | Issue ledger | 4 | `75PhjtbBdr__r04` | partially_fixed | partially_fixed | partially_fixed | Expanded80 failure taxonomy | Even the best expanded80 model sometimes upgrades partial evidence into a full fix. Observed 4 times for Issue ledger on expanded80. |

## Writing Use

- Use `stale_criticism` for Figure 1 and the opening paragraph.
- Use `over_crediting_long_response` to show why response length is not resolution evidence.
- Use `partial_fix_ambiguity` to justify the four-label rubric.
- Use `accuracy_trap_fixed_cases` to motivate macro-F1 and per-label recovery.
- Use expanded80 aggregate rows for the RQ3/RQ4 bridge: transfer brittleness is mostly over-crediting unresolved issues, fixed under-recovery, and regression blindness.
