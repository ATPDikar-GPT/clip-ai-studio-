@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
echo ==============================================
echo          CLIP AI STUDIO - LOCAL START
echo ==============================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found.
  echo Install Python 3.11 x64 from https://www.python.org/downloads/ and enable Add Python to PATH.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creating virtual environment...
  py -3.11 -m venv .venv
  if errorlevel 1 goto PYTHON_ERROR
)
echo [2/3] Updating pip and installing dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto PIP_ERROR
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto PIP_ERROR
echo [3/3] Starting CLIP AI...
echo The browser will open at http://localhost:8501
echo Keep this window open while using the app.
".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
pause
exit /b 0
:PYTHON_ERROR
echo Could not create the Python 3.11 environment. Confirm Python 3.11 x64 is installed.
pause
exit /b 1
:PIP_ERROR
echo Dependency installation failed. Check your internet connection and the error above.
pause
exit /b 1
