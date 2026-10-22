@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
cd /d "%ROOT%"
set "ENV=%ROOT%dependencies\python313"
set "COMPAT=%ROOT%dependencies\python313-compat"
set "PYTHONPATH=%COMPAT%"
set "PYTHONPYCACHEPREFIX=%ROOT%dependencies\python313-pycache"
set "BASEPY="
set "MANUALPY="
set "PANDA_WHEEL=https://buildbot.panda3d.org/downloads/fb20b1b214ebaf167ff777ddd22ab00811fcb3c5/panda3d-1.11.0.dev4050-cp313-cp313-win_amd64.whl"

echo Altis Python 3.13 environment setup
echo Source: %ROOT%
echo Runtime: %ENV%
echo.

if not exist "%ROOT%requirements.txt" (
  echo [ERROR] requirements.txt was not found in the Altis source root.
  goto :failed
)

if not exist "%ROOT%dependencies\panda\direct\" (
  echo [ERROR] Cannot find Altis's existing Direct package:
  echo   %ROOT%dependencies\panda\direct
  echo Extract this setup file into the root of the Altis source folder.
  goto :failed
)

echo Locating a working 64-bit Python 3.13 interpreter...

rem Standard python.org per-user and machine-wide install paths.
call :consider_python "%LocalAppData%\Programs\Python\Python313\python.exe"
call :consider_python "%ProgramFiles%\Python313\python.exe"
call :consider_python "%ProgramFiles%\Python 3.13\python.exe"

rem Registered Python installations, including custom install paths.
for /f "tokens=2,*" %%A in ('reg query "HKCU\Software\Python\PythonCore\3.13\InstallPath" /ve 2^>nul ^| findstr /I "REG_SZ"') do call :consider_python "%%Bpython.exe"
for /f "tokens=2,*" %%A in ('reg query "HKLM\Software\Python\PythonCore\3.13\InstallPath" /ve 2^>nul ^| findstr /I "REG_SZ"') do call :consider_python "%%Bpython.exe"
for /f "tokens=2,*" %%A in ('reg query "HKLM\Software\WOW6432Node\Python\PythonCore\3.13\InstallPath" /ve 2^>nul ^| findstr /I "REG_SZ"') do call :consider_python "%%Bpython.exe"

rem Python executables on PATH, excluding the Windows Store alias.
for /f "delims=" %%P in ('where python.exe 2^>nul ^| findstr /V /I "\WindowsApps\"') do call :consider_python "%%P"

rem Use the Python launcher only if it can return a real, working interpreter.
if not defined BASEPY for /f "delims=" %%P in ('py -3.13 -c "import sys; print(sys.executable)" 2^>nul') do call :consider_python "%%P"

if defined BASEPY goto :python_found

echo.
echo Automatic detection did not find a usable Python 3.13 installation.
echo If Python 3.13 is installed in a custom folder, enter the full path to its python.exe.
echo Example: C:\Users\YourName\AppData\Local\Programs\Python\Python313\python.exe
set /p "MANUALPY=Python 3.13 python.exe path (or press Enter to stop): "
set "MANUALPY=%MANUALPY:"=%"
if not defined MANUALPY goto :no_python313
call :consider_python "%MANUALPY%"
if not defined BASEPY goto :no_python313

:python_found
echo Using Python: %BASEPY%
for /f "delims=" %%V in ('"%BASEPY%" --version 2^>^&1') do echo %%V

echo.
rem Remove only a broken or partial project-local Python 3.13 environment.
if exist "%ENV%\" if not exist "%ENV%\Scripts\python.exe" rmdir /s /q "%ENV%"
if exist "%ENV%\Scripts\python.exe" (
  "%ENV%\Scripts\python.exe" -c "import sys,struct; raise SystemExit(0 if sys.version_info[:2] == (3,13) and struct.calcsize('P') == 8 else 1)" >nul 2>nul
  if errorlevel 1 (
    echo Removing the incomplete project-local Python 3.13 environment...
    rmdir /s /q "%ENV%"
  )
)

if not exist "%ENV%\Scripts\python.exe" (
  echo Creating the project-local Python 3.13 virtual environment...
  "%BASEPY%" -m venv "%ENV%"
  if errorlevel 1 goto :venv_failed
)

if not exist "%ENV%\Scripts\python.exe" goto :venv_failed
"%ENV%\Scripts\python.exe" -c "import sys,struct; raise SystemExit(0 if sys.version_info[:2] == (3,13) and struct.calcsize('P') == 8 else 1)" >nul 2>nul
if errorlevel 1 goto :venv_failed

echo.
echo Installing the existing requirements.txt...
"%ENV%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
"%ENV%\Scripts\python.exe" -m pip install -r "%ROOT%requirements.txt"
if errorlevel 1 goto :failed

echo.
echo Installing Panda3D 1.11.0.dev4050 from its exact CPython 3.13 Windows wheel...
echo This bypasses index discovery, which failed on some systems.
"%ENV%\Scripts\python.exe" -m pip install --no-cache-dir "%PANDA_WHEEL%"
if errorlevel 1 goto :panda_failed

echo.
echo Applying Altis's tested Python 3.13 compatibility pins...
"%ENV%\Scripts\python.exe" -m pip install "pymongo==4.9.2" "StrEnum==0.4.15" "six==1.17.0"
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
echo The original Python 3.9 runtime and launchers have not been intentionally changed.
echo.
echo NOTE: This prepares the runtime only. It does not configure the database or launch the game.
pause
exit /b 0

:consider_python
if defined BASEPY exit /b 0
if not exist "%~1" exit /b 0
"%~1" -c "import sys,struct; raise SystemExit(0 if sys.version_info[:2] == (3,13) and struct.calcsize('P') == 8 else 1)" >nul 2>nul
if errorlevel 1 exit /b 0
set "BASEPY=%~1"
exit /b 0

:no_python313
echo.
echo [ERROR] No working 64-bit Python 3.13 executable was found.
echo The path entered may be missing, may point to Python 3.9, or may be 32-bit.
echo Install 64-bit Python 3.13 from python.org, then rerun this setup.
echo Default installation paths are detected automatically.
echo If it is installed elsewhere, rerun this setup and enter its full python.exe path.
goto :failed

:venv_failed
echo.
echo [ERROR] Failed to create or validate the project-local Python 3.13 environment.
echo Base interpreter: %BASEPY%
echo Expected virtual-environment interpreter: %ENV%\Scripts\python.exe
echo If this environment remains incomplete, delete only dependencies\python313 and rerun setup.
goto :failed

:panda_failed
echo.
echo [ERROR] Could not download the exact Panda3D wheel from its direct download URL.
echo Check internet access to buildbot.panda3d.org and rerun setup.
echo The installer no longer relies on pip discovering the development wheel in an index.
goto :failed

:failed
echo.
echo Setup failed. Review the error above before retrying.
echo The original Python 3.9 runtime and launchers have not been intentionally changed.
pause
exit /b 1
