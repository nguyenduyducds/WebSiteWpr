@echo off
echo ========================================
echo   BUILD ONE FILE EXE (PORTABLE)
echo ========================================
echo.

REM Clean old builds
echo [1/2] Cleaning old builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Build with PyInstaller - ONE FILE
echo.
echo [2/2] Building single EXE file...
echo This may take 5-10 minutes...
echo.

pyinstaller --clean --noconfirm ^
    --onefile ^
    --windowed ^
    --name "LVCMediaWeb" ^
    --icon "logo.ico" ^
    --add-data "templates;templates" ^
    --add-data "animaition;animaition" ^
    --add-data "logo.ico;." ^
    --hidden-import "PIL._tkinter_finder" ^
    --hidden-import "pkg_resources.py2_warn" ^
    --hidden-import "selenium" ^
    --hidden-import "undetected_chromedriver" ^
    --hidden-import "customtkinter" ^
    --hidden-import "openpyxl" ^
    --hidden-import "docx" ^
    --hidden-import "odf" ^
    --collect-all "customtkinter" ^
    --collect-all "selenium" ^
    --collect-all "undetected_chromedriver" ^
    main.py

if errorlevel 1 (
    echo.
    echo ❌ BUILD FAILED!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ BUILD SUCCESSFUL!
echo ========================================
echo.
echo 📁 Output: dist\LVCMediaWeb.exe
echo 📦 Size: ~50-80 MB (single file)
echo.
echo 💡 This is a PORTABLE EXE:
echo    - No installation needed
echo    - Copy to any Windows PC and run
echo    - First run may be slower (extracting files)
echo.

REM Open output folder
if exist "dist\LVCMediaWeb.exe" (
    explorer "dist"
) else (
    echo ❌ EXE file not found!
)

echo.
pause
