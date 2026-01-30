# Hướng dẫn Build Installer với Inno Setup

## 📋 Yêu cầu

1. **Inno Setup 6.x** - Download tại: https://jrsoftware.org/isdl.php
2. **PyInstaller** - Đã cài trong venv
3. **Python 3.8+** với tất cả dependencies

## 🔨 Các bước build

### Bước 1: Build EXE với PyInstaller

```bash
# Activate venv
venv\Scripts\activate

# Build EXE
python -m PyInstaller WprTool.spec --clean

# Hoặc dùng batch file
build_exe.bat
```

**Kết quả:** File `dist/WprTool.exe` được tạo

### Bước 2: Kiểm tra EXE

```bash
# Test EXE trước khi build installer
cd dist
WprTool.exe
```

Đảm bảo:
- ✅ Tool mở được
- ✅ Login được
- ✅ Post bài được
- ✅ Không có lỗi import

### Bước 3: Build Installer với Inno Setup

**Cách 1: Dùng Inno Setup GUI**

1. Mở **Inno Setup Compiler**
2. File → Open → Chọn `WprTool_Installer.iss`
3. Build → Compile (hoặc Ctrl+F9)
4. Đợi build xong

**Cách 2: Dùng Command Line**

```bash
# Nếu đã add Inno Setup vào PATH
iscc WprTool_Installer.iss

# Hoặc dùng full path
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" WprTool_Installer.iss
```

**Kết quả:** File `dist/WprTool_Setup_v3.0.0.exe` được tạo

### Bước 4: Test Installer

1. Chạy `dist/WprTool_Setup_v3.0.0.exe`
2. Cài đặt vào thư mục test
3. Chạy tool từ Start Menu hoặc Desktop
4. Test đầy đủ chức năng

## 📦 Cấu trúc sau khi build

```
dist/
├── WprTool.exe                      # EXE file (từ PyInstaller)
└── WprTool_Setup_v3.0.0.exe        # Installer (từ Inno Setup)
```

## 🎯 File ISS đã được update

### Version mới: **v3.0.0**

**Tính năng mới:**
- ✅ REST API Direct Method (10x faster)
- ✅ Auto-fallback to Selenium
- ✅ 100% reliable title/content/image saving
- ✅ Smart video embed extraction
- ✅ Enhanced car image API

### Thay đổi trong ISS:

1. **Version**: 2.0.1 → 3.0.0
2. **Welcome message**: Updated với features mới
3. **UninstallDelete**: Tự động xóa files tạm
4. **Icons**: Thêm Quick Launch icon
5. **Languages**: Thêm Vietnamese support
6. **Code section**: Thêm pre/post install checks

## 🔧 Tùy chỉnh ISS

### Thay đổi version:

```pascal
#define MyAppVersion "3.0.0"  // Đổi version ở đây
```

### Thêm files:

```pascal
[Files]
Source: "your_file.txt"; DestDir: "{app}"; Flags: ignoreversion
```

### Thay đổi icon:

```pascal
SetupIconFile=icon.ico  // Đặt file icon.ico vào root folder
```

### Thêm registry keys:

```pascal
[Registry]
Root: HKCU; Subkey: "Software\WprTool"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
```

## 📝 Checklist trước khi release

- [ ] Test EXE trên máy sạch (không có Python)
- [ ] Test Installer trên máy sạch
- [ ] Kiểm tra tất cả features hoạt động
- [ ] Test REST API method
- [ ] Test Selenium fallback
- [ ] Test video embed extraction
- [ ] Test car image API
- [ ] Kiểm tra uninstaller
- [ ] Scan virus (VirusTotal)
- [ ] Tạo README cho user

## 🚀 Build script tự động

Tạo file `build_all.bat`:

```batch
@echo off
echo ========================================
echo Building WprTool v3.0.0
echo ========================================

echo.
echo [1/3] Building EXE with PyInstaller...
call venv\Scripts\activate
python -m PyInstaller WprTool.spec --clean
if errorlevel 1 goto error

echo.
echo [2/3] Building Installer with Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" WprTool_Installer.iss
if errorlevel 1 goto error

echo.
echo [3/3] Done!
echo ========================================
echo Installer created: dist\WprTool_Setup_v3.0.0.exe
echo ========================================
pause
exit /b 0

:error
echo.
echo ========================================
echo ERROR: Build failed!
echo ========================================
pause
exit /b 1
```

Chạy:
```bash
build_all.bat
```

## 📊 Kích thước file

**Ước tính:**
- EXE file: ~150-200 MB (với Chrome Portable bundled)
- Installer: ~160-210 MB (compressed)

**Giảm kích thước:**
- Bỏ Chrome Portable khỏi bundle (yêu cầu user cài Chrome)
- Dùng UPX compress (có thể bị antivirus flag)
- Exclude unused modules trong spec file

## 🐛 Troubleshooting

### Lỗi: "Cannot find WprTool.exe"
→ Chạy PyInstaller trước: `build_exe.bat`

### Lỗi: "ISCC.exe not found"
→ Cài Inno Setup hoặc sửa path trong script

### Lỗi: "Missing dependencies"
→ Kiểm tra `requirements.txt` và rebuild EXE

### Installer không chạy được
→ Kiểm tra antivirus, thử disable tạm thời

### EXE bị antivirus block
→ Sign code với certificate (optional)
→ Submit false positive report

## ✅ Hoàn tất!

Sau khi build xong:

1. **Test installer** trên máy sạch
2. **Upload** lên GitHub Releases hoặc hosting
3. **Share** link download với users
4. **Tạo changelog** cho version mới

**File installer:** `dist/WprTool_Setup_v3.0.0.exe`

**Enjoy!** 🎉
