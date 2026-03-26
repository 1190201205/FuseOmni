from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Sequence

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset


@register_dataset("wenetspeech")
class WenetSpeechDataset(BaseDataset):
    """Load WenetSpeech metadata and convert segments to message-format ASR samples."""

    _SUPPORTED_SUBSETS = ("L", "M", "S", "DEV", "TEST_NET", "TEST_MEETING")

    def __init__(
        self,
        dataset_root: str | Path,
        subset: str | Sequence[str] = "",
        max_samples: int | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__("wenetspeech", dataset_root, **kwargs)
        self.metadata_path = self._resolve_metadata_path()
        self.data_root = self.metadata_path.parent
        self.subsets = self._resolve_subsets(subset)
        self.max_samples = max_samples
        self.stats = {
            "loaded": 0,
            "skipped_missing_audio_samples": 0,
        }
        self.load_data()

    def load_data(self) -> None:
        for audio_entry in self._iter_audio_entries(self.metadata_path):
            audio_rel_path = str(audio_entry.get("path") or "").strip()
            if not audio_rel_path:
                continue

            audio_abs_path = self.data_root / audio_rel_path
            if not audio_abs_path.is_file():
                self.stats["skipped_missing_audio_samples"] += 1
                continue

            relative_audio_path = self._relative_audio_path(audio_abs_path)
            for segment in audio_entry.get("segments") or []:
                segment_subsets = [
                    str(item).strip().upper()
                    for item in segment.get("subsets") or []
                    if str(item).strip()
                ]
                if self.subsets and not set(segment_subsets).intersection(self.subsets):
                    continue

                text = self._normalize_transcript(segment.get("text", ""))
                if not text:
                    continue

                segment_id = str(segment.get("sid") or "").strip()
                if not segment_id:
                    continue

                self.samples.append(
                    {
                        "id": f"wenetspeech_{segment_id}",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "text": None,
                                        "audio_path": relative_audio_path,
                                        "audio_start_sec": float(
                                            segment.get("begin_time", 0.0)
                                        ),
                                        "audio_end_sec": float(
                                            segment.get("end_time", 0.0)
                                        ),
                                    }
                                ],
                            },
                            {
                                "role": "assistant",
                                "content": [
                                    {
                                        "text": text,
                                        "audio_path": None,
                                    }
                                ],
                            },
                        ],
                        "task": "ASR",
                        "data_source": self._build_data_source(segment_subsets),
                    }
                )
                self.stats["loaded"] += 1
                if self.max_samples is not None and len(self.samples) >= self.max_samples:
                    return

    def _resolve_metadata_path(self) -> Path:
        candidates = (
            self.dataset_root / "WenetSpeech.json",
            self.dataset_root / "train" / "WenetSpeech.json",
        )
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise FileNotFoundError(
            f"WenetSpeech metadata file not found under: {self.dataset_root}"
        )

    def _resolve_subsets(self, subset: str | Sequence[str]) -> List[str]:
        requested = [item.upper() for item in self.normalize_selection(subset)]
        if not requested:
            return []

        invalid = [
            subset_name
            for subset_name in requested
            if subset_name not in self._SUPPORTED_SUBSETS
        ]
        if invalid:
            valid = '", "'.join(self._SUPPORTED_SUBSETS)
            raise ValueError(
                f'Invalid subset "{invalid[0]}". Expected one of "{valid}" or empty.'
            )
        return requested

    def _relative_audio_path(self, audio_abs_path: Path) -> str:
        try:
            return audio_abs_path.relative_to(self.dataset_root).as_posix()
        except ValueError:
            return audio_abs_path.relative_to(self.data_root).as_posix()

    def _build_data_source(self, segment_subsets: List[str]) -> str:
        if self.subsets:
            return f"wenetspeech_{'_'.join(self.subsets)}"
        if segment_subsets:
            return f"wenetspeech_{'_'.join(segment_subsets)}"
        return "wenetspeech"

    @staticmethod
    def _normalize_transcript(transcript: str) -> str:
        return str(transcript or "").strip()

    @staticmethod
    def _iter_audio_entries(metadata_path: Path) -> Iterator[Dict[str, object]]:
        with metadata_path.open("r", encoding="utf-8") as handle:
            seen_audios_key = False
            in_array = False
            in_string = False
            escape = False
            brace_depth = 0
            buffer: List[str] = []
            key_window: List[str] = []

            while True:
                chunk = handle.read(8192)
                if not chunk:
                    break

                for char in chunk:
                    if not seen_audios_key:
                        key_window.append(char)
                        if len(key_window) > 16:
                            key_window.pop(0)
                        if "".join(key_window).endswith('"audios"'):
                            seen_audios_key = True
                        continue

                    if not in_array:
                        if char == "[":
                            in_array = True
                        continue

                    if brace_depth == 0:
                        if char == "{":
                            buffer = [char]
                            brace_depth = 1
                            in_string = False
                            escape = False
                        elif char == "]":
                            return
                        continue

                    buffer.append(char)
                    if in_string:
                        if escape:
                            escape = False
                        elif char == "\\":
                            escape = True
                        elif char == '"':
                            in_string = False
                        continue

                    if char == '"':
                        in_string = True
                    elif char == "{":
                        brace_depth += 1
                    elif char == "}":
                        brace_depth -= 1
                        if brace_depth == 0:
                            yield json.loads("".join(buffer))
                            buffer = []
