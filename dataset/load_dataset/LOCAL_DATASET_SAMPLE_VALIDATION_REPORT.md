# Local Dataset Sample Validation Report

- Config: `/data/share/voice_model_project/FuseOmni/dataset/load_dataset/multi_dataset_config.yaml`
- Root remap: `/mnt/afs/share/voice_model_project` -> `/data/share/voice_model_project`
- Sample count per dataset: `3`

## Process

1. Read `dataset/load_dataset/multi_dataset_config.yaml`.
2. For each newly added dataset, remap the configured root to the local `/data/share/...` prefix.
3. Instantiate the registered loader with `max_samples=<sample-count>`.
4. Validate top-level fields, `messages` structure, and whether each non-null `audio_path` resolves to an existing file.

## libritts

- Original root: `/mnt/afs/share/voice_model_project/datasets/LibriTTS`
- Local root: `/data/share/voice_model_project/datasets/LibriTTS`
- Loader kwargs: `{"subset": "", "max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/LibriTTS"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`libritts_train_clean_100_103_1241_000000_000001` task=`TTS` data_source=`libritts_train_clean_100`
    - structure: ok
    - audio_path: null
    - audio_path: `train-clean-100/103/1241/103_1241_000000_000001.wav` -> `/data/share/voice_model_project/datasets/LibriTTS/train-clean-100/103/1241/103_1241_000000_000001.wav` (exists=True)
    - sample json:
```json
{
  "id": "libritts_train_clean_100_103_1241_000000_000001",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Convert the text to speech.\n matthew Cuthbert is surprised",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": null,
          "audio_path": "train-clean-100/103/1241/103_1241_000000_000001.wav"
        }
      ]
    }
  ],
  "task": "TTS",
  "data_source": "libritts_train_clean_100"
}
```
  - sample[1] id=`libritts_train_clean_100_103_1241_000004_000002` task=`TTS` data_source=`libritts_train_clean_100`
    - structure: ok
    - audio_path: null
    - audio_path: `train-clean-100/103/1241/103_1241_000004_000002.wav` -> `/data/share/voice_model_project/datasets/LibriTTS/train-clean-100/103/1241/103_1241_000004_000002.wav` (exists=True)
    - sample json:
```json
{
  "id": "libritts_train_clean_100_103_1241_000004_000002",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Convert the text to speech.\n In fact, he had looked at twenty very much as he looked at sixty, lacking a little of the grayness.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": null,
          "audio_path": "train-clean-100/103/1241/103_1241_000004_000002.wav"
        }
      ]
    }
  ],
  "task": "TTS",
  "data_source": "libritts_train_clean_100"
}
```
  - sample[2] id=`libritts_train_clean_100_103_1241_000007_000001` task=`TTS` data_source=`libritts_train_clean_100`
    - structure: ok
    - audio_path: null
    - audio_path: `train-clean-100/103/1241/103_1241_000007_000001.wav` -> `/data/share/voice_model_project/datasets/LibriTTS/train-clean-100/103/1241/103_1241_000007_000001.wav` (exists=True)
    - sample json:
```json
{
  "id": "libritts_train_clean_100_103_1241_000007_000001",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Convert the text to speech.\n \"But there was a passenger dropped off for you-a little girl.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": null,
          "audio_path": "train-clean-100/103/1241/103_1241_000007_000001.wav"
        }
      ]
    }
  ],
  "task": "TTS",
  "data_source": "libritts_train_clean_100"
}
```
- Status: passed

## vctk

- Original root: `/mnt/afs/share/voice_model_project/datasets/VCTK`
- Local root: `/data/share/voice_model_project/datasets/VCTK`
- Loader kwargs: `{"split": "train", "max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/VCTK"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`vctk_p225_001` task=`TTS` data_source=`vctk`
    - structure: ok
    - audio_path: null
    - audio_path: `wav48_silence_trimmed/p225/p225_001_mic1.flac` -> `/data/share/voice_model_project/datasets/VCTK/wav48_silence_trimmed/p225/p225_001_mic1.flac` (exists=True)
    - sample json:
```json
{
  "id": "vctk_p225_001",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Convert the text to speech.\n Please call Stella.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": null,
          "audio_path": "wav48_silence_trimmed/p225/p225_001_mic1.flac"
        }
      ]
    }
  ],
  "task": "TTS",
  "data_source": "vctk"
}
```
  - sample[1] id=`vctk_p225_002` task=`TTS` data_source=`vctk`
    - structure: ok
    - audio_path: null
    - audio_path: `wav48_silence_trimmed/p225/p225_002_mic1.flac` -> `/data/share/voice_model_project/datasets/VCTK/wav48_silence_trimmed/p225/p225_002_mic1.flac` (exists=True)
    - sample json:
```json
{
  "id": "vctk_p225_002",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Convert the text to speech.\n Ask her to bring these things with her from the store.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": null,
          "audio_path": "wav48_silence_trimmed/p225/p225_002_mic1.flac"
        }
      ]
    }
  ],
  "task": "TTS",
  "data_source": "vctk"
}
```
  - sample[2] id=`vctk_p225_003` task=`TTS` data_source=`vctk`
    - structure: ok
    - audio_path: null
    - audio_path: `wav48_silence_trimmed/p225/p225_003_mic1.flac` -> `/data/share/voice_model_project/datasets/VCTK/wav48_silence_trimmed/p225/p225_003_mic1.flac` (exists=True)
    - sample json:
```json
{
  "id": "vctk_p225_003",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Convert the text to speech.\n Six spoons of fresh snow peas, five thick slabs of blue cheese, and maybe a snack for her brother Bob.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": null,
          "audio_path": "wav48_silence_trimmed/p225/p225_003_mic1.flac"
        }
      ]
    }
  ],
  "task": "TTS",
  "data_source": "vctk"
}
```
- Status: passed

## librispeech

- Original root: `/mnt/afs/share/voice_model_project/datasets/LibriSpeech`
- Local root: `/data/share/voice_model_project/datasets/LibriSpeech`
- Loader kwargs: `{"subset": "train-clean-100", "max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/LibriSpeech"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`librispeech_train-clean-100_103-1240-0000` task=`ASR` data_source=`librispeech_train-clean-100`
    - structure: ok
    - audio_path: `train-clean-100/103/1240/103-1240-0000.flac` -> `/data/share/voice_model_project/datasets/LibriSpeech/train-clean-100/103/1240/103-1240-0000.flac` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "librispeech_train-clean-100_103-1240-0000",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Transcribe the English audio into text.",
          "audio_path": "train-clean-100/103/1240/103-1240-0000.flac"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "CHAPTER ONE MISSUS RACHEL LYNDE IS SURPRISED MISSUS RACHEL LYNDE LIVED JUST WHERE THE AVONLEA MAIN ROAD DIPPED DOWN INTO A LITTLE HOLLOW FRINGED WITH ALDERS AND LADIES EARDROPS AND TRAVERSED BY A BROOK",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "ASR",
  "data_source": "librispeech_train-clean-100"
}
```
  - sample[1] id=`librispeech_train-clean-100_103-1240-0001` task=`ASR` data_source=`librispeech_train-clean-100`
    - structure: ok
    - audio_path: `train-clean-100/103/1240/103-1240-0001.flac` -> `/data/share/voice_model_project/datasets/LibriSpeech/train-clean-100/103/1240/103-1240-0001.flac` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "librispeech_train-clean-100_103-1240-0001",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Transcribe the English audio into text.",
          "audio_path": "train-clean-100/103/1240/103-1240-0001.flac"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "THAT HAD ITS SOURCE AWAY BACK IN THE WOODS OF THE OLD CUTHBERT PLACE IT WAS REPUTED TO BE AN INTRICATE HEADLONG BROOK IN ITS EARLIER COURSE THROUGH THOSE WOODS WITH DARK SECRETS OF POOL AND CASCADE BUT BY THE TIME IT REACHED LYNDE'S HOLLOW IT WAS A QUIET WELL CONDUCTED LITTLE STREAM",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "ASR",
  "data_source": "librispeech_train-clean-100"
}
```
  - sample[2] id=`librispeech_train-clean-100_103-1240-0002` task=`ASR` data_source=`librispeech_train-clean-100`
    - structure: ok
    - audio_path: `train-clean-100/103/1240/103-1240-0002.flac` -> `/data/share/voice_model_project/datasets/LibriSpeech/train-clean-100/103/1240/103-1240-0002.flac` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "librispeech_train-clean-100_103-1240-0002",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Transcribe the English audio into text.",
          "audio_path": "train-clean-100/103/1240/103-1240-0002.flac"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "FOR NOT EVEN A BROOK COULD RUN PAST MISSUS RACHEL LYNDE'S DOOR WITHOUT DUE REGARD FOR DECENCY AND DECORUM IT PROBABLY WAS CONSCIOUS THAT MISSUS RACHEL WAS SITTING AT HER WINDOW KEEPING A SHARP EYE ON EVERYTHING THAT PASSED FROM BROOKS AND CHILDREN UP",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "ASR",
  "data_source": "librispeech_train-clean-100"
}
```
- Status: passed

## wenetspeech

- Original root: `/mnt/afs/share/voice_model_project/datasets/WenetSpeech`
- Local root: `/data/share/voice_model_project/datasets/WenetSpeech`
- Loader kwargs: `{"subset": "L", "max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/WenetSpeech"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`wenetspeech_Y0000000000_--5llN02F84_S00000` task=`ASR` data_source=`wenetspeech_L`
    - structure: ok
    - audio_path: `train/audio/train/youtube/B00000/Y0000000000_--5llN02F84.opus` -> `/data/share/voice_model_project/datasets/WenetSpeech/train/audio/train/youtube/B00000/Y0000000000_--5llN02F84.opus` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "wenetspeech_Y0000000000_--5llN02F84_S00000",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "请将这段中文语音转换为纯文本。",
          "audio_path": "train/audio/train/youtube/B00000/Y0000000000_--5llN02F84.opus",
          "audio_start_sec": 20.08,
          "audio_end_sec": 24.4
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "怎么样这些日子住得还习惯吧",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "ASR",
  "data_source": "wenetspeech_L"
}
```
  - sample[1] id=`wenetspeech_Y0000000000_--5llN02F84_S00002` task=`ASR` data_source=`wenetspeech_L`
    - structure: ok
    - audio_path: `train/audio/train/youtube/B00000/Y0000000000_--5llN02F84.opus` -> `/data/share/voice_model_project/datasets/WenetSpeech/train/audio/train/youtube/B00000/Y0000000000_--5llN02F84.opus` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "wenetspeech_Y0000000000_--5llN02F84_S00002",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "请将这段中文语音转换为纯文本。",
          "audio_path": "train/audio/train/youtube/B00000/Y0000000000_--5llN02F84.opus",
          "audio_start_sec": 25.0,
          "audio_end_sec": 26.28
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "挺好的",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "ASR",
  "data_source": "wenetspeech_L"
}
```
  - sample[2] id=`wenetspeech_Y0000000000_--5llN02F84_S00003` task=`ASR` data_source=`wenetspeech_L`
    - structure: ok
    - audio_path: `train/audio/train/youtube/B00000/Y0000000000_--5llN02F84.opus` -> `/data/share/voice_model_project/datasets/WenetSpeech/train/audio/train/youtube/B00000/Y0000000000_--5llN02F84.opus` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "wenetspeech_Y0000000000_--5llN02F84_S00003",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "请将这段中文语音转换为纯文本。",
          "audio_path": "train/audio/train/youtube/B00000/Y0000000000_--5llN02F84.opus",
          "audio_start_sec": 26.68,
          "audio_end_sec": 30.48
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "对了美静这段日子经常不和我们一起用餐",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "ASR",
  "data_source": "wenetspeech_L"
}
```
- Status: passed

## fleurs

- Original root: `/mnt/afs/share/voice_model_project/datasets/FLEURS`
- Local root: `/data/share/voice_model_project/datasets/FLEURS`
- Loader kwargs: `{"split": "train", "language": "en_us", "max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/FLEURS"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`fleurs_en_us_train_151_11559549184357409250` task=`ASR` data_source=`fleurs_en_us_train`
    - structure: ok
    - audio_path: `raw/en_us/audio/train/11559549184357409250.wav` -> `/data/share/voice_model_project/datasets/FLEURS/raw/en_us/audio/train/11559549184357409250.wav` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "fleurs_en_us_train_151_11559549184357409250",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Transcribe the English audio into text.",
          "audio_path": "raw/en_us/audio/train/11559549184357409250.wav"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Sir Richard Branson's Virgin Group had a bid for the bank rejected prior to the bank’s nationalisation.",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "ASR",
  "data_source": "fleurs_en_us_train"
}
```
  - sample[1] id=`fleurs_en_us_train_515_4521018244012475111` task=`ASR` data_source=`fleurs_en_us_train`
    - structure: ok
    - audio_path: `raw/en_us/audio/train/4521018244012475111.wav` -> `/data/share/voice_model_project/datasets/FLEURS/raw/en_us/audio/train/4521018244012475111.wav` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "fleurs_en_us_train_515_4521018244012475111",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Transcribe the English audio into text.",
          "audio_path": "raw/en_us/audio/train/4521018244012475111.wav"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "The approach to obtaining information was different. No longer did pressure reside within individual recall, but the ability to recall text became more of a focus.",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "ASR",
  "data_source": "fleurs_en_us_train"
}
```
  - sample[2] id=`fleurs_en_us_train_21_5196818739829249943` task=`ASR` data_source=`fleurs_en_us_train`
    - structure: ok
    - audio_path: `raw/en_us/audio/train/5196818739829249943.wav` -> `/data/share/voice_model_project/datasets/FLEURS/raw/en_us/audio/train/5196818739829249943.wav` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "fleurs_en_us_train_21_5196818739829249943",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Transcribe the English audio into text.",
          "audio_path": "raw/en_us/audio/train/5196818739829249943.wav"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Hsieh implied during the election that Ma might flee the country during a time of crisis.",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "ASR",
  "data_source": "fleurs_en_us_train"
}
```
- Status: passed

## commonvoice

- Original root: `/mnt/afs/share/voice_model_project/datasets/CommonVoice`
- Local root: `/data/share/voice_model_project/datasets/CommonVoice`
- Loader kwargs: `{"split": "train", "language": "zh-TW", "max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/CommonVoice"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`commonvoice_zh-TW_train_common_voice_zh-TW_30575781` task=`ASR` data_source=`commonvoice_zh-TW_train`
    - structure: ok
    - audio_path: `raw/zh-TW/clips/common_voice_zh-TW_30575781.mp3` -> `/data/share/voice_model_project/datasets/CommonVoice/raw/zh-TW/clips/common_voice_zh-TW_30575781.mp3` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "commonvoice_zh-TW_train_common_voice_zh-TW_30575781",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "请将这段中文语音转换为纯文本。",
          "audio_path": "raw/zh-TW/clips/common_voice_zh-TW_30575781.mp3"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "某個手勢代表覆議",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "ASR",
  "data_source": "commonvoice_zh-TW_train"
}
```
  - sample[1] id=`commonvoice_zh-TW_train_common_voice_zh-TW_30575782` task=`ASR` data_source=`commonvoice_zh-TW_train`
    - structure: ok
    - audio_path: `raw/zh-TW/clips/common_voice_zh-TW_30575782.mp3` -> `/data/share/voice_model_project/datasets/CommonVoice/raw/zh-TW/clips/common_voice_zh-TW_30575782.mp3` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "commonvoice_zh-TW_train_common_voice_zh-TW_30575782",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "请将这段中文语音转换为纯文本。",
          "audio_path": "raw/zh-TW/clips/common_voice_zh-TW_30575782.mp3"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "桃園市中正路",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "ASR",
  "data_source": "commonvoice_zh-TW_train"
}
```
  - sample[2] id=`commonvoice_zh-TW_train_common_voice_zh-TW_30575783` task=`ASR` data_source=`commonvoice_zh-TW_train`
    - structure: ok
    - audio_path: `raw/zh-TW/clips/common_voice_zh-TW_30575783.mp3` -> `/data/share/voice_model_project/datasets/CommonVoice/raw/zh-TW/clips/common_voice_zh-TW_30575783.mp3` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "commonvoice_zh-TW_train_common_voice_zh-TW_30575783",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "请将这段中文语音转换为纯文本。",
          "audio_path": "raw/zh-TW/clips/common_voice_zh-TW_30575783.mp3"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "高鐵聯外公路臺南段",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "ASR",
  "data_source": "commonvoice_zh-TW_train"
}
```
- Status: passed

## audiocaps

- Original root: `/mnt/afs/share/voice_model_project/datasets/AudioCaps`
- Local root: `/data/share/voice_model_project/datasets/AudioCaps`
- Loader kwargs: `{"split": "train", "max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/AudioCaps"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`audiocaps_train_91139` task=`AudioCaptioning` data_source=`audiocaps_train`
    - structure: ok
    - audio_path: `extracted_audio/train/91139_r1nicOVtvkQ_130.wav` -> `/data/share/voice_model_project/datasets/AudioCaps/extracted_audio/train/91139_r1nicOVtvkQ_130.wav` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "audiocaps_train_91139",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": null,
          "audio_path": "extracted_audio/train/91139_r1nicOVtvkQ_130.wav"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "A woman talks nearby as water pours",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "AudioCaptioning",
  "data_source": "audiocaps_train",
  "metadata": {
    "audiocap_id": 91139,
    "youtube_id": "r1nicOVtvkQ",
    "start_time": 130,
    "audio_length": 480000
  }
}
```
  - sample[1] id=`audiocaps_train_58146` task=`AudioCaptioning` data_source=`audiocaps_train`
    - structure: ok
    - audio_path: `extracted_audio/train/58146_UDGBjjwyaqE_20.wav` -> `/data/share/voice_model_project/datasets/AudioCaps/extracted_audio/train/58146_UDGBjjwyaqE_20.wav` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "audiocaps_train_58146",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": null,
          "audio_path": "extracted_audio/train/58146_UDGBjjwyaqE_20.wav"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Multiple clanging and clanking sounds",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "AudioCaptioning",
  "data_source": "audiocaps_train",
  "metadata": {
    "audiocap_id": 58146,
    "youtube_id": "UDGBjjwyaqE",
    "start_time": 20,
    "audio_length": 480000
  }
}
```
  - sample[2] id=`audiocaps_train_11542` task=`AudioCaptioning` data_source=`audiocaps_train`
    - structure: ok
    - audio_path: `extracted_audio/train/11542_3eJ9RynJzP8_80.wav` -> `/data/share/voice_model_project/datasets/AudioCaps/extracted_audio/train/11542_3eJ9RynJzP8_80.wav` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "audiocaps_train_11542",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": null,
          "audio_path": "extracted_audio/train/11542_3eJ9RynJzP8_80.wav"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "The wind is blowing, insects are singing, and rustling occurs",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "AudioCaptioning",
  "data_source": "audiocaps_train",
  "metadata": {
    "audiocap_id": 11542,
    "youtube_id": "3eJ9RynJzP8",
    "start_time": 80,
    "audio_length": 480000
  }
}
```
- Status: passed

## clotho

- Original root: `/mnt/afs/share/voice_model_project/datasets/Clotho`
- Local root: `/data/share/voice_model_project/datasets/Clotho`
- Loader kwargs: `{"split": "train", "max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/Clotho"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`clotho_development_Distorted_AM_Radio_noise_cap1` task=`audio_captioning` data_source=`clotho_development`
    - structure: ok
    - audio_path: `development/Distorted AM Radio noise.wav` -> `/data/share/voice_model_project/datasets/Clotho/development/Distorted AM Radio noise.wav` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "clotho_development_Distorted_AM_Radio_noise_cap1",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": null,
          "audio_path": "development/Distorted AM Radio noise.wav"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "A muddled noise of broken channel of the TV",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "audio_captioning",
  "data_source": "clotho_development",
  "file_name": "Distorted AM Radio noise.wav",
  "caption_index": 1,
  "references": [
    "A muddled noise of broken channel of the TV",
    "A television blares the rhythm of a static TV.",
    "Loud television static dips in and out of focus",
    "The loud buzz of static constantly changes pitch and volume.",
    "heavy static and the beginnings of a signal on a transistor radio"
  ],
  "metadata": {
    "keywords": [
      "noise",
      "radio"
    ],
    "sound_id": 117790,
    "sound_link": "https://freesound.org/people/lavatorius/sounds/117790",
    "start_end_samples": "[139264, 1293089]",
    "manufacturer": "lavatorius",
    "license": "http://creativecommons.org/publicdomain/zero/1.0/"
  }
}
```
  - sample[1] id=`clotho_development_Distorted_AM_Radio_noise_cap2` task=`audio_captioning` data_source=`clotho_development`
    - structure: ok
    - audio_path: `development/Distorted AM Radio noise.wav` -> `/data/share/voice_model_project/datasets/Clotho/development/Distorted AM Radio noise.wav` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "clotho_development_Distorted_AM_Radio_noise_cap2",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": null,
          "audio_path": "development/Distorted AM Radio noise.wav"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "A television blares the rhythm of a static TV.",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "audio_captioning",
  "data_source": "clotho_development",
  "file_name": "Distorted AM Radio noise.wav",
  "caption_index": 2,
  "references": [
    "A muddled noise of broken channel of the TV",
    "A television blares the rhythm of a static TV.",
    "Loud television static dips in and out of focus",
    "The loud buzz of static constantly changes pitch and volume.",
    "heavy static and the beginnings of a signal on a transistor radio"
  ],
  "metadata": {
    "keywords": [
      "noise",
      "radio"
    ],
    "sound_id": 117790,
    "sound_link": "https://freesound.org/people/lavatorius/sounds/117790",
    "start_end_samples": "[139264, 1293089]",
    "manufacturer": "lavatorius",
    "license": "http://creativecommons.org/publicdomain/zero/1.0/"
  }
}
```
  - sample[2] id=`clotho_development_Distorted_AM_Radio_noise_cap3` task=`audio_captioning` data_source=`clotho_development`
    - structure: ok
    - audio_path: `development/Distorted AM Radio noise.wav` -> `/data/share/voice_model_project/datasets/Clotho/development/Distorted AM Radio noise.wav` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "clotho_development_Distorted_AM_Radio_noise_cap3",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": null,
          "audio_path": "development/Distorted AM Radio noise.wav"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Loud television static dips in and out of focus",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "audio_captioning",
  "data_source": "clotho_development",
  "file_name": "Distorted AM Radio noise.wav",
  "caption_index": 3,
  "references": [
    "A muddled noise of broken channel of the TV",
    "A television blares the rhythm of a static TV.",
    "Loud television static dips in and out of focus",
    "The loud buzz of static constantly changes pitch and volume.",
    "heavy static and the beginnings of a signal on a transistor radio"
  ],
  "metadata": {
    "keywords": [
      "noise",
      "radio"
    ],
    "sound_id": 117790,
    "sound_link": "https://freesound.org/people/lavatorius/sounds/117790",
    "start_end_samples": "[139264, 1293089]",
    "manufacturer": "lavatorius",
    "license": "http://creativecommons.org/publicdomain/zero/1.0/"
  }
}
```
- Status: passed

## openhermes25

- Original root: `/mnt/afs/share/voice_model_project/datasets/OpenHermes-2___5`
- Local root: `/data/share/voice_model_project/datasets/OpenHermes-2___5`
- Loader kwargs: `{"max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/OpenHermes-2___5"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`openhermes25_airoboros2.2_orca_0` task=`text_sft` data_source=`airoboros2.2`
    - structure: ok
    - audio_path: null
    - audio_path: null
    - sample json:
```json
{
  "id": "openhermes25_airoboros2.2_orca_0",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Every day, a tree drops 7 leaves. How many leaves would it drop in a month of February in a non-leap year? Include your logic.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Here's the logic behind this:\n\n1. We know that February has 28 days in a non-leap year.\n2. If the tree drops 7 leaves every day, then over the course of February, it would drop:\n   Leaves dropped in February = Leaves per day * Days in February\n   = 7 leaves * 28 days\n   = 196 leaves\n\nSo, the tree would drop 196 leaves in February in a non-leap year.",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "text_sft",
  "data_source": "airoboros2.2",
  "metadata": {
    "source": "airoboros2.2",
    "category": "orca",
    "skip_prompt_formatting": false,
    "json_file": "openhermes2_5.json",
    "sample_index": 0
  }
}
```
  - sample[1] id=`openhermes25_airoboros2.2_multiple_choice_1` task=`text_sft` data_source=`airoboros2.2`
    - structure: ok
    - audio_path: null
    - audio_path: null
    - sample json:
```json
{
  "id": "openhermes25_airoboros2.2_multiple_choice_1",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "In analytical chemistry, what is the principle behind the use of an internal standard in quantitative analysis?\nA. It compensates for variations in sample preparation and instrumental response.\nB. It enhances the sensitivity of the analytical method.\nC. It reduces the detection limit of the analytical method.\nD. It increases the resolution between analyte peaks in chromatography.\nE. None of the above.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "A. It compensates for variations in sample preparation and instrumental response.",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "text_sft",
  "data_source": "airoboros2.2",
  "metadata": {
    "source": "airoboros2.2",
    "category": "multiple_choice",
    "skip_prompt_formatting": false,
    "json_file": "openhermes2_5.json",
    "sample_index": 1
  }
}
```
  - sample[2] id=`openhermes25_airoboros2.2_orca_2` task=`text_sft` data_source=`airoboros2.2`
    - structure: ok
    - audio_path: null
    - audio_path: null
    - sample json:
```json
{
  "id": "openhermes25_airoboros2.2_orca_2",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "A rectangular garden has a length of 25 feet and a width of 15 feet. If you want to build a fence around the entire garden, how many feet of fencing will you need?",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "To determine the amount of fencing needed, we first need to calculate the perimeter of the rectangle. The formula for the perimeter of a rectangle is P = 2(L+W), where L is the length and W is the width.\n\nPerimeter = 2(L+W)\n                 = 2(25 feet + 15 feet)\n                 = 2(40 feet)\n                 = 80 feet\n\nSo, you will need 80 feet of fencing to enclose the entire garden.",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "text_sft",
  "data_source": "airoboros2.2",
  "metadata": {
    "source": "airoboros2.2",
    "category": "orca",
    "skip_prompt_formatting": false,
    "json_file": "openhermes2_5.json",
    "sample_index": 2
  }
}
```
- Status: passed

## ultrachat

- Original root: `/mnt/afs/share/voice_model_project/datasets/ultrachat`
- Local root: `/data/share/voice_model_project/datasets/ultrachat`
- Loader kwargs: `{"max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/ultrachat"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`ultrachat_0` task=`text_sft` data_source=`ultrachat`
    - structure: ok
    - audio_path: null
    - audio_path: null
    - audio_path: null
    - audio_path: null
    - audio_path: null
    - audio_path: null
    - sample json:
```json
{
  "id": "ultrachat_0",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "How can cross training benefit groups like runners, swimmers, or weightlifters?",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Cross training can benefit groups like runners, swimmers, or weightlifters in the following ways:\n\n1. Reduces the risk of injury: Cross training involves different types of exercises that work different muscle groups. This reduces the risk of overuse injuries that may result from repetitive use of the same muscles.\n\n2. Improves overall fitness: Cross training helps improve overall fitness levels by maintaining a balance of strength, endurance, flexibility, and cardiovascular fitness.\n\n3. Breaks monotony: Cross training adds variety to your fitness routine by introducing new exercises, which can help you stay motivated and avoid boredom that often comes with doing the same exercises repeatedly.\n\n4. Increases strength: Cross training helps in building strength by incorporating exercises that target different muscle groups. This helps you build strength in areas that may be underdeveloped.\n\n5. Enhances performance: Cross training allows you to work on different aspects of fitness that are essential for your sport or activity. For example, a runner can benefit from strength training as it helps build stronger muscles and improves running economy.\n\nOverall, cross training offers numerous benefits to athletes and fitness enthusiasts. By incorporating other forms of exercise into their routine, individuals can improve their overall fitness, reduce the risk of injury, and enhance their performance.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "That makes sense. I've been wanting to improve my running time, but I never thought about incorporating strength training. Do you have any recommendations for specific exercises?",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Sure, here are some strength training exercises that can benefit runners:\n\n1. Squats: Squats target the glutes, quadriceps, and hamstrings. They help improve lower-body strength, power, and stability, making them an excellent exercise for runners.\n\n2. Lunges: Lunges target the same muscles as squats but also work the hip flexors and help improve balance.\n\n3. Deadlifts: Deadlifts are a compound exercise that targets the glutes, hamstrings, and lower back. They improve lower body strength, power, and stability.\n\n4. Plyometric exercises: Plyometric exercises such as jump squats, box jumps, or single-leg hops can help improve explosive power, which is crucial for sprinting.\n\n5. Calf raises: Calf raises target the calves and help improve running economy by strengthening the muscles that propel you forward.\n\nIt's important to remember to start with lighter weights and proper form to avoid injury. I recommend consulting with a personal trainer or coach for guidance on proper form and technique.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "Hmm, I'm not really a fan of weightlifting though. Can I incorporate other forms of exercise into my routine to improve my running time?",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Yes, absolutely! In addition to strength training, there are many other types of exercises that can help improve running performance without involving weightlifting. Here are some examples:\n\n1. Plyometric exercises: Plyometric exercises like jump squats, box jumps or single-leg jumps improve explosive power which can make your runs more efficient.\n\n2. Hill training
```
  - sample[1] id=`ultrachat_1` task=`text_sft` data_source=`ultrachat`
    - structure: ok
    - audio_path: null
    - audio_path: null
    - audio_path: null
    - audio_path: null
    - audio_path: null
    - audio_path: null
    - sample json:
```json
{
  "id": "ultrachat_1",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Are there any particular physical benefits to mindful walking, such as improved posture or increased physical fitness?",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Yes, there are physical benefits to mindful walking, such as improved posture, increased physical fitness, and better balance. Mindful walking can also help relieve tension in the body, reduce stress, and improve flexibility. It can also improve circulation and help with weight management. By tuning into the body, mindful walking can also help individuals identify and address any imbalances or discomfort, leading to a healthier and more aligned body.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "That sounds great! Can you give me some tips on how to incorporate mindful walking into my daily routine?",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Sure, here are some tips on how to incorporate mindful walking into your daily routine:\n\n1. Choose a quiet and peaceful environment for your walk. This could be a park, a quiet neighborhood, or even a garden.\n\n2. Start by tuning into your breath and becoming aware of your surroundings. Take deep and slow breaths in and out.\n\n3. Pay attention to the sensations in your body as you walk. Notice the movement of your feet, the weight shifting from one leg to the other, and the movement of your arms.\n\n4. Focus your attention on your surroundings. Notice the colors, smells, and sounds around you. Engage your senses fully and take everything in.\n\n5. Be present and let go of any thoughts or worries that may arise. Bring your attention back to the present moment and continue to observe your surroundings as you walk.\n\n6. Try to maintain a slow and steady pace. This will help you stay present and focused on your walk.\n\n7. Set an intention for your walk, such as gratitude or compassion. This will help you stay focused and centered during your practice.\n\nBy incorporating mindful walking into your daily routine, you can experience many physical and mental benefits. Enjoy your walk!",
          "audio_path": null
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "Wow, I never realized that walking could have so many benefits. I think I need to start incorporating mindful walking into my daily routine. But what if I live in a busy city and can't find a quiet place to walk? How can I still practice mindful walking in a noisy environment?",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "That's a great question! Even in a busy city with lots of noise, there are still ways to practice mindful walking. Here are few strategies:\n\n1. Use headphones or earplugs to block out noise. You can listen to calming music or sounds that help you relax, or simply use earplugs to muffle the sound.\n\n2. Focus on your breath, rather than your surroundings. In a noisy environment, it can be easy to get distracted by the surrounding sounds. Instead, focus on your breath and the sensation of walking as much as possible.\n\n3. Use a mantra or phrase to help you stay centered. Choose a word or phrase that is meaningful to you (e.g. \"peace\" or \"I am calm\") and repeat it to yourself quietly as you walk.\n\n4. Practice walking at a different time of day. If the noise is too overwhelming during the day, try walking early in the morning, or later in the evening when it's quieter.\n\n5. Solo walking can be helpful. Sometimes, walking in busy or noisy areas can lead to overstimulation, so try walking alone or with a small group to reduce so
```
  - sample[2] id=`ultrachat_2` task=`text_sft` data_source=`ultrachat`
    - structure: ok
    - audio_path: null
    - audio_path: null
    - audio_path: null
    - audio_path: null
    - audio_path: null
    - audio_path: null
    - sample json:
```json
{
  "id": "ultrachat_2",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "What percentage of the Earth's surface is covered by oceans?",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "About 71% of the Earth's surface is covered by oceans.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "Wow, that's a lot of water! No wonder we call it the blue planet.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Yes, it certainly is! The oceans play a vital role in regulating the Earth's climate and supporting life on our planet. And they're also a great source of food, energy, and recreation for us humans!",
          "audio_path": null
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "text": "Absolutely! I love visiting the beach and going for a swim in the ocean. It's amazing how vast and powerful the sea can be, yet also so peaceful and calming.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "As an AI language model, I have never gone to the beach or swam in the ocean, but based on what you said, I am sure it's a wonderful experience. The ocean is a place of great beauty and mystery, full of fascinating creatures and hidden treasures waiting to be discovered. It can be both a source of wonder and a reminder of the awesome power of nature.",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "text_sft",
  "data_source": "ultrachat",
  "metadata": {
    "source": "ultrachat",
    "num_turns": 3,
    "src_file": "train_0.jsonl",
    "orig_id": "2"
  }
}
```
- Status: passed

## spoken_squad

- Original root: `/mnt/afs/share/voice_model_project/datasets/Spoken-SQuAD`
- Local root: `/data/share/voice_model_project/datasets/Spoken-SQuAD`
- Loader kwargs: `{"split": "train", "max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/Spoken-SQuAD"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`spoken_squad_train_5733be284776f4190066117f` task=`QA` data_source=`spoken_squad_train`
    - structure: ok
    - audio_path: null
    - audio_path: null
    - sample json:
```json
{
  "id": "spoken_squad_train_5733be284776f4190066117f",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Read the passage and answer the question.\n\nContext: architecturally the school has a catholic character. atop the main building school dome is the golden statue of the virgin mary. immediately in front of the main building in facing it is a copper statue of christ with arms appraised with the legend and the bad meow names. next to the main building is the basilica of the sacred heart. immediately behind the basilica is the grotto im mary in place of prayer and reflection. it is a replica of the grotto at lourdes france where the virgin mary reputedly appeared to st bernadette still burning eighteen fifty eight. at the end of the main drive and in a direct line that connects through three statues in the gold dome is as simple modern stone statue of mary.\n\nQuestion: What is in front of the Notre Dame Main Building?",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "a copper statue of christ",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "QA",
  "data_source": "spoken_squad_train",
  "metadata": {
    "title": "University_of_Notre_Dame",
    "context": "architecturally the school has a catholic character. atop the main building school dome is the golden statue of the virgin mary. immediately in front of the main building in facing it is a copper statue of christ with arms appraised with the legend and the bad meow names. next to the main building is the basilica of the sacred heart. immediately behind the basilica is the grotto im mary in place of prayer and reflection. it is a replica of the grotto at lourdes france where the virgin mary reputedly appeared to st bernadette still burning eighteen fifty eight. at the end of the main drive and in a direct line that connects through three statues in the gold dome is as simple modern stone statue of mary.",
    "question": "What is in front of the Notre Dame Main Building?",
    "answers": {
      "text": [
        "a copper statue of christ"
      ],
      "answer_start": [
        187
      ]
    },
    "source_file": "raw/train.json",
    "source_id": "5733be284776f4190066117f"
  }
}
```
  - sample[1] id=`spoken_squad_train_5733be284776f41900661180` task=`QA` data_source=`spoken_squad_train`
    - structure: ok
    - audio_path: null
    - audio_path: null
    - sample json:
```json
{
  "id": "spoken_squad_train_5733be284776f41900661180",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Read the passage and answer the question.\n\nContext: architecturally the school has a catholic character. atop the main building school dome is the golden statue of the virgin mary. immediately in front of the main building in facing it is a copper statue of christ with arms appraised with the legend and the bad meow names. next to the main building is the basilica of the sacred heart. immediately behind the basilica is the grotto im mary in place of prayer and reflection. it is a replica of the grotto at lourdes france where the virgin mary reputedly appeared to st bernadette still burning eighteen fifty eight. at the end of the main drive and in a direct line that connects through three statues in the gold dome is as simple modern stone statue of mary.\n\nQuestion: The Basilica of the Sacred heart at Notre Dame is beside to which structure?",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "the main building",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "QA",
  "data_source": "spoken_squad_train",
  "metadata": {
    "title": "University_of_Notre_Dame",
    "context": "architecturally the school has a catholic character. atop the main building school dome is the golden statue of the virgin mary. immediately in front of the main building in facing it is a copper statue of christ with arms appraised with the legend and the bad meow names. next to the main building is the basilica of the sacred heart. immediately behind the basilica is the grotto im mary in place of prayer and reflection. it is a replica of the grotto at lourdes france where the virgin mary reputedly appeared to st bernadette still burning eighteen fifty eight. at the end of the main drive and in a direct line that connects through three statues in the gold dome is as simple modern stone statue of mary.",
    "question": "The Basilica of the Sacred heart at Notre Dame is beside to which structure?",
    "answers": {
      "text": [
        "the main building"
      ],
      "answer_start": [
        58
      ]
    },
    "source_file": "raw/train.json",
    "source_id": "5733be284776f41900661180"
  }
}
```
  - sample[2] id=`spoken_squad_train_5733bf84d058e614000b61bf` task=`QA` data_source=`spoken_squad_train`
    - structure: ok
    - audio_path: null
    - audio_path: null
    - sample json:
```json
{
  "id": "spoken_squad_train_5733bf84d058e614000b61bf",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Read the passage and answer the question.\n\nContext: as in most other universities notre dame students write a number of news media outlets. the nine stand and run out lets include three newspapers but the radio and television station in several magazines and journals. he gonna sell one page journal in september eighteen seventy six the scholastic magazine is issued twice monthly in claims to be the oldest continuous collegiate publication in the united states. the other magazine the juggler is released twice a year and focuses on student literature and art for. they dont hear book is published annually. the newspapers have varying publication interests with the observer published daily and mainly reporting university in other news and staffed by students from both notre dame and st marys college. unlike scholastic in the dome the observer is an independent publications and does not have the faculty advisor or any editorial oversight from the university. in nineteen eighty seven when some students believe that the observer began to shelly conservative bias liberal newspaper common sense was published. likewise in ten thousand three when other students believe that the papers showed a liberal bias the conservative paper irish rover went into production. neither papers published as often as the observer however all three are distributed to all students. finally in spring two thousand eight an undergraduate journal for political science research beyond politics made its debut.\n\nQuestion: How often is Notre Dame's the Juggler published?",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "twice",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "QA",
  "data_source": "spoken_squad_train",
  "metadata": {
    "title": "University_of_Notre_Dame",
    "context": "as in most other universities notre dame students write a number of news media outlets. the nine stand and run out lets include three newspapers but the radio and television station in several magazines and journals. he gonna sell one page journal in september eighteen seventy six the scholastic magazine is issued twice monthly in claims to be the oldest continuous collegiate publication in the united states. the other magazine the juggler is released twice a year and focuses on student literature and art for. they dont hear book is published annually. the newspapers have varying publication interests with the observer published daily and mainly reporting university in other news and staffed by students from both notre dame and st marys college. unlike scholastic in the dome the observer is an independent publications and does not have the faculty advisor or any editorial oversight from the university. in nineteen eighty seven when some students believe that the observer began to shelly conservative bias liberal newspaper common sense was published. likewise in ten thousand three when other students believe that the papers showed a liberal bias the conservative paper irish rover went into production. neither papers published as often as the observer however all three are distributed to all students. finally in spring two thousand eight an undergraduate journal for political science research beyond politics made its debut.",
    "question": "How often is Notre Dame's the Juggler published?",
    "answers": {
      "text": [
        "twice"
      ],
      "answer_start": [
        316
      ]
    },
    "source_file": "raw/train.json",
    "source_id": "5733bf84d058e614000b61bf"
  }
}
```
- Status: passed

## musan

- Original root: `/mnt/afs/share/voice_model_project/datasets/MUSAN`
- Local root: `/data/share/voice_model_project/datasets/MUSAN`
- Loader kwargs: `{"split": "train", "max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/MUSAN"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`musan_train_music_fma_music-fma-0000_3dd3f64729` task=`AudioClassification` data_source=`musan_train`
    - structure: ok
    - audio_path: `audio/musan/music/fma/music-fma-0000.wav` -> `/data/share/voice_model_project/datasets/MUSAN/audio/musan/music/fma/music-fma-0000.wav` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "musan_train_music_fma_music-fma-0000_3dd3f64729",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Classify this audio into one of three categories: speech, music, or noise.",
          "audio_path": "audio/musan/music/fma/music-fma-0000.wav"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "music",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "AudioClassification",
  "data_source": "musan_train",
  "metadata": {
    "category": "music",
    "source": "fma",
    "source_path": "music/fma/music-fma-0000.wav",
    "annotation_file": "music/fma/ANNOTATIONS",
    "annotation_text": "electronica N Airglow",
    "genres": [
      "electronica"
    ],
    "vocals": "N",
    "artist": "Airglow"
  }
}
```
  - sample[1] id=`musan_train_music_fma_music-fma-0001_ee43864c26` task=`AudioClassification` data_source=`musan_train`
    - structure: ok
    - audio_path: `audio/musan/music/fma/music-fma-0001.wav` -> `/data/share/voice_model_project/datasets/MUSAN/audio/musan/music/fma/music-fma-0001.wav` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "musan_train_music_fma_music-fma-0001_ee43864c26",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Classify this audio into one of three categories: speech, music, or noise.",
          "audio_path": "audio/musan/music/fma/music-fma-0001.wav"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "music",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "AudioClassification",
  "data_source": "musan_train",
  "metadata": {
    "category": "music",
    "source": "fma",
    "source_path": "music/fma/music-fma-0001.wav",
    "annotation_file": "music/fma/ANNOTATIONS",
    "annotation_text": "electronica N Airglow",
    "genres": [
      "electronica"
    ],
    "vocals": "N",
    "artist": "Airglow"
  }
}
```
  - sample[2] id=`musan_train_music_fma_music-fma-0002_8b9c8d35d9` task=`AudioClassification` data_source=`musan_train`
    - structure: ok
    - audio_path: `audio/musan/music/fma/music-fma-0002.wav` -> `/data/share/voice_model_project/datasets/MUSAN/audio/musan/music/fma/music-fma-0002.wav` (exists=True)
    - audio_path: null
    - sample json:
```json
{
  "id": "musan_train_music_fma_music-fma-0002_8b9c8d35d9",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Classify this audio into one of three categories: speech, music, or noise.",
          "audio_path": "audio/musan/music/fma/music-fma-0002.wav"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "music",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "AudioClassification",
  "data_source": "musan_train",
  "metadata": {
    "category": "music",
    "source": "fma",
    "source_path": "music/fma/music-fma-0002.wav",
    "annotation_file": "music/fma/ANNOTATIONS",
    "annotation_text": "electronica N Airglow",
    "genres": [
      "electronica"
    ],
    "vocals": "N",
    "artist": "Airglow"
  }
}
```
- Status: passed

## tulu3_sft_mixture

- Original root: `/mnt/afs/share/voice_model_project/datasets/tulu-3-sft-mixture`
- Local root: `/data/share/voice_model_project/datasets/tulu-3-sft-mixture`
- Loader kwargs: `{"split": "train", "subset": "", "max_samples": 3, "dataset_root": "/data/share/voice_model_project/datasets/tulu-3-sft-mixture"}`
- Loaded samples: `3`
- Sample checks:
  - sample[0] id=`oasst1_5921` task=`text_sft` data_source=`ai2-adapt-dev/oasst1_converted`
    - structure: ok
    - audio_path: null
    - audio_path: null
    - sample json:
```json
{
  "id": "oasst1_5921",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Create a snippet of Terraform HCL code that create an AWS autoscaling group, and an ALB in front to expose an application to internet.",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Sure, here's an example Terraform HCL code that creates an AWS Autoscaling Group and an Application Load Balancer to expose an application to the internet:\n``` \n# Configure the AWS provider\nprovider \"aws\" {\n  region = \"us-east-1\"\n}\n\n# Create a security group to allow traffic to the ALB\nresource \"aws_security_group\" \"alb_sg\" {\n  name_prefix = \"alb_sg\"\n  ingress {\n    from_port = 80\n    to_port = 80\n    protocol = \"tcp\"\n    cidr_blocks = [\"0.0.0.0/0\"]\n  }\n}\n\n# Create an ALB and target group\nresource \"aws_lb\" \"alb\" {\n  name               = \"example-alb\"\n  internal           = false\n  load_balancer_type = \"application\"\n\n  subnets = [\"subnet-12345678\", \"subnet-87654321\"]\n\n  security_groups = [aws_security_group.alb_sg.id]\n\n  tags = {\n    Environment = \"production\"\n  }\n}\n\nresource \"aws_lb_target_group\" \"target_group\" {\n  name        = \"example-target-group\"\n  port        = 80\n  protocol    = \"HTTP\"\n  vpc_id      = \"vpc-12345678\"\n\n  health_check {\n    path = \"/health\"\n  }\n\n  tags = {\n    Environment = \"production\"\n  }\n}\n\n# Create an autoscaling group\nresource \"aws_launch_configuration\" \"launch_configuration\" {\n  name_prefix   = \"example-lc-\"\n  image_id      = \"ami-12345678\"\n  instance_type = \"t2.micro\"\n\n  # Other settings here (e.g. security groups, userdata, etc.)\n}\n\nresource \"aws_autoscaling_group\" \"autoscaling_group\" {\n  name                      = \"example-asg\"\n  launch_configuration      = aws_launch_configuration.launch_configuration.id\n  target_group_arns         = [aws_lb_target_group.target_group.arn]\n  health_check_type         = \"EC2\"\n  min_size                  = 1\n  max_size                  = 3\n  desired_capacity          = 2\n  vpc_zone_identifier       = [\"subnet-12345678\", \"subnet-87654321\"]\n  termination_policies      = [\"Default\"]\n  wait_for_capacity_timeout = \"10m\"\n\n  tags = {\n    Environment = \"production\"\n  }\n}\n``` \nNote that you will need to customize the settings for your specific use case (e.g. specify your own AMI ID, VPC ID, subnet IDs, etc.). This is just an example to give you an idea of how to create an autoscaling group with an ALB in Terraform.",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "text_sft",
  "data_source": "ai2-adapt-dev/oasst1_converted",
  "metadata": {
    "source": "ai2-adapt-dev/oasst1_converted",
    "split": "train",
    "parquet_file": "train-00000-of-00006.parquet"
  }
}
```
  - sample[1] id=`oasst1_1096` task=`text_sft` data_source=`ai2-adapt-dev/oasst1_converted`
    - structure: ok
    - audio_path: null
    - audio_path: null
    - sample json:
```json
{
  "id": "oasst1_1096",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "¿Por qué crees que cada año es más difícil tener una casa propia en comparación a décadas anteriores?",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "Existen varios factores que pueden contribuir a que cada año sea más difícil tener una casa propia en comparación con décadas anteriores. Algunos de los factores más importantes son:\n- El aumento del precio de la vivienda: En muchas ciudades del mundo, el precio de la vivienda ha aumentado considerablemente en las últimas décadas, lo que hace que sea más difícil para muchas personas comprar una casa propia. Esto se debe a una combinación de factores, incluyendo la escasez de viviendas disponibles, el aumento de la demanda de viviendas, y el aumento del costo de la construcción.\n- La falta de acceso a créditos: En algunos casos, las personas pueden tener dificultades para obtener un crédito hipotecario debido a la falta de historial crediticio o ingresos estables. Esto hace que sea más difícil para muchas personas comprar una casa propia.\n- El aumento de la deuda estudiantil: Muchos jóvenes que buscan comprar una casa propia también enfrentan una gran deuda estudiantil, lo que puede dificultar el ahorro para un pago inicial o el cumplimiento de los requisitos de los prestamistas hipotecarios.\n- Cambios demográficos: Las tendencias demográficas también pueden afectar el mercado de la vivienda. Por ejemplo, el aumento de las tasas de divorcio ha dado lugar a más hogares unipersonales, lo que puede dificultar a algunas personas pagar una hipoteca por su cuenta.",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "text_sft",
  "data_source": "ai2-adapt-dev/oasst1_converted",
  "metadata": {
    "source": "ai2-adapt-dev/oasst1_converted",
    "split": "train",
    "parquet_file": "train-00000-of-00006.parquet"
  }
}
```
  - sample[2] id=`oasst1_2492` task=`text_sft` data_source=`ai2-adapt-dev/oasst1_converted`
    - structure: ok
    - audio_path: null
    - audio_path: null
    - sample json:
```json
{
  "id": "oasst1_2492",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "text": "Cuál es equivalente a una bombilla de 100w en led",
          "audio_path": null
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "text": "La equivalencia entre una bombilla incandescente de 100 vatios y un LED depende de varios factores, como la eficiencia energética del LED y la cantidad de luz que emite. En general, los LED son mucho más eficientes energéticamente que las bombillas incandescentes, por lo que un LED de menor potencia puede ser suficiente para producir la misma cantidad de luz que una bombilla incandescente de 100 vatios.\n\nComo referencia, un LED de alrededor de 10-14 vatios puede producir la misma cantidad de luz que una bombilla incandescente de 100 vatios. Sin embargo, la mejor manera de determinar la equivalencia exacta es comparar la cantidad de lúmenes que emite el LED con la cantidad de lúmenes que emite la bombilla incandescente de 100 vatios.",
          "audio_path": null
        }
      ]
    }
  ],
  "task": "text_sft",
  "data_source": "ai2-adapt-dev/oasst1_converted",
  "metadata": {
    "source": "ai2-adapt-dev/oasst1_converted",
    "split": "train",
    "parquet_file": "train-00000-of-00006.parquet"
  }
}
```
- Status: passed

## Summary

- Overall result: `passed`
- Datasets with failures: `0`

