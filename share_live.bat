@echo off
title DeadlockGuard - Live Public Sharing Tool
cls
echo ===================================================================
echo               DeadlockGuard - Live Share for Friends
echo ===================================================================
echo.
echo 1. Starting the DeadlockGuard Web App on your computer...
echo.

REM Start Streamlit minimized in background
start /min "" "C:\User_manual\kavin\anaconda3\python.exe" -m streamlit run app.py --server.port 8501 --server.headless false

timeout /t 3 >nul

echo 2. Opening your browser at http://localhost:8501 ...
start http://localhost:8501

echo.
echo ===================================================================
echo   HOW YOUR FRIEND CAN ACCESS THIS:
echo ===================================================================
echo.
echo   [A] If your friend is on the SAME WI-FI / HOTSPOT:
echo       Open PowerShell and type 'ipconfig' to get your IPv4 Address.
echo       Give your friend this URL: http://YOUR_IP:8501
echo.
echo   [B] If your friend is at home / far away (Instant Public Link):
echo       Connecting to instant secure tunnel... (Press Ctrl+C to stop)
echo ===================================================================
echo.

REM Instant secure tunnel via SSH - no account needed!
ssh -o StrictHostKeyChecking=no -R 80:localhost:8501 a.pinggy.io

pause
