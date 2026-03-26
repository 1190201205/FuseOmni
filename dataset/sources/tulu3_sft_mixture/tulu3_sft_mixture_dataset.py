from __future__ import annotations

from pathlib import Path
from typing import Any, List

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset


@register_dataset("tulu3_sft_mixture")
class Tulu3SFTMixtureDataset(BaseDataset):
    """Load processed Tulu-3 SFT Mixture jsonl shards."""

    def __init__(
        self,
        dataset_root: str | Path,
        split: str = "",
        subset: str = "",
        max_samples: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("tulu3_sft_mixture", dataset_root, **kwargs)
        self.split = (split or "").strip().lower()
        self.subset = subset
        self.max_samples = max_samples
        self.load_data()

    def load_data(self) -> None:
        jsonl_dir = self.dataset_root / "jsonl"
        if not jsonl_dir.is_dir():
            raise FileNotFoundError(f"Tulu jsonl directory not found: {jsonl_dir}")

        requested_files = self.normalize_selection(self.subset)
        if requested_files:
            jsonl_paths: List[Path] = []
            for item in requested_files:
                candidate = Path(item)
                if not candidate.suffix:
                    candidate = candidate.with_suffix(".jsonl")
                if not candidate.is_absolute():
                    candidate = jsonl_dir / candidate
                jsonl_paths.append(candidate.resolve())
        else:
            if self.split and self.split != "train":
                raise ValueError(
                    'Invalid split for tulu3_sft_mixture. Expected "train" or empty.'
                )
            jsonl_paths = sorted(jsonl_dir.glob("*.jsonl"))

        self.samples.extend(self.load_jsonl_paths(jsonl_paths, self.max_samples))
