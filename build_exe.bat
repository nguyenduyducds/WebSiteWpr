@echo off
echo ========================================
echo        Building WprTool.exe
echo ========================================

echo.
echo [1/4] Installing PyInstaller...
pip install pyinstaller

echo.
echo [2/4] Installing required packages...
pip install -r requirements.txt

echo.
echo [3/4] Building executable...
pyinstaller --clean WprTool.spec

echo.
echo [4/4] Copying additional files...
if exist "dist\WprTool.exe" (
    echo Creating WprTool package directory...
    mkdir "dist\WprTool_Package" 2>nul
    
    echo Copying executable...
    copy "dist\WprTool.exe" "dist\WprTool_Package\" >nul
    
    echo Copying sample files...
    copy "sample_posts.csv" "dist\WprTool_Package\" >nul
    copy "BATCH_POSTING_GUIDE.md" "dist\WprTool_Package\" >nul
    copy "AUTO_VIDEO_POST_GUIDE.md" "dist\WprTool_Package\" >nul
    copy "VIDEO_EMBED_GUIDE.md" "dist\WprTool_Package\" >nul
    copy "fix_thumbnail_issue.md" "dist\WprTool_Package\" >nul
    copy "CHANGELOG.md" "dist\WprTool_Package\" >nul
    copy "config.json" "dist\WprTool_Package\" >nul
    
    echo Creating output directories...
    mkdir "dist\WprTool_Package\thumbnails" 2>nul
    
    echo.
    echo ========================================
    echo        Build Complete!
    echo ========================================
    echo.
    echo Executable location: dist\WprTool.exe
    echo Package location: dist\WprTool_Package\
    echo.
    echo Files included:
    echo - WprTool.exe (Main application - Standalone)
    echo - config.json (Configuration)
    echo - sample_posts.csv (Sample data)
    echo - BATCH_POSTING_GUIDE.md (Batch posting guide)
    echo - AUTO_VIDEO_POST_GUIDE.md (Auto video guide)
    echo - VIDEO_EMBED_GUIDE.md (Video embed troubleshooting)
    echo - fix_thumbnail_issue.md (Thumbnail fix guide)
    echo - thumbnails\ (Output folder)
    echo.
    echo Note: WprTool.exe is a standalone executable that includes
    echo all dependencies. Chrome drivers will be downloaded automatically.
    echo.
    echo Size: ~113 MB
    echo.
    pause
    exit /b 0
)

echo.
echo ========================================
echo        Build Failed!
echo ========================================
echo Please check the error messages above.
pause
exit /b 1