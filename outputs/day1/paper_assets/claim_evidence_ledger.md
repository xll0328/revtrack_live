# Claim Evidence Ledger

This ledger separates paper-ready claims from stress evidence and not-ready claims.

## C1_in_domain_structured_advantage (ready)

Claim: On the hardened ICLR 2024 clean-dev benchmark, structured revision evidence improves macro-F1 over semantic baselines.

Support: clean dev v7 has 148 rows; Structured accuracy 0.682, macro-F1 0.704; MPNet accuracy 0.581, macro-F1 0.389; Structured without overrides macro-F1 0.424; standard validation covers 301/301 active audit rows after ICLR 2023 random80 promotion.

Risk/counterevidence: The strongest positive result is still in-domain ICLR 2024; the scaled ICLR 2025 frontier is active-sampled and label-skewed, so it supports hardened cross-year frontier claims rather than broad venue-level prevalence estimates.

Next step: Use expanded80 as a hardened cross-year frontier and add more venues/years before broad generalization claims.

Artifacts: `clean_dev_metrics.csv; null_baseline_comparison.csv; iclr2024_human_validation_v1_pending_metrics.json`

## C2_accuracy_trap (ready)

Claim: Accuracy alone is misleading for revision-status tracking under label skew.

Support: ICLR 2024 majority baseline accuracy 0.581, macro-F1 0.184; ICLR 2025 majority baseline accuracy 0.762, macro-F1 0.216; ICLR 2025 TF-IDF exactly matches the majority baseline with fixed F1 0.000.

Risk/counterevidence: The ICLR 2025 evidence is from a small repro stress sample, so use it as an illustrative failure mode, not a benchmark estimate.

Next step: Keep majority/null baselines in every new venue/year table and require label-level recovery in claims.

Artifacts: `null_baseline_comparison.csv; iclr2025_v2_error_profile.csv`

## C3_iclr2024_pool_quality (ready)

Claim: The current ICLR 2024 candidate pool is large enough for local in-domain experiments and has exhausted active disagreement sampling after train v8.

Support: candidate-pool audit ok=True; rows 230; complete rate 1.000; multi-model disagreement rows 82; residual frontier after v8 0.

Risk/counterevidence: This is an in-domain ICLR 2024 claim only; it does not establish cross-year or cross-venue generalization.

Next step: Freeze exact dataset split/version before paper submission and include audit report in reproducibility package.

Artifacts: `iclr2024_candidate_pool_quality_gate.json; frontier_status.csv; transfer_label_distribution.csv`

## C4_cross_year_brittleness (ready)

Claim: Cross-year transfer to ICLR 2025 is brittle and exposes weak fixed-case recovery on both a stress set and a hardened expanded frontier.

Support: ICLR 2025 repro v2 rows 21; Structured accuracy 0.571, macro-F1 0.227, fixed F1 0.200; best macro-F1 among current repro transfer models is ModernBERT at 0.238. Expanded80 standard rows 80; best expanded80 model issue_ledger reaches accuracy 0.850, macro-F1 0.469, fixed F1 0.429.

Risk/counterevidence: Expanded80 is a standard single-user active frontier and should not be used as an estimate of natural label prevalence.

Next step: Add a second annotator only for IAA claims; add another venue/year before broad generalization claims.

Artifacts: `iclr2025_v2_transfer_metrics.csv; iclr2025_v2_error_profile.csv; iclr2025_expanded80_standard_transfer_metrics.csv; iclr2025_expanded80_candidate_pool_quality_gate.json`

## C5_human_validation_complete (ready)

Claim: The benchmark has complete standard human-validation labels with reproducible packet, leakage, and key-alignment audits.

Support: packet audits pass for ICLR 2024 v1, ICLR 2025 v1, ICLR 2025 v2, ICLR 2025 expanded80 v1, NeurIPS 2024 limit100 v1, and ICLR 2023 random80 v1: True; human-validation labels cover 301/301 active audit rows; signoff promotion status ok with 61 promoted rows; expanded80 promotion status ok with 80 promoted rows; NeurIPS 2024 promotion status standard_single_user_confirmed_2026_04_28 with 80 promoted rows; ICLR 2023 random80 promotion status ok with 80 promoted rows.

Risk/counterevidence: This validates the current standard labels; a separate second-annotator pass would be needed only for inter-annotator reliability claims.

Next step: Use these labels as the paper's current human validation standard and reserve effort for scaling transfer evidence.

Artifacts: `audit_human_validation_packet.py; iclr2024_human_validation_v1_pending_metrics.json; iclr2025_repro_human_validation_v2_pending_metrics.json; iclr2025_expanded80_human_validation_v1_standard_metrics.json; iclr2023_limit80_random80_human_validation_v1_standard_metrics.json; ai_signoff_human_validation_promotion.json; neurips2024_limit100_standard_validation_promotion.json; iclr2023_limit80_random80_standard_validation_promotion.json`

## C7_prompted_llm_transfer_stress (ready)

Claim: Prompted LLMs and vote ensembles are competitive in-domain but remain brittle under cross-year and cross-venue transfer.

Support: ICLR 2024 prompted baselines reach up to 0.350-0.352 macro-F1, while ICLR 2025 expanded80 remains below the 0.226 majority reference: the strongest single prompted model reaches 0.161 and the strongest calibrated vote reaches 0.094. On the user-confirmed NeurIPS 2024 standard single-user active frontier, the best prompted row is 0.181 macro-F1, near the 0.177 majority reference.

Risk/counterevidence: Prompted results depend on API model aliases and prompt formatting. NeurIPS 2024 is user-confirmed single-pass standard validation, not independent IAA, and bootstrap intervals capture sample instability only, not annotator uncertainty.

Next step: Use these results as bounded reliability evidence; add targeted prompt/calibration ablations and a second annotator before broader LLM-generalization or IAA claims.

Artifacts: `prompted_llm_ensemble_summary.json; prompted_llm_bootstrap_intervals.md; postprocess_rule_search.json`

## C6_publishable_cross_year_benchmark (ready)

Claim: A scaled ICLR 2025 cross-year frontier has user-confirmed standard labels and transfer metrics.

Support: Expanded ICLR 2025 pool quality gate ok=True; rows 322; complete rate 0.963; multi-model disagreement rows 244. Standard validation covers 80/80 rows with label-evidence audit ok=True; best model issue_ledger macro-F1 0.469.

Risk/counterevidence: This is a hardened active-sampled frontier, not a natural-prevalence estimate for all ICLR 2025 issues.

Next step: Add second annotator coverage if claiming IAA; otherwise use as hardened cross-year frontier evidence.

Artifacts: `iclr2025_expanded80_candidate_pool_quality_gate.json; iclr2025_expanded80_human_validation_v1_standard_metrics.json; iclr2025_expanded80_standard_transfer_metrics.csv; docs/cross_venue_plan.md`

## C8_neurips_cross_venue_frontier (ready)

Claim: A user-confirmed NeurIPS 2024 standard single-user active frontier adds a second venue axis for transfer brittleness analysis.

Support: NeurIPS 2024 limit100 standard validation has 80 user-confirmed rows with partial=44 and unresolved=36. The candidate pool has 393 complete rows and 316 full-stack disagreement rows. The best transferred model is MPNet with accuracy 0.550, macro-F1 0.348, partial F1 0.516, and unresolved F1 0.875.

Risk/counterevidence: The NeurIPS frontier is a disagreement-focused standard single-user active frontier; it is not a natural-prevalence sample and not an independent IAA result.

Next step: Add a non-ICLR random/stratified slice and a second annotator before broad venue-level prevalence or IAA claims.

Artifacts: `neurips2024_limit100_standard_validation_manifest.json; neurips2024_limit100_standard_transfer_metrics.csv; neurips2024_limit100_standard_failure_taxonomy.md`

## C9_iclr2023_random_stratified_slice (ready)

Claim: A user-confirmed ICLR 2023 random/stratified standard slice adds broader external-validity evidence beyond disagreement-focused active frontiers.

Support: ICLR 2023 random80 standard validation covers 80/80 rows with labels fixed=5, partially_fixed=49, unresolved=26. Label-evidence audit ok=True; best transfer row issue_ledger has accuracy 1.000 and macro-F1 0.750.

Risk/counterevidence: This is standard single-user validation from user-confirmed resolved candidates, not independent IAA. The stratified sample reduces active-frontier bias but should still be reported by measured slice design, not as natural venue prevalence.

Next step: Use this as bounded random/stratified external-validity evidence; add independent second-annotator coverage only if claiming IAA.

Artifacts: `iclr2023_limit80_random80_standard_validation_promotion.json; iclr2023_limit80_random80_human_validation_v1_standard_metrics.json; iclr2023_limit80_random80_standard_transfer_metrics.csv; iclr2023_limit80_random80_standard_failure_taxonomy.md`
