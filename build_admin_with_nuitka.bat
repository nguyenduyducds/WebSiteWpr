
@echo off
set "VENV_DIR=venv\Scripts\activate.bat"

if exist "%VENV_DIR%" (
    call "%VENV_DIR%"
) else (
    echo [WARNING] Venv not found, using global python
)

echo [INFO] Starting Compilation for Admin Manager...
echo [WARN] This process may take a few minutes (10-20 mins).

nuitka --standalone --onefile ^
    --enable-plugin=tk-inter ^
    --include-package=customtkinter ^
    --include-data-file=logo.ico=logo.ico ^
    --company-name="LVC Media" ^
    --product-name="LVC Key Manager" ^
    --file-version=2.1.0 ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=logo.ico ^
    --output-dir=build_nuitka_admin ^
    --output-filename="LVC Key Manager.exe" ^
    --remove-output ^
    admin_manager.py

echo.
echo ===================================================
echo [DONE] Build Complete! Check the 'build_nuitka_admin' folder.
echo ===================================================
pause
