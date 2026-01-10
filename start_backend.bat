@echo off
echo ========================================
echo VAM Web MVP - Backend Server
echo ========================================
echo.

cd /d "%~dp0backend"

REM 仮想環境が存在しなければ作成
if not exist "venv" (
    echo 仮想環境を作成中...
    python -m venv venv
)

REM 仮想環境をアクティベート
call venv\Scripts\activate.bat

REM 依存関係をインストール
echo 依存関係をインストール中...
pip install -r requirements.txt -q

echo.
echo ========================================
echo FastAPI サーバーを起動します
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.

REM 重要: backendディレクトリ内で実行
uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
