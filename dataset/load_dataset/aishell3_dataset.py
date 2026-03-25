from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterator, List

try:
    from torch.utils.data import Dataset
except Exception:  # pragma: no cover - fallback for environments without torch
    class Dataset:  # type: ignore[override]
        """Fallback base class when PyTorch is not installed."""


class AIShell3Dataset(Dataset):
    """Load AISHELL-3 content files and convert each row to TTS message samples."""

    _SUPPORTED_SPLITS = ("train", "test")
    _PINYIN_TOKEN_RE = re.compile(r"^[a-z]+[0-5]?$")

    def __init__(self, dataset_root: str | Path, split: str = "") -> None:
        """
        Args:
            dataset_root: Path to `datasets/AISHELL-3`.
            split: One of "train", "test", or empty string for all splits.
        """
        normalized_split = (split or "").strip().lower()
        if normalized_split and normalized_split not in self._SUPPORTED_SPLITS:
            valid = '", "'.join(self._SUPPORTED_SPLITS)
            raise ValueError(
                f'Invalid split "{split}". Expected one of "{valid}" or empty.'
            )

        self.dataset_root = Path(dataset_root).expanduser().resolve()
        self.splits = [normalized_split] if normalized_split else list(self._SUPPORTED_SPLITS)
        self.samples: List[Dict[str, object]] = []
        self.stats = self._empty_stats()

        for split_name in self.splits:
            self.samples.extend(self._load_split(split_name))

    @staticmethod
    def _empty_stats() -> Dict[str, int]:
        return {
            "loaded": 0,
            "skipped_missing_audio_samples": 0,
        }

    def _load_split(self, split_name: str) -> List[Dict[str, object]]:
        split_root = self.dataset_root / split_name
        content_path = split_root / "content.txt"
        wav_root = split_root / "wav"

        if not content_path.is_file():
            raise FileNotFoundError(f"Content file not found: {content_path}")
        if not wav_root.is_dir():
            raise FileNotFoundError(f"Wav directory not found: {wav_root}")

        split_samples: List[Dict[str, object]] = []
        with content_path.open("r", encoding="utf-8") as handle:
            for row_index, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line:
                    continue

                parts = line.split("\t", maxsplit=1)
                if len(parts) != 2:
                    raise ValueError(
                        f"Invalid content format at {content_path}:{row_index}"
                    )

                audio_name, transcript_raw = parts
                audio_rel_path = self._build_audio_rel_path(split_name, audio_name)
                audio_abs_path = self.dataset_root / audio_rel_path

                if not audio_abs_path.is_file():
                    self.stats["skipped_missing_audio_samples"] += 1
                    continue

                transcript = self._normalize_transcript(transcript_raw)
                if not transcript:
                    raise ValueError(
                        f"Empty transcript after normalization at {content_path}:{row_index}"
                    )

                sample_id = self._build_sample_id(split_name, audio_name)
                split_samples.append(
                    {
                        "id": sample_id,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "text": transcript,
                                        "audio_path": None,
                                    }
                                ],
                            },
                            {
                                "role": "assistant",
                                "content": [
                                    {
                                        "text": None,
                                        "audio_path": f"/mnt/afs/share/voice_model_project/datasets/AISHELL-3/{audio_rel_path}",
                                    }
                                ],
                            },
                        ],
                        "task": "TTS",
                        "data_source": f"aishell3_{split_name}",
                    }
                )
                self.stats["loaded"] += 1

        return split_samples

    @classmethod
    def _normalize_transcript(cls, transcript: str) -> str:
        tokens = transcript.split()
        if not tokens:
            return ""

        odd_tokens = tokens[1::2]
        if odd_tokens and all(cls._looks_like_pinyin(token) for token in odd_tokens):
            return "".join(tokens[::2])

        cleaned_tokens = [token for token in tokens if not cls._looks_like_pinyin(token)]
        return "".join(cleaned_tokens)

    @classmethod
    def _looks_like_pinyin(cls, token: str) -> bool:
        return bool(cls._PINYIN_TOKEN_RE.fullmatch(token))

    @staticmethod
    def _build_audio_rel_path(split_name: str, audio_name: str) -> str:
        utterance_id = Path(audio_name).stem
        if len(utterance_id) < 7:
            raise ValueError(f"Unexpected utterance id format: {audio_name}")

        speaker_id = utterance_id[:7]
        return Path(split_name, "wav", speaker_id, audio_name).as_posix()

    @staticmethod
    def _build_sample_id(split_name: str, audio_name: str) -> str:
        utterance_id = Path(audio_name).stem
        if len(utterance_id) < 7:
            raise ValueError(f"Unexpected utterance id format: {audio_name}")

        speaker_id = utterance_id[:7]
        return f"aishell3_{split_name}_{speaker_id}_{utterance_id}"

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
        description="Load AISHELL-3 and optionally export as TTS jsonl."
    )
    parser.add_argument(
        "dataset_root",
        help="Path to AISHELL-3 root directory (contains train/ and test/).",
    )
    parser.add_argument(
        "--split",
        default="",
        help='Split name: "train", "test", or empty for all.',
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output jsonl file path.",
    )
    return parser


if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    dataset = AIShell3Dataset(dataset_root=args.dataset_root, split=args.split)
    print(f"Loaded {len(dataset)} samples from splits: {', '.join(dataset.splits)}")
    if dataset.stats["skipped_missing_audio_samples"] > 0:
        print(
            "Skipped "
            f"{dataset.stats['skipped_missing_audio_samples']} samples with missing audio files."
        )

    if args.output:
        output_path = dataset.to_jsonl(args.output)
        print(f"Saved converted samples to: {output_path}")
    elif len(dataset) > 0:
        print(json.dumps(dataset[0], ensure_ascii=False, indent=2))
