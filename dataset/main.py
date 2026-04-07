import argparse
import json
import random
from pathlib import Path
from typing import Any, Dict

try:
    import yaml
except ImportError as exc:
    raise ImportError("PyYAML is required. Install with: pip install pyyaml") from exc

from dataset.registry import build_dataset
from dataset.base.dataset import BaseDataset

# Ensure all dataset subclasses are registered by importing them
import dataset.sources.aishell1.aishell1_dataset
import dataset.sources.aishell3.aishell3_dataset
import dataset.sources.libritts.libritts_dataset
import dataset.sources.vctk.vctk_dataset
import dataset.sources.voiceassistant400k.voiceassistant400k_dataset
import dataset.sources.mmsu.mmsu_dataset
import dataset.sources.librispeech.librispeech_dataset
import dataset.sources.wenetspeech.wenetspeech_dataset
import dataset.sources.fleurs.fleurs_dataset
import dataset.sources.commonvoice.commonvoice_dataset
import dataset.sources.audiocaps.audiocaps_dataset
import dataset.sources.clotho.clotho_dataset
import dataset.sources.openhermes25.openhermes25_dataset
import dataset.sources.ultrachat.ultrachat_dataset
import dataset.sources.spoken_squad.spoken_squad_dataset
import dataset.sources.musan.musan_dataset
import dataset.sources.tulu3_sft_mixture.tulu3_sft_mixture_dataset


class MultiDataset(BaseDataset):
    """
    从 YAML 配置文件动态加载并合并多个按照 BaseDataset 重构的数据集。
    """
    def __init__(self, config_path: str | Path) -> None:
        super().__init__("multi_dataset", dataset_root="")
        self.config_path = Path(config_path).expanduser().resolve()
        config = self._load_config(self.config_path)

        output_cfg = config.get("output", {})
        self._shuffle = bool(output_cfg.get("shuffle", False))
        self._seed = output_cfg.get("seed", 42)
        
        self.datasets_cfg = config.get("datasets", {})

        # 基类约定的加载数据方法
        self.load_data()

        if self._shuffle:
            rng = random.Random(self._seed)
            rng.shuffle(self.samples)

    @staticmethod
    def _load_config(path: Path) -> Dict[str, Any]:
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {path}")
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    def load_data(self) -> None:
        for name, cfg in self.datasets_cfg.items():
            if not cfg.get("enabled", True):
                continue
            
            root = cfg.get("root")
            if not root:
                raise ValueError(f"Dataset '{name}' is missing 'root' in config.")
                
            before = len(self.samples)
            dataset_kwargs = {
                key: value
                for key, value in cfg.items()
                if key not in {"enabled", "root"}
            }
            if dataset_kwargs.get("max_samples") == "":
                dataset_kwargs["max_samples"] = None

            # 动态构建注册的数据集
            ds = build_dataset(
                name=name,
                dataset_root=root,
                **dataset_kwargs,
            )
            self.samples.extend(ds.samples)
            print(f"[{name}] loaded {len(self.samples) - before} samples")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="从 YAML 配置动态加载多个数据集并合并，可选导出为 jsonl。"
    )
    # Default config points to dataset/load_dataset/multi_dataset_config.yaml
    default_config = Path(__file__).parent / "load_dataset" / "multi_dataset_config.yaml"
    parser.add_argument(
        "--config",
        default=str(default_config),
        help="YAML 配置文件路径。",
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
