# Fix: Vimeo Token 401 Unauthorized

## 🔴 Vấn đề

Token hiện tại bị lỗi **401 Unauthorized**:
```
{"error":"You must provide a valid authenticated access token."}
```

**Token hiện tại:**
```
864ebfba0855016fd5fd76729ad004c5
```

Token này:
- ✅ Format đúng (32 ký tự, alphanumeric)
- ❌ Không được Vimeo API chấp nhận

---

## 🎯 Giải pháp: Generate Token MỚI

### Bước 1: Vào Vimeo Developer Portal

Mở browser và vào:
```
https://developer.vimeo.com/apps
```

Đăng nhập nếu chưa đăng nhập.

### Bước 2: Chọn App

Bạn sẽ thấy app của mình (có thể tên là "WprTool" hoặc tên khác).

Click vào app đó.

### Bước 3: Vào tab "Authentication"

Trong trang app, click tab **"Authentication"** (không phải "Details").

### Bước 4: Xóa token cũ (nếu có)

Scroll xuống phần **"Personal Access Tokens"**.

Nếu thấy token cũ trong danh sách, click **"Delete"** hoặc **"Revoke"** để xóa nó.

### Bước 5: Generate Token MỚI

Scroll lên phần **"Generate an Access Token"**.

**QUAN TRỌNG:** Phải tick đủ các scopes sau:

```
✅ Public          - View public videos
✅ Private         - View private videos  
✅ Purchased       - View purchased videos
✅ Create          - Create new videos
✅ Edit            - Edit video metadata
✅ Delete          - Delete videos
✅ Upload          - Upload videos
✅ Video Files     - Manage video files
```

**Lưu ý:** Tick NHIỀU scopes hơn tốt hơn thiếu!

### Bước 6: Click "Generate"

Click nút **"Generate"** hoặc **"Generate Token"**.

### Bước 7: Copy Token MỚI

Sau khi generate, bạn sẽ thấy một token MỚI hiện ra.

Token này sẽ dài hơn token cũ (khoảng 50-100 ký tự).

Ví dụ:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6A7B8C9D0E1F2
```

**Copy toàn bộ token này!**

⚠️ **QUAN TRỌNG:** Token chỉ hiện 1 lần! Nếu đóng trang mà chưa copy, phải generate lại.

### Bước 8: Paste vào Config

Mở file `vimeo_api_config.json` và thay token cũ bằng token mới:

```json
{
    "access_token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0...",  ← Token MỚI
    "client_id": "c98b7960179d9b0a7057603f1c8a88def562250e",
    "client_secret": "pftWGNTTxptr8taF5t4MHzYPn8ure2h4WMdmZXCE..."
}
```

**Save file.**

### Bước 9: Test lại

```bash
python debug_vimeo_token.py
```

Nếu thành công, bạn sẽ thấy:

```
✅ SUCCESS! User info:
  Name: Your Name
  Link: https://vimeo.com/user123456
  
Quota info:
  Total: 500.0 MB
  Used: 0.0 MB
  Free: 500.0 MB
```

---

## 🔍 Tại sao Token cũ không hoạt động?

Có thể vì:

1. **Token được generate từ "Unauthenticated" mode**
   - Vimeo có 2 loại token: Authenticated và Unauthenticated
   - Unauthenticated token không có quyền gì
   - Phải dùng Authenticated token

2. **Token thiếu scopes**
   - Token được generate mà không tick scopes
   - Vimeo API từ chối token không có quyền

3. **Token bị revoke**
   - Có thể bạn đã delete token này trước đó
   - Hoặc Vimeo tự động revoke vì lý do bảo mật

4. **Token format sai**
   - Token 32 ký tự thường là token cũ hoặc test token
   - Token thật thường dài hơn (50-100 ký tự)

---

## 📋 Checklist Generate Token Đúng

Khi generate token, đảm bảo:

- [ ] Đã đăng nhập Vimeo
- [ ] Đã vào https://developer.vimeo.com/apps
- [ ] Đã chọn app của mình
- [ ] Đã vào tab **"Authentication"** (không phải "Details")
- [ ] Đã scroll xuống **"Generate an Access Token"**
- [ ] Đã tick **ÍT NHẤT** các scopes: Public, Private, Upload, Edit, Video Files
- [ ] Đã click **"Generate"**
- [ ] Token hiện ra dài khoảng 50-100 ký tự
- [ ] Đã copy toàn bộ token
- [ ] Đã paste vào `vimeo_api_config.json`
- [ ] Đã save file
- [ ] Đã test: `python debug_vimeo_token.py`

---

## 🎯 Token đúng trông như thế nào?

### ❌ Token SAI (32 ký tự):
```
864ebfba0855016fd5fd76729ad004c5
```

### ✅ Token ĐÚNG (50-100 ký tự):
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0
```

Token đúng:
- Dài hơn (50-100 ký tự)
- Có cả chữ hoa và chữ thường
- Có thể có dấu gạch ngang `-` hoặc underscore `_`

---

## 🆘 Nếu vẫn lỗi

### Thử 1: Generate token với TẤT CẢ scopes

Tick tất cả các scopes có trong danh sách, không bỏ sót cái nào.

### Thử 2: Tạo app MỚI

1. Vào https://developer.vimeo.com/apps
2. Click "Create App"
3. Điền thông tin:
   - Name: WprTool2
   - Description: Auto upload
   - URL: http://localhost
4. Generate token từ app mới này

### Thử 3: Check account Vimeo

Đảm bảo:
- Account Vimeo đã verify email
- Account không bị suspend
- Account có quota upload (ít nhất 500 MB)

### Thử 4: Dùng OAuth flow (Advanced)

Nếu Personal Access Token không hoạt động, có thể cần dùng OAuth 2.0 flow.

Nhưng thường Personal Access Token là đủ.

---

## 📞 Support

Nếu vẫn không được, có thể:

1. **Check Vimeo API Status:**
   - https://status.vimeo.com/
   - Xem có sự cố API không

2. **Contact Vimeo Support:**
   - https://vimeo.com/help/contact
   - Hỏi về API token issue

3. **Check Vimeo Developer Forum:**
   - https://vimeo.com/forums/api
   - Có thể người khác gặp vấn đề tương tự

---

**Tóm tắt:** Token hiện tại không hợp lệ. Cần generate token MỚI từ Vimeo Developer Portal với đủ scopes (Public, Private, Upload, Edit, Video Files).
