# Oral Casebook

Representative failure cases for oral Q&A and rebuttal discussion.

| # | Failure mode | Split | Model | Support | Gold | Predictions | Issue |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| 1 | stale_criticism | iclr2024_signoff | - | - | fixed | tfidf=partially_fixed, structured=partially_fixed | `w7P92BEsb2__r01` |
| 2 | accuracy_trap_fixed_cases | iclr2025_repro_v2 | tfidf | 5 | fixed | tfidf=partially_fixed, structured=partially_fixed | `w7P92BEsb2__r01` |
| 3 | over_crediting_unresolved | iclr2025_expanded80_standard | structured | 66 | unresolved | tfidf=partially_fixed, structured=fixed | `1qP3lsatCR__r01` |
| 4 | fixed_under_recovery | iclr2025_expanded80_standard | tfidf | 4 | fixed | tfidf=partially_fixed, structured=fixed | `Kak2ZH5Itp__r02` |
| 5 | regression_blindness | iclr2025_expanded80_standard | tfidf | 6 | regressed | tfidf=partially_fixed, structured=fixed | `VNMJfBBUd5__r04` |
| 6 | partial_vs_fixed_boundary | iclr2025_expanded80_standard | issue_ledger | 4 | partially_fixed | tfidf=partially_fixed, structured=partially_fixed | `75PhjtbBdr__r04` |
| 7 | evidence_quality_fix | iclr2024_signoff | - | - | fixed | n/a | `kmn0BhQk7p__r04` |
| 8 | over_crediting_long_response | iclr2024_signoff | - | - | unresolved | n/a | `My7lkRNnL9__r01` |
| 9 | partial_fix_ambiguity | iclr2024_signoff | - | - | partially_fixed | n/a | `9k0krNzvlV__r02` |

## Case 1: stale_criticism

- issue: `w7P92BEsb2__r01`
- split/model: `iclr2024_signoff` / `-`
- claim: A static critique can preserve an old concern even after revision evidence directly fixes it.
- model risk: predicts partially_fixed or unresolved because the original concern remains semantically plausible
- why it matters: This example separates revision-aware judgment from static semantic plausibility.
- review concern excerpt: [weaknesses] One point that needs to be address in the paper is that of computational cost. After all, one of the motivations of using PINNs in parallel is computational efficiency, so it would be good to have a comparison in terms of same. [questions] See...
- revision evidence excerpt: Figure 6 and Lines 510-530 compare errors and computational costs

## Case 2: accuracy_trap_fixed_cases

- issue: `w7P92BEsb2__r01`
- split/model: `iclr2025_repro_v2` / `tfidf`
- claim: A majority-like model can score well by predicting partially_fixed while missing fixed cases.
- model risk: high accuracy, low fixed-label recovery
- why it matters: This is the core reason the paper reports macro-F1 and per-label recovery.
- review concern excerpt: [weaknesses] One point that needs to be address in the paper is that of computational cost. After all, one of the motivations of using PINNs in parallel is computational efficiency, so it would be good to have a comparison in terms of same. [questions] See...
- revision evidence excerpt: Figure 6 and Lines 510-530 compare errors and computational costs

## Case 3: over_crediting_unresolved

- issue: `1qP3lsatCR__r01`
- split/model: `iclr2025_expanded80_standard` / `structured`
- claim: Transfer models often treat a response or local edit as resolution even when the original concern remains open. Observed 66 times for Structured on expanded80.
- model risk: over-credits unresolved concerns as fixed or partially fixed
- why it matters: This is the practical stale-assistant failure: the model would stop tracking an unresolved concern.
- review concern excerpt: [weaknesses] * **Notations and problem formulation hard to follow:** Many notations are introduced, making the reading of section 3 a bit cumbersome. Maybe putting some of the mathematical details and ILP formulations in Appendix could help lighten the...
- revision evidence excerpt: Thank you for your acknowledgment and insightful comments. Your feedback is extremely helpful, and we are committed to addressing each question you have raised. **** ### Weakness 1: Notations and problem formulation hard to follow. To address the reviewer's...

## Case 4: fixed_under_recovery

- issue: `Kak2ZH5Itp__r02`
- split/model: `iclr2025_expanded80_standard` / `tfidf`
- claim: Semantic baselines can miss direct fixes when the old criticism remains lexically salient. Observed 4 times for TF-IDF on expanded80.
- model risk: keeps a fixed concern alive as partially fixed or unresolved
- why it matters: This motivates fixed-case F1 rather than accuracy-only reporting.
- review concern excerpt: [weaknesses] 1. Several factors in asserting the assumptions could not be carefully controlled. Table 1 line 180: GPT4-as-a-judge is used to confirm the quality of responses in different languages, however, there is no guarantee that the scores for...
- revision evidence excerpt: Thanks for your insightful questions and we believe they hold significant value for our work. We try to resolve your concerns below. > W1: The quality of GPT-as-a-judge in different languages Please refer to the `General Response about GPT-4 on...

## Case 5: regression_blindness

- issue: `VNMJfBBUd5__r04`
- split/model: `iclr2025_expanded80_standard` / `tfidf`
- claim: Regression cases are rare but high-risk: several baselines smooth them into non-regression labels. Observed 6 times for TF-IDF on expanded80.
- model risk: misses cases where the revision introduces or worsens a problem
- why it matters: This justifies keeping the regressed label while avoiding strong regression-performance claims.
- review concern excerpt: [weaknesses] (1) The use of $arccos(\cdot)$ in Eq.(2) is ambigious as $cos\(\cdot\)$ is used in Eq.(3) and Eq.(4) as well. (2) The calculation of GCD across all model layers is not clearly formulated for each sample. (3) The influence of the clean sample by...
- revision evidence excerpt: Dear Reviewer AHKK, We are truly thankful for the reviewer’s positive feedback. **Q1. The reason for using $\arccos$ in Eq.(2), while employing $\cos$ in Eq.(3) and Eq.(4).** **R1:** Thank you! We explain the reason for the definition of Gradient Circular...

## Case 6: partial_vs_fixed_boundary

- issue: `75PhjtbBdr__r04`
- split/model: `iclr2025_expanded80_standard` / `issue_ledger`
- claim: Even the best expanded80 model sometimes upgrades partial evidence into a full fix. Observed 4 times for Issue ledger on expanded80.
- model risk: collapses partial resolution into fixed
- why it matters: This is the central label-boundary risk for benchmark reliability.
- review concern excerpt: [weaknesses] 1) In your paper, the choice of top-k seems to be very important, so how do you determine the setting of k? You said "we retrieve a paired caption with derived textual labels for each view, which then serves as weak label set of size k for the...
- revision evidence excerpt: Dear Reviewers, Area Chairs, Program Chairs, and Senior Area Chairs, We address the reviewers' concerns with the following updates and improvements, and submit an improved manuscript highlighted in red: 1. **Paired caption retrieval and label binding**:...

## Case 7: evidence_quality_fix

- issue: `kmn0BhQk7p__r04`
- split/model: `iclr2024_signoff` / `-`
- claim: Concrete added evidence, such as cross-labeling, can fully resolve a reviewer concern.
- model risk: misses concise factual fixes when the surrounding review is long
- why it matters: This example separates revision-aware judgment from static semantic plausibility.
- review concern excerpt: [weaknesses] - Labelling procedure for obtaining ground truths for the dataset should get multiple labels for each profile to make the results statistically significant. For instance , the following example is hard to label as the moon landing took place in...
- revision evidence excerpt: Since then we have cross-labeled ~25% of the dataset

## Case 8: over_crediting_long_response

- issue: `My7lkRNnL9__r01`
- split/model: `iclr2024_signoff` / `-`
- claim: A long response can acknowledge a limitation without resolving it.
- model risk: predicts fixed because the response is detailed and polite
- why it matters: This example separates revision-aware judgment from static semantic plausibility.
- review concern excerpt: [weaknesses] - The theoretical analysis focuses only on shallow 2-layer networks, and I’m uncertain that the Adaptive Feedback rule can be easily extended to analyze deeper networks, as the error signal has to pass through multiple hidden layers either...
- revision evidence excerpt: Authors acknowledge the theory remains limited to one-hidden-layer networks and only add discussion plus extra empirical clarifications.

## Case 9: partial_fix_ambiguity

- issue: `9k0krNzvlV__r02`
- split/model: `iclr2024_signoff` / `-`
- claim: Some revisions add experiments and framing but leave part of the value proposition unresolved.
- model risk: collapses partially_fixed into fixed
- why it matters: This example separates revision-aware judgment from static semantic plausibility.
- review concern excerpt: [weaknesses] **Contribution to Open Model Watermarking**. As the authors show, open-model watermarking using distillation is not robust against fine-tuning. I am unclear about the contribution of the authors to open model watermarking. No prior work has...
- revision evidence excerpt: Added sample-efficiency plots, experiments with multiple keys, and clearer framing of the open-model watermarking contribution.
