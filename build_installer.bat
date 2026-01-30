@echo off
echo ========================================
echo WprTool Installer Builder
echo ========================================
echo.

REM Check if Inno Setup is installed
set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %INNO_PATH% (
    echo ERROR: Inno Setup not found!
    echo.
    echo Please install Inno Setup 6 from:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo Default installation path: C:\Program Files (x86)\Inno Setup 6\
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking WprTool.exe...
if not exist "dist\WprTool.exe" (
    echo ERROR: WprTool.exe not found in dist folder!
    echo Please run: pyinstaller --clean WprTool.spec
    echo.
    pause
    exit /b 1
)
echo OK - WprTool.exe found

echo.
echo [2/3] Compiling Inno Setup script...
%INNO_PATH% "WprTool_Installer.iss"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Inno Setup compilation failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Build complete!
echo.
echo Installer created at: dist\WprTool_Setup_v2.0.exe
echo.
echo ========================================
echo SUCCESS!
echo ========================================
pause
