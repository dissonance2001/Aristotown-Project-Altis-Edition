@echo off
setlocal EnableExtensions
for %%I in ("%~dp0.") do set "ALTIS_ROOT=%%~fI"
set "PYTHON=%ALTIS_ROOT%\dependencies\python313\Scripts\python.exe"
set "PYTHONPATH=%ALTIS_ROOT%\dependencies\python313-compat"
set "PYTHONPYCACHEPREFIX=%ALTIS_ROOT%\dependencies\python313-pycache"
set "PYTHONUNBUFFERED=1"
set "ASTRON_DIR=%ALTIS_ROOT%\dependencies\astron"
set "MONGO_DIR=%ASTRON_DIR%\mongo\Server\3.6\bin"
set "MONGOD=%MONGO_DIR%\mongod.exe"
set "MONGO_DATA=%ASTRON_DIR%\databases\astrondb"

if /i "%~1"=="ASTRON" goto ASTRON
if /i "%~1"=="UBERDOG" goto UBERDOG
if /i "%~1"=="AI" goto AI

cd /d "%ALTIS_ROOT%"
if not exist "%ALTIS_ROOT%\toontown\toonbase\ClientStart.py" (
  echo ERROR: Altis source root not detected.
  echo This launcher must be placed in the root folder beside toontown, otp and dependencies.
  pause
  exit /b 1
)
if not exist "%PYTHON%" (
  echo ERROR: Python 3.13 environment not found: "%PYTHON%"
  echo Run Setup_Python313_Altis.bat from this source root first.
  pause
  exit /b 1
)
call :ENSURE_MONGO
if errorlevel 1 (
  pause
  exit /b 1
)
netstat -ano -p TCP | findstr ":7199" | findstr "LISTENING" >nul
if not errorlevel 1 (
  echo ERROR: Something is already listening on Astron port 7199.
  echo Stop any existing Astron, AI and UberDOG windows before running this launcher.
  echo The launcher will not reuse an Astron instance because its database config cannot be verified.
  pause
  exit /b 1
)

echo Starting Altis Python 3.13 services using the existing database configuration...
echo Source root: %ALTIS_ROOT%
echo.

start "Altis Astron Python 3.13" "%ComSpec%" /k call "%~f0" ASTRON
echo Waiting for Astron startup...
for /L %%I in (1,1,30) do (
  netstat -ano -p TCP | findstr ":7199" | findstr "LISTENING" >nul
  if not errorlevel 1 goto ASTRON_READY
  timeout /t 1 /nobreak >nul
)
echo ERROR: Astron did not begin listening on port 7199 within 30 seconds. Check the Astron window.
pause
exit /b 1

:ASTRON_READY
start "Altis UberDOG Python 3.13" "%ComSpec%" /k call "%~f0" UBERDOG
echo Waiting for UberDOG startup...
timeout /t 6 /nobreak >nul
start "Altis AI Python 3.13" "%ComSpec%" /k call "%~f0" AI
echo Altis services have been launched. This launcher will now close.
exit /b 0

:ASTRON
cd /d "%ASTRON_DIR%"
echo Starting Astron with the original cluster.yml and MongoDB on port 27017.
if exist "%ASTRON_DIR%\astrond.exe" (
  astrond.exe --loglevel info config\cluster.yml
) else (
  astrond --loglevel info config\cluster.yml
)
echo Astron exited.
pause
exit /b

:UBERDOG
cd /d "%ALTIS_ROOT%"
"%PYTHON%" -u -X faulthandler -m toontown.uberdog.ServiceStart --base-channel 1000000 --max-channels 999999 --stateserver 4002 --astron-ip 127.0.0.1:7199 --eventlogger-ip 127.0.0.1:7197 dependencies/config/general.prc dependencies/config/release/dev.prc
echo UberDOG exited.
pause
exit /b

:AI
cd /d "%ALTIS_ROOT%"
"%PYTHON%" -u -X faulthandler -m toontown.ai.ServiceStart --base-channel 402000000 --max-channels 999999 --stateserver 4002 --astron-ip 127.0.0.1:7199 --eventlogger-ip 127.0.0.1:7197 --district-name "Nuttyriver" dependencies/config/general.prc dependencies/config/release/dev.prc
echo AI exited.
pause
exit /b

:ENSURE_MONGO
rem Use an already-running MongoDB service when present; otherwise start Altis's bundled MongoDB.
netstat -ano -p TCP | findstr ":27017" | findstr "LISTENING" >nul
if not errorlevel 1 (
  echo MongoDB is already listening on port 27017. Using the existing service.
  exit /b 0
)

if not exist "%MONGOD%" (
  echo ERROR: No MongoDB server is running, and Altis's bundled mongod.exe was not found:
  echo "%MONGOD%"
  echo Restore the bundled MongoDB files or install MongoDB and start it on port 27017.
  exit /b 1
)

if not exist "%MONGO_DATA%" mkdir "%MONGO_DATA%"
if not exist "%MONGO_DATA%" (
  echo ERROR: Could not create MongoDB data directory:
  echo "%MONGO_DATA%"
  exit /b 1
)

echo Starting Altis's bundled MongoDB on 127.0.0.1:27017...
start "Altis MongoDB" /D "%MONGO_DIR%" "%MONGOD%" --dbpath "%MONGO_DATA%" --port 27017 --bind_ip 127.0.0.1
for /L %%I in (1,1,30) do (
  timeout /t 1 /nobreak >nul
  netstat -ano -p TCP | findstr ":27017" | findstr "LISTENING" >nul
  if not errorlevel 1 goto MONGO_READY
)
echo ERROR: Bundled MongoDB did not begin listening on port 27017 within 30 seconds.
echo Check the Altis MongoDB window for the error.
exit /b 1

:MONGO_READY
timeout /t 2 /nobreak >nul
echo Bundled MongoDB is listening on port 27017.
exit /b 0
