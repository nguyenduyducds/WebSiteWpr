# 🌐 Hướng Dẫn Sử Dụng Chrome Portable

## 🎯 **2 Cách Sử Dụng Tool:**

### **Cách 1: Dùng Chrome của máy (Hiện tại)** ✅
- **Ưu điểm**: File nhỏ (~113 MB), không cần download thêm
- **Nhược điểm**: Phụ thuộc Chrome version của máy, có thể bị lỗi

### **Cách 2: Dùng Chrome Portable (Khuyến nghị)** 🌟
- **Ưu điểm**: Ổn định 100%, không phụ thuộc máy user
- **Nhược điểm**: File lớn (~300 MB)

---

## 🚀 **Setup Chrome Portable (Tự động)**

### **Bước 1: Chạy script setup**
```bash
python setup_chrome_portable.py
```

Script sẽ tự động:
1. Download Chrome for Testing (v131.0.6778.204)
2. Download ChromeDriver tương ứng
3. Extract và setup vào đúng thư mục
4. Verify installation

### **Bước 2: Update WprTool.spec**

Thêm dòng này vào `datas`:
```python
datas = [
    ('chrome_portable', 'chrome_portable'),  # ← Thêm dòng này
    ('driver', 'driver'),
    ('config.json', '.'),
    # ... rest
]
```

### **Bước 3: Rebuild tool**
```bash
pyinstaller --clean WprTool.spec
```

### **Bước 4: Copy files vào package**
```bash
# Windows
xcopy chrome_portable dist\WprTool_Package\chrome_portable\ /E /I /Y
copy driver\chromedriver.exe dist\WprTool_Package\driver\
```

---

## 📦 **Setup Chrome Portable (Thủ công)**

### **Bước 1: Download Chrome**
```
Link: https://googlechromelabs.github.io/chrome-for-testing/
Version: 131.0.6778.204

Chrome:
https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/win64/chrome-win64.zip

ChromeDriver:
https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/win64/chromedriver-win64.zip
```

### **Bước 2: Extract files**
```
1. Extract chrome-win64.zip → chrome_portable/
2. Extract chromedriver-win64.zip → driver/
```

### **Bước 3: Verify structure**
```
AuToWebWpr/
├── chrome_portable/
│   ├── chrome.exe          ← Phải có file này
│   ├── chrome_100_percent.pak
│   ├── chrome_200_percent.pak
│   └── ... (nhiều files khác)
├── driver/
│   └── chromedriver.exe    ← Phải có file này
```

---

## 🔧 **Code đã được update**

File `model/selenium_wp.py` đã hỗ trợ Chrome Portable:

```python
# Tự động tìm Chrome Portable nếu có
if os.path.exists(chrome_path):
    options.binary_location = chrome_path
    print("[SELENIUM] Using portable Chrome")
else:
    print("[SELENIUM] Using system Chrome")
```

**Không cần sửa code gì thêm!** Tool sẽ tự động:
1. Tìm Chrome Portable trước
2. Nếu không có → Dùng Chrome của máy
3. Fallback nếu cả 2 đều fail

---

## 📊 **So sánh:**

| Feature | System Chrome | Portable Chrome |
|---------|---------------|-----------------|
| Kích thước | ~113 MB | ~300 MB |
| Ổn định | ⚠️ Phụ thuộc máy | ✅ 100% |
| Tương thích | ⚠️ Có thể lỗi | ✅ Luôn OK |
| Setup | ✅ Dễ | ⚠️ Cần download |
| Update | ✅ Tự động | ❌ Phải rebuild |

---

## 🎯 **Khuyến nghị:**

### **Dùng System Chrome nếu:**
- Chỉ dùng cá nhân
- Máy đã có Chrome
- Muốn file nhỏ gọn
- Không gặp lỗi version

### **Dùng Portable Chrome nếu:**
- Tool cho nhiều người
- Muốn ổn định tuyệt đối
- Gặp lỗi "version not supported"
- Máy không có Chrome

---

## 🐛 **Troubleshooting:**

### **Lỗi: "Cannot initialize Chrome"**
```
Giải pháp:
1. Chạy setup_chrome_portable.py
2. Rebuild tool
3. Hoặc cài Chrome trên máy
```

### **Lỗi: "Version not supported"**
```
Giải pháp:
1. Dùng Chrome Portable (khuyến nghị)
2. Hoặc update Chrome trên máy
```

### **Lỗi: "Chrome not found"**
```
Giải pháp:
1. Verify chrome_portable/chrome.exe exists
2. Rebuild với WprTool.spec updated
3. Check console logs
```

---

## 📝 **Quick Start:**

```bash
# Setup Chrome Portable
python setup_chrome_portable.py

# Update spec file (thêm chrome_portable vào datas)

# Rebuild
pyinstaller --clean WprTool.spec

# Done! Tool bây giờ có Chrome Portable
```

---

**Bạn muốn setup Chrome Portable không?** 
Chạy: `python setup_chrome_portable.py` 🚀