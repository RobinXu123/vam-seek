@echo off
echo ========================================
echo VAM Web MVP - Frontend Server
echo ========================================
echo.

cd /d "%~dp0frontend"

echo フロントエンドサーバーを起動します
echo URL: http://localhost:5173
echo.

python -m http.server 5173

pause
