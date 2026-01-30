# Cách lấy Vimeo Access Token (Chi tiết có ảnh)

## 🎯 Vấn đề hiện tại

Bạn đã điền:
```json
{
    "access_token": "https://api.vimeo.com/oauth/access_token",  ❌ SAI - Đây là URL
    "client_id": "c98b7960179d9b0a7057603f1c8a88def562250e",     ✅ ĐÚNG
    "client_secret": "pftWGNTTxptr8taF5t4MHzYPn8ure2h4WMdmZXCE..." ✅ ĐÚNG
}
```

**access_token** phải là một chuỗi token dài, không phải URL!

---

## 📋 Các bước lấy Access Token

### Bước 1: Vào Vimeo Developer Portal

1. Mở browser
2. Vào: **https://developer.vimeo.com/apps**
3. Đăng nhập Vimeo (nếu chưa đăng nhập)

### Bước 2: Chọn App của bạn

Bạn sẽ thấy danh sách apps. Click vào app bạn đã tạo.

(Nếu chưa có app, click **"Create App"** và tạo mới)

### Bước 3: Vào tab "Authentication"

Trong trang app, bạn sẽ thấy các tabs:
- Details
- **Authentication** ← Click vào đây
- Webhooks
- ...

### Bước 4: Generate Access Token

Scroll xuống phần **"Generate an Access Token"**

Bạn sẽ thấy:

```
┌─────────────────────────────────────────────┐
│ Generate an Access Token                    │
├─────────────────────────────────────────────┤
│                                             │
│ Select the scopes you need:                 │
│                                             │
│ ☐ Public                                    │
│ ☐ Private                                   │
│ ☐ Purchased                                 │
│ ☐ Create                                    │
│ ☐ Edit                                      │
│ ☐ Delete                                    │
│ ☐ Interact                                  │
│ ☐ Upload                                    │
│ ☐ Video Files                               │
│ ☐ Stats                                     │
│                                             │
│ [Generate] button                           │
└─────────────────────────────────────────────┘
```

### Bước 5: Chọn Scopes (Quyền)

**QUAN TRỌNG:** Phải tick các scopes này:

- ✅ **Public** - Xem video public
- ✅ **Private** - Xem video private
- ✅ **Create** - Tạo video mới
- ✅ **Edit** - Sửa video metadata
- ✅ **Upload** - Upload video
- ✅ **Video Files** - Quản lý video files

(Có thể tick thêm các scopes khác nếu muốn)

### Bước 6: Click "Generate"

Click nút **"Generate"** hoặc **"Generate Token"**

### Bước 7: Copy Access Token

Sau khi generate, bạn sẽ thấy một chuỗi token dài như:

```
1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
```

**Copy toàn bộ chuỗi này!**

⚠️ **LƯU Ý:** Token chỉ hiện 1 lần! Nếu bạn đóng trang mà chưa copy, phải generate lại.

### Bước 8: Paste vào config file

Mở file `vimeo_api_config.json` và paste token vào:

```json
{
    "access_token": "1234567890abcdefghijklmnopqrstuvwxyz...",  ← Paste vào đây
    "client_id": "c98b7960179d9b0a7057603f1c8a88def562250e",
    "client_secret": "pftWGNTTxptr8taF5t4MHzYPn8ure2h4WMdmZXCE..."
}
```

Save file.

---

## 🧪 Test lại

Sau khi paste token đúng, chạy:

```bash
python test_vimeo_api.py
```

Nếu thành công, bạn sẽ thấy:

```
✅ API client initialized!
✅ User info retrieved!

👤 User: Your Name
💾 Total Quota: 500.0 MB
📊 Used: 50.0 MB (10.0%)
✅ Free: 450.0 MB

🎉 API is ready to use!
```

---

## 🔍 Cách phân biệt Token đúng/sai

### ❌ SAI (URL):
```
https://api.vimeo.com/oauth/access_token
```

### ✅ ĐÚNG (Token):
```
1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
```

Token thật:
- Dài khoảng 50-100 ký tự
- Chỉ có chữ và số (a-z, A-Z, 0-9)
- Không có dấu `/` hay `://`
- Không bắt đầu bằng `http`

---

## 🐛 Troubleshooting

### Vấn đề 1: Không thấy nút "Generate"

**Nguyên nhân:** Bạn chưa vào đúng tab

**Giải pháp:**
1. Vào https://developer.vimeo.com/apps
2. Click vào app của bạn
3. Click tab **"Authentication"** (không phải "Details")
4. Scroll xuống phần "Generate an Access Token"

### Vấn đề 2: Generate rồi nhưng không thấy token

**Nguyên nhân:** Chưa tick scopes

**Giải pháp:**
1. Tick ít nhất: Public, Private, Upload, Edit, Video Files
2. Click "Generate" lại

### Vấn đề 3: Token bị lỗi "Invalid"

**Nguyên nhân:** Token đã hết hạn hoặc bị revoke

**Giải pháp:**
1. Vào https://developer.vimeo.com/apps
2. Chọn app
3. Tab "Authentication"
4. Scroll xuống "Personal Access Tokens"
5. Delete token cũ
6. Generate token mới

### Vấn đề 4: "Insufficient scope"

**Nguyên nhân:** Token không có đủ quyền

**Giải pháp:**
1. Generate token mới
2. Nhớ tick đủ scopes: Public, Private, Upload, Edit, Video Files

---

## 📸 Hình minh họa (Text-based)

```
Vimeo Developer Portal
├── My Apps
│   └── WprTool (Your App)
│       ├── Details
│       ├── Authentication ← VÀO ĐÂY
│       │   ├── Client Identifier: c98b796...
│       │   ├── Client Secrets: pftWGNT...
│       │   └── Generate an Access Token
│       │       ├── Select scopes:
│       │       │   ✅ Public
│       │       │   ✅ Private
│       │       │   ✅ Upload
│       │       │   ✅ Edit
│       │       │   ✅ Video Files
│       │       └── [Generate] ← CLICK ĐÂY
│       │           └── Token: 1234567890abc... ← COPY CÁI NÀY
│       └── Webhooks
```

---

## ✅ Checklist

Trước khi test, check lại:

- [ ] Đã vào https://developer.vimeo.com/apps
- [ ] Đã chọn app
- [ ] Đã vào tab "Authentication"
- [ ] Đã tick scopes: Public, Private, Upload, Edit, Video Files
- [ ] Đã click "Generate"
- [ ] Đã copy token (chuỗi dài, không phải URL)
- [ ] Đã paste vào `vimeo_api_config.json`
- [ ] Đã save file
- [ ] Đã chạy `python test_vimeo_api.py`

Nếu tất cả OK → Bạn sẽ thấy user info và quota! 🎉

---

**Tóm tắt:** Token phải là chuỗi ký tự dài, không phải URL! Generate từ tab "Authentication" trong Vimeo Developer Portal.
