@echo off
chcp 65001 >nul
echo ========================================
echo    Building WprTool v2.0.4
echo ========================================

echo.
echo [1/5] Cleaning old builds...
if exist "dist" (
    echo Removing old dist folder...
    rmdir /s /q "dist"
)
if exist "build" (
    echo Removing old build folder...
    rmdir /s /q "build"
)

echo.
echo [2/5] Installing PyInstaller...
pip install pyinstaller

echo.
echo [3/5] Installing required packages...
pip install -r requirements.txt

echo.
echo [4/5] Building executable with PyInstaller...
echo This may take 5-10 minutes...
pyinstaller --clean WprTool.spec

echo.
echo [5/5] Verifying build...
if exist "dist\LVCMediaWeb\LVCMediaWeb.exe" (
    echo.
    echo ========================================
    echo        ✅ Build Complete!
    echo ========================================
    echo.
    echo 📦 Build location: dist\LVCMediaWeb\
    echo 📁 Main executable: dist\LVCMediaWeb\LVCMediaWeb.exe
    echo.
    echo 📊 Build includes:
    echo   ✅ WprTool.exe (Main application)
    echo   ✅ Chrome Portable (Bundled browser)
    echo   ✅ ChromeDriver (Automation driver)
    echo   ✅ All Python dependencies
    echo   ✅ Templates folder (HTML themes)
    echo   ✅ Model folder (AI + Config)
    echo.
    echo 🆕 New in v2.0.4:
    echo   🤖 AI Thumbnail customization tab
    echo   📱 Auto aspect ratio detection (9:16/16:9)
    echo   🖼️ Before/After preview
    echo   ⚙️ Configurable AI settings
    echo   📉 Optimized content images (180px)
    echo.
    echo 📏 Estimated size: ~500-700 MB
    echo.
    echo ⚠️ Next steps:
    echo   1. Test: cd dist\WprTool ^&^& WprTool.exe
    echo   2. Create installer: Open Inno Setup and compile WprTool_v2.0.1.iss
    echo   3. Output: Output\WprTool_Setup_v2.0.4.exe
    echo.
    pause
    exit /b 0
)

echo.
echo ========================================
echo        ❌ Build Failed!
echo ========================================
echo.
echo Please check the error messages above.
echo.
echo Common issues:
echo   - Missing dependencies: pip install -r requirements.txt
echo   - PyInstaller not installed: pip install pyinstaller
echo   - Spec file errors: Check WprTool.spec
echo.
pause
exit /b 1
