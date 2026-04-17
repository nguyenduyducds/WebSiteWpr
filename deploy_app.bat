@echo off
echo [INFO] Deploying App to LVC_Release folder...

set "SOURCE_DIR=%~dp0"
set "BUILD_DIR=%SOURCE_DIR%build_nuitka"
set "RELEASE_DIR=%SOURCE_DIR%LVC_Release"

if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"

echo [1/7] Copying Main App...
copy "%BUILD_DIR%\LVC Media Web.exe" "%RELEASE_DIR%\" >nul

echo [2/7] Copying Configuration Files...
if exist "config.json" copy "config.json" "%RELEASE_DIR%\" >nul
if exist "vimeo_api_config.json" copy "vimeo_api_config.json" "%RELEASE_DIR%\" >nul
if exist "license_keys_db.json" copy "license_keys_db.json" "%RELEASE_DIR%\" >nul
if exist "kill_chrome.bat" copy "kill_chrome.bat" "%RELEASE_DIR%\" >nul
if exist "logo.ico" copy "logo.ico" "%RELEASE_DIR%\" >nul

echo [3/7] Copying Cookie Files...
for %%f in (cookies_*.pkl) do copy "%%f" "%RELEASE_DIR%\" >nul

echo [4/7] Copying Chrome Driver...
if not exist "%RELEASE_DIR%\driver" mkdir "%RELEASE_DIR%\driver"
if exist "driver\chromedriver.exe" copy "driver\chromedriver.exe" "%RELEASE_DIR%\driver\" >nul
echo    - chromedriver.exe OK

echo [5/7] Copying Chrome Portable...
if exist "chrome_portable" xcopy "chrome_portable" "%RELEASE_DIR%\chrome_portable\" /E /I /Y /Q >nul
echo    - Chrome Portable OK

echo [6/7] Copying Templates and Animations...
if exist "templates" xcopy "templates" "%RELEASE_DIR%\templates\" /E /I /Y /Q >nul
echo    - Templates OK
if exist "animaition" xcopy "animaition" "%RELEASE_DIR%\animaition\" /E /I /Y /Q >nul
echo    - Animations OK

echo [7/7] Creating Required Folders...
if not exist "%RELEASE_DIR%\chrome_profiles" mkdir "%RELEASE_DIR%\chrome_profiles"
if not exist "%RELEASE_DIR%\thumbnails" mkdir "%RELEASE_DIR%\thumbnails"

echo.
echo ===================================================
echo [SUCCESS] App deployed to: LVC_Release
echo ===================================================
echo.
pause
