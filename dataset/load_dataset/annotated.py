from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterator, List

# =========================
# 1) 依赖导入与兼容兜底
# =========================
# 优先使用 PyTorch 的 Dataset 基类；
# 如果当前环境未安装 torch，则定义一个同名空基类，让脚本仍可运行（例如仅做数据转换）。
try:
    from torch.utils.data import Dataset
except Exception:  # pragma: no cover - fallback for environments without torch
    class Dataset:  # type: ignore[override]
        """Fallback base class when PyTorch is not installed."""


# =========================
# 2) AIShell-1 数据集封装
# =========================
# 作用：读取 AIShell-1 的 csv 标注文件，转换成统一 message-format 样本结构。
class AIShell1Dataset(Dataset):
    """Load AIShell-1 CSV files and convert each row to message-format samples."""

    # split 名称与对应 csv 文件映射
    _SPLIT_TO_CSV = {
        "train": "speech_asr_aishell_trainsets.csv",
        "dev": "speech_asr_aishell_devsets.csv",
        "test": "speech_asr_aishell_testsets.csv",
    }

    # -------------------------
    # 2.1 初始化与参数校验
    # -------------------------
    # - 支持单个 split（train/dev/test）或空字符串表示全部
    # - 规范化路径、构建 split 列表、汇总样本到 self.samples
    def __init__(self, dataset_root: str | Path, split: str = "") -> None:
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

    # -------------------------
    # 2.2 加载单个 split
    # -------------------------
    # - 读取 csv
    # - 校验 Audio:FILE 不为空
    # - 清洗文本标签
    # - 构建统一样本结构（messages/task/data_source）
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
                                        "audio_path": audio_rel_path,
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

    # -------------------------
    # 2.3 文本清洗
    # -------------------------
    # AIShell 标签常是“按字 + 空格分隔”，这里把所有空白去掉，得到连续文本。
    @staticmethod
    def _normalize_transcript(transcript: str) -> str:
        return "".join(transcript.split())

    # -------------------------
    # 2.4 样本 ID 构造
    # -------------------------
    # 从音频相对路径中提取说话人目录名和音频文件名（不含后缀），生成唯一 ID。
    @staticmethod
    def _build_sample_id(split_name: str, audio_rel_path: str) -> str:
        audio_path = Path(audio_rel_path)
        speaker_id = audio_path.parent.name
        utterance_id = audio_path.stem
        return f"aishell1_{split_name}_{speaker_id}_{utterance_id}"

    # -------------------------
    # 2.5 Dataset 协议方法
    # -------------------------
    # 提供长度、按索引访问、可迭代能力，兼容常见数据管道。
    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> Dict[str, object]:
        return self.samples[index]

    def __iter__(self) -> Iterator[Dict[str, object]]:
        return iter(self.samples)

    # -------------------------
    # 2.6 导出为 JSONL
    # -------------------------
    # 每行一个 JSON 样本，便于后续训练/处理流水线消费。
    def to_jsonl(self, output_path: str | Path) -> Path:
        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            for sample in self.samples:
                handle.write(json.dumps(sample, ensure_ascii=False) + "\n")
        return output_path


# =========================
# 3) 命令行参数定义
# =========================
# 支持：
# - 必填 dataset_root
# - 可选 split
# - 可选 output（若提供则导出 jsonl）
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


# =========================
# 4) 脚本入口
# =========================
# - 加载数据集并打印样本数
# - 如果传了 --output 就导出 jsonl
# - 否则打印第一条样本（用于快速检查）
if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    dataset = AIShell1Dataset(dataset_root=args.dataset_root, split=args.split)
    print(f"Loaded {len(dataset)} samples from splits: {', '.join(dataset.splits)}")

    if args.output:
        output_path = dataset.to_jsonl(args.output)
        print(f"Saved converted samples to: {output_path}")
    elif len(dataset) > 0:
        print(json.dumps(dataset[0], ensure_ascii=False, indent=2))