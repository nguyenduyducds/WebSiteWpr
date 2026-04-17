@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 Building LVCMediaWeb v2.0.4
echo ========================================

echo.
echo [1/3] 🔨 Building EXE with PyInstaller...
call venv\Scripts\activate
python -m PyInstaller WprTool.spec --clean --noconfirm
if errorlevel 1 goto error

echo.
echo [1.5/3] 📂 Copying resources manually...
if not exist "dist\LVCMediaWeb\animaition" mkdir "dist\LVCMediaWeb\animaition"
xcopy /E /I /Y "animaition" "dist\LVCMediaWeb\animaition"
copy /Y "logo.ico" "dist\LVCMediaWeb\"

echo.
echo [2/3] 📦 Building Installer with Inno Setup...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" WprTool_v2.0.1.iss
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    "C:\Program Files\Inno Setup 6\ISCC.exe" WprTool_v2.0.1.iss
) else (
    echo ❌ Inno Setup not found!
    echo Please install from: https://jrsoftware.org/isdl.php
    goto error
)
if errorlevel 1 goto error

echo.
echo [3/3] ✅ Done!
echo ========================================
echo 📦 Installer created successfully!
echo 📁 Location: Output\LVCMediaWeb_Setup_v2.0.4.exe
echo ========================================
echo.
echo 🎯 Next steps:
echo 1. Test installer on clean machine
echo 2. Upload to GitHub Releases
echo 3. Share with users
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo ❌ ERROR: Build failed!
echo ========================================
echo.
echo 🔍 Troubleshooting:
echo - Check if venv is activated
echo - Check if all dependencies installed
echo - Check if Inno Setup is installed
echo - Check build logs above for details
echo.
pause
exit /b 1
