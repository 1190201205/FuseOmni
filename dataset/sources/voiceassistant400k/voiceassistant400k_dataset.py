from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Sequence

from dataset.base.dataset import BaseDataset
from dataset.registry import register_dataset

@register_dataset("voiceassistant400k")
class VoiceAssistant400KDataset(BaseDataset):
    """Convert VoiceAssistant-400K jsonl records to flat message/audio samples."""

    _AUDIO_PLACEHOLDER = "<|audio|>"

    def __init__(
        self,
        dataset_root: str | Path,
        metadata_name: str = "data.jsonl",
        max_samples: int | None = None,
        **kwargs: Any
    ) -> None:
        super().__init__("voiceassistant400k", dataset_root, **kwargs)
        self.metadata_path = self.dataset_root / metadata_name
        self.audio_root = self.dataset_root / "audio"

        if not self.metadata_path.is_file():
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_path}")
        if not self.audio_root.is_dir():
            raise FileNotFoundError(f"Audio directory not found: {self.audio_root}")

        self.last_stats = self._empty_stats()
        self.max_samples = max_samples

        self.load_data()

    @staticmethod
    def _empty_stats() -> Dict[str, int]:
        return {
            "loaded": 0,
            "skipped_missing_audio_samples": 0,
            "missing_audio_files": 0,
            "skipped_invalid_samples": 0,
        }

    def load_data(self) -> None:
        stats = self._empty_stats()

        with self.metadata_path.open("r", encoding="utf-8") as handle:
            for line_no, raw_line in enumerate(handle, start=1):
                if not raw_line.strip():
                    continue

                try:
                    record = json.loads(raw_line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON at {self.metadata_path}:{line_no}: {exc}") from exc

                sample = self._convert_record(record, stats)
                if sample is None:
                    continue

                self.samples.append(sample)
                stats["loaded"] += 1

                if self.max_samples is not None and stats["loaded"] >= self.max_samples:
                    break

        self.last_stats = stats

    def _convert_record(
        self,
        record: Dict[str, Any],
        stats: Dict[str, int],
    ) -> Dict[str, Any] | None:
        messages = record.get("messages")
        audio_rel_paths = record.get("audios")

        if not isinstance(messages, list) or not isinstance(audio_rel_paths, list):
            stats["skipped_invalid_samples"] += 1
            return None
        if not audio_rel_paths:
            stats["skipped_invalid_samples"] += 1
            return None

        audio_output_paths = self._resolve_audio_paths(audio_rel_paths, stats)
        if audio_output_paths is None:
            return None

        try:
            sample_id, data_source = self._build_metadata(audio_rel_paths)
        except ValueError:
            stats["skipped_invalid_samples"] += 1
            return None

        expected_audio_messages = 0
        transformed_messages: List[Dict[str, Any]] = []
        audio_index = 0

        for message in messages:
            if not isinstance(message, dict):
                stats["skipped_invalid_samples"] += 1
                return None

            role = message.get("role")
            if role not in {"system", "user", "assistant"}:
                stats["skipped_invalid_samples"] += 1
                return None

            normalized_message = {
                "content": [
                    {
                        "text": self._normalize_content(message.get("content")),
                        "audio_path": None
                    }
                ],
                "role": role
            }

            if role != "system":
                expected_audio_messages += 1
                if audio_index >= len(audio_output_paths):
                    stats["skipped_invalid_samples"] += 1
                    return None

                audio_role = Path(audio_rel_paths[audio_index]).parts[0]
                if audio_role != role:
                    stats["skipped_invalid_samples"] += 1
                    return None

                normalized_message["content"][0]["audio_path"] = audio_output_paths[audio_index]
                audio_index += 1

            transformed_messages.append(normalized_message)

        if expected_audio_messages != len(audio_output_paths):
            stats["skipped_invalid_samples"] += 1
            return None

        return {
            "id": sample_id,
            "task": "Dialogues",
            "data_source": data_source,
            "messages": transformed_messages,
        }

    def _resolve_audio_paths(
        self,
        audio_rel_paths: Sequence[Any],
        stats: Dict[str, int],
    ) -> List[str] | None:
        resolved_paths: List[str] = []

        for audio_rel_path in audio_rel_paths:
            if not isinstance(audio_rel_path, str) or not audio_rel_path.strip():
                stats["skipped_invalid_samples"] += 1
                return None

            audio_path = self.audio_root / Path(audio_rel_path)
            if not audio_path.is_file():
                stats["skipped_missing_audio_samples"] += 1
                stats["missing_audio_files"] += 1
                return None

            resolved_paths.append(self._format_output_path(audio_path))

        return resolved_paths

    def _build_metadata(self, audio_rel_paths: Sequence[str]) -> tuple[str, str]:
        parsed_paths = [self._parse_audio_rel_path(audio_rel_path) for audio_rel_path in audio_rel_paths]
        subsets = {subset for _, subset, _, _ in parsed_paths}
        speakers = {speaker for _, _, speaker, _ in parsed_paths}

        if len(subsets) != 1 or len(speakers) != 1:
            raise ValueError("Audio paths in one sample must share subset and speaker.")

        subset = parsed_paths[0][1]
        speaker = parsed_paths[0][2]
        stems = [stem for _, _, _, stem in parsed_paths]
        utterance_id = self._build_utterance_id(stems)

        sample_id = f"VoiceAssistant-400K_audio_{subset}_{speaker}_{utterance_id}"
        data_source = f"VoiceAssistant-400K_{subset}"
        return sample_id, data_source

    @staticmethod
    def _parse_audio_rel_path(audio_rel_path: str) -> tuple[str, str, str, str]:
        parts = Path(audio_rel_path).parts
        if len(parts) < 4:
            raise ValueError(f"Unexpected audio path format: {audio_rel_path}")

        role = parts[0]
        speaker = parts[-2]
        stem = Path(parts[-1]).stem
        subset = "_".join(parts[1:-2]) if len(parts) > 4 else parts[1]

        if role not in {"user", "assistant"}:
            raise ValueError(f"Unexpected audio role in path: {audio_rel_path}")

        return role, subset, speaker, stem

    @staticmethod
    def _build_utterance_id(stems: Sequence[str]) -> str:
        if not stems:
            raise ValueError("Audio stem list cannot be empty.")
        if len(set(stems)) == 1:
            return stems[0]

        common_prefix = os.path.commonprefix(list(stems)).rstrip("_-")
        return common_prefix or stems[0]

    @classmethod
    def _normalize_content(cls, content: Any) -> str | None:
        if content is None:
            return None

        normalized = content if isinstance(content, str) else str(content)
        if not normalized.strip():
            return None
        if normalized.strip() == cls._AUDIO_PLACEHOLDER:
            return None
        return normalized

    @staticmethod
    def _format_output_path(path: Path) -> str:
        try:
            relative_path = path.resolve().relative_to(Path.cwd().resolve())
            return relative_path.as_posix()
        except ValueError:
            return path.resolve().as_posix()
