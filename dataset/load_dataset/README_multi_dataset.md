# 多数据集加载器

## 文件说明

| 文件 | 说明 |
|------|------|
| `../main.py` | 多数据集加载主程序 |
| `multi_dataset_config.yaml` | 数据集配置文件 |

## 快速开始

```bash
# 使用默认配置，打印第一条样本预览
python -m dataset.main

# 指定配置文件
python -m dataset.main --config dataset/load_dataset/my_config.yaml

# 导出合并后的数据为 jsonl
python -m dataset.main --output train.jsonl
```

## 配置文件说明

```yaml
datasets:
  aishell1:
    enabled: true          # 是否启用该数据集
    root: datasets/AIShell-1  # 数据集根目录
    split: train           # 加载哪个分片，空字符串表示全部
    max_samples: 5000      # 最多加载多少条，null 表示不限

  fleurs:
    enabled: false
    root: datasets/FLEURS
    split: train
    language: en_us
    max_samples: 1000

output:
  shuffle: true            # 合并后是否随机打乱
  seed: 42                 # 随机种子
```

### 各数据集支持的 split

| 数据集 | 可用 split |
|--------|-----------|
| `aishell1` | `train` / `dev` / `test` / `""`（全部） |
| `aishell3` | `train` / `test` / `""`（全部） |
| `voiceassistant400k` | 无 split 概念，忽略该字段 |
| `mmsu` | 无 split 概念，忽略该字段 |
| `librispeech` | 使用 `subset` 指定一个或多个训练子集 |
| `wenetspeech` | 使用 `subset` 指定 `L/M/S/DEV/TEST_*` |
| `fleurs` | 使用 `split` 和 `language` |
| `commonvoice` | 使用 `split` 和 `language` |
| `audiocaps` | `train` / `validation` / `test` / `""`（全部） |
| `clotho` | `train` / `validation` / `test` / `""`（全部） |
| `openhermes25` | 无 split 概念，默认读取处理后的 jsonl |
| `tulu3_sft_mixture` | `split=train`，可用 `subset` 指定 shard 文件名 |

## 扩展新数据集

1. 在 `dataset/sources/<name>/` 下创建新的 `*_dataset.py`，继承 `BaseDataset` 并使用 `register_dataset(...)` 注册：

```python
@register_dataset("my_dataset")
class MyDataset(BaseDataset):
    def __init__(self, dataset_root: str | Path, max_samples: int | None = None, **kwargs):
        super().__init__("my_dataset", dataset_root, **kwargs)
        self.max_samples = max_samples
        self.load_data()
```

2. 在 `dataset/main.py` 中增加对应模块导入，确保注册生效。

3. 在 `multi_dataset_config.yaml` 中添加配置项。除了 `enabled` 和 `root` 以外，其余字段会透传给具体数据集构造函数：

```yaml
datasets:
  my_dataset:
    enabled: true
    root: datasets/MyDataset
    split: train
    language: en_us
    max_samples: 1000
```
