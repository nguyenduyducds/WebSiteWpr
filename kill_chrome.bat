@echo off
echo ========================================
echo   SAFE KILL: CHROME PORTABLE ONLY
echo ========================================
echo.

echo Killing Chrome Portable processes in this folder...
powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object { $_.Name -eq 'chrome.exe' -and $_.ExecutablePath -like '*%~dp0*' } | ForEach-Object { Write-Host 'Killing PID:' $_.ProcessId; Stop-Process -Id $_.ProcessId -Force }"

echo Killing ChromeDriver in this folder...
powershell -NoProfile -Command "Get-WmiObject Win32_Process | Where-Object { $_.Name -eq 'chromedriver.exe' -and $_.ExecutablePath -like '*%~dp0*' } | ForEach-Object { Write-Host 'Killing PID:' $_.ProcessId; Stop-Process -Id $_.ProcessId -Force }"

echo.
echo ========================================
echo   DONE! Only LOCAL Chrome killed.
echo ========================================
echo.
timeout /t 2 >nul
