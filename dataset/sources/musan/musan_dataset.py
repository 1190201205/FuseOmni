from __future__ import annotations

from pathlib import Path
from typing import Any, List

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset


@register_dataset("musan")
class MUSANDataset(BaseDataset):
    """Load processed MUSAN jsonl manifests."""

    _SPLIT_TO_FILE = {
        "train": "metadata/musan_train_audio_classification.jsonl",
        "dev": "metadata/musan_dev_audio_classification.jsonl",
        "test": "metadata/musan_test_audio_classification.jsonl",
        "all": "metadata/musan_all_audio_classification.jsonl",
    }

    def __init__(
        self,
        dataset_root: str | Path,
        split: str = "",
        max_samples: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("musan", dataset_root, **kwargs)
        normalized_split = (split or "").strip().lower()
        if normalized_split and normalized_split not in self._SPLIT_TO_FILE:
            valid = '", "'.join(self._SPLIT_TO_FILE.keys())
            raise ValueError(
                f'Invalid split "{split}". Expected one of "{valid}" or empty.'
            )

        self.splits: List[str] = [normalized_split] if normalized_split else ["train", "dev", "test"]
        self.max_samples = max_samples
        self.load_data()

    def load_data(self) -> None:
        jsonl_paths = [self.dataset_root / self._SPLIT_TO_FILE[name] for name in self.splits]
        self.samples.extend(self.load_jsonl_paths(jsonl_paths, self.max_samples))
