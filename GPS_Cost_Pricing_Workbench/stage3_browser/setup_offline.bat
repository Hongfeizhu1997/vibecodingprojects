@echo off
echo GPS Cost Pricing Workbench - Offline Library Setup
echo ==============================================
echo.
echo This downloads JavaScript libraries so the app works without internet.
echo.

REM Check if curl is available (Windows 10+)
where curl >nul 2>&1
if errorlevel 1 (
  echo ERROR: curl not found. Please download manually:
  echo   1. https://unpkg.com/dexie@3/dist/dexie.min.js  -> save as dexie.min.js
  echo   2. https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js  -> save as xlsx.full.min.js
  echo Then edit index.html to replace the two CDN script tags with:
  echo   ^<script src="dexie.min.js"^>^</script^>
  echo   ^<script src="xlsx.full.min.js"^>^</script^>
  pause
  exit /b 1
)

echo Downloading Dexie.js (IndexedDB library)...
curl -L "https://unpkg.com/dexie@3/dist/dexie.min.js" -o "dexie.min.js"
if errorlevel 1 ( echo FAILED to download Dexie.js & goto :err )

echo Downloading SheetJS (Excel library)...
curl -L "https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js" -o "xlsx.full.min.js"
if errorlevel 1 ( echo FAILED to download SheetJS & goto :err )

echo.
echo Updating index.html to use local files...
powershell -Command "(Get-Content index.html) -replace 'https://unpkg.com/dexie@3/dist/dexie.min.js', 'dexie.min.js' -replace 'https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js', 'xlsx.full.min.js' | Set-Content index.html"

echo.
echo Done! The app is now fully offline-capable.
echo Open index.html in Chrome or Edge to start.
echo.
pause
exit /b 0

:err
echo.
echo Setup incomplete. Check your internet connection and try again.
pause
exit /b 1
