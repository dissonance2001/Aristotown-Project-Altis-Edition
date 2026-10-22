@echo off
setlocal
for %%I in ("%~dp0.") do set "ALTIS_ROOT=%%~fI"
cd /d "%ALTIS_ROOT%"
set "PYTHON=%ALTIS_ROOT%\dependencies\python313\Scripts\python.exe"
set "PYTHONPATH=%ALTIS_ROOT%\dependencies\python313-compat"
set "PYTHONPYCACHEPREFIX=%ALTIS_ROOT%\dependencies\python313-pycache"
set "PYTHONUNBUFFERED=1"
set "TT_GAMESERVER=127.0.0.1"
set "TT_PLAYCOOKIE=1"
set "TT_USERNAME=1"
set "TT_PASSWORD=1"
if not exist "%PYTHON%" (
  echo ERROR: Python 3.13 environment not found: "%PYTHON%"
  pause
  exit /b 1
)
title Aristotown Client Python 3.13
"%PYTHON%" -u -X faulthandler -m toontown.toonbase.ClientStart
echo.
echo Client exited. Press any key to close this window.
pause >nul
