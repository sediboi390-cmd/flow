@echo off
title Price Tracker UI
echo Starting Price Tracker UI...
echo Open: http://localhost:5050
echo.
start "" "http://localhost:5050"
"C:\Users\Supremo\AppData\Local\Programs\Python\Python312\python.exe" "%~dp0server.py"
pause
