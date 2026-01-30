# 🌐 Hướng Dẫn Setup Chrome Portable

## 🎯 **Mục đích:**
Bundle Chrome portable vào tool để:
- Không phụ thuộc Chrome của user
- Version cố định, không bị lỗi
- Chạy được trên mọi máy

## 📥 **Bước 1: Download Chrome Portable**

### **Option 1: Chrome for Testing (Recommended)**
```
Link: https://googlechromelabs.github.io/chrome-for-testing/
Version: 131.0.6778.204 (Stable)

Download:
- chrome-win64.zip
- chromedriver-win64.zip
```

### **Option 2: Chromium Portable**
```
Link: https://chromium.woolyss.com/
Download: chromium-win64.zip
```

## 📁 **Bước 2: Cấu trúc thư mục**

```
AuToWebWpr/
├── chrome_portable/
│   ├── chrome.exe          # Chrome executable
│   ├── chrome_100_percent.pak
│   ├── chrome_200_percent.pak
│   ├── resources.pak
│   ├── icudtl.dat
│   ├── v8_context_snapshot.bin
│   └── ... (all Chrome files)
├── driver/
│   └── chromedriver.exe    # ChromeDriver
├── dist/
│   └── WprTool_Package/
│       ├── WprTool.exe
│       ├── chrome_portable/  # Bundle Chrome vào đây
│       └── driver/
```

## 🔧 **Bước 3: Sửa code để dùng Chrome Portable**

### **File: model/selenium_wp.py**

```python
def init_driver(self, headless=False):
    options = uc.ChromeOptions()
    
    # Tìm Chrome portable
    if getattr(sys, 'frozen', False):
        # Running as exe
        base_path = sys._MEIPASS
        chrome_path = os.path.join(base_path, 'chrome_portable', 'chrome.exe')
        driver_path = os.path.join(base_path, 'driver', 'chromedriver.exe')
    else:
        # Running as script
        chrome_path = os.path.join(os.path.dirname(__file__), '..', 'chrome_portable', 'chrome.exe')
        driver_path = os.path.join(os.path.dirname(__file__), '..', 'driver', 'chromedriver.exe')
        chrome_path = os.path.abspath(chrome_path)
        driver_path = os.path.abspath(driver_path)
    
    # Set Chrome binary location
    if os.path.exists(chrome_path):
        options.binary_location = chrome_path
        print(f"[SELENIUM] Using portable Chrome: {chrome_path}")
    else:
        print("[SELENIUM] Portable Chrome not found, using system Chrome")
    
    # ... rest of options ...
    
    if os.path.exists(driver_path):
        self.driver = uc.Chrome(options=options, driver_executable_path=driver_path)
    else:
        self.driver = uc.Chrome(options=options)
```

## 📦 **Bước 4: Update PyInstaller spec**

### **File: WprTool.spec**

```python
datas = [
    ('chrome_portable', 'chrome_portable'),  # Bundle Chrome
    ('driver', 'driver'),
    ('config.json', '.'),
    # ... other files
]
```

## 🚀 **Bước 5: Build với Chrome Portable**

```bash
# 1. Download Chrome for Testing
# 2. Extract vào chrome_portable/
# 3. Download ChromeDriver tương ứng
# 4. Extract vào driver/
# 5. Build
pyinstaller --clean WprTool.spec
```

## 📊 **Kích thước:**

- **Không có Chrome**: ~113 MB
- **Có Chrome Portable**: ~250-300 MB
- **Trade-off**: Kích thước lớn hơn nhưng ổn định 100%

## ✅ **Ưu điểm:**

1. **Không cần Chrome trên máy user**
2. **Version cố định** - Không bị lỗi compatibility
3. **Chạy được mọi nơi** - Portable 100%
4. **Không conflict** với Chrome của user
5. **Dễ debug** - Biết chính xác version đang dùng

## ❌ **Nhược điểm:**

1. **Kích thước lớn** - ~300 MB thay vì 113 MB
2. **Download lâu hơn** - Nếu share qua internet
3. **Update Chrome** - Phải rebuild khi update Chrome

## 🎯 **Khuyến nghị:**

### **Nên dùng Chrome Portable nếu:**
- Tool dùng cho nhiều người
- Muốn ổn định tuyệt đối
- Không quan tâm kích thước file

### **Không cần Chrome Portable nếu:**
- Chỉ dùng cá nhân
- Máy đã có Chrome
- Muốn file nhỏ gọn

## 📝 **Download Links:**

### **Chrome for Testing (Stable)**
```
https://googlechromelabs.github.io/chrome-for-testing/
Version: 131.0.6778.204

Chrome: 
https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/win64/chrome-win64.zip

ChromeDriver:
https://storage.googleapis.com/chrome-for-testing-public/131.0.6778.204/win64/chromedriver-win64.zip
```

### **Chromium (Latest)**
```
https://chromium.woolyss.com/
https://download-chromium.appspot.com/
```

---

**Bạn muốn tôi setup Chrome Portable vào tool không?** 🤔