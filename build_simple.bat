@echo off
echo ========================================
echo   BUILD SIMPLE EXE - NO INSTALLER
echo ========================================
echo.

REM Clean old builds
echo [1/3] Cleaning old builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Build with PyInstaller - ONE FOLDER (easier, faster)
echo.
echo [2/3] Building EXE with PyInstaller...
echo This will create a portable folder with all files
echo.
pyinstaller --clean --noconfirm WprTool.spec

if errorlevel 1 (
    echo.
    echo ❌ BUILD FAILED!
    pause
    exit /b 1
)

REM Copy additional files
echo.
echo [3/3] Copying additional files...
if exist "dist\LVCMediaWeb" (
    xcopy /Y /I "animaition" "dist\LVCMediaWeb\animaition\"
    xcopy /Y /I "templates" "dist\LVCMediaWeb\templates\"
    copy /Y "logo.ico" "dist\LVCMediaWeb\" 2>nul
    copy /Y "README.txt" "dist\LVCMediaWeb\" 2>nul
    
    echo.
    echo ========================================
    echo   ✅ BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo 📁 Output folder: dist\LVCMediaWeb\
    echo 🚀 Run: dist\LVCMediaWeb\LVCMediaWeb.exe
    echo.
    echo 💡 You can copy the entire "LVCMediaWeb" folder
    echo    to any computer and run it directly!
    echo.
    
    REM Open output folder
    explorer "dist\LVCMediaWeb"
) else (
    echo ❌ Build folder not found!
)

echo.
pause
