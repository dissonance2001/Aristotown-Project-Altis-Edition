@echo off
cd ..
title Project Altis UberDOG
mode con: cols=60 lines=20

rem Read the contents of PPYTHON_PATH into %PPYTHON_PATH%:
set /P PYTHON_PATH=<PYTHON_PATH

rem Define some constants for our UberDOG server:
set MAX_CHANNELS=999999
set STATESERVER=4002
set ASTRON_IP=127.0.0.1:7199
set EVENTLOGGER_IP=127.0.0.1:7197
set BASE_CHANNEL=1000000
set PYTHONFAULTHANDLER=1
set PYTHONUNBUFFERED=1

:main

"dependencies/panda/python/python.exe" -u -X faulthandler -m toontown.uberdog.ServiceStart --base-channel %BASE_CHANNEL% ^
               --max-channels %MAX_CHANNELS% --stateserver %STATESERVER% ^
               --astron-ip %ASTRON_IP% --eventlogger-ip %EVENTLOGGER_IP%
echo.
echo [Process exited with code %ERRORLEVEL%]
PAUSE
goto main
