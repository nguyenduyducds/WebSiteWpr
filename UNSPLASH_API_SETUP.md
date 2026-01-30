# 🖼️ Hướng Dẫn Setup Unsplash API (Lấy Ảnh Xe Tự Động)

## Tính năng
- Tự động lấy 3 ảnh xe sang từ Unsplash dựa trên tiêu đề bài viết
- Nhận diện hãng xe: Ferrari, Lamborghini, Porsche, BMW, Mercedes, v.v.
- Miễn phí 50 requests/giờ

## Bước 1: Đăng ký Unsplash API (MIỄN PHÍ)

1. Truy cập: https://unsplash.com/developers
2. Click "Register as a developer"
3. Đăng nhập hoặc tạo tài khoản mới
4. Tạo ứng dụng mới:
   - Application name: `WordPress Auto Poster`
   - Description: `Automatically fetch car images for blog posts`
5. Copy **Access Key** (dạng: `abc123xyz...`)

## Bước 2: Cấu hình API Key

Mở file `model/image_api.py` và thay đổi dòng:

```python
self.access_key = "YOUR_UNSPLASH_ACCESS_KEY"
```

Thành:

```python
self.access_key = "abc123xyz..."  # Paste Access Key của bạn vào đây
```

## Bước 3: Sử dụng

### Đăng bài lẻ:
- Để trống 3 ô "Ảnh Content"
- Tick checkbox "🚗 Tự động lấy ảnh xe từ API"
- Hệ thống sẽ tự động lấy 3 ảnh dựa trên tiêu đề

### Batch posting:
- Hệ thống tự động lấy ảnh cho mỗi bài viết
- Nhận diện hãng xe từ tiêu đề
- Tải về và chèn vào bài viết

## Ví dụ

**Tiêu đề:** "Ferrari F8 Tributo Review 2024"
→ Tự động lấy 3 ảnh Ferrari

**Tiêu đề:** "Top 10 Luxury Cars"
→ Tự động lấy 3 ảnh xe sang tổng quát

## Giới hạn API

- **Free tier:** 50 requests/giờ
- Mỗi bài viết = 1 request
- Đủ cho ~50 bài/giờ

## Lưu ý

- Ảnh từ Unsplash có bản quyền miễn phí (không cần credit)
- Chất lượng cao, phù hợp cho blog
- Nếu không setup API key, tính năng sẽ bị bỏ qua (không lỗi)

## Alternative: Pexels API

Nếu muốn dùng Pexels thay vì Unsplash:
1. Đăng ký tại: https://www.pexels.com/api/
2. Copy API key
3. Sửa trong `model/image_api.py`:
   ```python
   # Uncomment PexelsImageAPI và thay API key
   ```
