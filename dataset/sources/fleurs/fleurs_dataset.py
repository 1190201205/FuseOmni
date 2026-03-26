from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Sequence

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset


@register_dataset("fleurs")
class FLEURSDataset(BaseDataset):
    """Load FLEURS TSV metadata and convert it to message-format ASR samples."""

    _TSV_FIELD_COUNT = 7
    _TRANSCRIPT_INDEX = 2
    _AUDIO_NAME_INDEX = 1
    _RECORD_ID_INDEX = 0

    def __init__(
        self,
        dataset_root: str | Path,
        split: str = "train",
        language: str | Sequence[str] = "",
        max_samples: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("fleurs", dataset_root, **kwargs)
        normalized_split = (split or "").strip()
        self.split_names = (
            [normalized_split] if normalized_split else self._discover_splits()
        )
        self.languages = self._resolve_languages(language)
        self.max_samples = max_samples
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
                    f"FLEURS language directory not found: {missing[0]}"
                )
            return requested

        discovered = sorted(path.name for path in raw_root.iterdir() if path.is_dir())
        if not discovered:
            raise FileNotFoundError(f"No FLEURS languages found under: {raw_root}")
        return discovered

    def _discover_splits(self) -> List[str]:
        raw_root = self._raw_root()
        split_names = set()
        for language_root in raw_root.iterdir():
            if not language_root.is_dir():
                continue
            for tsv_path in language_root.glob("*.tsv"):
                split_names.add(tsv_path.stem)
        if not split_names:
            raise FileNotFoundError(f"No FLEURS TSV files found under: {raw_root}")
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
            raise FileNotFoundError(f"FLEURS TSV file not found: {tsv_path}")

        split_samples: List[Dict[str, object]] = []
        with tsv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, delimiter="\t")
            for row_index, row in enumerate(reader, start=1):
                if remaining_limit is not None and len(split_samples) >= remaining_limit:
                    break
                if not row:
                    continue
                if len(row) < self._TSV_FIELD_COUNT:
                    raise ValueError(f"Invalid row at {tsv_path}:{row_index}")

                record_id = row[self._RECORD_ID_INDEX].strip()
                audio_name = row[self._AUDIO_NAME_INDEX].strip()
                transcript = row[self._TRANSCRIPT_INDEX].strip()

                if not record_id or not audio_name or not transcript:
                    raise ValueError(f"Missing required field at {tsv_path}:{row_index}")

                audio_rel_path = self._resolve_audio_rel_path(
                    language_root=language_root,
                    split_name=split_name,
                    audio_name=audio_name,
                )
                audio_stem = Path(audio_name).stem
                split_samples.append(
                    {
                        "id": f"fleurs_{language_name}_{split_name}_{record_id}_{audio_stem}",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "text": None,
                                        "audio_path": audio_rel_path,
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
                        "data_source": f"fleurs_{language_name}_{split_name}",
                    }
                )

        return split_samples

    def _resolve_audio_rel_path(
        self,
        language_root: Path,
        split_name: str,
        audio_name: str,
    ) -> str:
        candidates = (
            language_root / "audio" / split_name / audio_name,
            language_root / "audio" / audio_name,
        )
        for audio_path in candidates:
            if audio_path.is_file():
                return audio_path.relative_to(self.dataset_root).as_posix()

        raise FileNotFoundError(
            "FLEURS extracted audio file not found: "
            f"{language_root / 'audio' / split_name / audio_name}"
        )
