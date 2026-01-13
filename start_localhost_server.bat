@echo off
title Project Altis CLI Launcher

:menu
cls
goto run

:run
cls
goto db

:db
cls
goto yaml

:yaml
cls 
echo = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
echo Starting Localhost!
echo = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
cd scripts
echo Launching Astron...
START astron_yaml-win32.bat
echo Launching the Uberdog Server...
START uberdog-win32.bat
echo Launching the AI Server...
START ai-win32.bat
echo.
SET TT_GAMESERVER=127.0.0.1
echo.
goto game


:mongo
cls 
echo = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
echo Starting Localhost!
echo = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
cd scripts
echo Launching Mongo...
START mongo-win32.bat
echo Launching Astron...
START astron_mongo-win32.bat
echo Launching the Uberdog Server...
START uberdog-win32.bat
echo Launching the AI Server...
START ai-win32.bat
echo.
SET TT_GAMESERVER=127.0.0.1
echo.
goto game

:connect
cls
echo = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
echo What Server are you connecting to!
echo = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
set /P TT_GAMESERVER="Server IP: "
goto game

:awsserver
set TT_GAMESERVER=82.5.38.255

:localhost
set TT_GAMESERVER=127.0.0.1

:game
cls
echo = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
echo Username [!] Bye!
echo = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
EXIT /B