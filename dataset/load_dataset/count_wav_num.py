from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
root = project_root / "datasets" / "RealTalk-CN"
wav_count = sum(1 for _ in root.rglob("*.wav"))
print(f".wav 文件总数: {wav_count}")
