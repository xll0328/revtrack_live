# Annotation Quickstart

Use this sheet first:

- [iclr2024_priority_sheet_mpnet_prefilled.tsv](/data/sony/emnlp2026_revtrack/experiments/day0/iclr2024_priority_sheet_mpnet_prefilled.tsv)
- Optional browser packet: [iclr2024_priority_packet.html](/data/sony/emnlp2026_revtrack/outputs/day0/iclr2024_priority_packet.html)

## What To Edit

Fill only these columns at first:

- `gold_label`
- `evidence_span`
- `notes`

Leave the suggestion columns untouched so they remain auditable.

## How To Read The Sheet

- `suggested_label`: current best guess from either silver follow-up comments or the strongest local semantic model
- `suggestion_source`: where that guess came from
- `silver_label`: existing noisy label if the issue already has a reviewer follow-up signal
- `heuristic_label`, `tfidf_label`, `modernbert_label`, `mpnet_label`: model-side references
- `top_response_excerpt`: the single most relevant author response chunk
- `aligned_response_excerpt`: concatenated top response evidence
- `revision_summary`: broader revision context

## Practical Rule

When `silver_label` exists, start by checking whether the reviewer follow-up comment still supports it.

When there is no `silver_label`, prioritize disagreements where:

- `heuristic_label` says `fixed` or `regressed`
- `mpnet_label` says `partially_fixed` or `unresolved`

Those are usually the most informative boundaries.

## Fast Labeling Pattern

1. Read `review_excerpt`
2. Read `top_response_excerpt`
3. Skim `revision_summary`
4. Check `suggested_label`
5. Write your final `gold_label`
6. Paste one short supporting quote into `evidence_span`

## Browser Packet

Render the packet if you want a more readable view than raw TSV:

```bash
python scripts/render_annotation_packet.py \
  --sheet experiments/day0/iclr2024_priority_sheet_mpnet_prefilled.tsv \
  --output outputs/day0/iclr2024_priority_packet.html \
  --title "ICLR 2024 priority packet"
```

Best usage pattern:

- open the HTML packet and the TSV side by side
- filter `Only high-conflict rows`
- start with rows that have `silver_label` filled
- write the final label only in the TSV so the source of truth stays simple

## After Labeling

Audit the sheet:

```bash
python scripts/audit_annotation_sheet.py \
  --sheet experiments/day0/iclr2024_priority_sheet_mpnet_prefilled.tsv
```

Build the first clean dev set:

```bash
python scripts/build_labeled_dataset.py \
  --candidates data/processed/iclr2024_issue_candidates.jsonl \
  --sheet experiments/day0/iclr2024_priority_sheet_mpnet_prefilled.tsv \
  --output data/processed/iclr2024_clean_dev_v1.jsonl
```
