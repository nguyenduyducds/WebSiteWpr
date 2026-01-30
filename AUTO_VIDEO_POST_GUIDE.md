# 📹 Hướng Dẫn Auto Upload Video & Đăng Bài

## 🎯 Tính Năng Mới

Sau khi upload video lên Vimeo, hệ thống **TỰ ĐỘNG**:
1. ✅ Lấy tên video làm **Title** bài viết
2. ✅ Lấy embed code làm **Content** (body) bài viết  
3. ✅ Tạo **Thumbnail** từ video (Smart AI)
4. ✅ Set thumbnail làm **Ảnh Đại Diện** (Featured Image)
5. ✅ Thêm vào **Hàng Chờ** để đăng bài
6. ✅ Có thể chạy **AUTO** để đăng tất cả

## 🚀 Cách Sử Dụng

### Bước 1: Upload Video
1. Vào tab **"☁️ Upload Video"**
2. Chọn video cần upload (có thể chọn nhiều file)
3. Đảm bảo checkbox **"📝 Tự động thêm vào hàng chờ đăng bài"** được tích ✅
4. Nhấn **"⬆️ Bắt đầu Upload"**

### Bước 2: Chờ Upload Hoàn Tất
- Hệ thống sẽ upload từng video
- Mỗi video ~1.5-2 phút
- Sau mỗi video upload xong:
  - ✅ Tạo embed code
  - ✅ **Tạo thumbnail (Smart AI)**
  - ✅ **Tự động thêm vào hàng chờ (có thumbnail)**

### Bước 3: Kiểm Tra Hàng Chờ
1. Vào tab **"📦 Batch & Hàng Chờ"**
2. Xem danh sách video đã được thêm
3. Mỗi video sẽ có:
   - **Title**: Tên file video (đã làm sạch)
   - **Content**: Embed code Vimeo
   - **Thumbnail**: Ảnh đại diện (featured image)

### Bước 4: Chạy AUTO Đăng Bài
1. Nhấn nút **"🚀 CHAY AUTO"**
2. Hệ thống sẽ tự động:
   - Đăng từng bài viết lên WordPress
   - Upload thumbnail làm ảnh đại diện
   - Video embed sẽ hiển thị trong bài
   - Người dùng có thể xem video trực tiếp

## 📋 Ví Dụ Quy Trình

### Input (Upload)
```
File: Alex_Murdaugh_Case_Crime_part2.mp4
```

### Output (Bài Viết WordPress)
```
Title: Alex Murdaugh Case Crime part2

Featured Image: thumb_1158643400.jpg (tự động upload)

Content: 
<div style="padding:56.25% 0 0 0;position:relative;">
  <iframe src="https://player.vimeo.com/video/1158643400..." 
          frameborder="0" 
          allow="autoplay; fullscreen; picture-in-picture" 
          style="position:absolute;top:0;left:0;width:100%;height:100%;">
  </iframe>
</div>
<script src="https://player.vimeo.com/api/player.js"></script>
```

### Kết Quả
- ✅ Bài viết có tiêu đề rõ ràng
- ✅ **Ảnh đại diện đẹp (từ video)**
- ✅ Video hiển thị đầy đủ, responsive
- ✅ Người dùng có thể xem ngay
- ✅ **SEO tốt hơn với featured image**

## 🎨 Thumbnail Features

### Smart AI Thumbnail
- **Tự động phân tích** 5 frames từ video
- **Chọn frame tốt nhất** dựa trên:
  - ✅ Độ nét (sharpness)
  - ✅ Độ sáng (brightness)
  - ✅ Độ tương phản (contrast)
- **Tránh frame xấu**:
  - ❌ Quá tối (< 40)
  - ❌ Quá sáng (> 220)
  - ❌ Mờ (low sharpness)

### Vị Trí Phân Tích
- Bỏ qua 15% đầu video (intro)
- Bỏ qua 15% cuối video (outro)
- Phân tích 70% giữa video (nội dung chính)

### Fallback
- Nếu OpenCV không có → Screenshot từ trình duyệt
- Tự động crop để loại bỏ UI Vimeo
- Vẫn đảm bảo có thumbnail

## 📸 Featured Image trong WordPress

### Tự Động Upload
1. Sau khi upload video xong
2. Thumbnail được lưu local: `thumbnails/thumb_[VIDEO_ID].jpg`
3. Khi đăng bài, hệ thống:
   - Upload thumbnail lên WordPress Media Library
   - Set làm Featured Image cho bài viết
   - Hiển thị trong danh sách bài viết
   - Hiển thị khi share social media

### Lợi Ích
- ✅ **SEO tốt hơn**: Google ưu tiên bài có ảnh
- ✅ **Social Share**: Facebook/Twitter hiển thị ảnh đẹp
- ✅ **User Experience**: Người dùng thấy preview trước khi click
- ✅ **Professional**: Website trông chuyên nghiệp hơn

## ⚙️ Tùy Chọn

### Tự Động Thêm Vào Hàng Chờ
- **Bật** (mặc định): Video tự động vào hàng chờ sau upload
- **Tắt**: Chỉ upload, không thêm vào hàng chờ

### Chạy Ẩn (Headless)
- **Bật** (mặc định): Nhanh hơn, không hiện trình duyệt
- **Tắt**: Chậm hơn, nhưng thấy được quá trình

## 🔄 Quy Trình Hoàn Chỉnh

```
1. Chọn Video Files
   ↓
2. Upload lên Vimeo (headless)
   ↓
3. Lấy Video ID + Embed Code
   ↓
4. Tạo Thumbnail (Smart AI)
   ├─ Phân tích 5 frames
   ├─ Chọn frame đẹp nhất
   └─ Lưu: thumbnails/thumb_[ID].jpg
   ↓
5. Tự động thêm vào Hàng Chờ
   ├─ Title: Tên video (cleaned)
   ├─ Content: Embed code
   ├─ Featured Image: Thumbnail path
   └─ Video Link: https://vimeo.com/[ID]
   ↓
6. Nhấn "CHAY AUTO"
   ↓
7. Đăng lên WordPress
   ├─ Upload thumbnail → Media Library
   ├─ Set Featured Image
   ├─ Paste embed code
   └─ Publish
   ↓
8. ✅ Hoàn tất!
```

## 💡 Tips & Tricks

### 1. Upload Nhiều Video Cùng Lúc
- Chọn nhiều file (Ctrl + Click)
- Hệ thống upload tuần tự
- Tất cả tự động vào hàng chờ
- **Mỗi video có thumbnail riêng**

### 2. Đặt Tên File Có Ý Nghĩa
- Tên file = Title bài viết
- Ví dụ: `Breaking_News_Today.mp4` → "Breaking News Today"
- Tránh: `video1.mp4`, `test.mp4`

### 3. Kiểm Tra Thumbnail
- Sau upload, xem folder `thumbnails/`
- Kiểm tra chất lượng ảnh
- Nếu không đẹp, có thể thay thế thủ công

### 4. Chạy AUTO Khi Đi Ngủ
- Upload tất cả video
- Nhấn "CHAY AUTO"
- Để máy chạy qua đêm
- Sáng dậy đã có hàng trăm bài **với ảnh đẹp**!

## 📊 So Sánh

### Trước (Thủ Công)
```
1. Upload video lên Vimeo
2. Chờ xử lý
3. Lấy embed code
4. Tạo thumbnail thủ công (Photoshop/Canva)
5. Upload thumbnail lên WordPress
6. Tạo bài viết mới
7. Paste embed code
8. Set featured image
9. Publish

Tổng: ~15-20 phút/video
```

### Sau (Tự Động)
```
1. Chọn video → Upload
2. Nhấn "CHAY AUTO"

Tổng: ~2 phút/video (tự động 100%!)
```

## ⚠️ Lưu Ý Quan Trọng

### OpenCV Required
- Cần cài đặt: `pip install opencv-python`
- Nếu không có, dùng screenshot fallback
- Chất lượng vẫn tốt

### Thumbnail Storage
- Lưu local: `thumbnails/`
- Tự động upload lên WordPress
- Không cần xóa file local (dùng lại được)

### Featured Image Size
- WordPress tự động resize
- Tạo nhiều kích thước (thumbnail, medium, large)
- Tối ưu cho mobile và desktop

## 🎉 Kết Quả

**Trước:**
- Upload video thủ công
- Tạo thumbnail thủ công
- Copy embed code
- Tạo bài viết WordPress
- Upload thumbnail
- Set featured image
- Paste embed code
- Đăng bài
- **Tổng**: ~15-20 phút/video

**Sau:**
- Chọn video → Upload
- Nhấn "CHAY AUTO"
- **Tổng**: ~2 phút/video (tự động hoàn toàn!)
- **Bonus**: Thumbnail đẹp, SEO tốt, Professional!

---
*Cập nhật: 27/01/2026 - Auto Video Post + Featured Image* 🎬📸✅

## 🚀 Cách Sử Dụng

### Bước 1: Upload Video
1. Vào tab **"☁️ Upload Video"**
2. Chọn video cần upload (có thể chọn nhiều file)
3. Đảm bảo checkbox **"📝 Tự động thêm vào hàng chờ đăng bài"** được tích ✅
4. Nhấn **"⬆️ Bắt đầu Upload"**

### Bước 2: Chờ Upload Hoàn Tất
- Hệ thống sẽ upload từng video
- Mỗi video ~1.5-2 phút
- Sau mỗi video upload xong:
  - ✅ Tạo embed code
  - ✅ Tạo thumbnail
  - ✅ **Tự động thêm vào hàng chờ**

### Bước 3: Kiểm Tra Hàng Chờ
1. Vào tab **"📦 Batch & Hàng Chờ"**
2. Xem danh sách video đã được thêm
3. Mỗi video sẽ có:
   - **Title**: Tên file video (đã làm sạch)
   - **Content**: Embed code Vimeo

### Bước 4: Chạy AUTO Đăng Bài
1. Nhấn nút **"🚀 CHAY AUTO"**
2. Hệ thống sẽ tự động:
   - Đăng từng bài viết lên WordPress
   - Video embed sẽ hiển thị trong bài
   - Người dùng có thể xem video trực tiếp

## 📋 Ví Dụ Quy Trình

### Input (Upload)
```
File: Alex_Murdaugh_Case_Crime_part2.mp4
```

### Output (Bài Viết WordPress)
```
Title: Alex Murdaugh Case Crime part2
Content: 
<div style="padding:56.25% 0 0 0;position:relative;">
  <iframe src="https://player.vimeo.com/video/1158643400..." 
          frameborder="0" 
          allow="autoplay; fullscreen; picture-in-picture" 
          style="position:absolute;top:0;left:0;width:100%;height:100%;">
  </iframe>
</div>
<script src="https://player.vimeo.com/api/player.js"></script>
```

### Kết Quả
- ✅ Bài viết có tiêu đề rõ ràng
- ✅ Video hiển thị đầy đủ, responsive
- ✅ Người dùng có thể xem ngay

## ⚙️ Tùy Chọn

### Tự Động Thêm Vào Hàng Chờ
- **Bật** (mặc định): Video tự động vào hàng chờ sau upload
- **Tắt**: Chỉ upload, không thêm vào hàng chờ

### Chạy Ẩn (Headless)
- **Bật** (mặc định): Nhanh hơn, không hiện trình duyệt
- **Tắt**: Chậm hơn, nhưng thấy được quá trình

## 🎨 Định Dạng Content

### Embed Code Vimeo
```html
<div style="padding:56.25% 0 0 0;position:relative;">
  <iframe src="https://player.vimeo.com/video/[VIDEO_ID]..." 
          frameborder="0" 
          allow="autoplay; fullscreen; picture-in-picture" 
          style="position:absolute;top:0;left:0;width:100%;height:100%;">
  </iframe>
</div>
<script src="https://player.vimeo.com/api/player.js"></script>
```

### Đặc Điểm
- ✅ **Responsive**: Tự động điều chỉnh kích thước
- ✅ **16:9 Ratio**: Tỷ lệ chuẩn cho video
- ✅ **Fullscreen**: Hỗ trợ xem toàn màn hình
- ✅ **Autoplay**: Có thể tự động phát (tùy cấu hình)

## 🔄 Quy Trình Hoàn Chỉnh

```
1. Chọn Video Files
   ↓
2. Upload lên Vimeo (headless)
   ↓
3. Lấy Video ID + Embed Code
   ↓
4. Tạo Thumbnail
   ↓
5. Tự động thêm vào Hàng Chờ
   ├─ Title: Tên video (cleaned)
   ├─ Content: Embed code
   └─ Video Link: https://vimeo.com/[ID]
   ↓
6. Nhấn "CHAY AUTO"
   ↓
7. Đăng lên WordPress
   ↓
8. ✅ Hoàn tất!
```

## 💡 Tips & Tricks

### 1. Upload Nhiều Video Cùng Lúc
- Chọn nhiều file (Ctrl + Click)
- Hệ thống upload tuần tự
- Tất cả tự động vào hàng chờ

### 2. Đặt Tên File Có Ý Nghĩa
- Tên file = Title bài viết
- Ví dụ: `Breaking_News_Today.mp4` → "Breaking News Today"
- Tránh: `video1.mp4`, `test.mp4`

### 3. Kiểm Tra Trước Khi Đăng
- Xem danh sách hàng chờ
- Có thể xóa bài không muốn đăng
- Chỉnh sửa thứ tự nếu cần

### 4. Chạy AUTO Khi Đi Ngủ
- Upload tất cả video
- Nhấn "CHAY AUTO"
- Để máy chạy qua đêm
- Sáng dậy đã có hàng trăm bài!

## ⚠️ Lưu Ý Quan Trọng

### Content Tự Động
- Nếu bạn **KHÔNG** muốn content tự động
- Bỏ tích checkbox **"Tự động thêm vào hàng chờ"**
- Upload xong, tự thêm content thủ công

### Chỉnh Sửa Content
- Sau khi thêm vào hàng chờ
- Hiện tại **CHƯA** có chức năng edit
- Nếu muốn sửa, phải xóa và thêm lại

### Video Processing
- Video vẫn đang xử lý trên Vimeo
- Embed code hoạt động ngay
- Chất lượng video tăng dần theo thời gian

## 🎉 Kết Quả

**Trước:**
- Upload video thủ công
- Copy embed code
- Tạo bài viết WordPress
- Paste embed code
- Đăng bài
- **Tổng**: ~10-15 phút/video

**Sau:**
- Chọn video → Upload
- Nhấn "CHAY AUTO"
- **Tổng**: ~2 phút/video (tự động hoàn toàn!)

---
*Cập nhật: 27/01/2026 - Auto Video Post Feature* 🎬✅