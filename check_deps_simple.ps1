# Script kiem tra dependencies cua WprTool.exe
Write-Host '=== KIEM TRA DEPENDENCIES CUA WPRTOOLS ===' -ForegroundColor Cyan
Write-Host ''

$distPath = 'dist\WprTool\_internal'

if (-not (Test-Path $distPath)) {
    Write-Host 'ERROR: Khong tim thay thu muc dist\WprTool\_internal' -ForegroundColor Red
    Write-Host 'Vui long build exe truoc khi chay script nay' -ForegroundColor Yellow
    exit 1
}

Write-Host 'Dang kiem tra thu vien...' -ForegroundColor Yellow
Write-Host ''

# Danh sach thu vien can thiet
$requiredLibs = @('cv2', 'numpy', 'PIL', 'selenium', 'undetected_chromedriver', 'playwright', 'bs4', 'requests', 'urllib3', 'vimeo', 'customtkinter', 'dotenv', 'webdriver_manager')

$missingLibs = @()
$foundLibs = @()

foreach ($lib in $requiredLibs) {
    $libPath = Join-Path $distPath $lib
    if (Test-Path $libPath) {
        Write-Host "OK $lib" -ForegroundColor Green
        $foundLibs += $lib
    } else {
        Write-Host "MISSING $lib" -ForegroundColor Red
        $missingLibs += $lib
    }
}

Write-Host ''
Write-Host '=== KET QUA KIEM TRA ===' -ForegroundColor Cyan
Write-Host "Tim thay: $($foundLibs.Count)/$($requiredLibs.Count) thu vien"

if ($missingLibs.Count -eq 0) {
    Write-Host ''
    Write-Host 'TAT CA THU VIEN DA DAY DU!' -ForegroundColor Green
} else {
    Write-Host ''
    Write-Host 'Thu vien bi thieu:' -ForegroundColor Red
    foreach ($lib in $missingLibs) {
        Write-Host "  - $lib" -ForegroundColor Red
    }
}
