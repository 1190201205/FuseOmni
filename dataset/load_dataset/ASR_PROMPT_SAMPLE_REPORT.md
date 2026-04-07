# ASR Prompt Sample Report

保存时间：2026-04-01

该文件记录本次对 `FuseOmni/dataset` 中 ASR 数据格式修改后的抽样结果。
抽样方式为直接实例化对应数据集 loader，并读取首条样本的 `messages[0].content[0].text`。

## Sample Results

| Dataset | Loader Args | Generated Prompt |
| --- | --- | --- |
| `aishell1` | `split='train', max_samples=1` | `请将这段中文语音转换为纯文本。` |
| `librispeech` | `subset='train-clean-100', max_samples=1` | `Transcribe the English audio into text.` |
| `wenetspeech` | `subset='L', max_samples=1` | `请将这段中文语音转换为纯文本。` |
| `commonvoice` | `split='train', language='zh-TW', max_samples=1` | `请将这段中文语音转换为纯文本。` |
| `commonvoice` | `split='train', language='yue', max_samples=1` | `Transcribe the Cantonese audio into text.` |
| `fleurs` | `split='train', language='en_us', max_samples=1` | `Transcribe the English audio into text.` |
| `fleurs` | `split='train', language='fr_fr', max_samples=1` | `Transcribe the French audio into text.` |

## Notes

- 中文 ASR 统一使用：`请将这段中文语音转换为纯文本。`
- 其他语种 ASR 使用：`Transcribe the <source_language> audio into text.`
- `zh-TW` 被归类为中文提示。
- `yue` 当前生成为 Cantonese 提示，而不是中文提示。
