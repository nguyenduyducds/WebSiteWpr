@echo off
chcp 65001 >nul
title LVC Media - Build Nuitka Full

echo ========================================
echo  LVC Media Web - Build Nuitka (FULL)
echo  Ma hoa code + Day du thu vien
echo ========================================
echo.

REM === Activate venv ===
if exist "venv\Scripts\activate.bat" (
    echo [1/6] Activating venv...
    call venv\Scripts\activate.bat
) else (
    echo [WARN] Venv not found, using global Python
)

REM === Check nuitka ===
python -m nuitka --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Nuitka not found! Installing...
    pip install nuitka
)

REM === Check ordered-set for faster builds ===
python -c "import ordered_set" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing ordered-set...
    pip install ordered-set
)

REM === Check and install missing packages ===
echo [INFO] Checking dependencies...
python -c "import yt_dlp" >nul 2>&1
if errorlevel 1 ( echo [INFO] Installing yt-dlp... & pip install yt-dlp )
python -c "import cloudscraper" >nul 2>&1
if errorlevel 1 ( echo [INFO] Installing cloudscraper... & pip install cloudscraper )
python -c "import scipy" >nul 2>&1
if errorlevel 1 ( echo [INFO] Installing scipy... & pip install scipy )

echo.
echo [2/6] Cleaning old build output...
if exist "build_nuitka" rmdir /s /q "build_nuitka"
mkdir "build_nuitka"

echo.
echo [3/6] Starting Nuitka compilation...
echo       (Lan dau co the mat 15-30 phut, lan sau nhanh hon)
echo.

python -m nuitka ^
    --standalone ^
    --onefile ^
    --enable-plugin=tk-inter ^
    --include-package=customtkinter ^
    --include-package=selenium ^
    --include-package=undetected_chromedriver ^
    --include-package=cv2 ^
    --include-package=numpy ^
    --include-package=PIL ^
    --include-package=requests ^
    --include-package=urllib3 ^
    --include-package=bs4 ^
    --include-package=playwright ^
    --include-package=vimeo ^
    --include-package=yt_dlp ^
    --include-package=cloudscraper ^
    --include-package=webdriver_manager ^
    --include-package=packaging ^
    --include-package=pyperclip ^
    --include-package=scipy ^
    --include-package=certifi ^
    --include-package=charset_normalizer ^
    --include-package=idna ^
    --include-package=dotenv ^
    --include-package=model ^
    --include-package=view ^
    --include-package=controller ^
    --include-module=winreg ^
    --include-module=ctypes ^
    --include-module=ctypes.wintypes ^
    --include-module=xml.etree.ElementTree ^
    --include-module=xmlrpc.client ^
    --include-module=http.client ^
    --include-module=http.cookiejar ^
    --include-module=concurrent.futures ^
    --include-module=pickle ^
    --include-module=uuid ^
    --include-module=hashlib ^
    --include-module=base64 ^
    --include-module=mimetypes ^
    --include-module=webbrowser ^
    --include-module=socket ^
    --include-module=platform ^
    --include-module=zipfile ^
    --include-module=tempfile ^
    --include-module=shutil ^
    --include-module=csv ^
    --include-module=dataclasses ^
    --nofollow-import-to=torch ^
    --nofollow-import-to=torchvision ^
    --nofollow-import-to=torchaudio ^
    --nofollow-import-to=basicsr ^
    --nofollow-import-to=facexlib ^
    --nofollow-import-to=gfpgan ^
    --nofollow-import-to=realesrgan ^
    --nofollow-import-to=tensorflow ^
    --nofollow-import-to=keras ^
    --nofollow-import-to=sklearn ^
    --nofollow-import-to=setuptools ^
    --nofollow-import-to=distutils ^
    --nofollow-import-to=pytest ^
    --nofollow-import-to=IPython ^
    --nofollow-import-to=jupyter ^
    --include-data-dir=templates=templates ^
    --include-data-dir=animaition=animaition ^
    --include-data-dir=model/js_worker=model/js_worker ^
    --include-data-files=logo.ico=logo.ico ^
    --include-data-files=vimeo_api_config.json=vimeo_api_config.json ^
    --include-data-files=config_template.json=config_template.json ^
    --company-name="LVC Media" ^
    --product-name="LVC Auto Web" ^
    --file-version=2.1.0 ^
    --file-description="LVC Media Auto Web Publisher" ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=logo.ico ^
    --output-dir=build_nuitka ^
    --output-filename="LVC Media Web.exe" ^
    --remove-output ^
    --assume-yes-for-downloads ^
    --report=build_nuitka\compilation_report.xml ^
    main.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo [FAILED] Build that bai!
    echo Xem log o tren.
    echo ========================================
    pause
    exit /b 1
)

echo.
echo [4/6] Copying runtime assets...

if exist "chrome_portable" (
    echo    - chrome_portable...
    xcopy /E /I /Y /Q "chrome_portable" "build_nuitka\chrome_portable" >nul
)
if exist "driver" (
    echo    - driver...
    xcopy /E /I /Y /Q "driver" "build_nuitka\driver" >nul
)
if exist "animaition" (
    echo    - animaition...
    xcopy /E /I /Y /Q "animaition" "build_nuitka\animaition" >nul
)
if exist "templates" (
    echo    - templates...
    xcopy /E /I /Y /Q "templates" "build_nuitka\templates" >nul
)
if exist "vimeo_api_config.json" copy /Y "vimeo_api_config.json" "build_nuitka\" >nul
if exist "config_template.json" copy /Y "config_template.json" "build_nuitka\" >nul
if exist "thumbnail_ai_config.json" copy /Y "thumbnail_ai_config.json" "build_nuitka\" >nul
if exist "logo.ico" copy /Y "logo.ico" "build_nuitka\" >nul

echo.
echo [5/6] Creating README...
(
echo LVC Media Web - Auto Publisher v2.1.0
echo ======================================
echo Chay "LVC Media Web.exe" de bat dau.
echo KHONG xoa bat ky file/folder nao trong thu muc nay.
) > "build_nuitka\README.txt"

echo.
echo ========================================
echo [6/6] BUILD HOAN THANH!
echo  Output: build_nuitka\LVC Media Web.exe
echo ========================================
dir /b "build_nuitka\"
echo.
pause
exit /b 0
