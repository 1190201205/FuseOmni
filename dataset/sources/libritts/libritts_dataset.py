from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset


@register_dataset("libritts")
class LibriTTSDataset(BaseDataset):
    """Load LibriTTS train subsets and convert them to message-format TTS samples."""

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
        super().__init__("libritts", dataset_root, **kwargs)
        self.subsets = self._resolve_subsets(subset)
        self.max_samples = max_samples
        self.stats = {
            "loaded": 0,
            "skipped_missing_audio_samples": 0,
        }
        self.load_data()

    def load_data(self) -> None:
        loaded = 0
        for subset_name in self.subsets:
            for sample in self._iter_subset_samples(subset_name):
                self.samples.append(sample)
                loaded += 1
                self.stats["loaded"] += 1
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
                    f"LibriTTS subset directory not found: {missing[0]}"
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
                f"No LibriTTS subset directories found under: {self.dataset_root}"
            )
        return discovered

    def _iter_subset_samples(self, subset_name: str) -> Iterable[Dict[str, object]]:
        subset_root = self.dataset_root / subset_name
        transcript_files = sorted(subset_root.rglob("*.trans.tsv"))
        if not transcript_files:
            raise FileNotFoundError(f"No transcript files found in: {subset_root}")

        data_source = f"libritts_{subset_name.replace('-', '_')}"

        for transcript_file in transcript_files:
            with transcript_file.open("r", encoding="utf-8") as handle:
                for row_index, raw_line in enumerate(handle, start=1):
                    line = raw_line.strip()
                    if not line:
                        continue

                    parts = line.split("\t")
                    if len(parts) < 3:
                        raise ValueError(
                            f"Invalid transcript format at {transcript_file}:{row_index}"
                        )

                    utterance_id = parts[0].strip()
                    transcript = parts[2].strip()
                    if not utterance_id:
                        raise ValueError(
                            f"Empty utterance id at {transcript_file}:{row_index}"
                        )
                    if not transcript:
                        raise ValueError(
                            f"Empty normalized transcript at {transcript_file}:{row_index}"
                        )

                    audio_path = transcript_file.parent / f"{utterance_id}.wav"
                    if not audio_path.is_file():
                        self.stats["skipped_missing_audio_samples"] += 1
                        continue

                    yield {
                        "id": f"{data_source}_{utterance_id}",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "text": self.build_tts_instruction(transcript),
                                        "audio_path": None,
                                    }
                                ],
                            },
                            {
                                "role": "assistant",
                                "content": [
                                    {
                                        "text": None,
                                        "audio_path": audio_path.relative_to(
                                            self.dataset_root
                                        ).as_posix(),
                                    }
                                ],
                            },
                        ],
                        "task": "TTS",
                        "data_source": data_source,
                    }
