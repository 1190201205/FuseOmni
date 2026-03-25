#!/usr/bin/env bash
set -u
export HF_ENDPOINT=https://hf-mirror.com

REPO="ddwang2000/MMSU"
LOCAL_DIR="MMSU"

export HF_HUB_DOWNLOAD_TIMEOUT=120

download_until_ok() {
  local pattern="$1"
  local attempt=1

  while true; do
    echo "[$(date '+%F %T')] 开始下载: $pattern (第 ${attempt} 次尝试)"

    if hf download "$REPO" \
      --repo-type dataset \
      --local-dir "$LOCAL_DIR" \
      --include "$pattern"; then
      echo "[$(date '+%F %T')] 下载完成: $pattern"
      break
    fi

    echo "[$(date '+%F %T')] 下载失败: $pattern"
    echo "[$(date '+%F %T')] 20 秒后重试..."
    attempt=$((attempt + 1))
    sleep 20
  done
}

mkdir -p "$LOCAL_DIR"

download_until_ok "data/*"
download_until_ok "audio/*"
download_until_ok "README.md"

echo "[$(date '+%F %T')] 全部下载完成"
