from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any, Dict, Iterator, List

try:
    import yaml
except ImportError as exc:
    raise ImportError("PyYAML is required. Install with: pip install pyyaml") from exc

try:
    from torch.utils.data import Dataset
except Exception:
    class Dataset:  # type: ignore[override]
        """Fallback base class when PyTorch is not installed."""


from aishell1_dataset import AIShell1Dataset
from aishell3_dataset import AIShell3Dataset
from voiceassistant400k_dataset import VoiceAssistant400KDataset
from mmsu_dataset import MMSUDataset


class MultiDataset(Dataset):
    """从 YAML 配置文件加载多个数据集并合并。

    配置示例见 multi_dataset_config.yaml。
    每个数据集可独立设置 split 和 max_samples，合并后可选随机打乱。
    """

    def __init__(self, config_path: str | Path) -> None:
        self.config_path = Path(config_path).expanduser().resolve()
        config = self._load_config(self.config_path)

        output_cfg = config.get("output", {})
        self._shuffle = bool(output_cfg.get("shuffle", False))
        self._seed = output_cfg.get("seed", 42)

        self.samples: List[Dict[str, Any]] = []
        self._load_all(config.get("datasets", {}))

        if self._shuffle:
            rng = random.Random(self._seed)
            rng.shuffle(self.samples)

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_config(path: Path) -> Dict[str, Any]:
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {path}")
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    def _load_all(self, datasets_cfg: Dict[str, Any]) -> None:
        loaders = {
            "aishell1": self._load_aishell1,
            "aishell3": self._load_aishell3,
            "voiceassistant400k": self._load_voiceassistant400k,
            "mmsu": self._load_mmsu,
        }
        for name, cfg in datasets_cfg.items():
            if not cfg.get("enabled", True):
                continue
            loader = loaders.get(name)
            if loader is None:
                raise ValueError(f"Unknown dataset '{name}' in config.")
            root = cfg.get("root")
            if not root:
                raise ValueError(f"Dataset '{name}' is missing 'root' in config.")
            max_samples = cfg.get("max_samples") or None
            split = cfg.get("split", "")
            before = len(self.samples)
            loader(root=root, split=split, max_samples=max_samples)
            print(f"[{name}] loaded {len(self.samples) - before} samples")

    # ------------------------------------------------------------------
    # per-dataset loaders
    # ------------------------------------------------------------------

    def _load_aishell1(self, root: str, split: str, max_samples: int | None) -> None:
        ds = AIShell1Dataset(dataset_root=root, split=split)
        samples = ds.samples
        if max_samples is not None:
            samples = samples[:max_samples]
        self.samples.extend(samples)

    def _load_aishell3(self, root: str, split: str, max_samples: int | None) -> None:
        ds = AIShell3Dataset(dataset_root=root, split=split)
        samples = ds.samples
        if max_samples is not None:
            samples = samples[:max_samples]
        self.samples.extend(samples)

    def _load_voiceassistant400k(self, root: str, split: str, max_samples: int | None) -> None:
        ds = VoiceAssistant400KDataset(dataset_root=root)
        self.samples.extend(ds.iter_samples(max_samples=max_samples))

    def _load_mmsu(self, root: str, split: str, max_samples: int | None) -> None:
        ds = MMSUDataset(dataset_root=root, limit=max_samples)
        self.samples.extend(ds.samples)

    # ------------------------------------------------------------------
    # Dataset interface
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        return self.samples[index]

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return iter(self.samples)

    def to_jsonl(self, output_path: str | Path) -> Path:
        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as fh:
            for sample in self.samples:
                fh.write(json.dumps(sample, ensure_ascii=False) + "\n")
        return output_path


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="从 YAML 配置加载多个数据集并合并，可选导出为 jsonl。"
    )
    parser.add_argument(
        "--config",
        default=str(Path(__file__).parent / "multi_dataset_config.yaml"),
        help="YAML 配置文件路径（默认与本脚本同目录的 multi_dataset_config.yaml）。",
    )
    parser.add_argument(
        "--output",
        default="",
        help="可选输出 jsonl 文件路径。",
    )
    return parser


if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    dataset = MultiDataset(config_path=args.config)
    print(f"合并后共 {len(dataset)} 条样本")

    if args.output:
        out = dataset.to_jsonl(args.output)
        print(f"已保存至: {out}")
    elif len(dataset) > 0:
        print(json.dumps(dataset[0], ensure_ascii=False, indent=2))
