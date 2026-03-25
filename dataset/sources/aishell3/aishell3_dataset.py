from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Any

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset

@register_dataset("aishell3")
class AIShell3Dataset(BaseDataset):
    """Load AISHELL-3 content files and convert each row to TTS message samples."""

    _SUPPORTED_SPLITS = ("train", "test")
    _PINYIN_TOKEN_RE = re.compile(r"^[a-z]+[0-5]?$")

    def __init__(self, dataset_root: str | Path, split: str = "", max_samples: int | None = None, **kwargs: Any) -> None:
        super().__init__("aishell3", dataset_root, **kwargs)
        normalized_split = (split or "").strip().lower()
        if normalized_split and normalized_split not in self._SUPPORTED_SPLITS:
            valid = '", "'.join(self._SUPPORTED_SPLITS)
            raise ValueError(
                f'Invalid split "{split}". Expected one of "{valid}" or empty.'
            )

        self.splits = [normalized_split] if normalized_split else list(self._SUPPORTED_SPLITS)
        self.stats = self._empty_stats()
        self.max_samples = max_samples

        self.load_data()

    @staticmethod
    def _empty_stats() -> Dict[str, int]:
        return {"loaded": 0, "skipped_missing_audio_samples": 0}

    def load_data(self) -> None:
        for split_name in self.splits:
            if self.max_samples is not None and len(self.samples) >= self.max_samples:
                break
            self._load_split(split_name)

    def _load_split(self, split_name: str) -> None:
        split_root = self.dataset_root / split_name
        content_path = split_root / "content.txt"
        wav_root = split_root / "wav"

        if not content_path.is_file():
            raise FileNotFoundError(f"Content file not found: {content_path}")
        if not wav_root.is_dir():
            raise FileNotFoundError(f"Wav directory not found: {wav_root}")

        with content_path.open("r", encoding="utf-8") as handle:
            for row_index, raw_line in enumerate(handle, start=1):
                if self.max_samples is not None and len(self.samples) >= self.max_samples:
                    break

                line = raw_line.strip()
                if not line:
                    continue

                parts = line.split("\t", maxsplit=1)
                if len(parts) != 2:
                    raise ValueError(f"Invalid content format at {content_path}:{row_index}")

                audio_name, transcript_raw = parts
                audio_rel_path = self._build_audio_rel_path(split_name, audio_name)
                audio_abs_path = self.dataset_root / audio_rel_path

                if not audio_abs_path.is_file():
                    self.stats["skipped_missing_audio_samples"] += 1
                    continue

                transcript = self._normalize_transcript(transcript_raw)
                if not transcript:
                    raise ValueError(f"Empty transcript after normalization at {content_path}:{row_index}")

                sample_id = self._build_sample_id(split_name, audio_name)
                self.samples.append(
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
