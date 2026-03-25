from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterator, List

try:
    from torch.utils.data import Dataset
except Exception:  # pragma: no cover - fallback for environments without torch
    class Dataset:  # type: ignore[override]
        """Fallback base class when PyTorch is not installed."""


class AIShell1Dataset(Dataset):
    """Load AIShell-1 CSV files and convert each row to message-format samples."""

    _SPLIT_TO_CSV = {
        "train": "speech_asr_aishell_trainsets.csv",
        "dev": "speech_asr_aishell_devsets.csv",
        "test": "speech_asr_aishell_testsets.csv",
    }

    def __init__(self, dataset_root: str | Path, split: str = "") -> None:
        """
        Args:
            dataset_root: Path to `datasets/AIShell-1`.
            split: One of "train", "dev", "test", or empty string for all splits.
        """
        normalized_split = (split or "").strip().lower()
        if normalized_split and normalized_split not in self._SPLIT_TO_CSV:
            valid = '", "'.join(self._SPLIT_TO_CSV.keys())
            raise ValueError(
                f'Invalid split "{split}". Expected one of "{valid}" or empty.'
            )

        self.dataset_root = Path(dataset_root).expanduser().resolve()
        self.splits = [normalized_split] if normalized_split else ["train", "dev", "test"]
        self.samples: List[Dict[str, object]] = []

        for split_name in self.splits:
            self.samples.extend(self._load_split(split_name))

    def _load_split(self, split_name: str) -> List[Dict[str, object]]:
        csv_path = self.dataset_root / self._SPLIT_TO_CSV[split_name]
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        split_samples: List[Dict[str, object]] = []
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row_index, row in enumerate(reader, start=2):
                audio_rel_path = (row.get("Audio:FILE") or "").strip()
                transcript_raw = row.get("Text:LABEL") or ""

                if not audio_rel_path:
                    raise ValueError(
                        f'Empty "Audio:FILE" at {csv_path}:{row_index}'
                    )

                transcript = self._normalize_transcript(transcript_raw)
                sample_id = self._build_sample_id(split_name, audio_rel_path)

                split_samples.append(
                    {
                        "id": sample_id,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "text": None,
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

        return split_samples

    @staticmethod
    def _normalize_transcript(transcript: str) -> str:
        # AIShell labels are whitespace-separated chars, e.g. "甚 至 ..."; remove all gaps.
        return "".join(transcript.split())

    @staticmethod
    def _build_sample_id(split_name: str, audio_rel_path: str) -> str:
        audio_path = Path(audio_rel_path)
        speaker_id = audio_path.parent.name
        utterance_id = audio_path.stem
        return f"aishell1_{split_name}_{speaker_id}_{utterance_id}"

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> Dict[str, object]:
        return self.samples[index]

    def __iter__(self) -> Iterator[Dict[str, object]]:
        return iter(self.samples)

    def to_jsonl(self, output_path: str | Path) -> Path:
        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            for sample in self.samples:
                handle.write(json.dumps(sample, ensure_ascii=False) + "\n")
        return output_path


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Load AIShell-1 and optionally export as jsonl."
    )
    parser.add_argument(
        "dataset_root",
        help="Path to AIShell-1 root directory (contains speech_asr_aishell_*sets.csv).",
    )
    parser.add_argument(
        "--split",
        default="",
        help='Split name: "train", "dev", "test", or empty for all.',
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output jsonl file path.",
    )
    return parser


if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    dataset = AIShell1Dataset(dataset_root=args.dataset_root, split=args.split)
    print(f"Loaded {len(dataset)} samples from splits: {', '.join(dataset.splits)}")

    if args.output:
        output_path = dataset.to_jsonl(args.output)
        print(f"Saved converted samples to: {output_path}")
    elif len(dataset) > 0:
        print(json.dumps(dataset[0], ensure_ascii=False, indent=2))
