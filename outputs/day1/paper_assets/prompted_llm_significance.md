# Prompted LLM Significance vs Majority

Paired stratified bootstrap on macro-F1 deltas (method - majority).

| Dataset | Method | n | Macro-F1 | Delta vs Majority | 95% CI (Delta) | p(Delta<=0) | Status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| ICLR24 | Majority | 148 | 0.184 | 0.000 | [0.000, 0.000] | 1.000 | reference |
| ICLR24 | GPT-5.5 (v2) | 148 | 0.350 | 0.167 | [0.093, 0.250] | 0.000 | above_majority |
| ICLR24 | GPT-4.1-mini | 148 | 0.347 | 0.164 | [0.091, 0.245] | 0.000 | above_majority |
| ICLR24 | Qwen2.5-72B | 148 | 0.334 | 0.150 | [0.082, 0.227] | 0.000 | above_majority |
| ICLR24 | Vote-3 (top) | 148 | 0.352 | 0.168 | [0.096, 0.251] | 0.000 | above_majority |
| ICLR24 | Vote-3 (+U+F-cal) | 148 | 0.350 | 0.167 | [0.097, 0.244] | 0.000 | above_majority |
| ICLR25 | Majority | 80 | 0.226 | 0.000 | [0.000, 0.000] | 1.000 | reference |
| ICLR25 | GPT-5.5 (v2) | 80 | 0.081 | -0.145 | [-0.200, -0.068] | 1.000 | overlap_or_below |
| ICLR25 | GPT-4.1-mini | 80 | 0.066 | -0.160 | [-0.176, -0.136] | 1.000 | overlap_or_below |
| ICLR25 | Qwen2.5-72B | 80 | 0.072 | -0.154 | [-0.192, -0.113] | 1.000 | overlap_or_below |
| ICLR25 | Vote-3 (top) | 80 | 0.071 | -0.155 | [-0.194, -0.115] | 1.000 | overlap_or_below |
| ICLR25 | Vote-3 (+U+F-cal) | 80 | 0.094 | -0.132 | [-0.198, -0.047] | 0.999 | overlap_or_below |
| NeurIPS24 | Majority | 80 | 0.177 | 0.000 | [0.000, 0.000] | 1.000 | reference |
| NeurIPS24 | GPT-5.5 (v2) | 80 | 0.171 | -0.006 | [-0.019, 0.004] | 0.862 | overlap_or_below |
| NeurIPS24 | GPT-4.1-mini | 80 | 0.181 | 0.003 | [-0.012, 0.018] | 0.319 | overlap_or_below |
| NeurIPS24 | Qwen2.5-72B | 80 | 0.165 | -0.012 | [-0.032, 0.006] | 0.910 | overlap_or_below |
| NeurIPS24 | Vote-3 (top) | 80 | 0.179 | 0.001 | [-0.014, 0.014] | 0.444 | overlap_or_below |
| NeurIPS24 | Vote-3 (+U+F-cal) | 80 | 0.167 | -0.011 | [-0.024, 0.001] | 0.966 | overlap_or_below |

Interpretation boundary: this is split-level sample uncertainty only; it does not include annotator uncertainty or API stochasticity.
