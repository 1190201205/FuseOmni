# Missing Dataset Converter Audit

整理时间：2026-04-07

## 范围

本文件只检查 `FuseOmni/dataset` 当前缺失、但在 `pruning_stage_training_datasets_by_task.md` 中要求纳入的 5 个数据集：

- UltraChat
- Spoken-SQuAD
- AMI
- MUSAN
- CHiME-6

检查目标分两部分：

1. 仓库里是否已经有可复用的格式转换代码。
2. 如果没有，当前本地原始数据的 metadata 格式是什么。

## 结论总表

| 数据集 | `FuseOmni/dataset` 是否缺失 | 仓库中是否已有转换代码 | 代码位置 | 本地原始 metadata 是否已确认 |
| --- | --- | --- | --- | --- |
| UltraChat | 是 | 是 | `datasets/ultrachat/generate_jsonl.py` | 是 |
| Spoken-SQuAD | 是 | 是 | `load_dataset/spoken_squad_dataset.py` | 是 |
| AMI | 是 | 否 | 无 | 否，本地未下载 |
| MUSAN | 是 | 是 | `load_dataset/musan_dataset.py` | 是 |
| CHiME-6 | 是 | 否 | 无 | 部分确认，仅看到音频命名规则 |

## 1. UltraChat

### 是否已有转换代码

有。现成转换脚本在：

- `datasets/ultrachat/generate_jsonl.py`

该脚本会把原始 `train_*.jsonl` 转成统一的多轮文本 `messages` 格式，输出：

- `datasets/ultrachat/ultrachat_train_text_sft.jsonl`

### 原始 metadata 格式

原始数据位于：

- `datasets/ultrachat/snapshots/f220fe796ce3ed62fbe1681b45ce6cbc9c6cabe0/train_*.jsonl`

每一行是一个 JSON 对象，核心字段是：

- `id`: 样本 id
- `data`: 轮次列表，按 `[user, assistant, user, assistant, ...]` 交替排列

样例：

```json
{"id": "0", "data": ["user turn 1", "assistant turn 1", "user turn 2", "assistant turn 2"]}
```

### 对接建议

对 `FuseOmni/dataset` 来说，这个数据集不需要重新研究 raw schema，直接复用现有脚本逻辑即可。

建议注册名：

- `ultrachat`

## 2. Spoken-SQuAD

### 是否已有转换代码

有。现成转换脚本在：

- `load_dataset/spoken_squad_dataset.py`

辅助构建脚本在：

- `load_dataset/build_spoken_squad.sh`

当前仓库里也已经有导出的统一格式文件：

- `datasets/Spoken-SQuAD/spoken_squad_train_qa.jsonl`
- `datasets/Spoken-SQuAD/spoken_squad_validation_qa.jsonl`
- `datasets/Spoken-SQuAD/spoken_squad_test_wer44_qa.jsonl`
- `datasets/Spoken-SQuAD/spoken_squad_test_wer54_qa.jsonl`

### 原始 metadata 格式

原始数据位于：

- `datasets/Spoken-SQuAD/raw/train.json`
- `datasets/Spoken-SQuAD/raw/test.json`
- `datasets/Spoken-SQuAD/raw/test_WER44.json`
- `datasets/Spoken-SQuAD/raw/test_WER54.json`

每一行是一个 JSON 对象，字段包括：

- `id`
- `title`
- `context`
- `question`
- `answers.text`
- `answers.answer_start`

样例：

```json
{
  "id": "5733be284776f4190066117f",
  "title": "University_of_Notre_Dame",
  "context": "...",
  "question": "What is in front of the Notre Dame Main Building?",
  "answers": {
    "text": ["a copper statue of christ"],
    "answer_start": [187]
  }
}
```

### 对接建议

这部分同样不需要重新摸索 raw schema，直接把现有 `SpokenSquadDataset` 重构到 `FuseOmni/dataset/sources/spoken_squad/` 即可。

建议注册名：

- `spoken_squad`

## 3. AMI

### 是否已有转换代码

没有。

本次检索范围内，没有发现：

- `AMI` 对应的 dataset loader
- `AMI` 对应的 build/export 脚本
- `AMI` 对应的现成统一 jsonl

### 本地原始 metadata 是否可确认

当前不能。

原因是本地没有看到 `datasets/AMI` 目录，也没有任何 `AMI` 原始数据文件，因此无法从本地数据中提取 raw metadata 格式。

### 当前状态

AMI 目前是双重缺失：

1. `FuseOmni/dataset` 内没有 source。
2. 仓库其他位置也没有现成转换代码。
3. 本地原始数据也未下载，无法继续逆向 metadata 结构。

### 对接建议

AMI 需要先补原始数据，再决定 metadata 解析方案。

建议注册名：

- `ami`

## 4. MUSAN

### 是否已有转换代码

有。现成转换脚本在：

- `load_dataset/musan_dataset.py`

当前仓库里也已经有导出的统一 metadata：

- `datasets/MUSAN/metadata/musan_train_audio_classification.jsonl`
- `datasets/MUSAN/metadata/musan_dev_audio_classification.jsonl`
- `datasets/MUSAN/metadata/musan_test_audio_classification.jsonl`
- `datasets/MUSAN/metadata/musan_all_audio_classification.jsonl`

### 原始 metadata 格式

MUSAN 不是单一标注文件，而是“目录结构 + 音频文件 + `ANNOTATIONS` sidecar”。

原始目录结构核心是：

```text
datasets/MUSAN/audio/musan/{music|speech|noise}/{source}/...
```

例如：

```text
datasets/MUSAN/audio/musan/music/fma/music-fma-0000.wav
datasets/MUSAN/audio/musan/speech/librivox/speech-librivox-0097.wav
```

其中部分 source 目录下有 `ANNOTATIONS` 文件。

`music` 类标注样例：

```text
music-fma-0026 blues Y Cullah
music-fma-0097 pop,electronica Y Quiet_Music_for_Tiny_Robots
```

可解析为：

- `clip_id`
- `genres`
- `vocals`
- `artist`

`speech` 类标注样例：

```text
speech-librivox-0097 f german
speech-librivox-0169 m english
```

可解析为：

- `clip_id`
- `speaker_gender`
- `language`

`noise` 类通常没有统一文本标注，主要依赖目录层级和文件名。

### 对接建议

MUSAN 的 raw schema 已经被 `load_dataset/musan_dataset.py` 处理过，可以直接迁移到 `FuseOmni/dataset/sources/musan/`。

建议注册名：

- `musan`

## 5. CHiME-6

### 是否已有转换代码

没有。

本次检索范围内，没有发现：

- `CHiME-6` 对应的 dataset loader
- `CHiME-6` 对应的 build/export 脚本
- `CHiME-6` 对应的统一 jsonl 产物

### 当前本地数据情况

原始包位于：

- `datasets/CHiME/CHiME6_train.tar.gz`
- `datasets/CHiME/CHiME6_dev.tar.gz`
- `datasets/CHiME/CHiME6_eval.tar.gz`

为了做本地 inspection，还额外创建了：

- `datasets/CHiME-6/`

并尝试把 `train/dev` 解压进去。当前能确认到的 raw 文件命名规则至少包括：

- 近讲麦：`S03_P09.wav`
- 远场阵列通道：`S03_U01.CH1.wav`

这说明 raw 数据里至少包含：

- 会话或场景 id，例如 `S03`
- 人佩戴麦克风/近讲通道，例如 `P09`
- 远场设备 id，例如 `U01`
- 通道号，例如 `CH1`

### 原始 metadata 格式是否已确认

当前只确认了一部分。

本地 inspection 过程中：

- 已看到 `audio/train` 和 `audio/dev` 目录；
- 但尚未在已解出的部分里看到可直接引用的 transcription / annotation / JSON / STM / UEM 文件；
- `CHiME6_eval.tar.gz` 还存在读取权限问题，无法本地继续检查。

因此，当前只能确认“音频命名格式”，不能确认完整的原始 metadata 文件结构。

### 当前状态

CHiME-6 目前是：

1. `FuseOmni/dataset` 内没有 source。
2. 仓库其他位置没有现成转换代码。
3. 本地有原始归档，但 metadata 文件结构仍未完全确认。

### 对接建议

CHiME-6 下一步应优先做两件事：

1. 完整解压并确认 transcription / annotation 文件位置。
2. 再设计 `FuseOmni/dataset/sources/chime6/` 的 parser。

建议注册名：

- `chime6`

## 总结

这 5 个缺失数据集可以分成两类：

### 已有可复用转换代码，只是还没接入 `FuseOmni/dataset`

- UltraChat
- Spoken-SQuAD
- MUSAN

### 仓库内没有转换代码，且还需要进一步确认原始 metadata

- AMI
- CHiME-6

其中：

- `AMI` 的阻塞点是本地没有原始数据；
- `CHiME-6` 的阻塞点是本地只确认到音频文件命名，尚未拿到完整标注文件结构。
