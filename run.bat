@echo off
title DeadlockGuard - Explainable Deadlock Recovery Web App
echo ========================================================
echo   Starting DeadlockGuard Web Application...
echo   URL: http://localhost:8501
echo ========================================================

REM Use Anaconda Python if present, otherwise default to python
if exist "C:\User_manual\kavin\anaconda3\python.exe" (
    "C:\User_manual\kavin\anaconda3\python.exe" -m streamlit run app.py
) else (
    python -m streamlit run app.py
)
pause
