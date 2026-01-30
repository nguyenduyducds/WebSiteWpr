# 📋 Hướng Dẫn Paste Ảnh Từ Clipboard

## ✨ Tính Năng Mới: Paste Ảnh Trực Tiếp

Bây giờ bạn có thể **chụp màn hình và paste ảnh trực tiếp** vào trường "Link Ảnh Thumbnail" mà không cần lưu file thủ công!

---

## 🎯 Cách Sử Dụng

### Phương Pháp 1: Chụp Toàn Màn Hình
1. **Nhấn phím `PrtScn`** (Print Screen) để chụp toàn bộ màn hình
2. **Click vào ô "Link Ảnh Thumbnail"** trong form đăng bài
3. **Nhấn `Ctrl+V`** để paste ảnh
4. ✅ **Xong!** Ảnh sẽ tự động được lưu vào thư mục `thumbnails/` và đường dẫn sẽ tự động điền vào ô

### Phương Pháp 2: Chụp Vùng Chọn (Windows 10/11)
1. **Nhấn `Win + Shift + S`** để mở Snipping Tool
2. **Chọn vùng** bạn muốn chụp
3. **Click vào ô "Link Ảnh Thumbnail"**
4. **Nhấn `Ctrl+V`**
5. ✅ **Xong!**

### Phương Pháp 3: Copy Ảnh Từ File Explorer
1. **Click phải vào file ảnh** trong File Explorer
2. **Chọn "Copy"** (hoặc nhấn `Ctrl+C`)
3. **Click vào ô "Link Ảnh Thumbnail"**
4. **Nhấn `Ctrl+V`**
5. ✅ **Xong!**

---

## 📁 Lưu Trữ Tự Động

- Tất cả ảnh paste sẽ được lưu vào thư mục: `thumbnails/`
- Tên file tự động: `pasted_thumb_YYYYMMDD_HHMMSS.png`
- Ví dụ: `pasted_thumb_20260127_170230.png`

---

## 🎨 Định Dạng Hỗ Trợ

Khi paste từ clipboard:
- ✅ Screenshot (PNG)
- ✅ Copy ảnh từ trình duyệt
- ✅ Copy file ảnh (.png, .jpg, .jpeg, .webp, .gif, .bmp)

---

## 💡 Tips & Tricks

### 1. Chụp Nhanh Với Snipping Tool
- `Win + Shift + S` → Chọn vùng → `Ctrl+V` vào ô
- Nhanh nhất cho việc chụp một phần màn hình

### 2. Chụp Cửa Sổ Cụ Thể
- `Alt + PrtScn` → Chụp cửa sổ đang active
- `Ctrl+V` vào ô

### 3. Xóa Ảnh Tự Động
- Sau khi đăng bài thành công, ảnh thumbnail sẽ **tự động bị xóa** khỏi thư mục `thumbnails/`
- Giúp tiết kiệm dung lượng ổ cứng

---

## 🔧 Test Tính Năng

Nếu muốn test riêng tính năng này:

```bash
# Chạy demo đơn giản
python demo_clipboard_paste.py

# Hoặc test clipboard
python test_clipboard_paste.py
```

---

## ⚠️ Lưu Ý

1. **Clipboard phải chứa ảnh**: Nếu clipboard trống hoặc chứa text, sẽ có thông báo lỗi
2. **Quyền ghi file**: Đảm bảo ứng dụng có quyền tạo thư mục `thumbnails/`
3. **Định dạng PNG**: Tất cả ảnh paste sẽ được lưu dưới dạng PNG để đảm bảo chất lượng

---

## 🎉 Ví Dụ Workflow

### Đăng Bài Video Facebook Nhanh:

1. **Mở video Facebook** trên trình duyệt
2. **Chụp thumbnail** (Win + Shift + S)
3. **Mở ứng dụng** → Tab "Đăng Bài Lẻ"
4. **Nhập tiêu đề** video
5. **Paste link Facebook** vào ô Video URL
6. **Click vào ô Thumbnail** → **Ctrl+V**
7. **Nhấn "🚀 ĐĂNG NGAY"**

✅ **Xong trong vài giây!**

---

## 🐛 Troubleshooting

### Lỗi: "Clipboard không chứa ảnh"
- ✅ Hãy chụp màn hình trước (PrtScn hoặc Win+Shift+S)
- ✅ Đảm bảo bạn đã copy ảnh, không phải text

### Lỗi: "Không thể lưu ảnh"
- ✅ Kiểm tra quyền ghi file trong thư mục ứng dụng
- ✅ Đảm bảo ổ đĩa còn dung lượng trống

### Paste không hoạt động
- ✅ Đảm bảo đã click vào ô "Link Ảnh Thumbnail"
- ✅ Nhấn đúng tổ hợp phím `Ctrl+V` (không phải `Ctrl+Shift+V`)

---

## 📦 Dependencies

Tính năng này sử dụng thư viện **Pillow** (PIL):

```bash
pip install Pillow
```

Đã được thêm vào `requirements.txt` tự động.

---

## 🚀 Tương Lai

Các tính năng có thể thêm:
- [ ] Crop/resize ảnh trước khi lưu
- [ ] Preview ảnh sau khi paste
- [ ] Hỗ trợ paste nhiều ảnh cùng lúc
- [ ] Tự động optimize kích thước ảnh

---

**Chúc bạn sử dụng vui vẻ! 🎉**
