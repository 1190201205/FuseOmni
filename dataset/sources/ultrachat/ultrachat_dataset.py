from __future__ import annotations

from pathlib import Path
from typing import Any

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset


@register_dataset("ultrachat")
class UltraChatDataset(BaseDataset):
    """Load processed UltraChat jsonl manifests."""

    def __init__(
        self,
        dataset_root: str | Path,
        metadata_name: str = "ultrachat_train_text_sft.jsonl",
        max_samples: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("ultrachat", dataset_root, **kwargs)
        self.metadata_path = self.dataset_root / metadata_name
        self.max_samples = max_samples
        self.load_data()

    def load_data(self) -> None:
        self.samples.extend(self.load_jsonl_paths([self.metadata_path], self.max_samples))
