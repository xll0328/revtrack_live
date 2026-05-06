# Figure 1 Running Example Candidates

Goal: pick one example that immediately communicates RevTrack's central idea:

> A review criticism can sound plausible in isolation, but after revision the correct scientific judgment is whether that criticism still holds.

## Recommended Lead Example

### `w7P92BEsb2__r01` — fixed

- Paper: `PIED: Physics-Informed Experimental Design for Inverse Problems`
- Reviewer concern: the paper should address computational cost, since efficiency is part of the motivation.
- Revision evidence: the response points to Figure 6 and Lines 510-530 comparing errors and computational costs.
- Why it works for Figure 1:
  - the concern is short, concrete, and easy to understand
  - the revision evidence is also concrete
  - the correct label is clearly `fixed`
  - it shows why static critique is insufficient: the old criticism still sounds reasonable unless the model checks revision evidence

Figure 1 layout:

| panel | content |
| --- | --- |
| A. Original concern | "What about computational cost?" |
| B. Revision evidence | Figure/line-level addition comparing errors and costs |
| C. Static-assistant failure | repeats or preserves the old criticism |
| D. RevTrack target | `fixed`: the issue was directly addressed |

Best use: Introduction and Figure 1.

## Strong Contrast Example

### `My7lkRNnL9__r01` — unresolved

- Paper: `Forward Learning with Top-Down Feedback: Empirical and Analytical Characterization`
- Reviewer concern: theory is limited to shallow two-layer networks and may not extend to deeper networks.
- Revision evidence: the response adds discussion and empirical clarifications but acknowledges the theory remains limited.
- Why it works:
  - shows the opposite side of the task: a long response does not imply resolution
  - useful for explaining over-crediting failures
  - label is `unresolved`, not merely negative sentiment

Best use: failure taxonomy, not Figure 1 lead.

## Partial-Fix Example

### `9k0krNzvlV__r02` — partially fixed

- Paper: `On the Learnability of Watermarks for Language Models`
- Reviewer concern: contribution to open-model watermarking and sample-efficiency assumptions are unclear.
- Revision evidence: authors add sample-efficiency experiments, multiple-key experiments, and clearer framing.
- Why it works:
  - many real rebuttal outcomes are partial, not binary fixed/unfixed
  - helps justify the four-label design
  - a good example for the label-rubric section

Best use: Task definition and label rubric.

## Backup Fixed Example

### `kmn0BhQk7p__r04` — fixed

- Paper: `Beyond Memorization: Violating Privacy via Inference with Large Language Models`
- Reviewer concern: dataset labels need multiple annotators or cross-labeling for statistical significance.
- Revision evidence: authors cross-label roughly 25% of the dataset.
- Why it works:
  - concise and concrete
  - useful if the PIED example turns out too domain-specific

Best use: short in-text example or appendix.

## Selection Rule

Use `w7P92BEsb2__r01` for Figure 1 unless a visual inspection of the paper/revision packet reveals that the cited cost comparison is hard to show cleanly. Use `My7lkRNnL9__r01` as the paired negative example in the analysis section.
