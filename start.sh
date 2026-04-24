#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Python仮想環境を作成しています..."
  python3 -m venv .venv
fi

source .venv/bin/activate

if [ -f ".env" ]; then
  echo ".env を読み込んでいます..."
  set -a
  . ./.env
  set +a
else
  echo ".env がないため、メールはプレビュー保存モードで動作します..."
fi

echo "必要なパッケージを確認しています..."
python -m pip install -r requirements.txt

echo "アプリを起動します: http://127.0.0.1:5000"
python app.py
