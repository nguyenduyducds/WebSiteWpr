
@echo off
set "VENV_DIR=venv\Scripts\activate.bat"

if exist "%VENV_DIR%" (
    call "%VENV_DIR%"
) else (
    echo [WARNING] Venv not found, using global python
)

echo [INFO] Starting Compilation with Nuitka...
echo [WARN] This process may take a few minutes (10-20 mins).
echo [WARN] If Nuitka asks to download a C compiler (MinGW), please TYPE 'yes' and press ENTER.

nuitka --standalone --onefile ^
    --enable-plugin=tk-inter ^
    --include-package=customtkinter ^
    --include-data-dir=templates=templates ^
    --include-data-dir=model/js_worker=model/js_worker ^
    --include-data-dir=animaition=animaition ^
    --include-data-file=logo.ico=logo.ico ^
    --include-data-file=vimeo_api_config.json=vimeo_api_config.json ^
    --company-name="LVC Media" ^
    --product-name="LVC Auto Web" ^
    --file-version=2.1.0 ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=logo.ico ^
    --output-dir=build_nuitka ^
    --output-filename="LVC Media Web.exe" ^
    --remove-output ^
    main.py

echo.
echo ===================================================
echo [DONE] Build Complete! Check the 'build_nuitka' folder.
echo ===================================================
pause
