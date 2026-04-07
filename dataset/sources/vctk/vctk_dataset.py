from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset


@register_dataset("vctk")
class VCTKDataset(BaseDataset):
    """Load VCTK text and mic1 audio pairs and convert them to TTS samples."""

    _SUPPORTED_SPLITS = ("train",)

    def __init__(
        self,
        dataset_root: str | Path,
        split: str = "train",
        max_samples: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("vctk", dataset_root, **kwargs)
        normalized_split = (split or "").strip().lower()
        if normalized_split and normalized_split not in self._SUPPORTED_SPLITS:
            valid = '", "'.join(self._SUPPORTED_SPLITS)
            raise ValueError(
                f'Invalid split "{split}". Expected one of "{valid}" or empty.'
            )

        self.split = normalized_split or "train"
        self.max_samples = max_samples
        self.text_root = self.dataset_root / "txt"
        self.audio_root = self.dataset_root / "wav48_silence_trimmed"
        if not self.text_root.is_dir():
            raise FileNotFoundError(f"Text directory not found: {self.text_root}")
        if not self.audio_root.is_dir():
            raise FileNotFoundError(f"Audio directory not found: {self.audio_root}")

        self.stats = {
            "loaded": 0,
            "skipped_missing_audio_samples": 0,
            "skipped_empty_text_samples": 0,
        }
        self.load_data()

    def load_data(self) -> None:
        for speaker_dir in sorted(self.text_root.iterdir()):
            if not speaker_dir.is_dir():
                continue

            for text_path in sorted(speaker_dir.glob("*.txt")):
                if self.max_samples is not None and len(self.samples) >= self.max_samples:
                    return

                transcript = text_path.read_text(encoding="utf-8").strip()
                if not transcript:
                    self.stats["skipped_empty_text_samples"] += 1
                    continue

                speaker_id = speaker_dir.name
                stem = text_path.stem
                if not stem.startswith(f"{speaker_id}_"):
                    raise ValueError(f"Unexpected VCTK text filename: {text_path}")

                audio_path = self.audio_root / speaker_id / f"{stem}_mic1.flac"
                if not audio_path.is_file():
                    self.stats["skipped_missing_audio_samples"] += 1
                    continue

                utterance_id = stem[len(speaker_id) + 1 :]
                self.samples.append(
                    {
                        "id": f"vctk_{speaker_id}_{utterance_id}",
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
                        "data_source": "vctk",
                    }
                )
                self.stats["loaded"] += 1
