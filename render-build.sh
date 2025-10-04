#!/usr/bin/env bash
set -euo pipefail

# 安裝系統套件：MeCab 與編譯工具
apt-get update
apt-get install -y --no-install-recommends \
  mecab libmecab-dev mecab-ipadic-utf8 \
  build-essential g++ pkg-config

# 安裝 Python 相依
pip install --upgrade pip
pip install -r requirements.txt

# 顯示一下 MeCab 版本，方便偵錯
mecab -v || true
