from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset

@register_dataset("mmsu")
class MMSUDataset(BaseDataset):
    """Load MMSU parquet files and convert to message-format samples for AudioQA."""

    def __init__(
        self,
        dataset_root: str | Path,
        max_samples: int | None = None,
        **kwargs: Any
    ) -> None:
        super().__init__("mmsu", dataset_root, **kwargs)
        if pd is None:
            raise ImportError("pandas is required. Install with: pip install pandas")

        self.max_samples = max_samples
        self.load_data()

    def load_data(self) -> None:
        data_dir = self.dataset_root / "data"
        if not data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")

        parquet_files = sorted(data_dir.glob("*.parquet"))
        if not parquet_files:
            raise FileNotFoundError(f"No parquet files found in: {data_dir}")

        count = 0
        skipped_count = 0
        for pq_file in parquet_files:
            df = pd.read_parquet(pq_file)
            for _, row in df.iterrows():
                if self.max_samples is not None and count >= self.max_samples:
                    break
                
                sample = self._convert_row(row)
                if sample is None:
                    skipped_count += 1
                    continue
                    
                self.samples.append(sample)
                count += 1
        
        # print(f"Finished loading MMSU. Valid: {count}, Skipped (not found): {skipped_count}")

    def _convert_row(self, row: Any) -> Dict[str, object] | None:
        sample_id = row.get("id", "")
        question = row.get("question", "")
        choice_a = row.get("choice_a", "")
        choice_b = row.get("choice_b", "")
        choice_c = row.get("choice_c", "")
        choice_d = row.get("choice_d", "")
        answer_gt = row.get("answer_gt", "")
        category = row.get("category", "")

        audio_info = row.get("audio", {})
        if isinstance(audio_info, dict):
            audio_filename = audio_info.get("path", "")
        else:
            audio_filename = str(audio_info) if audio_info else ""

        if not audio_filename:
            return None

        clean_name = audio_filename.replace("audio/", "")
        pure_name = Path(clean_name).stem
        
        found_audio_path = None
        base_audio_dir = self.dataset_root / "audio"
        
        for ext in [".wav", ".mp3"]:
            test_path = base_audio_dir / f"{pure_name}{ext}"
            if test_path.exists():
                found_audio_path = str(test_path)
                break
        
        if found_audio_path is None:
            return None

        question_text = f"{question}\nA. {choice_a}\nB. {choice_b}\nC. {choice_c}\nD. {choice_d}"
        data_source = f"MMSU_{category}" if category else "MMSU"

        return {
            "id": f"MMSU_{sample_id}",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": question_text,
                            "audio_path": found_audio_path,
                        }
                    ],
                },
                {
                    "role": "assistant",
                    "content": [
                        {
                            "text": answer_gt,
                            "audio_path": None,
                        }
                    ],
                },
            ],
            "task": "AudioQA",
            "data_source": data_source,
        }
