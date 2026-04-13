@echo off
setlocal enabledelayedexpansion

:: ============================================================================
::  GPS Pricing Workbench — Master Build Script
::  Builds Stage 3 and Stage 4 into standalone .exe packages,
::  then assembles a distributable folder + zip.
::
::  Run from GPS_Pricing_Workbench\ root:
::      build\build_all.bat
:: ============================================================================

set ROOT=%~dp0..
set BUILD=%~dp0
set DIST=%ROOT%\dist
set PKG=%DIST%\GPS_Pricing_Workbench

echo.
echo  ============================================================
echo   GPS Pricing Workbench — Build All
echo  ============================================================
echo.

:: ── Check Python ──────────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found. Please install Python 3.12+.
    pause & exit /b 1
)

:: ── Check / install PyInstaller ───────────────────────────────────────────────
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo  Installing PyInstaller...
    pip install pyinstaller --quiet
)

:: ── Check / install Flask + openpyxl ─────────────────────────────────────────
echo  Checking dependencies...
pip install flask openpyxl --quiet

:: ── Clean previous dist ───────────────────────────────────────────────────────
if exist "%PKG%" (
    echo  Removing old dist folder...
    rmdir /s /q "%PKG%"
)
mkdir "%PKG%"

:: ── Build Stage 3 ─────────────────────────────────────────────────────────────
echo.
echo  [1/4] Building Stage 3 — Sales Cost...
echo  -----------------------------------------------
python -m PyInstaller "%BUILD%stage3.spec" --distpath "%DIST%" --workpath "%BUILD%work" --noconfirm
if errorlevel 1 (
    echo.
    echo  ERROR: Stage 3 build failed. See output above.
    pause & exit /b 1
)
echo  Stage 3 build complete.

:: ── Build Stage 4 ─────────────────────────────────────────────────────────────
echo.
echo  [2/4] Building Stage 4 — GVE Validation...
echo  -----------------------------------------------
python -m PyInstaller "%BUILD%stage4.spec" --distpath "%DIST%" --workpath "%BUILD%work" --noconfirm
if errorlevel 1 (
    echo.
    echo  ERROR: Stage 4 build failed. See output above.
    pause & exit /b 1
)
echo  Stage 4 build complete.

:: ── Assemble distribution package ────────────────────────────────────────────
echo.
echo  [3/4] Assembling distribution package...
echo  -----------------------------------------------

:: Move stage builds into the package folder
move "%DIST%\Stage3_SalesCost" "%PKG%\Stage3_SalesCost"
move "%DIST%\Stage4_GVE"       "%PKG%\Stage4_GVE"

:: Copy user manual
copy "%ROOT%\GPS_Pricing_Workbench_UserManual.pptx" "%PKG%\GPS_Pricing_Workbench_UserManual.pptx"

:: Create the Launch All shortcut bat inside the package
(
echo @echo off
echo echo.
echo echo  Starting GPS Pricing Workbench...
echo echo  - Stage 3 ^(Sales Cost^)  at http://localhost:5003
echo echo  - Stage 4 ^(GVE^)         at http://localhost:5004
echo echo.
echo echo  Two browser tabs will open automatically.
echo echo  Close both console windows to stop the servers.
echo echo.
echo start "Stage 3 - Sales Cost" "%~dp0Stage3_SalesCost\Stage3_SalesCost.exe"
echo timeout /t 3 /nobreak ^>nul
echo start "Stage 4 - GVE" "%~dp0Stage4_GVE\Stage4_GVE.exe"
) > "%PKG%\Launch All Stages.bat"

:: Create a README
(
echo GPS Pricing Workbench — Distribution Package
echo =============================================
echo.
echo CONTENTS:
echo   Stage3_SalesCost\   - Sales Cost Calculation tool ^(port 5003^)
echo   Stage4_GVE\         - GVE Validation tool ^(port 5004^)
echo   GPS_Pricing_Workbench_UserManual.pptx - User manual
echo   Launch All Stages.bat - Start both tools at once
echo.
echo HOW TO USE:
echo   1. Double-click "Launch All Stages.bat" to start both tools.
echo      Your browser will open automatically.
echo   2. Or launch each stage individually from its folder.
echo.
echo DATA:
echo   Each stage creates pricing.db in its own folder on first run.
echo   Your data persists between sessions in these .db files.
echo.
echo SHARED DATABASE ^(optional^):
echo   To share data between stages, set the GPS_DB_PATH environment
echo   variable to the same .db file path before launching.
echo.
echo No Python installation required.
) > "%PKG%\README.txt"

:: ── Create zip ────────────────────────────────────────────────────────────────
echo.
echo  [4/4] Creating zip archive...
echo  -----------------------------------------------
set ZIPFILE=%DIST%\GPS_Pricing_Workbench.zip
if exist "%ZIPFILE%" del "%ZIPFILE%"

powershell -NoProfile -Command "Compress-Archive -Path '%PKG%' -DestinationPath '%ZIPFILE%'"
if errorlevel 1 (
    echo  WARNING: Could not create zip ^(PowerShell compress failed^).
    echo  Distribution folder is ready at: %PKG%
) else (
    echo  Zip created: %ZIPFILE%
)

:: ── Done ──────────────────────────────────────────────────────────────────────
echo.
echo  ============================================================
echo   Build complete!
echo  ============================================================
echo.
echo   Distributable folder : %PKG%\
echo   Zip for sharing      : %ZIPFILE%
echo.
echo   Share the .zip file with recipients.
echo   They just unzip and double-click "Launch All Stages.bat".
echo.
pause
