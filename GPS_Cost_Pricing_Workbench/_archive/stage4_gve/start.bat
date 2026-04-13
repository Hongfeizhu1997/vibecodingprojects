@echo off
title GPS Pricing Workbench — Stage 4: GVE Validation
echo Starting Stage 4: GVE Validation...
echo.
set PYTHONPATH=%~dp0
if not defined GPS_DB_PATH set GPS_DB_PATH=%~dp0pricing.db
if not defined GPS_PORT set GPS_PORT=5004
"C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" "%~dp0app.py"
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start. Make sure Python is installed.
    pause
)
