from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from revtrack.prompts import build_chat_messages, build_prompt
from revtrack.schema import LABELS, IssueExample, Prediction


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _extract_label(text: str) -> str:
    try:
        payload = json.loads(text)
        label = str(payload.get("label", "")).strip().lower()
        if label in LABELS:
            return label
    except json.JSONDecodeError:
        pass
    lowered = text.lower()
    for label in LABELS:
        if re.search(rf"\b{re.escape(label)}\b", lowered):
            return label
    return "unresolved"


@dataclass
class GenerationConfig:
    model_name: str
    max_new_tokens: int = 128
    temperature: float = 0.0
    top_p: float = 1.0
    device_map: str = "auto"
    dtype: str = "auto"
    trust_remote_code: bool = False
    local_files_only: bool = False


class HeuristicBackend:
    def predict(self, example: IssueExample) -> Prediction:
        review_tokens = _tokenize(example.review_text)
        response_text = f"{example.author_response} {example.revision_summary}".lower()
        overlap = len(review_tokens & _tokenize(response_text))

        fixed_cues = (
            "added table",
            "we added",
            "new experiment",
            "new ablation",
            "section",
            "appendix",
            "released code",
            "included",
            "now report",
        )
        partial_cues = (
            "clarified",
            "discuss",
            "partially",
            "limited",
            "brief",
            "space",
        )
        unresolved_cues = (
            "future work",
            "left for future",
            "beyond the scope",
            "do not",
            "unable",
            "cannot",
            "not included",
        )
        regressed_cues = (
            "removed",
            "dropped",
            "worse",
            "decrease",
            "regression",
            "longer runtime",
        )

        if any(cue in response_text for cue in regressed_cues):
            label = "regressed"
        elif any(cue in response_text for cue in fixed_cues) and overlap >= 2:
            label = "fixed"
        elif any(cue in response_text for cue in unresolved_cues):
            label = "unresolved"
        elif any(cue in response_text for cue in partial_cues) or overlap >= 1:
            label = "partially_fixed"
        else:
            label = "unresolved"

        return Prediction(
            id=example.id,
            predicted_label=label,
            raw_output=label,
            metadata={"backend": "heuristic", "token_overlap": overlap},
        )


class TransformersBackend:
    def __init__(self, config: GenerationConfig):
        self.config = config
        self._model = None
        self._tokenizer = None

    def _ensure_loaded(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self._tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=self.config.trust_remote_code,
            local_files_only=self.config.local_files_only,
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            device_map=self.config.device_map,
            dtype=self.config.dtype,
            trust_remote_code=self.config.trust_remote_code,
            local_files_only=self.config.local_files_only,
        )

    def predict(self, example: IssueExample) -> Prediction:
        self._ensure_loaded()
        tokenizer = self._tokenizer
        model = self._model
        if hasattr(tokenizer, "apply_chat_template") and getattr(tokenizer, "chat_template", None):
            prompt = tokenizer.apply_chat_template(
                build_chat_messages(example),
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            prompt = build_prompt(example)
        model_max_length = getattr(tokenizer, "model_max_length", 4096)
        if not isinstance(model_max_length, int) or model_max_length > 1_000_000:
            model_max_length = 4096
        max_input_length = max(model_max_length - self.config.max_new_tokens, 512)
        encoded = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_input_length,
        ).to(model.device)
        generation_kwargs: dict[str, Any] = {
            "max_new_tokens": self.config.max_new_tokens,
            "do_sample": self.config.temperature > 0,
            "top_p": self.config.top_p,
            "pad_token_id": tokenizer.eos_token_id,
        }
        if self.config.temperature > 0:
            generation_kwargs["temperature"] = self.config.temperature
        output_ids = model.generate(**encoded, **generation_kwargs)
        new_tokens = output_ids[0][encoded["input_ids"].shape[1] :]
        raw_output = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        label = _extract_label(raw_output)
        return Prediction(
            id=example.id,
            predicted_label=label,
            raw_output=raw_output,
            metadata={
                "backend": "transformers",
                "model": self.config.model_name,
                "prompt_tokens": int(encoded["input_ids"].shape[1]),
                "model_max_length": model_max_length,
            },
        )
