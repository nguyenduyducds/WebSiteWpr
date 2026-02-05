# Script kiểm tra dependencies của WprTool.exe
Write-Host "=== KIỂM TRA DEPENDENCIES CỦA WPRTOOLS ===" -ForegroundColor Cyan
Write-Host ""

$distPath = "dist\WprTool\_internal"

if (-not (Test-Path $distPath)) {
    Write-Host "ERROR: Không tìm thấy thư mục $distPath" -ForegroundColor Red
    Write-Host "Vui lòng build exe trước khi chạy script này" -ForegroundColor Yellow
    exit 1
}

Write-Host "Đang kiểm tra thư viện..." -ForegroundColor Yellow
Write-Host ""

# Danh sách thư viện cần thiết
$requiredLibs = @(
    "cv2",
    "numpy",
    "PIL",
    "selenium",
    "undetected_chromedriver",
    "playwright",
    "bs4",
    "requests",
    "urllib3",
    "vimeo",
    "customtkinter",
    "dotenv",
    "webdriver_manager"
)

$missingLibs = @()
$foundLibs = @()

foreach ($lib in $requiredLibs) {
    $libPath = Join-Path $distPath $lib
    if (Test-Path $libPath) {
        Write-Host "✓ $lib" -ForegroundColor Green
        $foundLibs += $lib
        
        # Kiểm tra kích thước
        $size = (Get-ChildItem -Path $libPath -Recurse | Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        Write-Host "  Kích thước: $sizeMB MB" -ForegroundColor Gray
    } else {
        Write-Host "✗ $lib - THIẾU!" -ForegroundColor Red
        $missingLibs += $lib
    }
}

Write-Host ""
Write-Host "=== KẾT QUẢ KIỂM TRA ===" -ForegroundColor Cyan

# Kiểm tra DLL files
Write-Host ""
Write-Host "Kiểm tra DLL files quan trọng:" -ForegroundColor Yellow
$requiredDlls = @(
    "python310.dll",
    "VCRUNTIME140.dll",
    "MSVCP140.dll",
    "libcrypto-1_1.dll",
    "libssl-1_1.dll"
)

foreach ($dll in $requiredDlls) {
    $dllPath = Join-Path $distPath $dll
    if (Test-Path $dllPath) {
        $size = (Get-Item $dllPath).Length
        $sizeMB = [math]::Round($size / 1MB, 2)
        Write-Host "✓ $dll ($sizeMB MB)" -ForegroundColor Green
    } else {
        Write-Host "✗ $dll - THIẾU!" -ForegroundColor Red
    }
}

# Kiểm tra cv2.pyd
Write-Host ""
Write-Host "Kiểm tra OpenCV binary:" -ForegroundColor Yellow
$cv2Pyd = Join-Path $distPath "cv2\cv2.pyd"
if (Test-Path $cv2Pyd) {
    $size = (Get-Item $cv2Pyd).Length
    $sizeMB = [math]::Round($size / 1MB, 2)
    Write-Host "✓ cv2.pyd ($sizeMB MB)" -ForegroundColor Green
} else {
    Write-Host "✗ cv2.pyd - THIẾU!" -ForegroundColor Red
}

# Tổng kết
Write-Host ""
Write-Host "=== TỔNG KẾT ===" -ForegroundColor Cyan
Write-Host "Tìm thấy: $($foundLibs.Count)/$($requiredLibs.Count) thư viện" -ForegroundColor $(if ($missingLibs.Count -eq 0) { "Green" } else { "Yellow" })

if ($missingLibs.Count -gt 0) {
    Write-Host ""
    Write-Host "Thư viện bị thiếu:" -ForegroundColor Red
    foreach ($lib in $missingLibs) {
        Write-Host "  - $lib" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Vui lòng build lại exe với WprTool.spec đã được cập nhật" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "✓ TẤT CẢ THƯ VIỆN ĐÃ ĐẦY ĐỦ!" -ForegroundColor Green
    
    # Tính tổng kích thước
    $totalSize = (Get-ChildItem -Path $distPath -Recurse | Measure-Object -Property Length -Sum).Sum
    $totalSizeMB = [math]::Round($totalSize / 1MB, 2)
    Write-Host "Tổng kích thước thư mục _internal: $totalSizeMB MB" -ForegroundColor Cyan
    
    $exeSize = (Get-Item "dist\WprTool\WprTool.exe").Length
    $exeSizeMB = [math]::Round($exeSize / 1MB, 2)
    Write-Host "Kích thước WprTool.exe: $exeSizeMB MB" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "Bạn có thể test exe bằng cách chạy: .\test_exe.bat" -ForegroundColor Yellow
}

Write-Host ""
