from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Sequence

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset


@register_dataset("clotho")
class ClothoDataset(BaseDataset):
    """Load processed Clotho jsonl manifests."""

    _CAPTION_ID_SUFFIX_RE = re.compile(r"_cap\d+$")
    _SPLIT_TO_FILE = {
        "train": "Clotho_train_AudioCaptioning.jsonl",
        "validation": "Clotho_validation_AudioCaptioning.jsonl",
        "test": "Clotho_test_AudioCaptioning.jsonl",
    }

    def __init__(
        self,
        dataset_root: str | Path,
        split: str = "",
        max_samples: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("clotho", dataset_root, **kwargs)
        normalized_split = (split or "").strip().lower()
        if normalized_split and normalized_split not in self._SPLIT_TO_FILE:
            valid = '", "'.join(self._SPLIT_TO_FILE.keys())
            raise ValueError(
                f'Invalid split "{split}". Expected one of "{valid}" or empty.'
            )

        self.splits: List[str] = (
            [normalized_split] if normalized_split else list(self._SPLIT_TO_FILE.keys())
        )
        self.max_samples = max_samples
        self.load_data()

    def load_data(self) -> None:
        jsonl_paths = [self.dataset_root / self._SPLIT_TO_FILE[name] for name in self.splits]
        self.samples.extend(self._load_clotho_jsonl_paths(jsonl_paths, self.max_samples))

    @classmethod
    def _load_clotho_jsonl_paths(
        cls,
        jsonl_paths: Sequence[str | Path],
        max_samples: int | None = None,
    ) -> List[Dict[str, Any]]:
        samples: List[Dict[str, Any]] = []

        for raw_path in jsonl_paths:
            jsonl_path = Path(raw_path).expanduser().resolve()
            if not jsonl_path.is_file():
                raise FileNotFoundError(f"JSONL file not found: {jsonl_path}")

            with jsonl_path.open("r", encoding="utf-8") as handle:
                for line_index, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue

                    try:
                        raw_sample = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise ValueError(
                            f"Invalid JSONL at {jsonl_path}:{line_index}"
                        ) from exc

                    expanded_samples = cls._expand_legacy_reference_sample(raw_sample)
                    for sample in expanded_samples:
                        if max_samples is not None and len(samples) >= max_samples:
                            return samples
                        samples.append(sample)

        return samples

    @classmethod
    def _expand_legacy_reference_sample(
        cls,
        sample: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        references = sample.get("references")
        if not isinstance(references, list):
            return [sample]

        normalized_references = [
            str(reference).strip() for reference in references if str(reference).strip()
        ]
        if not normalized_references or cls._is_reference_sample_expanded(sample):
            return [sample]

        assistant_item = cls._get_first_assistant_content_item(sample)
        if assistant_item is None:
            return [sample]

        sample_id = str(sample.get("id", "")).strip()
        base_id = cls._CAPTION_ID_SUFFIX_RE.sub("", sample_id)
        expanded_samples: List[Dict[str, Any]] = []

        for caption_index, caption in enumerate(normalized_references, start=1):
            expanded_sample = copy.deepcopy(sample)
            if base_id:
                expanded_sample["id"] = f"{base_id}_cap{caption_index}"
            expanded_sample["caption_index"] = caption_index

            expanded_assistant_item = cls._get_first_assistant_content_item(expanded_sample)
            if expanded_assistant_item is None:
                return [sample]
            expanded_assistant_item["text"] = caption
            expanded_assistant_item.setdefault("audio_path", None)

            expanded_samples.append(expanded_sample)

        return expanded_samples

    @classmethod
    def _is_reference_sample_expanded(cls, sample: Dict[str, Any]) -> bool:
        if sample.get("caption_index") is not None:
            return True

        sample_id = str(sample.get("id", "")).strip()
        return bool(sample_id and cls._CAPTION_ID_SUFFIX_RE.search(sample_id))

    @staticmethod
    def _get_first_assistant_content_item(
        sample: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        messages = sample.get("messages")
        if not isinstance(messages, list):
            return None

        for message in messages:
            if not isinstance(message, dict) or message.get("role") != "assistant":
                continue

            content = message.get("content")
            if not isinstance(content, list) or not content:
                return None

            first_item = content[0]
            if isinstance(first_item, dict):
                return first_item
            return None

        return None
