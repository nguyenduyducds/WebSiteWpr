# Hướng dẫn Upload Video lên Vimeo

## ⚠️ LƯU Ý QUAN TRỌNG

Sau khi upload video lên Vimeo, **PHẢI ĐỢI** Vimeo process video xong mới có thể dùng embed code!

## ✅ TÍNH NĂNG MỚI (v3.0.0)

Tool giờ đã **TỰ ĐỘNG ĐỢI** video xử lý xong!

### Cách hoạt động:
1. Upload video lên Vimeo
2. Tool **GIỮ NGUYÊN TRANG** upload (không chuyển trang)
3. Tự động theo dõi:
   - ⏳ "Uploading X%" → Đợi đến 100%
   - 🔄 "Upload complete" → Đợi tối ưu hóa
   - 🔄 "Optimizing..." → Đợi xử lý xong
   - ✅ "Go to video" xuất hiện → Video sẵn sàng!
4. Tự động lấy embed code khi video đã xem được
5. Tự động tạo thumbnail

**Thời gian đợi tối đa:** 15 phút (900 giây)

### Lợi ích:
- ✅ Không cần đợi thủ công
- ✅ Không cần check Vimeo
- ✅ Video luôn sẵn sàng khi post lên WordPress
- ✅ Giảm lỗi "video không hiển thị"

## 🕐 Thời gian đợi

- **Video ngắn** (< 5 phút): 2-5 phút
- **Video trung bình** (5-15 phút): 5-10 phút  
- **Video dài** (> 15 phút): 10-30 phút

## ✅ Cách kiểm tra video đã sẵn sàng

### Trên Vimeo.com:

1. Vào trang video vừa upload
2. Kiểm tra:
   - ✅ **Thumbnail hiện rõ** (không còn icon camera đen)
   - ✅ **Video có thể play được**
   - ✅ **Không còn chữ "What's next" hoặc "Processing"**
   - ✅ **Có nút "Share" và "Embed"**

### Trong tool:

Khi upload xong, tool sẽ hiện:
```
✅ [UPLOADED] Video Title
🔗 Embed Code: <div style="padding:56.25%...
🖼 Thumbnail: C:\...\thumb_123456.jpg
```

**NHƯNG** video chưa thể xem được ngay!

## 🚫 Lỗi thường gặp

### Lỗi 1: Video không hiển thị trên WordPress
**Nguyên nhân:** Post bài ngay sau khi upload, video chưa được process

**Giải pháp:**
1. Đợi 5-10 phút
2. Vào Vimeo check video đã play được chưa
3. Nếu chưa → Đợi thêm
4. Nếu rồi → Post lại bài (hoặc edit bài cũ)

### Lỗi 2: Embed code bị lỗi
**Nguyên nhân:** Lấy embed code khi video đang process

**Giải pháp:**
1. Vào Vimeo
2. Click vào video
3. Click "Share" → "Embed"
4. Copy embed code MỚI
5. Paste vào tool và post lại

### Lỗi 3: Video bị private/restricted
**Nguyên nhân:** Vimeo account free có giới hạn

**Giải pháp:**
1. Vào Vimeo → Video Settings
2. Privacy → Chọn "Anyone" (Public)
3. Hoặc "Hide from Vimeo.com" (vẫn embed được)

## 💡 Workflow đúng

### Cách 1: Upload trước, post sau (KHUYẾN NGHỊ)

```
1. Upload video lên Vimeo (dùng tool)
   ↓
2. Đợi 5-10 phút (làm việc khác)
   ↓
3. Check video trên Vimeo (play được chưa?)
   ↓
4. Lấy embed code từ Vimeo
   ↓
5. Post lên WordPress (dùng tool)
   ↓
6. ✅ Video hiển thị OK!
```

### Cách 2: Batch upload (cho nhiều video)

```
1. Upload TẤT CẢ videos lên Vimeo
   ↓
2. Đợi 30-60 phút (đi ăn, nghỉ ngơi)
   ↓
3. Check tất cả videos đã OK
   ↓
4. Lấy embed codes
   ↓
5. Batch post lên WordPress
   ↓
6. ✅ Tất cả videos OK!
```

## 🔧 Tính năng tự động (✅ ĐÃ CÓ - v3.0.0)

Tool giờ đã có:
- ✅ Tự động check video status
- ✅ Đợi video process xong (tối đa 15 phút)
- ✅ Tự động lấy embed code khi sẵn sàng
- ✅ Thông báo khi video ready
- ✅ Giữ nguyên trang upload (không chuyển trang)

**Bạn chỉ cần bấm Upload và đợi tool làm hết!**

## 📊 Bảng thời gian ước tính

| Độ dài video | Thời gian process | Thời gian an toàn |
|--------------|-------------------|-------------------|
| < 2 phút | 2-3 phút | 5 phút |
| 2-5 phút | 3-5 phút | 7 phút |
| 5-10 phút | 5-8 phút | 10 phút |
| 10-20 phút | 8-15 phút | 20 phút |
| > 20 phút | 15-30 phút | 40 phút |

**Lưu ý:** Thời gian phụ thuộc vào:
- Chất lượng video (HD, 4K)
- Kích thước file
- Tải trọng server Vimeo
- Loại account (Free/Pro)

## ✅ Checklist trước khi post

- [ ] Video đã upload xong lên Vimeo
- [ ] Đã đợi ít nhất 5 phút
- [ ] Vào Vimeo check video play được
- [ ] Thumbnail hiện rõ ràng
- [ ] Không còn chữ "Processing"
- [ ] Đã lấy embed code mới nhất
- [ ] Privacy setting = Public hoặc Hide from Vimeo

**Nếu tất cả OK → Post lên WordPress!** 🎉

## 🆘 Nếu vẫn lỗi

1. **Check Vimeo account:**
   - Còn quota upload không?
   - Account bị limit không?
   - Video có vi phạm policy không?

2. **Check WordPress:**
   - Theme có support video embed không?
   - Plugin nào block iframe không?
   - Security setting có chặn Vimeo không?

3. **Test thủ công:**
   - Copy embed code từ Vimeo
   - Paste trực tiếp vào WordPress editor
   - Nếu vẫn lỗi → Vấn đề ở WordPress, không phải tool

---

**Tóm tắt:** Upload xong → Đợi 5-10 phút → Check video OK → Post bài → Success! 🚀
