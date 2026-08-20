@echo off
title Aristotown - Server Cluster (Astron)
cd ..
cd dependencies/astron

astrond.exe --loglevel debug config/astrond.yml
PAUSE
