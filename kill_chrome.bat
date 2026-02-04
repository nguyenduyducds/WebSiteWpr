@echo off
echo ========================================
echo   Kill All Chrome Processes
echo ========================================
echo.

echo Killing all Chrome processes...
taskkill /F /IM chrome.exe /T 2>nul

if %errorlevel% equ 0 (
    echo.
    echo ✅ All Chrome processes killed successfully!
) else (
    echo.
    echo ⚠️ No Chrome processes found or already closed.
)

echo.
echo ========================================
echo   Done!
echo ========================================
pause
