@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    TAO GOI CAI DAT CHO KHACH HANG
echo ========================================
echo.

set /p CUSTOMER_KEY="Nhap License Key cua khach hang: "

if "%CUSTOMER_KEY%"=="" (
    echo [ERROR] Ban phai nhap key!
    pause
    exit /b
)

set "CUSTOMER_DIR=Customer_%CUSTOMER_KEY%"

echo.
echo [1/3] Tao thu muc cho khach hang...
if exist "%CUSTOMER_DIR%" rmdir /s /q "%CUSTOMER_DIR%"
mkdir "%CUSTOMER_DIR%"

echo [2/3] Copy app va cac file can thiet...
xcopy "LVC_Release\*" "%CUSTOMER_DIR%\" /E /I /Y /Q >nul

echo [3/3] Tao database rieng cho khach hang nay...
echo [ > "%CUSTOMER_DIR%\license_keys_db.json"
echo     { >> "%CUSTOMER_DIR%\license_keys_db.json"
echo         "key": "%CUSTOMER_KEY%", >> "%CUSTOMER_DIR%\license_keys_db.json"
echo         "note": "", >> "%CUSTOMER_DIR%\license_keys_db.json"
echo         "hwid_lock": "GLOBAL", >> "%CUSTOMER_DIR%\license_keys_db.json"
echo         "activated_ip": null, >> "%CUSTOMER_DIR%\license_keys_db.json"
echo         "created_at": "2026-02-12 11:00:00" >> "%CUSTOMER_DIR%\license_keys_db.json"
echo     } >> "%CUSTOMER_DIR%\license_keys_db.json"
echo ] >> "%CUSTOMER_DIR%\license_keys_db.json"

echo.
echo ========================================
echo [SUCCESS] Goi cai dat da san sang!
echo ========================================
echo.
echo Thu muc: %CUSTOMER_DIR%
echo Key: %CUSTOMER_KEY%
echo.
echo Ban co the ZIP thu muc nay va gui cho khach hang.
echo.
pause
