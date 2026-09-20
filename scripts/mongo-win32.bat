@echo off
title Project Altis Mongo
mode con: cols=60 lines=20

cd /d "%~dp0"

"%~dp0..\dependencies\astron\mongo\Server\3.6\bin\mongod.exe" --dbpath "%~dp0..\dependencies\astron\mongo\astrondb-3.6" --bind_ip 127.0.0.1 --port 27017

pause