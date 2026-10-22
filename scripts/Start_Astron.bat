@echo off
setlocal EnableExtensions
for %%I in ("%~dp0..") do set "ALTIS_ROOT=%%~fI"
if not exist "%ALTIS_ROOT%\Start_Altis_Python313.bat" (
  echo ERROR: Start_Altis_Python313.bat was not found in the Altis source root.
  pause
  exit /b 1
)
call "%ALTIS_ROOT%\Start_Altis_Python313.bat" ASTRON
