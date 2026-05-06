from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_TEXT_FIELDS = ["concern_text", "aligned_response_excerpt", "revision_summary"]
LABELS = {"fixed", "partially_fixed", "unresolved", "regressed"}


def parse_named_path(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Expected NAME=PATH")
    name, path = value.split("=", 1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("Prediction name cannot be empty")
    return name, Path(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit a RevTrack candidate pool against venue/year quality gates.")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--output-json")
    parser.add_argument("--min-candidates", type=int, default=150)
    parser.add_argument("--min-complete-rate", type=float, default=0.70)
    parser.add_argument("--min-disagreements", type=int, default=25)
    parser.add_argument(
        "--prediction",
        action="append",
        type=parse_named_path,
        default=[],
        help="Optional prediction file as NAME=PATH. Repeat to compute disagreement counts.",
    )
    parser.add_argument("--fail-on-error", action="store_true")
    return parser.parse_args()


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_predictions(path: str | Path) -> dict[str, str]:
    predictions: dict[str, str] = {}
    for row in load_jsonl(path):
        issue_id = str(row.get("id") or row.get("issue_id") or "")
        label = str(row.get("predicted_label") or "")
        if issue_id:
            predictions[issue_id] = label
    return predictions


def has_text(value: Any) -> bool:
    return bool(" ".join(str(value or "").split()))


def completeness(row: dict[str, Any], fields: list[str]) -> bool:
    return all(has_text(row.get(field)) for field in fields)


def count_disagreements(
    candidate_ids: list[str],
    prediction_maps: dict[str, dict[str, str]],
) -> dict[str, Any]:
    if len(prediction_maps) < 2:
        return {
            "prediction_models": sorted(prediction_maps),
            "comparable_rows": 0,
            "disagreement_rows": 0,
            "high_disagreement_rows": 0,
            "missing_prediction_rows": len(candidate_ids) if prediction_maps else 0,
            "label_combo_counts": {},
        }

    comparable = 0
    disagreements = 0
    high_disagreements = 0
    missing = 0
    combos: Counter[str] = Counter()
    for issue_id in candidate_ids:
        labels = {
            name: pred_map.get(issue_id, "")
            for name, pred_map in prediction_maps.items()
        }
        if any(not label for label in labels.values()):
            missing += 1
            continue
        comparable += 1
        unique_labels = set(labels.values())
        combo = "; ".join(f"{name}={label}" for name, label in sorted(labels.items()))
        combos[combo] += 1
        if len(unique_labels) > 1:
            disagreements += 1
        if len(unique_labels) >= 3 or {"fixed", "regressed"}.issubset(unique_labels):
            high_disagreements += 1

    return {
        "prediction_models": sorted(prediction_maps),
        "comparable_rows": comparable,
        "disagreement_rows": disagreements,
        "high_disagreement_rows": high_disagreements,
        "missing_prediction_rows": missing,
        "label_combo_counts": dict(combos.most_common(20)),
    }


def audit_candidate_pool(
    candidates: list[dict[str, Any]],
    *,
    prediction_maps: dict[str, dict[str, str]] | None = None,
    min_candidates: int = 150,
    min_complete_rate: float = 0.70,
    min_disagreements: int = 25,
) -> dict[str, Any]:
    prediction_maps = prediction_maps or {}
    ids = [str(row.get("issue_id") or "") for row in candidates]
    duplicate_ids = sorted(issue_id for issue_id, count in Counter(ids).items() if issue_id and count > 1)
    missing_ids = sum(1 for issue_id in ids if not issue_id)
    complete_rows = sum(1 for row in candidates if completeness(row, REQUIRED_TEXT_FIELDS))
    row_count = len(candidates)
    complete_rate = complete_rows / row_count if row_count else 0.0
    field_rates = {
        field: (sum(1 for row in candidates if has_text(row.get(field))) / row_count if row_count else 0.0)
        for field in REQUIRED_TEXT_FIELDS
    }
    venues = Counter(str(row.get("venue") or "missing") for row in candidates)
    submissions = Counter(str(row.get("submission_id") or row.get("forum") or "missing") for row in candidates)
    review_fields = Counter(
        field
        for row in candidates
        for field in row.get("review_fields", [])
        if field
    )
    disagreement = count_disagreements(ids, prediction_maps)

    errors: list[str] = []
    warnings: list[str] = []
    if missing_ids:
        errors.append(f"{missing_ids} candidates are missing issue_id")
    if duplicate_ids:
        errors.append(f"duplicate issue_ids: {duplicate_ids}")
    if row_count < min_candidates:
        errors.append(f"candidate count {row_count} is below required minimum {min_candidates}")
    if complete_rate < min_complete_rate:
        errors.append(f"complete-field rate {complete_rate:.3f} is below required minimum {min_complete_rate:.3f}")
    if prediction_maps and disagreement["disagreement_rows"] < min_disagreements:
        errors.append(
            f"prediction disagreement rows {disagreement['disagreement_rows']} are below required minimum {min_disagreements}"
        )
    if not prediction_maps:
        warnings.append("no prediction files supplied; disagreement gate was not evaluated")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "rows": row_count,
        "unique_issue_ids": len(set(issue_id for issue_id in ids if issue_id)),
        "duplicate_issue_ids": duplicate_ids,
        "missing_issue_ids": missing_ids,
        "complete_rows": complete_rows,
        "complete_rate": complete_rate,
        "field_nonempty_rates": field_rates,
        "venue_counts": dict(venues.most_common()),
        "submission_count": len([item for item in submissions if item != "missing"]),
        "top_submission_issue_counts": dict(submissions.most_common(10)),
        "review_field_counts": dict(review_fields.most_common()),
        "disagreement": disagreement,
    }


def main() -> None:
    args = parse_args()
    predictions = {name: load_predictions(path) for name, path in args.prediction}
    report = audit_candidate_pool(
        load_jsonl(args.candidates),
        prediction_maps=predictions,
        min_candidates=args.min_candidates,
        min_complete_rate=args.min_complete_rate,
        min_disagreements=args.min_disagreements,
    )

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, sort_keys=True))
    if args.fail_on_error and report["errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
