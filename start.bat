@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python が見つかりません。Python 3 をインストールしてから、もう一度 start.bat を実行してください。
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Python仮想環境を作成しています...
  python -m venv .venv
  if errorlevel 1 (
    echo Python仮想環境の作成に失敗しました。
    pause
    exit /b 1
  )
)

if exist ".env" (
  echo .env を読み込んでいます...
  for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do (
    set "%%A=%%B"
  )
) else (
  echo .env がないため、メールはプレビュー保存モードで動作します...
)

echo 必要なパッケージを確認しています...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo パッケージのインストールに失敗しました。
  pause
  exit /b 1
)

echo アプリを起動します: http://127.0.0.1:5000
".venv\Scripts\python.exe" app.py

pause
