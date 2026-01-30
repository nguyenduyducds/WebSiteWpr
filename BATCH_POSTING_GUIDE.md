# Hướng dẫn sử dụng chế độ ĐĂNG HÀNG LOẠT

## Tính năng mới
Tool hiện đã hỗ trợ đăng **hàng loạt bài viết** tự động từ file CSV!

## Cách sử dụng

### Bước 1: Chuẩn bị file CSV
1. Mở file `sample_posts.csv` làm mẫu
2. Định dạng CSV phải có 4 cột:
   - `title`: Tiêu đề bài viết (BẮT BUỘC)
   - `video_url`: Link YouTube hoặc mã embed (tùy chọn)
   - `image_path`: Đường dẫn đầy đủ đến ảnh đại diện (tùy chọn)
   - `content`: Nội dung HTML tùy chỉnh (tùy chọn, để trống sẽ tự tạo)

### Bước 2: Điền dữ liệu
```csv
title,video_url,image_path,content
"Xe điện Tesla Model 3","https://youtube.com/watch?v=abc123","C:/images/tesla.jpg",""
"iPhone 15 Pro Max Review","https://youtube.com/watch?v=xyz789","C:/images/iphone.jpg","<p>Nội dung tùy chỉnh</p>"
```

**Lưu ý quan trọng:**
- Đường dẫn ảnh phải là đường dẫn TUYỆT ĐỐI (ví dụ: `C:/Users/Admin/Pictures/anh.jpg`)
- Nếu có dấu phẩy trong nội dung, phải bọc bằng dấu ngoặc kép `"..."`
- File phải lưu với encoding UTF-8

### Bước 3: Chạy tool
1. Đăng nhập WordPress như bình thường
2. Trong giao diện chính, tìm mục **"Chế độ đăng hàng loạt"**
3. Click nút **"Chọn CSV"** và chọn file CSV của bạn
4. Tool sẽ hiển thị số lượng bài viết đã load
5. Click nút **"ĐĂNG HÀNG LOẠT (CSV)"** màu cam

### Bước 4: Theo dõi tiến độ
- Tool sẽ tự động đăng từng bài viết
- Progress bar hiển thị: "Đang đăng 1/10", "Đang đăng 2/10"...
- Mỗi bài viết có delay 1 giây để tránh spam
- Nếu có lỗi, tool sẽ bỏ qua và tiếp tục bài tiếp theo

## Tối ưu hóa tốc độ
Tool đã được tối ưu để chạy nhanh hơn ~40-50%:
- Giảm thời gian chờ không cần thiết
- Bỏ qua bước chuyển Visual Editor
- Sử dụng JavaScript injection để nhập nội dung siêu nhanh

## Lưu ý
- **KHÔNG TẮT** trình duyệt trong khi tool đang chạy batch
- Nên test với 2-3 bài viết trước khi chạy hàng trăm bài
- Đảm bảo tất cả đường dẫn ảnh đều tồn tại
- Session đăng nhập được giữ nguyên, không cần login lại giữa các bài

## Ví dụ file CSV hoàn chỉnh
Xem file `sample_posts.csv` trong thư mục gốc.

---
**Chúc bạn sử dụng tool hiệu quả! 🚀**
