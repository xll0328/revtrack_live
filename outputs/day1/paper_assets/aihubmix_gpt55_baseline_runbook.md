# AIHubMix GPT-5.5 Baseline Runbook

Date: 2026-04-27

## Security Boundary

Do not hard-code API keys in scripts, commands, logs, notebooks, or result files.

The runner reads the key from `AIHUBMIX_API_KEY` or from a local `--api-key-file`.

If a key has been pasted into chat or logs, rotate it before running the paper-facing baseline.

Recommended local secret path:

```bash
mkdir -p .secrets
chmod 700 .secrets
printf '%s' 'YOUR_ROTATED_KEY' > .secrets/aihubmix.secret
chmod 600 .secrets/aihubmix.secret
```

`.secrets/` is ignored by `.gitignore`.

The Python snippet from AIHubMix:

```python
client = openai.OpenAI(api_key="<AIHUBMIX_API_KEY>", base_url="https://aihubmix.com/v1")
```

is exactly what `scripts/run_aihubmix_prompted_llm_baseline.py` does internally. The only difference is that the runner reads the key from a local secret file or environment variable instead of hard-coding it in source.

## Runner

Script: `scripts/run_aihubmix_prompted_llm_baseline.py`

Connectivity check: `scripts/check_aihubmix_connection.py`

Defaults:

- `base_url`: `https://aihubmix.com/v1`
- `model`: `gpt-5.5`
- API key env var: `AIHUBMIX_API_KEY`
- optional key file: `--api-key-file .secrets/aihubmix.secret`
- output mode: incremental JSONL
- resume mode: enabled

## Recommended Sequence

### 0. Connectivity Check

```bash
python scripts/check_aihubmix_connection.py \
  --model gpt-5.5 \
  --api-key-file .secrets/aihubmix.secret
```

Expected output: JSON with `"status": "ok"` and a short response preview.

### 1. Smoke Run: ICLR 2025 Expanded80, 8 Rows

```bash
python scripts/run_aihubmix_prompted_llm_baseline.py \
  --prompt-packet outputs/day1/prompted_llm_baselines/iclr2025_expanded80_prompt_packet.jsonl \
  --output-jsonl outputs/day1/prompted_llm_baselines/iclr2025_expanded80_gpt55_smoke_outputs.jsonl \
  --model gpt-5.5 \
  --api-key-file .secrets/aihubmix.secret \
  --limit 8 \
  --temperature 0 \
  --max-tokens 512

python scripts/evaluate_prompted_llm_baseline.py \
  --examples data/processed/iclr2025_expanded80_standard_validation_v1.jsonl \
  --llm-outputs outputs/day1/prompted_llm_baselines/iclr2025_expanded80_gpt55_smoke_outputs.jsonl \
  --normalized-predictions outputs/day1/prompted_llm_baselines/iclr2025_expanded80_gpt55_smoke_predictions.jsonl \
  --metrics-json outputs/day1/prompted_llm_baselines/iclr2025_expanded80_gpt55_smoke_metrics.json \
  --details-json outputs/day1/prompted_llm_baselines/iclr2025_expanded80_gpt55_smoke_details.json \
  --audit-json outputs/day1/prompted_llm_baselines/iclr2025_expanded80_gpt55_smoke_audit.json \
  --metrics-md outputs/day1/paper_assets/iclr2025_expanded80_gpt55_smoke_metrics.md \
  --model-key gpt55_smoke \
  --allow-subset
```

Gate: proceed only if invalid outputs are `0` or easy to fix with prompt/schema tightening.

### 2. Full ICLR 2025 Expanded80

```bash
python scripts/run_aihubmix_prompted_llm_baseline.py \
  --prompt-packet outputs/day1/prompted_llm_baselines/iclr2025_expanded80_prompt_packet.jsonl \
  --output-jsonl outputs/day1/prompted_llm_baselines/iclr2025_expanded80_gpt55_outputs.jsonl \
  --model gpt-5.5 \
  --api-key-file .secrets/aihubmix.secret \
  --temperature 0 \
  --max-tokens 512

python scripts/evaluate_prompted_llm_baseline.py \
  --examples data/processed/iclr2025_expanded80_standard_validation_v1.jsonl \
  --llm-outputs outputs/day1/prompted_llm_baselines/iclr2025_expanded80_gpt55_outputs.jsonl \
  --normalized-predictions outputs/day1/prompted_llm_baselines/iclr2025_expanded80_gpt55_predictions.jsonl \
  --metrics-json outputs/day1/prompted_llm_baselines/iclr2025_expanded80_gpt55_metrics.json \
  --details-json outputs/day1/prompted_llm_baselines/iclr2025_expanded80_gpt55_details.json \
  --audit-json outputs/day1/prompted_llm_baselines/iclr2025_expanded80_gpt55_audit.json \
  --metrics-md outputs/day1/paper_assets/iclr2025_expanded80_gpt55_metrics.md \
  --model-key gpt55
```

### 3. Full NeurIPS 2024 Resolved Candidate

Use this as resolved-candidate evidence until canonical promotion is written.

```bash
python scripts/run_aihubmix_prompted_llm_baseline.py \
  --prompt-packet outputs/day1/prompted_llm_baselines/neurips2024_limit100_resolved_candidate_prompt_packet.jsonl \
  --output-jsonl outputs/day1/prompted_llm_baselines/neurips2024_limit100_resolved_candidate_gpt55_outputs.jsonl \
  --model gpt-5.5 \
  --api-key-file .secrets/aihubmix.secret \
  --temperature 0 \
  --max-tokens 512

python scripts/evaluate_prompted_llm_baseline.py \
  --examples data/processed/neurips2024_limit100_resolved_candidate_validation_v1.jsonl \
  --llm-outputs outputs/day1/prompted_llm_baselines/neurips2024_limit100_resolved_candidate_gpt55_outputs.jsonl \
  --normalized-predictions outputs/day1/prompted_llm_baselines/neurips2024_limit100_resolved_candidate_gpt55_predictions.jsonl \
  --metrics-json outputs/day1/prompted_llm_baselines/neurips2024_limit100_resolved_candidate_gpt55_metrics.json \
  --details-json outputs/day1/prompted_llm_baselines/neurips2024_limit100_resolved_candidate_gpt55_details.json \
  --audit-json outputs/day1/prompted_llm_baselines/neurips2024_limit100_resolved_candidate_gpt55_audit.json \
  --metrics-md outputs/day1/paper_assets/neurips2024_limit100_resolved_candidate_gpt55_metrics.md \
  --model-key gpt55_resolved_candidate
```

## Reporting Boundary

- Report only clean-output runs with explicit model name and provider.
- Treat NeurIPS numbers as resolved-candidate evidence until canonical promotion is written.
- Do not call these results human validation or IAA.
- If invalid outputs occur, report invalid-output rate and rerun only after prompt/schema changes are documented.
