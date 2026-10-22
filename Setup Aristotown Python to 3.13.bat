@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "ROOT=%~dp0"
set "ENV=%ROOT%dependencies\python313"
set "COMPAT=%ROOT%dependencies\python313-compat"
set "PYTHONPATH=%COMPAT%"
set "PYTHONPYCACHEPREFIX=%ROOT%dependencies\python313-pycache"
set "BASEPY="
set "MANUALPY="
set "WHEEL=%ROOT%dependencies\panda3d-1.11.0.dev4050-cp313-cp313-win_amd64.whl"

echo Altis Python 3.13 environment setup
 echo Installer: local Panda3D 1.11.0.dev4050 wheel
 echo Source: %ROOT%
 echo Runtime: %ENV%
echo.

if not exist "%ROOT%requirements.txt" (
  echo [ERROR] requirements.txt was not found in the Altis source root.
  goto :failed
)
if not exist "%WHEEL%" (
  echo [ERROR] The required Panda3D wheel was not found:
  echo   %WHEEL%
  echo Put panda3d-1.11.0.dev4050-cp313-cp313-win_amd64.whl in the dependencies folder.
  goto :failed
)
if not exist "%ROOT%dependencies\panda\direct\" (
  echo [ERROR] Altis's existing Direct package was not found at:
  echo   %ROOT%dependencies\panda\direct
  goto :failed
)

echo Locating a working 64-bit Python 3.13 interpreter...
call :consider_python "%LocalAppData%\Programs\Python\Python313\python.exe"
call :consider_python "%ProgramFiles%\Python313\python.exe"
call :consider_python "%ProgramFiles%\Python 3.13\python.exe"
for /f "tokens=2,*" %%A in ('reg query "HKCU\Software\Python\PythonCore\3.13\InstallPath" /ve 2^>nul ^| findstr /I "REG_SZ"') do call :consider_python "%%Bpython.exe"
for /f "tokens=2,*" %%A in ('reg query "HKLM\Software\Python\PythonCore\3.13\InstallPath" /ve 2^>nul ^| findstr /I "REG_SZ"') do call :consider_python "%%Bpython.exe"
for /f "tokens=2,*" %%A in ('reg query "HKLM\Software\WOW6432Node\Python\PythonCore\3.13\InstallPath" /ve 2^>nul ^| findstr /I "REG_SZ"') do call :consider_python "%%Bpython.exe"
for /f "delims=" %%P in ('where python.exe 2^>nul ^| findstr /V /I "\WindowsApps\"') do call :consider_python "%%P"
if not defined BASEPY for /f "delims=" %%P in ('py -3.13 -c "import sys; print(sys.executable)" 2^>nul') do call :consider_python "%%P"

if not defined BASEPY (
  echo.
  echo Automatic detection did not find a working 64-bit Python 3.13 installation.
  echo Enter the full path to its python.exe, or press Enter to stop.
  set /p "MANUALPY=Python 3.13 python.exe path: "
  set "MANUALPY=%MANUALPY:"=%"
  if not defined MANUALPY goto :no_python313
  call :consider_python "%MANUALPY%"
  if not defined BASEPY goto :no_python313
)

echo Using Python: %BASEPY%
"%BASEPY%" --version

if exist "%ENV%\Scripts\python.exe" (
  "%ENV%\Scripts\python.exe" -c "import sys,struct; raise SystemExit(0 if sys.version_info[:2] == (3,13) and struct.calcsize('P') == 8 else 1)" >nul 2>nul
  if errorlevel 1 (
    echo Recreating the invalid project-local Python 3.13 environment...
    rmdir /s /q "%ENV%"
  )
) else if exist "%ENV%\" (
  echo Removing the incomplete project-local Python 3.13 environment...
  rmdir /s /q "%ENV%"
)

if not exist "%ENV%\Scripts\python.exe" (
  echo.
  echo Creating project-local Python 3.13 environment...
  "%BASEPY%" -m venv "%ENV%"
  if errorlevel 1 goto :venv_failed
)
if not exist "%ENV%\Scripts\python.exe" goto :venv_failed
"%ENV%\Scripts\python.exe" -c "import sys,struct; print('Environment Python:',sys.version.split()[0]); print('Architecture:',struct.calcsize('P')*8,'bit'); raise SystemExit(0 if sys.version_info[:2] == (3,13) and struct.calcsize('P') == 8 else 1)"
if errorlevel 1 goto :venv_failed

set "PY=%ENV%\Scripts\python.exe"
echo.
echo Upgrading pip...
"%PY%" -m pip install --upgrade pip
if errorlevel 1 goto :failed

echo.
echo Installing the existing requirements.txt...
"%PY%" -m pip install -r "%ROOT%requirements.txt"
if errorlevel 1 goto :failed

echo.
echo Installing Panda3D 1.11.0.dev4050 from the local dependencies wheel...
"%PY%" -m pip install --no-deps --force-reinstall "%WHEEL%"
if errorlevel 1 goto :panda_failed

echo.
echo Applying tested Python 3.13 compatibility pins...
"%PY%" -m pip install "pymongo==4.9.2" "StrEnum==0.4.15" "six==1.17.0" "dnspython==2.9.0"
if errorlevel 1 goto :failed

echo.
echo Copying Altis's Direct package into the compatibility path...
if not exist "%COMPAT%" mkdir "%COMPAT%"
xcopy "%ROOT%dependencies\panda\direct" "%COMPAT%\direct\" /E /I /Y >nul
if errorlevel 1 goto :failed

echo.
echo Verifying dependencies and imports...
"%PY%" -m pip check
if errorlevel 1 goto :failed
"%PY%" -c "import panda3d.core, pymongo, strenum, six, raven, requests, Crypto, yaml, semidbm; from direct.distributed.AstronInternalRepository import AstronInternalRepository; print('Panda3D:',panda3d.core.PandaSystem.getVersionString()); print('PyMongo:',pymongo.version); print('Direct Astron import: OK'); print('All imports OK')"
if errorlevel 1 goto :failed

echo.
echo Setup complete.
echo Python 3.13: %PY%
echo Direct compatibility path: %COMPAT%
echo Panda3D was installed from the local wheel; no download from buildbot.panda3d.org was needed.
echo The original Python 3.9 runtime and launchers were not intentionally modified.
echo.
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
echo Install 64-bit Python 3.13.17 from python.org or enter its actual python.exe path.
goto :failed

:venv_failed
echo.
echo [ERROR] Could not create or validate the project-local Python 3.13 environment.
echo Base interpreter: %BASEPY%
echo Expected: %ENV%\Scripts\python.exe
echo If necessary, remove only dependencies\python313 and rerun this setup.
goto :failed

:panda_failed
echo.
echo [ERROR] The local Panda3D wheel could not be installed:
echo   %WHEEL%
echo Check that the wheel is the CPython 3.13 Windows x64 build.
goto :failed

:failed
echo.
echo Setup failed. Review the error above before retrying.
echo The original Python 3.9 runtime and launchers were not intentionally modified.
pause
exit /b 1
