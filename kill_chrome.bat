@echo off
echo ========================================
echo   KILL ALL CHROME PROCESSES
echo ========================================
echo.

echo Killing Chrome processes...
taskkill /F /IM chrome.exe /T 2>nul
taskkill /F /IM chromedriver.exe /T 2>nul
taskkill /F /IM msedge.exe /T 2>nul
taskkill /F /IM msedgedriver.exe /T 2>nul

echo.
echo ========================================
echo   DONE! All Chrome processes killed.
echo ========================================
echo.
timeout /t 2 >nul
