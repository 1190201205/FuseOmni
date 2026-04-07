from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Sequence

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset


@register_dataset("commonvoice")
class CommonVoiceDataset(BaseDataset):
    """Load Common Voice TSV metadata and convert it to message-format ASR samples."""

    _IGNORED_TSV_STEMS = {
        "clip_durations",
        "validated_sentences",
        "unvalidated_sentences",
    }

    def __init__(
        self,
        dataset_root: str | Path,
        split: str = "train",
        language: str | Sequence[str] = "",
        max_samples: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("commonvoice", dataset_root, **kwargs)
        normalized_split = (split or "").strip()
        self.split_names = (
            [normalized_split] if normalized_split else self._discover_splits()
        )
        self.languages = self._resolve_languages(language)
        self.max_samples = max_samples
        self.stats = {
            "loaded": 0,
            "skipped_missing_audio_samples": 0,
        }
        self.load_data()

    def load_data(self) -> None:
        loaded = 0
        for language_name in self.languages:
            for split_name in self.split_names:
                self.samples.extend(
                    self._load_language_split(
                        language_name=language_name,
                        split_name=split_name,
                        remaining_limit=None
                        if self.max_samples is None
                        else max(self.max_samples - loaded, 0),
                    )
                )
                loaded = len(self.samples)
                if self.max_samples is not None and loaded >= self.max_samples:
                    return

    def _raw_root(self) -> Path:
        candidate = self.dataset_root / "raw"
        return candidate if candidate.is_dir() else self.dataset_root

    def _resolve_languages(self, language: str | Sequence[str]) -> List[str]:
        requested = self.normalize_selection(language)
        raw_root = self._raw_root()
        if requested:
            missing = [
                language_name
                for language_name in requested
                if not (raw_root / language_name).is_dir()
            ]
            if missing:
                raise FileNotFoundError(
                    f"Common Voice language directory not found: {missing[0]}"
                )
            return requested

        discovered = sorted(path.name for path in raw_root.iterdir() if path.is_dir())
        if not discovered:
            raise FileNotFoundError(
                f"No Common Voice languages found under: {raw_root}"
            )
        return discovered

    def _discover_splits(self) -> List[str]:
        raw_root = self._raw_root()
        split_names = set()
        for language_root in raw_root.iterdir():
            if not language_root.is_dir():
                continue
            for tsv_path in language_root.glob("*.tsv"):
                if tsv_path.stem not in self._IGNORED_TSV_STEMS:
                    split_names.add(tsv_path.stem)
        if not split_names:
            raise FileNotFoundError(
                f"No Common Voice TSV files found under: {raw_root}"
            )
        return sorted(split_names)

    def _load_language_split(
        self,
        language_name: str,
        split_name: str,
        remaining_limit: int | None,
    ) -> List[Dict[str, object]]:
        language_root = self._raw_root() / language_name
        tsv_path = language_root / f"{split_name}.tsv"
        if not tsv_path.is_file():
            raise FileNotFoundError(f"Common Voice TSV file not found: {tsv_path}")

        split_samples: List[Dict[str, object]] = []
        with tsv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row_index, row in enumerate(reader, start=2):
                if remaining_limit is not None and len(split_samples) >= remaining_limit:
                    break

                audio_name = (row.get("path") or "").strip()
                transcript = (row.get("sentence") or "").strip()
                if not audio_name:
                    raise ValueError(f'Empty "path" at {tsv_path}:{row_index}')
                if not transcript:
                    raise ValueError(f'Empty "sentence" at {tsv_path}:{row_index}')

                audio_abs_path = language_root / "clips" / audio_name
                if not audio_abs_path.is_file():
                    self.stats["skipped_missing_audio_samples"] += 1
                    continue

                split_samples.append(
                    {
                        "id": f"commonvoice_{language_name}_{split_name}_{Path(audio_name).stem}",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "text": self.build_asr_instruction(language_name),
                                        "audio_path": audio_abs_path.relative_to(
                                            self.dataset_root
                                        ).as_posix(),
                                    }
                                ],
                            },
                            {
                                "role": "assistant",
                                "content": [
                                    {
                                        "text": transcript,
                                        "audio_path": None,
                                    }
                                ],
                            },
                        ],
                        "task": "ASR",
                        "data_source": f"commonvoice_{language_name}_{split_name}",
                    }
                )
                self.stats["loaded"] += 1

        return split_samples
