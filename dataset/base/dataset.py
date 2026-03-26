from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence

try:
    from torch.utils.data import Dataset as TorchDataset
except ImportError:
    class TorchDataset:  # type: ignore[no-redef]
        """Fallback base class when PyTorch is not installed."""
        pass


class BaseDataset(TorchDataset):
    """
    统一的数据集基类。
    提供基础的样本遍历、长度获取、索引访问以及导出到 jsonl 的功能。
    子类需要实现 `load_data`，并将加载的字典添加到 `self.samples` 或者覆盖 `__iter__` 方法以支持流式读取。
    """
    
    def __init__(self, dataset_name: str, dataset_root: str | Path, **kwargs: Any) -> None:
        self.dataset_name = dataset_name
        self.dataset_root = Path(dataset_root).expanduser().resolve()
        # 默认将加载的样本存储在列表中
        self.samples: List[Dict[str, Any]] = []
        
    def load_data(self) -> None:
        """
        子类应该重写此方法去实际加载数据，并填充到 self.samples
        """
        raise NotImplementedError("Subclasses must implement `load_data`.")

    def format_process(self, raw_sample: Any) -> Dict[str, Any] | None:
        """
        可选的方法：将原始的一条数据格式化为框架需要的 Message 字典结构。
        返回 None 表示该条数据无效或跳过。
        """
        raise NotImplementedError("Subclasses must implement `format_process` if used.")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        return self.samples[index]

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return iter(self.samples)

    def to_jsonl(self, output_path: str | Path, max_samples: Optional[int] = None) -> Path:
        """
        将当前数据集导出为 jsonl 文件。
        """
        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        count = 0
        with output_path.open("w", encoding="utf-8") as handle:
            for sample in self:
                if max_samples is not None and count >= max_samples:
                    break
                handle.write(json.dumps(sample, ensure_ascii=False) + "\n")
                count += 1
        return output_path

    @staticmethod
    def normalize_selection(value: str | Sequence[str] | None) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]

        normalized: List[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                normalized.append(text)
        return normalized

    @staticmethod
    def load_jsonl_paths(
        jsonl_paths: Sequence[str | Path],
        max_samples: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        samples: List[Dict[str, Any]] = []

        for raw_path in jsonl_paths:
            jsonl_path = Path(raw_path).expanduser().resolve()
            if not jsonl_path.is_file():
                raise FileNotFoundError(f"JSONL file not found: {jsonl_path}")

            with jsonl_path.open("r", encoding="utf-8") as handle:
                for line_index, raw_line in enumerate(handle, start=1):
                    if max_samples is not None and len(samples) >= max_samples:
                        return samples

                    line = raw_line.strip()
                    if not line:
                        continue

                    try:
                        samples.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        raise ValueError(
                            f"Invalid JSONL at {jsonl_path}:{line_index}"
                        ) from exc

        return samples
