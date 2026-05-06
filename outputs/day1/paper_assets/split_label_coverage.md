# Split Label Coverage

This panel summarizes label availability for each paper-facing split.
Missing labels indicate where four-way interpretation should be treated as bounded.

| Split | Rows | Design | fixed | partially_fixed | unresolved | regressed | Missing labels |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| ICLR 2024 clean dev v7 | 148 | in_domain_standard | 50 | 86 | 11 | 1 | - |
| ICLR 2025 repro v2 | 21 | stress_set | 5 | 16 | 0 | 0 | unresolved,regressed |
| ICLR 2025 expanded80 | 80 | active_frontier | 4 | 4 | 66 | 6 | - |
| NeurIPS 2024 limit100 | 80 | active_frontier | 0 | 44 | 36 | 0 | fixed,regressed |
| ICLR 2023 random80 | 80 | random_stratified | 5 | 49 | 26 | 0 | regressed |

Boundary notes:
- Active-frontier splits are disagreement-harvested hard subsets, not natural prevalence samples.
- Missing-label splits should not be interpreted as full four-way coverage for prevalence claims.
