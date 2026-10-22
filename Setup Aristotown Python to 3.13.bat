@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
cd /d "%ROOT%"
set "ENV=%ROOT%dependencies\python313"
set "COMPAT=%ROOT%dependencies\python313-compat"
set "PYTHONPATH=%COMPAT%"
set "PYTHONPYCACHEPREFIX=%ENV%\pycache"

echo Altis Python 3.13 environment setup
echo Source: %ROOT%
echo Runtime: %ENV%
echo.

if not exist "%ROOT%requirements.txt" (
  echo ERROR: requirements.txt was not found in the Altis source root.
  echo Expected: %ROOT%requirements.txt
  pause
  exit /b 1
)

if not exist "%ROOT%dependencies\panda\direct\" (
  echo ERROR: Cannot find Altis's existing Direct package:
  echo   %ROOT%dependencies\panda\direct
  echo Extract this setup file into the root of the Altis source folder.
  pause
  exit /b 1
)

where py >nul 2>nul
if errorlevel 1 goto :no_py
py -3.13 -c "import sys; print(sys.version)" >nul 2>nul
if errorlevel 1 goto :no_python313

echo Python 3.13 detected.
if not exist "%ENV%\Scripts\python.exe" (
  echo.
  echo Creating a project-local Python 3.13 virtual environment...
  py -3.13 -m venv "%ENV%"
  if errorlevel 1 goto :failed
) else (
  echo Reusing the existing project-local environment.
)

echo.
echo Installing the existing requirements.txt...
"%ENV%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
"%ENV%\Scripts\python.exe" -m pip install -r "%ROOT%requirements.txt"
if errorlevel 1 goto :failed
echo.
echo Installing the tested Python 3.13 Panda3D build and compatibility pins...
"%ENV%\Scripts\python.exe" -m pip install --pre --extra-index-url https://archive.panda3d.org/ "panda3d==1.11.0.dev4050" "pymongo==4.9.2" "StrEnum==0.4.15" "six==1.17.0"
if errorlevel 1 goto :failed

echo.
echo Copying Altis's Direct package into the Python 3.13 compatibility path...
if not exist "%COMPAT%" mkdir "%COMPAT%"
xcopy "%ROOT%dependencies\panda\direct" "%COMPAT%\direct\" /E /I /Y >nul
if errorlevel 1 goto :failed

echo.
echo Verifying installed dependencies...
"%ENV%\Scripts\python.exe" -m pip check
if errorlevel 1 goto :failed
"%ENV%\Scripts\python.exe" -c "import panda3d.core, direct, pymongo, six, strenum, raven, requests, Crypto, yaml, semidbm; print('Panda3D:', panda3d.core.PandaSystem.getVersionString()); print('PyMongo:', pymongo.version); print('StrEnum module:', strenum.__file__); print('Direct:', direct.__file__); print('Requirements imports OK')"
if errorlevel 1 goto :failed

echo.
echo Setup complete.
echo Python 3.13: %ENV%\Scripts\python.exe
echo Python path: %COMPAT%
echo Your existing Python 3.9 runtime and launchers were not intentionally changed.
echo.
echo NOTE: This prepares the runtime only. It does not configure the production database or launch the game.
pause
exit /b 0

:no_py
echo ERROR: The Windows Python launcher 'py' was not found.
echo Install 64-bit Python 3.13 from python.org and include the Python launcher.
pause
exit /b 1

:no_python313
echo ERROR: Python 3.13 was not found by 'py -3.13'.
echo Install 64-bit Python 3.13, then run this setup again.
pause
exit /b 1

:failed
echo.
echo Setup failed. Review the error above before retrying.
echo The original Python 3.9 runtime and launchers are not intentionally modified by this script.
pause
exit /b 1
