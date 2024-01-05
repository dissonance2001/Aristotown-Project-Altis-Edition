@ECHO OFF
color 03
TITLE MongoDB
:top 
cd C:\Program Files\Toontown Infinite\astron
mongod --port 7030 --dbpath "C:\\Program Files\\Toontown Infinite\\astron\\data\\multiplayer"
goto top