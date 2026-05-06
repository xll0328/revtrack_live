from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from revtrack.io import save_examples
from revtrack.schema import IssueExample


ROOT = Path(__file__).resolve().parents[1]
EXPORT_SCRIPT = ROOT / "scripts" / "export_prompted_llm_baseline_packet.py"
EVAL_SCRIPT = ROOT / "scripts" / "evaluate_prompted_llm_baseline.py"
RUNNER_SCRIPT = ROOT / "scripts" / "run_local_prompted_llm_baseline.py"
AIHUBMIX_SCRIPT = ROOT / "scripts" / "run_aihubmix_prompted_llm_baseline.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


exporter = load_module(EXPORT_SCRIPT, "export_prompted_llm_baseline_packet")
evaluator = load_module(EVAL_SCRIPT, "evaluate_prompted_llm_baseline")
runner = load_module(RUNNER_SCRIPT, "run_local_prompted_llm_baseline")
aihubmix_runner = load_module(AIHUBMIX_SCRIPT, "run_aihubmix_prompted_llm_baseline")


def example(issue_id: str = "x1", label: str = "fixed") -> IssueExample:
    return IssueExample(
        id=issue_id,
        source="openreview",
        venue="TestVenue",
        paper_title="Paper X",
        review_text="Reviewer asks for an ablation.",
        author_response="We added the ablation in Table 2.",
        revision_summary="The revision adds Table 2 with the ablation.",
        gold_label=label,
    )


def test_exports_prompt_packet_without_gold_label_in_prompt(tmp_path: Path) -> None:
    examples = tmp_path / "examples.jsonl"
    packet = tmp_path / "packet.jsonl"
    report = tmp_path / "packet.md"
    save_examples(examples, [example()])

    manifest = exporter.export_packet(
        examples_path=examples,
        output_jsonl=packet,
        output_md=report,
        dataset_name="unit",
        max_field_chars=500,
    )

    row = json.loads(packet.read_text(encoding="utf-8").splitlines()[0])
    prompt_text = "\n".join(message["content"] for message in row["messages"])
    assert manifest["rows"] == 1
    assert row["metadata"]["gold_label_hidden"] is True
    assert "fixed" in prompt_text
    assert '"gold_label"' not in prompt_text
    assert "We added the ablation" in prompt_text


def test_evaluates_prompted_llm_outputs(tmp_path: Path) -> None:
    examples = tmp_path / "examples.jsonl"
    outputs = tmp_path / "llm_outputs.jsonl"
    normalized = tmp_path / "predictions.jsonl"
    metrics_json = tmp_path / "metrics.json"
    details_json = tmp_path / "details.json"
    audit_json = tmp_path / "audit.json"
    metrics_md = tmp_path / "metrics.md"
    save_examples(examples, [example("x1", "fixed"), example("x2", "unresolved")])
    outputs.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "id": "x1",
                        "predicted_label": "fixed",
                        "evidence_span": "We added the ablation.",
                        "rationale": "The requested evidence is added.",
                    }
                ),
                json.dumps(
                    {
                        "id": "x2",
                        "predicted_label": "partially_fixed",
                        "evidence_span": "Some response evidence.",
                        "rationale": "Partial progress.",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = evaluator.evaluate_llm_outputs(
        examples_path=examples,
        llm_outputs_path=outputs,
        normalized_predictions_path=normalized,
        metrics_json=metrics_json,
        details_json=details_json,
        audit_json=audit_json,
        metrics_md=metrics_md,
        model_key="prompted_llm",
    )

    assert result["audit"]["status"] == "ok"
    assert result["summary"]["accuracy"] == 0.5
    assert json.loads(metrics_json.read_text(encoding="utf-8"))["num_examples"] == 2.0
    assert "prompted_llm" in metrics_md.read_text(encoding="utf-8")


def test_evaluator_audits_invalid_outputs(tmp_path: Path) -> None:
    examples = tmp_path / "examples.jsonl"
    outputs = tmp_path / "llm_outputs.jsonl"
    save_examples(examples, [example("x1", "fixed")])
    outputs.write_text(json.dumps({"id": "x1", "predicted_label": "done"}) + "\n", encoding="utf-8")

    result = evaluator.evaluate_llm_outputs(
        examples_path=examples,
        llm_outputs_path=outputs,
        normalized_predictions_path=tmp_path / "predictions.jsonl",
        metrics_json=tmp_path / "metrics.json",
        details_json=tmp_path / "details.json",
        audit_json=tmp_path / "audit.json",
        metrics_md=tmp_path / "metrics.md",
        model_key="bad_llm",
    )

    assert result["audit"]["status"] == "error"
    assert result["audit"]["invalid_rows"][0]["issue_id"] == "x1"


def test_evaluator_allows_subset_smoke_runs(tmp_path: Path) -> None:
    examples = tmp_path / "examples.jsonl"
    outputs = tmp_path / "llm_outputs.jsonl"
    save_examples(examples, [example("x1", "fixed"), example("x2", "unresolved")])
    outputs.write_text(
        json.dumps(
            {
                "id": "x1",
                "predicted_label": "fixed",
                "evidence_span": "We added the ablation.",
                "rationale": "Direct evidence.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = evaluator.evaluate_llm_outputs(
        examples_path=examples,
        llm_outputs_path=outputs,
        normalized_predictions_path=tmp_path / "predictions.jsonl",
        metrics_json=tmp_path / "metrics.json",
        details_json=tmp_path / "details.json",
        audit_json=tmp_path / "audit.json",
        metrics_md=tmp_path / "metrics.md",
        model_key="subset_llm",
        allow_subset=True,
    )

    assert result["audit"]["status"] == "ok"
    assert result["audit"]["evaluated_examples"] == 1
    assert result["audit"]["missing_prediction_ids"] == ["x2"]
    assert result["summary"]["accuracy"] == 1.0


def test_local_runner_extracts_first_json_object() -> None:
    text = 'Sure. {"predicted_label":"fixed","evidence_span":"Added Table 2.","rationale":"Directly addressed."}'

    row = runner.normalize_generation("x1", text)

    assert row["id"] == "x1"
    assert row["predicted_label"] == "fixed"
    assert row["evidence_span"] == "Added Table 2."


def test_local_runner_marks_invalid_label() -> None:
    row = runner.normalize_generation("x1", '{"predicted_label":"done"}')

    assert row["predicted_label"] == "invalid"


class FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content: str) -> None:
        self.choices = [FakeChoice(content)]


class FakeChatCompletions:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse(
            '{"predicted_label":"unresolved","evidence_span":"No new experiment is added.",'
            '"rationale":"The concern is acknowledged but not addressed."}'
        )


class FakeChat:
    def __init__(self) -> None:
        self.completions = FakeChatCompletions()


class FakeClient:
    def __init__(self) -> None:
        self.chat = FakeChat()


def test_aihubmix_runner_uses_chat_completions_and_omits_api_key(tmp_path: Path) -> None:
    examples = tmp_path / "examples.jsonl"
    packet = tmp_path / "packet.jsonl"
    report = tmp_path / "packet.md"
    output = tmp_path / "outputs.jsonl"
    save_examples(examples, [example("x1", "unresolved")])
    exporter.export_packet(
        examples_path=examples,
        output_jsonl=packet,
        output_md=report,
        dataset_name="unit",
    )
    client = FakeClient()

    result = aihubmix_runner.run_aihubmix(
        prompt_packet=packet,
        output_jsonl=output,
        model="gpt-5.5",
        base_url="https://aihubmix.com/v1",
        api_key="secret-for-test",
        client=client,
    )

    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert result["written_rows"] == 1
    assert rows[0]["predicted_label"] == "unresolved"
    assert "secret-for-test" not in output.read_text(encoding="utf-8")
    assert client.chat.completions.calls[0]["model"] == "gpt-5.5"
    assert client.chat.completions.calls[0]["temperature"] == 0.0


def test_aihubmix_runner_resume_skips_completed_rows(tmp_path: Path) -> None:
    examples = tmp_path / "examples.jsonl"
    packet = tmp_path / "packet.jsonl"
    report = tmp_path / "packet.md"
    output = tmp_path / "outputs.jsonl"
    save_examples(examples, [example("x1", "unresolved")])
    exporter.export_packet(
        examples_path=examples,
        output_jsonl=packet,
        output_md=report,
        dataset_name="unit",
    )
    output.write_text(json.dumps({"id": "x1", "predicted_label": "unresolved"}) + "\n", encoding="utf-8")
    client = FakeClient()

    result = aihubmix_runner.run_aihubmix(
        prompt_packet=packet,
        output_jsonl=output,
        model="gpt-5.5",
        base_url="https://aihubmix.com/v1",
        api_key="secret-for-test",
        client=client,
        resume=True,
    )

    assert result["skipped_rows"] == 1
    assert result["written_rows"] == 0
    assert client.chat.completions.calls == []


def test_aihubmix_runner_reads_api_key_file(tmp_path: Path) -> None:
    key_file = tmp_path / "aihubmix.secret"
    key_file.write_text("secret-from-file\n", encoding="utf-8")

    assert (
        aihubmix_runner.read_api_key(env_name="MISSING_ENV_FOR_TEST", key_file=key_file)
        == "secret-from-file"
    )
