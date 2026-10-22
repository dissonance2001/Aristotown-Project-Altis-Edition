@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
cd /d "%ROOT%"
set "ENV=%ROOT%dependencies\python313"
set "COMPAT=%ROOT%dependencies\python313-compat"
set "PYTHONPATH=%COMPAT%"
set "PYTHONPYCACHEPREFIX=%ROOT%dependencies\python313-pycache"
set "BASEPY="

echo Altis Python 3.13 environment setup
echo Source: %ROOT%
echo Runtime: %ENV%
echo.

if not exist "%ROOT%requirements.txt" (
  echo [ERROR] requirements.txt was not found in the Altis source root.
  echo Expected: %ROOT%requirements.txt
  goto :failed
)

if not exist "%ROOT%dependencies\panda\direct\" (
  echo [ERROR] Cannot find Altis's existing Direct package:
  echo   %ROOT%dependencies\panda\direct
  echo Extract this setup file into the root of the Altis source folder.
  goto :failed
)

echo Locating a working 64-bit Python 3.13 interpreter...

rem First check the standard python.org per-user and machine-wide install paths.
call :consider_python "%LocalAppData%\Programs\Python\Python313\python.exe"
call :consider_python "%ProgramFiles%\Python313\python.exe"
call :consider_python "%ProgramFiles%\Python 3.13\python.exe"

rem Check Python's registered install paths, which also cover custom install locations.
for /f "tokens=2,*" %%A in ('reg query "HKCU\Software\Python\PythonCore\3.13\InstallPath" /ve 2^>nul ^| findstr /I "REG_SZ"') do call :consider_python "%%Bpython.exe"
for /f "tokens=2,*" %%A in ('reg query "HKLM\Software\Python\PythonCore\3.13\InstallPath" /ve 2^>nul ^| findstr /I "REG_SZ"') do call :consider_python "%%Bpython.exe"
for /f "tokens=2,*" %%A in ('reg query "HKLM\Software\WOW6432Node\Python\PythonCore\3.13\InstallPath" /ve 2^>nul ^| findstr /I "REG_SZ"') do call :consider_python "%%Bpython.exe"

rem Check Python executables available through PATH, excluding the Windows Store alias.
for /f "delims=" %%P in ('where python.exe 2^>nul ^| findstr /V /I "\WindowsApps\"') do call :consider_python "%%P"

rem Last, ask the Python launcher for its 3.13 interpreter path; ignore stale registrations.
if not defined BASEPY for /f "delims=" %%P in ('py -3.13 -c "import sys; print(sys.executable)" 2^>nul') do call :consider_python "%%P"

if not defined BASEPY goto :no_python313

echo Using Python: %BASEPY%
for /f "delims=" %%V in ('"%BASEPY%" --version 2^>^&1') do echo %%V

echo.
if not exist "%ENV%\Scripts\python.exe" (
  echo Creating a project-local Python 3.13 virtual environment...
  "%BASEPY%" -m venv "%ENV%"
  if errorlevel 1 goto :venv_failed
)

if not exist "%ENV%\Scripts\python.exe" goto :venv_failed
"%ENV%\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,13) else 1)" >nul 2>nul
if errorlevel 1 (
  echo [ERROR] The project-local environment exists but is not running Python 3.13 correctly.
  echo Remove only this incomplete environment folder, then run setup again:
  echo   %ENV%
  goto :failed
)

echo.
echo Installing the existing requirements.txt...
"%ENV%\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :failed
"%ENV%\Scripts\python.exe" -m pip install -r "%ROOT%requirements.txt"
if errorlevel 1 goto :failed

echo.
echo Installing the tested Python 3.13 Panda3D build and compatibility pins...
"%ENV%\Scripts\python.exe" -m pip install --pre --find-links https://archive.panda3d.org/branches/master/panda3d/ "panda3d==1.11.0.dev4050" "pymongo==4.9.2" "StrEnum==0.4.15" "six==1.17.0"
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
echo Your original Python 3.9 runtime and launchers were not intentionally changed.
echo.
echo NOTE: This prepares the runtime only. It does not configure the production database or launch the game.
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
echo [ERROR] No working 64-bit Python 3.13 executable could be found.
echo The Python launcher on this PC may still point to a removed installation such as C:\Open-Panda\python\python.exe.
echo Install 64-bit Python 3.13 from python.org, then run this setup again.
echo If Python is installed in a custom location, add its folder to PATH or register the installation.
goto :failed

:venv_failed
echo.
echo [ERROR] Failed to create the project-local Python 3.13 environment.
echo Base interpreter: %BASEPY%
echo Expected virtual-environment interpreter: %ENV%\Scripts\python.exe
echo No dependency installation will be attempted because the environment is incomplete.
goto :failed

:failed
echo.
echo Setup failed. Review the error above before retrying.
echo The original Python 3.9 runtime and launchers have not been intentionally modified.
pause
exit /b 1
