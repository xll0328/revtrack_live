# NeurIPS 2024 Limit100 Frontier Summary

This is a cross-venue feasibility and active-frontier summary. It is not a human-validation result yet.

## Extraction Repair

The NeurIPS 2024 extraction was repaired on 2026-04-27. `Author_Rebuttal` and `Official_Review*/-/Rebuttal` notes signed by authors are now treated as author responses before checking for official reviews, and response text is read from both `comment` and `rebuttal` fields. The previous 783-row pool mixed author rebuttals into review concerns and has been retired.

## Candidate Pool

| field | value |
| --- | ---: |
| venue | NeurIPS.cc/2024/Conference |
| sampled submissions | 100 |
| issue candidates | 393 |
| complete rows | 393 |
| complete-field rate | 1.000 |
| duplicate issue IDs | 0 |
| candidate gate | pass |

## Prediction Stack

| model | prediction file | label distribution |
| --- | --- | --- |
| TF-IDF | `outputs/day1/neurips2024_limit100_candidates_tfidf_train_iclr2024_v8_transfer_predictions.jsonl` | fixed=8; partially_fixed=385 |
| ModernBERT | `outputs/day1/neurips2024_limit100_candidates_modernbert_train_iclr2024_v8_transfer_predictions.jsonl` | fixed=181; partially_fixed=179; unresolved=32; regressed=1 |
| MPNet | `outputs/day1/neurips2024_limit100_candidates_mpnet_train_iclr2024_v8_transfer_predictions.jsonl` | fixed=129; partially_fixed=207; unresolved=47; regressed=10 |
| Issue ledger | `outputs/day1/neurips2024_limit100_candidates_issue_ledger_train_iclr2024_v8_transfer_predictions.jsonl` | fixed=84; partially_fixed=163; unresolved=143; regressed=3 |
| Structured | `outputs/day1/neurips2024_limit100_candidates_structured_train_iclr2024_v8_transfer_predictions.jsonl` | fixed=97; partially_fixed=284; unresolved=12 |

Full-stack candidate audit: `outputs/day1/neurips2024_limit100_candidate_pool_quality_gate_full_stack.json`.

- Comparable rows: 393
- Disagreement rows: 316
- High-disagreement rows: 93
- Errors: 0
- Warnings: 0

## Frontier Packet

| artifact | path |
| --- | --- |
| Multi-model frontier sheet | `experiments/day1/neurips2024_limit100_multi_frontier_structured_prefilled.tsv` |
| Multi-model HTML packet | `outputs/day1/neurips2024_limit100_multi_frontier_structured_packet.html` |
| Blind validation sheet | `experiments/day1/neurips2024_limit100_human_validation_v1_blind.tsv` |
| Blind validation HTML packet | `outputs/day1/neurips2024_limit100_human_validation_v1_blind_packet.html` |
| Hidden key sheet | `experiments/day1/neurips2024_limit100_human_validation_v1_key.tsv` |
| Audit sheet | `experiments/day1/neurips2024_limit100_human_validation_v1_audit.tsv` |
| Packet audit | `outputs/day1/neurips2024_limit100_human_validation_v1_packet_audit.json` |

The blind/key/audit packet has 80 rows and passes packet audit with 0 errors and 0 warnings.

Hidden assistant distribution for the active frontier:

- unresolved: 76
- regressed: 4

This distribution is intentionally frontier-biased because the packet targets model disagreement and suspected over-crediting/regression cases. It must not be interpreted as NeurIPS natural label prevalence.

## Resolved Candidate

The raw assistant draft has been converted into a conservative resolved-label candidate for user confirmation.

| artifact | path |
| --- | --- |
| Resolved adjudication TSV | `experiments/day1/neurips2024_limit100_resolved_adjudication_v1.tsv` |
| Candidate blind sheet | `experiments/day1/neurips2024_limit100_standard_label_candidate_blind.tsv` |
| Resolution manifest | `outputs/day1/neurips2024_limit100_resolution_manifest.json` |
| Resolution summary | `outputs/day1/paper_assets/neurips2024_limit100_resolution_summary.md` |
| Promotion dry run | `outputs/day1/neurips2024_limit100_standard_validation_promotion_dry_run.json` |
| Candidate transfer metrics | `outputs/day1/paper_assets/neurips2024_limit100_resolved_candidate_transfer_metrics.md` |
| Candidate failure taxonomy | `outputs/day1/paper_assets/neurips2024_limit100_resolved_candidate_failure_taxonomy.md` |

Resolved candidate distribution:

- partially_fixed: 44
- unresolved: 36

The four provisional `regressed` rows are downgraded to `partially_fixed` because no strict same-axis negative-change evidence is present. This resolved candidate is not independent human validation until user-confirmed promotion.

Promotion dry run: `ok`; promotable rows: 80; promoted canonical rows: 0.

## Safe Current Use

- Use this as evidence that NeurIPS 2024 is a feasible cross-venue source after schema repair.
- Use this as the active-frontier packet for the next standard-validation pass.
- Use the resolved candidate as the current user-confirmation sheet.
- Use the full-stack disagreement counts to motivate the next scaling sprint.

## Do Not Claim Yet

- NeurIPS independent human-validation performance.
- Cross-venue benchmark results before user-confirmed promotion.
- Natural NeurIPS label prevalence.
- Independent inter-annotator agreement.
