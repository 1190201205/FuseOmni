# 多数据集加载器

## 文件说明

| 文件 | 说明 |
|------|------|
| `../main.py` | 多数据集加载主程序，通过配置动态构建并合并多个 `dataset/sources/*` loader |
| `multi_dataset_config.yaml` | 多数据集配置文件，除 `enabled` / `root` 外的字段会作为 `kwargs` 透传给对应 loader |
| `verify_local_dataset_samples.py` | 本地抽样校验脚本，会按配置文件读取各数据集并检查样本结构与 `audio_path` |
| `LOCAL_DATASET_SAMPLE_VALIDATION_REPORT.md` | 本地抽样校验报告 |
| `ASR_PROMPT_SAMPLE_REPORT.md` | ASR 指令模板抽样报告 |
| `MISSING_DATASET_CONVERTER_AUDIT.md` | 缺失数据集转换器的审计记录 |

## 快速开始

```bash
# 使用默认配置，打印第一条样本预览
python -m dataset.main

# 指定配置文件
python -m dataset.main --config dataset/load_dataset/my_config.yaml

# 导出合并后的数据为 jsonl
python -m dataset.main --output train.jsonl
```

## 当前支持的数据集

### 1. 直接解析原始 metadata 的 loader

| 数据集 | 任务 | 关键参数 |
|--------|------|----------|
| `aishell1` | ASR | `split` |
| `aishell3` | TTS | `split` |
| `libritts` | TTS | `subset` |
| `vctk` | TTS | `split=train` |
| `voiceassistant400k` | Dialogues | 无额外参数 |
| `mmsu` | AudioQA | 无额外参数 |
| `librispeech` | ASR | `subset` |
| `wenetspeech` | ASR | `subset` |
| `fleurs` | ASR | `split`、`language` |
| `commonvoice` | ASR | `split`、`language` |

### 2. 读取处理后 jsonl 的 loader

| 数据集 | 任务 | 关键参数 |
|--------|------|----------|
| `audiocaps` | AudioCaptioning | `split` |
| `clotho` | AudioCaptioning | `split` |
| `ultrachat` | text_sft | `metadata_name`（可选） |
| `spoken_squad` | QA | `split` |
| `musan` | AudioClassification | `split` |
| `openhermes25` | text_sft | `metadata_name`（可选） |
| `tulu3_sft_mixture` | text_sft | `split`、`subset` |

## 配置文件说明

典型配置如下：

```yaml
datasets:
  aishell1:
    enabled: true
    root: /mnt/afs/share/voice_model_project/datasets/AIShell-1
    split: train
    max_samples: 2000

  fleurs:
    enabled: false
    root: /mnt/afs/share/voice_model_project/datasets/FLEURS
    split: train
    language: en_us
    max_samples: 2000

  ultrachat:
    enabled: false
    root: /mnt/afs/share/voice_model_project/datasets/ultrachat
    metadata_name: ultrachat_train_text_sft.jsonl
    max_samples: 2000

output:
  shuffle: true
  seed: 42
```

配置规则：

- `enabled`: 是否启用该数据集
- `root`: 数据集根目录
- `max_samples`: 最大加载条数；`null` 表示不限制
- 其余字段按数据集 loader 需要透传

## 各数据集参数约定

| 数据集 | 主要参数说明 |
|--------|--------------|
| `aishell1` | `split=train/dev/test/""` |
| `aishell3` | `split=train/test/""` |
| `libritts` | `subset=train-clean-100/train-clean-360/train-other-500/""` |
| `vctk` | `split=train`，当前无正式多 split |
| `voiceassistant400k` | 无 split 概念 |
| `mmsu` | 无 split 概念 |
| `librispeech` | `subset=train-clean-100/train-clean-360/train-other-500/""` |
| `wenetspeech` | `subset=L/M/S/DEV/TEST_NET/TEST_MEETING/""` |
| `fleurs` | `split` + `language` |
| `commonvoice` | `split` + `language` |
| `audiocaps` | `split=train/validation/test/""` |
| `clotho` | `split=train/validation/test/""` |
| `ultrachat` | 默认读取 `ultrachat_train_text_sft.jsonl` |
| `spoken_squad` | `split=train/validation/test_wer44/test_wer54/""`，同时接受 `dev/val/test` 别名 |
| `musan` | `split=train/dev/test/all/""` |
| `openhermes25` | 默认读取 `openhermes2_5_processed.jsonl` |
| `tulu3_sft_mixture` | `split=train/""`，`subset` 可指定一个或多个 shard 文件名 |

## 样本结构变化

当前 `dataset/sources/*` 的输出已经不再是“纯音频输入 / `text=None`”的单一形式，而是按任务类型做了更明确的指令建模。

### ASR

ASR 类 loader 现在会在 `user` 侧写入显式指令文本，例如：

- 中文 ASR：`请将这段中文语音转换为纯文本。`
- 英文 ASR：`Transcribe the English audio into text.`
- 其他语种：`Transcribe the <Language> audio into text.`

相关实现位于 `BaseDataset.build_asr_instruction(...)`。抽样结果可参考：

- `ASR_PROMPT_SAMPLE_REPORT.md`

### TTS

TTS 类 loader 现在统一使用：

- `user.content[0].text = Convert the text to speech.\n <transcript>`
- `assistant.content[0].audio_path = 目标音频路径`

相关实现位于 `BaseDataset.build_tts_instruction(...)`。

### Clotho 的兼容展开

`clotho` loader 现在兼容两种输入形式：

1. 已经展开的一条 caption 对应一条 sample
2. 旧格式中一个 sample 带 `references` 列表

若检测到旧格式且尚未展开，loader 会自动按 `references` 展开成多条样本，并补齐：

- `id = <base_id>_cap<index>`
- `caption_index`
- 对应的 assistant 文本

## 测试与审计

### 本地抽样验证

可直接运行：

```bash
python dataset/load_dataset/verify_local_dataset_samples.py
```

该脚本会：

1. 读取 `multi_dataset_config.yaml`
2. 对新接入数据集做本地 root 映射
3. 抽样若干条样本
4. 检查顶层字段、`messages` 结构以及 `audio_path` 是否能解析到真实文件

结果写入：

- `LOCAL_DATASET_SAMPLE_VALIDATION_REPORT.md`

### 缺失转换器审计

如果要追踪当前还缺哪些数据集转换器，参考：

- `MISSING_DATASET_CONVERTER_AUDIT.md`

该文件记录了：

- 哪些数据集在规划里需要纳入
- 仓库中是否已经存在可复用转换代码
- 本地原始 metadata 是否已经确认

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

3. 在 `multi_dataset_config.yaml` 中添加配置项。除了 `enabled` 和 `root` 之外，其余字段会透传给具体 loader：

```yaml
datasets:
  my_dataset:
    enabled: true
    root: /path/to/MyDataset
    split: train
    language: en_us
    max_samples: 1000
```

4. 如果是处理后 jsonl 数据集，优先复用 `BaseDataset.load_jsonl_paths(...)`；如果是 ASR / TTS 类任务，优先复用：

- `BaseDataset.build_asr_instruction(...)`
- `BaseDataset.build_tts_instruction(...)`
