from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterator, List

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore

try:
    from torch.utils.data import Dataset
except Exception:
    class Dataset:  # type: ignore[override]
        """Fallback base class when PyTorch is not installed."""


class MMSUDataset(Dataset):
    """Load MMSU parquet files and convert to message-format samples for AudioQA."""

    def __init__(
        self,
        dataset_root: str | Path,
        limit: int | None = None,
    ) -> None:
        """
        Args:
            dataset_root: Path to `datasets/MMSU`.
            limit: Optional limit on number of samples to load.
        """
        if pd is None:
            raise ImportError("pandas is required. Install with: pip install pandas")

        self.dataset_root = Path(dataset_root).expanduser().resolve()
        self.samples: List[Dict[str, object]] = []

        self._load_parquet_files(limit)

    def _load_parquet_files(self, limit: int | None) -> None:
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
                if limit is not None and count >= limit:
                    break
                
                sample = self._convert_row(row)
                
                # 如果返回 None，说明音频文件不存在，跳过该数据
                if sample is None:
                    skipped_count += 1
                    continue
                    
                self.samples.append(sample)
                count += 1
        
        print(f"Finished loading. Valid: {count}, Skipped (not found): {skipped_count}")

    def _convert_row(self, row) -> Dict[str, object] | None:
        sample_id = row.get("id", "")
        question = row.get("question", "")
        choice_a = row.get("choice_a", "")
        choice_b = row.get("choice_b", "")
        choice_c = row.get("choice_c", "")
        choice_d = row.get("choice_d", "")
        answer_gt = row.get("answer_gt", "")
        category = row.get("category", "")

        # 1. 获取原始音频文件名
        audio_info = row.get("audio", {})
        if isinstance(audio_info, dict):
            audio_filename = audio_info.get("path", "")
        else:
            audio_filename = str(audio_info) if audio_info else ""

        if not audio_filename:
            return None

        # 2. 移除可能已有的后缀，准备尝试 .wav 和 .mp3
        # 去掉 audio/ 前缀以便统一处理
        clean_name = audio_filename.replace("audio/", "")
        pure_name = Path(clean_name).stem  # 获取不带后缀的文件名
        
        # 3. 检查文件是否存在 (尝试 .wav 和 .mp3)
        found_audio_path = None
        # 基础目录，根据报错信息拼接
        base_audio_dir = self.dataset_root / "audio"
        
        for ext in [".wav", ".mp3"]:
            test_path = base_audio_dir / f"{pure_name}{ext}"
            if test_path.exists():
                found_audio_path = str(test_path)
                break
        
        # 4. 如果没找到，返回 None 以便删除（跳过）该样本
        if found_audio_path is None:
            # print(f"Warning: Audio file not found for {pure_name} (tried .wav/.mp3). Skipping.")
            return None

        # Format question with choices
        question_text = f"{question}\nA. {choice_a}\nB. {choice_b}\nC. {choice_c}\nD. {choice_d}"

        # Build data_source from category
        data_source = f"MMSU_{category}" if category else "MMSU"

        return {
            "id": f"MMSU_{sample_id}",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": question_text,
                            "audio_path": found_audio_path, # 使用检查后存在的绝对路径
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
        description="Load MMSU dataset and optionally export as jsonl."
    )
    parser.add_argument(
        "dataset_root",
        help="Path to MMSU root directory (contains data/*.parquet).",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output jsonl file path.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on number of samples.",
    )
    return parser


if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    # 这里的 dataset_root 传入 /mnt/afs/share/voice_model_project/datasets/MMSU
    dataset = MMSUDataset(dataset_root=args.dataset_root, limit=args.limit)
    print(f"Successfully loaded {len(dataset)} samples")

    if args.output:
        output_path = dataset.to_jsonl(args.output)
        print(f"Saved converted samples to: {output_path}")
    elif len(dataset) > 0:
        print(json.dumps(dataset[0], ensure_ascii=False, indent=2))