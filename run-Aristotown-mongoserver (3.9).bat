@echo off
setlocal

set "ROOT=%~dp0"
set "SCRIPTS=%ROOT%scripts"

echo ================================================================
echo Starting Aristotown: Project Altis local server...
echo ================================================================

rem NOTE: confirm this filename matches your actual mongo-starting
rem script (the one running mongod.exe --dbpath mongo/astrondb).
if not exist "%SCRIPTS%\mongo-win32.bat" (
    echo ERROR: Missing scripts\mongo-win32.bat
    pause
    exit /b 1
)

if not exist "%SCRIPTS%\astron_mongo-win32.bat" (
    echo ERROR: Missing scripts\astron_mongo-win32.bat
    pause
    exit /b 1
)

if not exist "%SCRIPTS%\uberdog-win32.bat" (
    echo ERROR: Missing scripts\uberdog-win32.bat
    pause
    exit /b 1
)

if not exist "%SCRIPTS%\ai-win32.bat" (
    echo ERROR: Missing scripts\ai-win32.bat
    pause
    exit /b 1
)

echo Starting MongoDB...
start "Altis - MongoDB" /D "%SCRIPTS%" cmd /k call "mongo-win32.bat"
timeout /t 3 /nobreak >nul

echo Starting Astron (MongoDB-backed config)...
start "Altis - Astron" /D "%SCRIPTS%" cmd /k call "astron_mongo-win32.bat"
timeout /t 2 /nobreak >nul

echo Starting UberDOG...
start "Altis - UberDOG" /D "%SCRIPTS%" cmd /k call "uberdog-win32.bat"
timeout /t 2 /nobreak >nul

echo Starting Game AI...
start "Altis - Game AI" /D "%SCRIPTS%" cmd /k call "ai-win32.bat"

echo.
echo MongoDB, Astron, UberDOG, and AI were launched.
echo You can close this window.
timeout /t 3 /nobreak >nul

endlocal
exit /b 0
