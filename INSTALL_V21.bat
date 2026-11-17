@echo off
setlocal EnableExtensions
chcp 65001 >nul
set "SRC=%~dp0app.py"
set "DST=C:\ClipAI"
echo CLIP AI v21 - TWITCH CLIPPER
 echo.
if not exist "%SRC%" goto NO_SOURCE
if not exist "%DST%\app.py" goto NO_INSTALL
if not exist "%DST%\backups" mkdir "%DST%\backups"
set "BAK=%DST%\backups\app_before_v21_%RANDOM%.py"
echo [1/3] Creating backup...
copy /b /y "%DST%\app.py" "%BAK%" >nul
if errorlevel 1 goto BACKUP_FAILED
echo [2/3] Installing CLIP AI v21...
copy /b /y "%SRC%" "%DST%\app.py" >nul
if errorlevel 1 goto COPY_FAILED
echo [3/3] Verifying installation...
fc /b "%SRC%" "%DST%\app.py" >nul
if errorlevel 1 goto VERIFY_FAILED
echo.
echo SUCCESS: CLIP AI v21 installed.
echo Backup: %BAK%
echo Existing projects, uploads, outputs and Twitch chat logs are preserved.
echo Start: C:\ClipAI\run_clip_ai.bat
echo.
pause
exit /b 0
:NO_SOURCE
echo ERROR: app.py is missing. Extract the complete ZIP first.
goto END_ERROR
:NO_INSTALL
echo ERROR: C:\ClipAI\app.py was not found. Check the installation folder.
goto END_ERROR
:BACKUP_FAILED
echo ERROR: Could not create backup. Old app was not replaced.
goto END_ERROR
:COPY_FAILED
echo ERROR: Could not copy the new app. Close CLIP AI and retry.
goto END_ERROR
:VERIFY_FAILED
echo ERROR: Verification failed. Backup is preserved.
goto END_ERROR
:END_ERROR
echo.
echo Installation stopped. Send a screenshot of this window.
pause
exit /b 1
