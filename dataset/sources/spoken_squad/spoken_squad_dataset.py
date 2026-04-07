from __future__ import annotations

from pathlib import Path
from typing import Any, List

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset


@register_dataset("spoken_squad")
class SpokenSquadDataset(BaseDataset):
    """Load processed Spoken-SQuAD jsonl manifests."""

    _SPLIT_TO_FILE = {
        "train": "spoken_squad_train_qa.jsonl",
        "validation": "spoken_squad_validation_qa.jsonl",
        "test_wer44": "spoken_squad_test_wer44_qa.jsonl",
        "test_wer54": "spoken_squad_test_wer54_qa.jsonl",
    }
    _ALIASES = {
        "dev": "validation",
        "val": "validation",
        "test": "validation",
    }

    def __init__(
        self,
        dataset_root: str | Path,
        split: str = "",
        max_samples: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("spoken_squad", dataset_root, **kwargs)
        normalized_split = (split or "").strip().lower()
        normalized_split = self._ALIASES.get(normalized_split, normalized_split)
        if normalized_split and normalized_split not in self._SPLIT_TO_FILE:
            valid = '", "'.join(list(self._SPLIT_TO_FILE.keys()) + list(self._ALIASES.keys()))
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
        self.samples.extend(self.load_jsonl_paths(jsonl_paths, self.max_samples))
