# Prompted LLM bootstrap intervals

Bootstrap confidence intervals are computed over examples from local gold/prediction detail files.
They capture sample instability only; they do not include annotator uncertainty or API stochasticity.

| Dataset | Method | n | Macro-F1 | 95% CI | Risk |
|---|---:|---:|---:|---:|---|
| ICLR24 | Majority | 148 | 0.184 | [0.167, 0.198] | reference |
| ICLR24 | GPT-5.5 | 148 | 0.350 | [0.279, 0.430] | above majority |
| ICLR24 | GPT-4.1-nano | 148 | 0.210 | [0.155, 0.263] | overlaps majority |
| ICLR24 | GPT-4.1-mini | 148 | 0.347 | [0.272, 0.437] | above majority |
| ICLR24 | Vote-3 (U+F) | 148 | 0.350 | [0.282, 0.428] | above majority |
| ICLR25 | Majority | 80 | 0.226 | [0.212, 0.237] | reference |
| ICLR25 | GPT-5.5 | 80 | 0.081 | [0.021, 0.158] | below majority |
| ICLR25 | GPT-4.1-nano | 80 | 0.161 | [0.116, 0.207] | below majority |
| ICLR25 | GPT-4.1-mini | 80 | 0.066 | [0.017, 0.114] | below majority |
| ICLR25 | Vote-3 (U+F) | 80 | 0.094 | [0.026, 0.184] | below majority |
| NeurIPS24 | Majority | 80 | 0.177 | [0.152, 0.199] | reference |
| NeurIPS24 | GPT-5.5 | 80 | 0.171 | [0.144, 0.193] | overlaps majority |
| NeurIPS24 | GPT-4.1-nano | 80 | 0.126 | [0.075, 0.179] | overlaps majority |
| NeurIPS24 | GPT-4.1-mini | 80 | 0.181 | [0.154, 0.203] | overlaps majority |
| NeurIPS24 | Vote-3 (U+F) | 80 | 0.167 | [0.141, 0.189] | overlaps majority |

## Interpretation

- Cross-year prompted transfer remains claim-risky: the ICLR25 selected LLM/vote rows are below or overlap the majority reference.
- NeurIPS24 intervals are useful bounded transfer evidence on a user-confirmed single-pass active frontier.
- These intervals support a reliability/benchmark framing, not a solved-system framing.
