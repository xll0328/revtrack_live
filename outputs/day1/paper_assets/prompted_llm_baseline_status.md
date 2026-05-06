# Prompted-LLM Baseline Status

Date: 2026-04-27

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

## GPT-5.5 Runbook

AIHubMix GPT-5.5 runbook: `outputs/day1/paper_assets/aihubmix_gpt55_baseline_runbook.md`

Status: runner and tests are ready. The environment variable `AIHUBMIX_API_KEY` is not set in the current shell, so no GPT-5.5 API run has been executed yet.

## Next Step

Run the same evaluator on a stronger instruction model or API model. The paper-facing claim should use a clean-output strong baseline, while this Qwen2.5-1.5B run remains a local smoke baseline.
