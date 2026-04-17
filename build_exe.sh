#!/bin/bash

echo "========================================"
echo "        Building WprTool"
echo "========================================"

echo
echo "[1/4] Installing PyInstaller..."
pip install pyinstaller

echo
echo "[2/4] Installing required packages..."
pip install -r requirements.txt

echo
echo "[3/4] Building executable..."
pyinstaller --clean WprTool.spec

echo
echo "[4/4] Copying additional files..."
if [ -d "dist/WprTool" ]; then
    echo "Copying sample files..."
    cp "sample_posts.csv" "dist/WprTool/" 2>/dev/null || true
    cp "BATCH_POSTING_GUIDE.md" "dist/WprTool/" 2>/dev/null || true
    
    echo "Creating output directories..."
    mkdir -p "dist/WprTool/thumbnails"
    
    echo
    echo "========================================"
    echo "        Build Complete!"
    echo "========================================"
    echo
    echo "Executable location: dist/WprTool/WprTool"
    echo
    echo "Files included:"
    echo "- WprTool (Main application)"
    echo "- driver/ (Chrome drivers)"
    echo "- config.json (Configuration)"
    echo "- sample_posts.csv (Sample data)"
    echo "- BATCH_POSTING_GUIDE.md (Guide)"
    echo "- thumbnails/ (Output folder)"
    echo
else
    echo
    echo "========================================"
    echo "        Build Failed!"
    echo "========================================"
    echo "Please check the error messages above."
fi