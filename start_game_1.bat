@echo off
title Aristotown - Game Client

cd /d "%~dp0"

rem --- Username ---
set Username=1

rem Le script distribue automatiquement ton pseudo à toutes les variables requises
set TTR_PLAYCOOKIE=%Username%
set PLAYCOOKIE=%Username%
set login_cookie=%Username%
set token=%Username%

set TTR_GAMESERVER=127.0.0.1
set PYTHONPATH=%~dp0;%PYTHONPATH%

C:\Panda3D-1.11.0-x64\python\ppython.exe toontown/toonbase/ClientStart.py

PAUSE
