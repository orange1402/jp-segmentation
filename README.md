# 日文教科書文本分詞工具 (Flask + fugashi)

本工具用 `fugashi`（MeCab 介面）進行日文斷詞，並以 Flask 提供簡單網頁介面。

## 快速開始
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
