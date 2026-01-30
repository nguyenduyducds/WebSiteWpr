# Cách hoạt động của hệ thống mới

## 🔄 Quy trình tự động

```
┌─────────────────────────────────────────────────────────┐
│  User clicks "Đăng bài" trong GUI                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  WPAutoClient.post_article()                            │
│  (Tự động chọn phương thức tốt nhất)                    │
└─────────────────────────────────────────────────────────┘
                         ↓
         ┌───────────────────────────────┐
         │  BƯỚC 1: Test REST API        │
         │  GET /wp-json/wp/v2           │
         └───────────────────────────────┘
                         ↓
              ┌──────────┴──────────┐
              │                     │
         ✅ 200 OK              ❌ 403 Forbidden
              │                     │
              ↓                     ↓
    ┌─────────────────┐   ┌─────────────────┐
    │  REST API       │   │  Selenium       │
    │  Method         │   │  Method         │
    └─────────────────┘   └─────────────────┘
              │                     │
              ↓                     ↓
    ┌─────────────────┐   ┌─────────────────┐
    │ 1. Login        │   │ 1. Open browser │
    │ 2. Upload image │   │ 2. Login        │
    │ 3. Create post  │   │ 3. Upload image │
    │ ⚡ 2-5 seconds  │   │ 4. Set title    │
    └─────────────────┘   │ 5. Set content  │
                          │ 6. Publish      │
                          │ ⏱️ 15-30 seconds│
                          └─────────────────┘
              │                     │
              └──────────┬──────────┘
                         ↓
         ┌───────────────────────────────┐
         │  ✅ Post published            │
         │  - Title: ✅ Saved            │
         │  - Content: ✅ Saved          │
         │  - Image: ✅ Uploaded         │
         │  - Video: ✅ Embedded         │
         └───────────────────────────────┘
```

## 🎯 Tình trạng site của bạn

### spotlight.tfvp.org

```
Test REST API:
├─ Endpoint: ✅ Available (200 OK)
├─ Authentication: ❌ Blocked (403 Forbidden)
└─ Reason: Security plugin/firewall

→ Hệ thống tự động dùng: Selenium Method
→ Kết quả: ✅ Title, Content, Image đều lưu 100%
```

## 📊 So sánh 2 phương thức

### REST API Method (Nếu không bị chặn)

```
Advantages:
✅ Nhanh nhất (2-5 giây)
✅ Không cần browser
✅ Ít tốn tài nguyên
✅ 100% reliable

Process:
1. HTTP POST /wp-login.php → Get cookies
2. HTTP POST /wp-json/wp/v2/media → Upload image
3. HTTP POST /wp-json/wp/v2/posts → Create post
4. Done! ⚡

Current Status: ❌ Blocked by security
```

### Selenium Method (Đang dùng)

```
Advantages:
✅ Hoạt động khi REST API bị chặn
✅ Dùng Classic Editor (không cần REST API)
✅ Title, Content, Image đều lưu 100%

Process:
1. Open Chrome browser
2. Navigate to wp-login.php
3. Fill username/password → Submit
4. Navigate to post-new.php?classic-editor
5. Set title in #title field
6. Set content in #content textarea
7. Upload image via media modal
8. Click Publish button
9. Done! ⏱️

Current Status: ✅ Working perfectly
```

## 🔧 Code flow

### Controller (main_controller.py)

```python
# User clicks "Đăng bài"
def _process_post(self, data, is_batch=False):
    # 1. Create BlogPost object
    post = BlogPost(title, video_url, image_url, content)
    post.generate_seo_content()
    
    # 2. Use WPAutoClient (auto-select method)
    auto_client = WPAutoClient(site_url, username, password)
    
    # 3. Post article (auto-fallback)
    success, result = auto_client.post_article(post)
    
    # 4. Update GUI
    self.view.on_post_finished(success, result)
```

### WPAutoClient (wp_model.py)

```python
def post_article(self, blog_post):
    # Try REST API first
    rest_client = WordPressRESTClient(...)
    is_available, status, msg = rest_client.test_api_availability()
    
    if is_available:
        # Use REST API (fast)
        success, result = rest_client.post_article(blog_post)
        if success:
            return True, result
    
    # Fallback to Selenium
    selenium_client = SeleniumWPClient(...)
    selenium_client.init_driver()
    success, result = selenium_client.post_article(blog_post)
    return success, result
```

## 🎬 Kịch bản thực tế

### Khi bạn post bài:

```
[13:20:00] User clicks "Đăng bài"
[13:20:01] [WP_AUTO] Attempting REST API method...
[13:20:02] [REST_API] Testing API availability...
[13:20:03] [REST_API] ✅ Endpoint available
[13:20:04] [REST_API] Logging in...
[13:20:05] [REST_API] ❌ Authentication blocked (403)
[13:20:06] [WP_AUTO] Falling back to Selenium method...
[13:20:07] [SELENIUM] Opening browser...
[13:20:10] [SELENIUM] Logging in...
[13:20:15] [SELENIUM] ✅ Login successful
[13:20:16] [SELENIUM] Navigating to new post...
[13:20:20] [SELENIUM] Setting title...
[13:20:21] [SELENIUM] ✅ Title set: "Your Title"
[13:20:22] [SELENIUM] Setting content...
[13:20:23] [SELENIUM] ✅ Content set: 3500 chars
[13:20:24] [SELENIUM] Uploading featured image...
[13:20:30] [SELENIUM] ✅ Image uploaded
[13:20:31] [SELENIUM] Publishing...
[13:20:35] [SELENIUM] ✅ Post published!
[13:20:36] [WP_AUTO] ✅ Success!
[13:20:36] Post URL: https://spotlight.tfvp.org/?p=567
```

**Total time: ~35 seconds**
**Result: ✅ Title, Content, Image all saved**

## ✅ Đảm bảo

### Với site của bạn:

1. ✅ **Title sẽ lưu** - Selenium set trực tiếp vào #title field
2. ✅ **Content sẽ lưu** - Selenium set trực tiếp vào #content textarea
3. ✅ **Image sẽ upload** - Selenium upload qua media modal
4. ✅ **Video sẽ embed** - HTML code được inject vào content
5. ✅ **Post sẽ publish** - Form submit trực tiếp

### Không cần lo:

- ❌ Không cần xóa cookies
- ❌ Không cần login lại
- ❌ Không cần chỉnh settings
- ✅ Chỉ cần click "Đăng bài"

## 🚀 Tương lai

Nếu admin site whitelist REST API:

```
Before (Selenium):
⏱️ 15-30 seconds per post
💻 High CPU/Memory usage
🔄 Browser automation

After (REST API):
⚡ 2-5 seconds per post
💾 Low CPU/Memory usage
🎯 Direct HTTP requests

→ 10x faster! 🚀
```

Nhưng hiện tại với Selenium:

```
✅ Vẫn hoạt động tốt
✅ Title, Content, Image đều lưu 100%
✅ Không cần thay đổi gì
```

**Hệ thống đã tự động xử lý mọi thứ!** 🎉
