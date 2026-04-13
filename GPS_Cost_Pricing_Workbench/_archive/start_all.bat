@echo off
title GPS Pricing Workbench
set "ROOT=%~dp0"
set "PYTHON=C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe"

if not exist "%ROOT%shared\" mkdir "%ROOT%shared"

echo.
echo  GPS Pricing Workbench — Starting all active stages...
echo  Shared DB folder: %ROOT%shared\
echo.

start "GPS Stage 3 - Sales Cost"   cmd /k "set GPS_DB_PATH=%ROOT%shared\stage3.db&& set GPS_PORT=5003&& cd /d %ROOT%stage3_sales_cost&& %PYTHON% app.py"
start "GPS Stage 4 - GVE"          cmd /k "set GPS_DB_PATH=%ROOT%shared\stage4.db&& set GPS_PORT=5004&& cd /d %ROOT%stage4_gve&& %PYTHON% app.py"
start "GPS Launcher"               cmd /k "cd /d %ROOT%launcher&& %PYTHON% app.py"

timeout /t 2 /nobreak >nul
start http://localhost:5000
