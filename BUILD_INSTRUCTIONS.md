# WprTool - Build Instructions

## Yêu cầu hệ thống
- Python 3.8+ 
- Windows 10/11 (hoặc Linux/Mac)
- RAM: 4GB+
- Dung lượng: 2GB trống

## Cách build exe

### Windows:
```bash
# Chạy script tự động
build_exe.bat

# Hoặc build thủ công:
pip install pyinstaller
pip install -r requirements.txt
pyinstaller --clean WprTool.spec
```

### Linux/Mac:
```bash
# Cấp quyền thực thi
chmod +x build_exe.sh

# Chạy script
./build_exe.sh

# Hoặc build thủ công:
pip install pyinstaller
pip install -r requirements.txt
pyinstaller --clean WprTool.spec
```

## Kết quả build

Sau khi build thành công, bạn sẽ có:

```
dist/WprTool/
├── WprTool.exe          # File thực thi chính
├── driver/              # Chrome drivers
├── config.json          # Cấu hình
├── sample_posts.csv     # Dữ liệu mẫu
├── BATCH_POSTING_GUIDE.md # Hướng dẫn
├── thumbnails/          # Thư mục output
└── [các file hệ thống khác]
```

## Chạy ứng dụng

1. Vào thư mục `dist/WprTool/`
2. Double-click `WprTool.exe`
3. Ứng dụng sẽ khởi động với giao diện GUI

## Tính năng chính

- ✅ Tự động đăng bài WordPress
- ✅ Tạo tài khoản Vimeo tự động
- ✅ Upload video lên Vimeo
- ✅ Batch processing
- ✅ Proxy support
- ✅ Smart thumbnail generation
- ✅ IP block detection
- ✅ VPN change notifications

## Troubleshooting

### Lỗi build:
- Đảm bảo Python 3.8+
- Cài đặt đầy đủ requirements
- Chạy với quyền Administrator

### Lỗi runtime:
- Kiểm tra antivirus (có thể block exe)
- Đảm bảo có kết nối internet
- Chrome driver sẽ tự động download

### Performance:
- File exe khoảng 200-300MB
- Khởi động lần đầu có thể chậm (10-15s)
- Sau đó chạy nhanh hơn

## Phân phối

File exe có thể chạy độc lập trên máy Windows khác mà không cần cài Python.

Chỉ cần copy toàn bộ thư mục `dist/WprTool/` sang máy khác và chạy `WprTool.exe`.