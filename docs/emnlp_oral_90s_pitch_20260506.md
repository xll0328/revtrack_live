# EMNLP Oral 90s Pitch (2026-05-06)

## 90-Second Script

RevTrack asks a temporal question that static review benchmarks miss:
after authors revise a paper, can a model correctly update whether each original concern is fixed, partially fixed, unresolved, or regressed?

Our key result is that structured revision evidence materially improves in-domain issue tracking:
on ICLR24 clean-dev, structured reaches macro-F1 0.704 versus 0.389 for the strongest semantic baseline.

But transfer is brittle.
On ICLR25 repro, TF-IDF matches majority accuracy at 0.762 while fixed F1 is 0.000, which shows an accuracy trap.
On the expanded ICLR25 active frontier, best macro-F1 is 0.469, and unresolved recovery remains weak for several methods.
On NeurIPS24 frontier, best macro-F1 is 0.348 and prompted systems remain near majority.

So the takeaway is not model SOTA.
The takeaway is that scientific assistants need revision-aware evaluation and issue-ledger reasoning, otherwise they repeat stale criticism or over-credit unresolved responses.

For reliability, we also completed a bounded mini60 second-pass check with agreement 1.0 and kappa 1.0, while keeping scope boundaries explicit:
this supports bounded reliability evidence, not full prevalence claims.

## Three Evidence Anchors (for Q&A)

1. In-domain gain:
   `structured macro-F1 0.704 vs MPNet 0.389` on ICLR24 clean-dev.
2. Accuracy trap:
   `ICLR25 repro TF-IDF accuracy = majority = 0.762`, but `fixed F1 = 0.000`.
3. Bounded reliability:
   mini60 second-pass `agreement=1.0`, `cohen_kappa=1.0`, `mismatches=0`.

## Boundary Line (must keep consistent)

- Expanded80 and NeurIPS24 are active disagreement frontiers; they support transfer-brittleness analysis, not natural-prevalence claims.
- mini60 IAA is bounded reliability support, not full two-annotator coverage of all packets.
