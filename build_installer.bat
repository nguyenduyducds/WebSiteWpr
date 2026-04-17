@echo off
echo ============================================
echo   BUILDING INSTALLER FOR WPRTOOL v2.0.3
echo ============================================
echo.

set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not exist %ISCC_PATH% (
    echo ❌ Inno Setup compiler (ISCC.exe) not found at default location!
    echo    Please install Inno Setup 6 or check your installation path.
    echo.
    pause
    exit /b 1
)

echo Found Inno Setup at: %ISCC_PATH%
echo.
echo Compiling WprTool_v2.0.1.iss ...
%ISCC_PATH% "WprTool_v2.0.1.iss"

if %errorlevel% neq 0 (
    echo.
    echo ❌ Compilation FAILED!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   ✅ INSTALLER CREATED SUCCESSFULLY!
echo ============================================
echo.
echo Location: Output\WP_Auto_Tool_Setup_v2.0.3.exe
echo.
pause
