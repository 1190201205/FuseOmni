import json
from pathlib import Path
import ast  # 解析 choices 字段（它是字符串，不是数组）

ROOT = Path("/data/share/voice_model_project/datasets/RealTalk-CN")
JSON_PATH = ROOT / "subset_json/multi_domain_colloquial/train.json"
AUDIO_BASE = ROOT / "media/storage/wangenzhi_space/direct_test/data_submit"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

item = data[0]

# 关键：audio_file 里是 Spoken3MC/wavs/...，本地实际在 Spoken3MC/download/wavs/...
audio_rel = item["audio_file"].replace("Spoken3MC/", "Spoken3MC/download/", 1)
audio_path = AUDIO_BASE / audio_rel

print("audio exists:", audio_path.exists())
print("top keys:", item.keys())
print("original_data keys:", item["original_data"].keys())

# choices 示例（字符串 -> list）
choices = ast.literal_eval(item["original_data"]["choices"])
print("choices[0:3]:", choices[:3])
