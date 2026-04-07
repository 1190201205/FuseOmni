from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Any

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset

@register_dataset("aishell1")
class AIShell1Dataset(BaseDataset):
    """Load AIShell-1 CSV files and convert each row to message-format samples."""

    _SPLIT_TO_CSV = {
        "train": "speech_asr_aishell_trainsets.csv",
        "dev": "speech_asr_aishell_devsets.csv",
        "test": "speech_asr_aishell_testsets.csv",
    }
    _ASR_INSTRUCTION = BaseDataset.build_asr_instruction("Chinese")

    def __init__(self, dataset_root: str | Path, split: str = "", max_samples: int | None = None, **kwargs: Any) -> None:
        super().__init__("aishell1", dataset_root, **kwargs)
        normalized_split = (split or "").strip().lower()
        if normalized_split and normalized_split not in self._SPLIT_TO_CSV:
            valid = '", "'.join(self._SPLIT_TO_CSV.keys())
            raise ValueError(
                f'Invalid split "{split}". Expected one of "{valid}" or empty.'
            )

        self.splits = [normalized_split] if normalized_split else ["train", "dev", "test"]
        self.max_samples = max_samples
        
        self.load_data()

    def load_data(self) -> None:
        for split_name in self.splits:
            if self.max_samples is not None and len(self.samples) >= self.max_samples:
                break
            self._load_split(split_name)

    def _load_split(self, split_name: str) -> None:
        csv_path = self.dataset_root / self._SPLIT_TO_CSV[split_name]
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row_index, row in enumerate(reader, start=2):
                if self.max_samples is not None and len(self.samples) >= self.max_samples:
                    break
                    
                audio_rel_path = (row.get("Audio:FILE") or "").strip()
                transcript_raw = row.get("Text:LABEL") or ""

                if not audio_rel_path:
                    raise ValueError(f'Empty "Audio:FILE" at {csv_path}:{row_index}')

                transcript = self._normalize_transcript(transcript_raw)
                sample_id = self._build_sample_id(split_name, audio_rel_path)

                self.samples.append(
                    {
                        "id": sample_id,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "text": self._ASR_INSTRUCTION,
                                        "audio_path": f"/mnt/afs/share/voice_model_project/datasets/AIShell-1/{audio_rel_path}",
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
                        "data_source": f"aishell1_{split_name}",
                    }
                )

    @staticmethod
    def _normalize_transcript(transcript: str) -> str:
        return "".join(transcript.split())

    @staticmethod
    def _build_sample_id(split_name: str, audio_rel_path: str) -> str:
        audio_path = Path(audio_rel_path)
        speaker_id = audio_path.parent.name
        utterance_id = audio_path.stem
        return f"aishell1_{split_name}_{speaker_id}_{utterance_id}"
