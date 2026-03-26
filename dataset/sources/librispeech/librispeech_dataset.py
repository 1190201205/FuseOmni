from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset


@register_dataset("librispeech")
class LibriSpeechDataset(BaseDataset):
    """Load LibriSpeech subsets and convert them to message-format ASR samples."""

    _DEFAULT_SUBSETS = (
        "train-clean-100",
        "train-clean-360",
        "train-other-500",
    )

    def __init__(
        self,
        dataset_root: str | Path,
        subset: str | Sequence[str] = "",
        max_samples: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("librispeech", dataset_root, **kwargs)
        self.subsets = self._resolve_subsets(subset)
        self.max_samples = max_samples
        self.load_data()

    def load_data(self) -> None:
        loaded = 0
        for subset_name in self.subsets:
            for sample in self._iter_subset_samples(subset_name):
                self.samples.append(sample)
                loaded += 1
                if self.max_samples is not None and loaded >= self.max_samples:
                    return

    def _resolve_subsets(self, subset: str | Sequence[str]) -> List[str]:
        requested = self.normalize_selection(subset)
        if requested:
            missing = [
                subset_name
                for subset_name in requested
                if not (self.dataset_root / subset_name).is_dir()
            ]
            if missing:
                raise FileNotFoundError(
                    f"LibriSpeech subset directory not found: {missing[0]}"
                )
            return requested

        available_defaults = [
            subset_name
            for subset_name in self._DEFAULT_SUBSETS
            if (self.dataset_root / subset_name).is_dir()
        ]
        if available_defaults:
            return available_defaults

        discovered = sorted(
            path.name
            for path in self.dataset_root.iterdir()
            if path.is_dir() and path.name.startswith("train-")
        )
        if not discovered:
            raise FileNotFoundError(
                f"No LibriSpeech subset directories found under: {self.dataset_root}"
            )
        return discovered

    def _iter_subset_samples(self, subset_name: str) -> Iterable[Dict[str, object]]:
        subset_root = self.dataset_root / subset_name
        transcript_files = sorted(subset_root.rglob("*.trans.txt"))
        if not transcript_files:
            raise FileNotFoundError(f"No transcript files found in: {subset_root}")

        for transcript_file in transcript_files:
            with transcript_file.open("r", encoding="utf-8") as handle:
                for row_index, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue

                    parts = line.split(maxsplit=1)
                    if len(parts) != 2:
                        raise ValueError(
                            f"Invalid transcript format at {transcript_file}:{row_index}"
                        )

                    utterance_id, transcript = parts
                    audio_path = transcript_file.parent / f"{utterance_id}.flac"
                    if not audio_path.is_file():
                        raise FileNotFoundError(f"Audio file not found: {audio_path}")

                    yield {
                        "id": f"librispeech_{subset_name}_{utterance_id}",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "text": None,
                                        "audio_path": audio_path.relative_to(
                                            self.dataset_root
                                        ).as_posix(),
                                    }
                                ],
                            },
                            {
                                "role": "assistant",
                                "content": [
                                    {
                                        "text": transcript.strip(),
                                        "audio_path": None,
                                    }
                                ],
                            },
                        ],
                        "task": "ASR",
                        "data_source": f"librispeech_{subset_name}",
                    }
