@echo off
echo GPS Cost Pricing Workbench - Offline Setup
echo ===========================================
echo.
echo Downloads Dexie.js and SheetJS for Stage 3 and Stage 4.
echo The HTML files already reference these local copies.
echo.

where curl >nul 2>&1
if errorlevel 1 (
  echo ERROR: curl not found. Please use Windows 10 or later.
  pause
  exit /b 1
)

echo [Stage 3] Downloading Dexie.js...
curl -L "https://unpkg.com/dexie@3/dist/dexie.min.js" -o "stage3_browser\dexie.min.js"
if errorlevel 1 ( echo FAILED & goto :err )

echo [Stage 3] Downloading SheetJS...
curl -L "https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js" -o "stage3_browser\xlsx.full.min.js"
if errorlevel 1 ( echo FAILED & goto :err )

echo [Stage 4] Downloading Dexie.js...
curl -L "https://unpkg.com/dexie@3/dist/dexie.min.js" -o "stage4_browser\dexie.min.js"
if errorlevel 1 ( echo FAILED & goto :err )

echo [Stage 4] Downloading SheetJS...
curl -L "https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js" -o "stage4_browser\xlsx.full.min.js"
if errorlevel 1 ( echo FAILED & goto :err )

echo.
echo ===========================================
echo Done! Both stages are now fully offline-capable.
echo Open GPS_Cost_Pricing_Workbench.html to launch.
echo ===========================================
echo.
pause
exit /b 0

:err
echo.
echo Setup failed. Check your internet connection and try again.
echo If your network blocks unpkg.com or cdn.sheetjs.com, download
echo the files manually and place them in stage3_browser\ and stage4_browser\
pause
exit /b 1
