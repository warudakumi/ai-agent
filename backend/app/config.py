import os
from pathlib import Path

# ベースディレクトリ
BASE_DIR = Path(__file__).resolve().parent.parent

# 静的ファイルディレクトリ
STATIC_DIR = os.path.join(BASE_DIR, "app", "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")

# アップロードディレクトリの作成（存在しない場合）
os.makedirs(UPLOAD_DIR, exist_ok=True)
