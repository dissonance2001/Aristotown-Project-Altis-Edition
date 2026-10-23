@echo off
setlocal
set "SCRIPT_DIR=%~dp0"

if exist "%SCRIPT_DIR%docker-compose.yml" (
    set "DOCKER_DIR=%SCRIPT_DIR%"
    for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"
) else (
    set "PROJECT_ROOT=%SCRIPT_DIR%"
    set "DOCKER_DIR=%SCRIPT_DIR%docker\"
)

cd /d "%PROJECT_ROOT%" || (
    echo ERROR: Could not open the Altis source root.
    pause
    exit /b 1
)

set "ALTIS_PYTHON=%PROJECT_ROOT%\dependencies\panda\python\python.exe"
if not exist "%ALTIS_PYTHON%" (
    echo The bundled Altis Python interpreter was not found:
    echo "%ALTIS_PYTHON%"
    echo Cannot safely export the Windows account bridge.
    pause
    exit /b 1
)

if not exist "%DOCKER_DIR%export_account_bridge.py" (
    echo The account-bridge exporter was not found:
    echo "%DOCKER_DIR%export_account_bridge.py"
    pause
    exit /b 1
)

if not exist "%DOCKER_DIR%docker-compose.yml" (
    echo The Docker Compose file was not found:
    echo "%DOCKER_DIR%docker-compose.yml"
    pause
    exit /b 1
)

where docker >nul 2>&1
if errorlevel 1 (
    echo Docker CLI was not found. Start or install Docker Desktop first.
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo Docker Desktop is not ready. Open Docker Desktop, then run this file again.
    pause
    exit /b 1
)

echo Exporting the account bridge using Altis's Windows Python...
"%ALTIS_PYTHON%" "%DOCKER_DIR%export_account_bridge.py" "%PROJECT_ROOT%\user\account-bridge" "%PROJECT_ROOT%\user\account-bridge-export.json"
if errorlevel 1 (
    echo.
    echo Docker was not started because the account bridge could not be read safely.
    pause
    exit /b 1
)

echo.
echo Starting the complete Aristotown Docker stack...
docker compose -f "%DOCKER_DIR%docker-compose.yml" up -d --build
if errorlevel 1 (
    echo.
    echo The stack did not start successfully. Open Docker Desktop and inspect the Aristotown container logs.
    pause
    exit /b 1
)

echo.
docker compose -f "%DOCKER_DIR%docker-compose.yml" ps
pause
