# 多数据集加载器

## 文件说明

| 文件 | 说明 |
|------|------|
| `multi_dataset.py` | 多数据集加载主程序 |
| `multi_dataset_config.yaml` | 数据集配置文件 |

## 快速开始

```bash
# 使用默认配置，打印第一条样本预览
python load_dataset/multi_dataset.py

# 指定配置文件
python load_dataset/multi_dataset.py --config my_config.yaml

# 导出合并后的数据为 jsonl
python load_dataset/multi_dataset.py --output train.jsonl
```

## 配置文件说明

```yaml
datasets:
  aishell1:
    enabled: true          # 是否启用该数据集
    root: datasets/AIShell-1  # 数据集根目录
    split: train           # 加载哪个分片，空字符串表示全部
    max_samples: 5000      # 最多加载多少条，null 表示不限

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

## 扩展新数据集

1. 在 `multi_dataset.py` 的 `_load_all` 方法中的 `loaders` 字典注册新数据集名称和对应加载方法：

```python
loaders = {
    ...
    "my_dataset": self._load_my_dataset,
}
```

2. 实现对应的加载方法：

```python
def _load_my_dataset(self, root: str, split: str, max_samples: int | None) -> None:
    ds = MyDataset(dataset_root=root, split=split)
    samples = ds.samples[:max_samples] if max_samples else ds.samples
    self.samples.extend(samples)
```

3. 在 `multi_dataset_config.yaml` 中添加配置项：

```yaml
datasets:
  my_dataset:
    enabled: true
    root: datasets/MyDataset
    split: train
    max_samples: 1000
```
