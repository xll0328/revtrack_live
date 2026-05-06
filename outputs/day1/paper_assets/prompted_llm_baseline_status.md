# Prompted-LLM Baseline Status

Date: 2026-05-06

## Implemented

- Prompt packet exporter: `scripts/export_prompted_llm_baseline_packet.py`
- Local chat-model runner: `scripts/run_local_prompted_llm_baseline.py`
- AIHubMix/OpenAI-compatible runner: `scripts/run_aihubmix_prompted_llm_baseline.py`
- Output evaluator/auditor: `scripts/evaluate_prompted_llm_baseline.py`

Prompt packets:

- `outputs/day1/prompted_llm_baselines/iclr2024_clean_dev_v7_prompt_packet.jsonl`
- `outputs/day1/prompted_llm_baselines/iclr2025_expanded80_prompt_packet.jsonl`
- `outputs/day1/prompted_llm_baselines/neurips2024_limit100_resolved_candidate_prompt_packet.jsonl`

Prompt leakage check: prompt messages contain `0` `gold_label` string hits across all three packets.

## Local Smoke Result

Model: `Qwen2.5-1.5B-Instruct`

Dataset: `ICLR 2025 expanded80 standard validation`

| rows | accuracy | macro-F1 | fixed F1 | partial F1 | unresolved F1 | regressed F1 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 80 | 0.113 | 0.062 | 0.114 | 0.000 | 0.135 | 0.000 |

Prediction distribution:

- `fixed`: 66
- `unresolved`: 8
- `invalid`: 6

Audit status: `error` because 6 rows did not produce valid parseable labels/evidence. This is a smoke/sanity baseline, not a final strong LLM result.

Key pattern: the local prompted model strongly over-credits unresolved and regressed concerns as `fixed`, matching the paper's central over-crediting failure mode.

Artifacts:

- raw outputs: `outputs/day1/prompted_llm_baselines/iclr2025_expanded80_qwen25_1p5b_outputs.jsonl`
- normalized predictions: `outputs/day1/prompted_llm_baselines/iclr2025_expanded80_qwen25_1p5b_predictions.jsonl`
- metrics: `outputs/day1/paper_assets/iclr2025_expanded80_qwen25_1p5b_metrics.md`
- audit: `outputs/day1/prompted_llm_baselines/iclr2025_expanded80_qwen25_1p5b_audit.json`

## Current Paper-Facing Summary (Refreshed)

The prompted-LMM ensemble assets and bootstrap intervals were regenerated on `2026-05-06`:

- `outputs/day1/prompted_llm_baselines/prompted_llm_ensemble_summary.json`
- `outputs/day1/prompted_llm_baselines/prompted_llm_bootstrap_intervals.md`
- `paper/tables/prompted_llm_ensemble.tex`
- `paper/tables/prompted_llm_bootstrap_intervals.tex`
- `paper/figures/figure3_prompted_llm_transfer.pdf`
- `paper/figures/figure4_prompted_llm_label_recall.pdf`
- `paper/figures/figure5_expanded80_confusion.pdf`
- `paper/figures/figure6_expanded80_error_stack.pdf`

Selected macro-F1 snapshot:

| split | Majority | GPT-5.5(v2) | Vote-3(U+F) | take-away |
| --- | ---: | ---: | ---: | --- |
| ICLR24 | 0.184 | 0.350 | 0.350 | in-domain prompted baselines are competitive |
| ICLR25 expanded80 | 0.226 | 0.081 | 0.094 | all prompted rows remain below majority |
| NeurIPS24 limit100 | 0.177 | 0.171 | 0.167 | near-majority, no robust transfer lift |

Bootstrap risk summary:

- ICLR24 prompted rows are above majority.
- ICLR25 prompted rows are below majority.
- NeurIPS24 prompted rows overlap majority.

This remains a reliability-stress result, not solved transfer performance.

## GPT-5.5 Runbook / Rerun Status

AIHubMix GPT-5.5 runbook: `outputs/day1/paper_assets/aihubmix_gpt55_baseline_runbook.md`

Status: runner and tests are ready. Historical GPT-5.5(v2) outputs are available in `outputs/day1/prompted_llm_baselines/`, but this shell still does not expose `AIHUBMIX_API_KEY`, so no fresh rerun has been launched in this session.

## Next Step

Primary: rerun one strong prompted API baseline with the current packet/version locks and re-export all prompted assets.  
Fallback: keep existing prompted evidence as bounded transfer-stress analysis and avoid stronger generalization claims.
