@echo off
setlocal
cd /d "%~dp0"
set "CAREER_LOCAL_SIGNUP=1"
if not exist ".venv\Scripts\python.exe" (
    py -3.12 -m venv .venv
    if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -c "import streamlit, tzdata" >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -m streamlit run app.py --server.address=127.0.0.1 --browser.gatherUsageStats=false
if errorlevel 1 goto failed
exit /b 0

:failed
echo Career Launch Agent could not start. Check the error above and confirm Python 3.12 is installed.
pause
exit /b 1
