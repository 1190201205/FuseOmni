from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterator, List, Sequence

try:
    from torch.utils.data import Dataset
except Exception:  # pragma: no cover - fallback for environments without torch
    class Dataset:  # type: ignore[override]
        """Fallback base class when PyTorch is not installed."""


class VoiceAssistant400KDataset(Dataset):
    """Convert VoiceAssistant-400K jsonl records to flat message/audio samples."""

    _AUDIO_PLACEHOLDER = "<|audio|>"

    def __init__(
        self,
        dataset_root: str | Path,
        metadata_name: str = "data.jsonl",
        load_all: bool = False,
    ) -> None:
        self.dataset_root = Path(dataset_root).expanduser().resolve()
        self.metadata_path = self.dataset_root / metadata_name
        self.audio_root = self.dataset_root / "audio"

        if not self.metadata_path.is_file():
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_path}")
        if not self.audio_root.is_dir():
            raise FileNotFoundError(f"Audio directory not found: {self.audio_root}")

        self.samples: List[Dict[str, Any]] | None = None
        self.last_stats = self._empty_stats()

        if load_all:
            self.samples = list(self.iter_samples())

    @staticmethod
    def _empty_stats() -> Dict[str, int]:
        return {
            "loaded": 0,
            "skipped_missing_audio_samples": 0,
            "missing_audio_files": 0,
            "skipped_invalid_samples": 0,
        }

    def _iter_samples(self, max_samples: int | None = None) -> Iterator[Dict[str, Any]]:
        stats = self._empty_stats()

        with self.metadata_path.open("r", encoding="utf-8") as handle:
            for line_no, raw_line in enumerate(handle, start=1):
                if not raw_line.strip():
                    continue

                try:
                    record = json.loads(raw_line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON at {self.metadata_path}:{line_no}: {exc}"
                    ) from exc

                sample = self._convert_record(record, stats)
                if sample is None:
                    continue

                stats["loaded"] += 1
                yield sample

                if max_samples is not None and stats["loaded"] >= max_samples:
                    break

        self.last_stats = stats

    def iter_samples(self, max_samples: int | None = None) -> Iterator[Dict[str, Any]]:
        return self._iter_samples(max_samples=max_samples)

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
                # "content": self._normalize_content(message.get("content")),
                # "audio": None,
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

                # normalized_message["audio"] = audio_output_paths[audio_index]
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

    def _materialize(self) -> None:
        if self.samples is None:
            self.samples = list(self.iter_samples())

    def __len__(self) -> int:
        self._materialize()
        assert self.samples is not None
        return len(self.samples)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        self._materialize()
        assert self.samples is not None
        return self.samples[index]

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        if self.samples is not None:
            return iter(self.samples)
        return self.iter_samples()

    def to_jsonl(
        self,
        output_path: str | Path,
        max_samples: int | None = None,
    ) -> Path:
        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self.samples is not None and max_samples is None:
            sample_iterable: Iterator[Dict[str, Any]] | List[Dict[str, Any]] = self.samples
        else:
            sample_iterable = self.iter_samples(max_samples=max_samples)

        with output_path.open("w", encoding="utf-8") as handle:
            for sample in sample_iterable:
                handle.write(json.dumps(sample, ensure_ascii=False) + "\n")

        return output_path


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert VoiceAssistant-400K data.jsonl into flat message/audio jsonl."
    )
    parser.add_argument(
        "dataset_root",
        help="Path to VoiceAssistant-400K root directory.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output jsonl file path.",
    )
    parser.add_argument(
        "--metadata-name",
        default="data.jsonl",
        help='Metadata filename under dataset root. Defaults to "data.jsonl".',
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional maximum number of valid samples to process.",
    )
    parser.add_argument(
        "--load-all",
        action="store_true",
        help="Load all converted samples into memory for Dataset-style access.",
    )
    return parser


if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    limit = args.limit if args.limit > 0 else None

    dataset = VoiceAssistant400KDataset(
        dataset_root=args.dataset_root,
        metadata_name=args.metadata_name,
        load_all=args.load_all,
    )

    if args.output:
        output_path = dataset.to_jsonl(args.output, max_samples=limit)
        print(f"Saved converted samples to: {output_path}")
        print(
            "Stats: "
            f"loaded={dataset.last_stats['loaded']}, "
            f"skipped_missing_audio_samples={dataset.last_stats['skipped_missing_audio_samples']}, "
            f"missing_audio_files={dataset.last_stats['missing_audio_files']}, "
            f"skipped_invalid_samples={dataset.last_stats['skipped_invalid_samples']}"
        )
    else:
        preview_samples = list(dataset.iter_samples(max_samples=1))
        if not preview_samples:
            print("No valid samples found.")
        else:
            print(json.dumps(preview_samples[0], ensure_ascii=False, indent=2))
            print(
                "Stats: "
                f"loaded={dataset.last_stats['loaded']}, "
                f"skipped_missing_audio_samples={dataset.last_stats['skipped_missing_audio_samples']}, "
                f"missing_audio_files={dataset.last_stats['missing_audio_files']}, "
                f"skipped_invalid_samples={dataset.last_stats['skipped_invalid_samples']}"
            )
