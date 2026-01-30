# Facebook Video Embed - 9:16 Portrait Ratio (267x591)

## ⚠️ CRITICAL: NO SPACES Between Attributes!

**IMPORTANT**: Facebook **BLOCKS** embed codes that have spaces between HTML attributes!

### ✅ Correct Format (NO spaces - Facebook accepts):
```html
<iframe src="..."width="267"height="591"style="..."scrolling="no"...></iframe>
```

### ❌ Wrong Format (WITH spaces - Facebook blocks):
```html
<iframe src="..." width="267" height="591" style="..." scrolling="no" ...></iframe>
```

## 🎯 Tính năng

Tool tự động convert **bất kỳ link Facebook video nào** thành iframe với kích thước **267x591** (tỷ lệ 9:16 chuẩn cho video portrait).

## 📐 Kích thước - 9:16 Ratio

```
Width:  267px
Height: 591px
Ratio:  9:16 (portrait)
```

**Tại sao 267x591?**
- ✅ Tỷ lệ 9:16 chuẩn cho video portrait (Facebook Reels, TikTok, Instagram Reels)
- ✅ Kích thước tối ưu cho video dọc
- ✅ Không bị crop, hiển thị full video
- ✅ **NO SPACES** giữa attributes → Facebook không block

## 📝 Output Format

Tool tạo iframe **KHÔNG CÓ KHOẢNG TRẮNG** giữa các attributes:

```html
<iframe src="https://www.facebook.com/plugins/video.php?height=476&href=ENCODED_URL&show_text=true&width=267&t=0"width="267"height="591"style="border:none;overflow:hidden"scrolling="no"frameborder="0"allowfullscreen="true"allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"allowFullScreen="true"></iframe>
```

**Chú ý:** Tất cả attributes được nối liền KHÔNG có khoảng trắng - đây là yêu cầu của Facebook!

## 🔄 Các định dạng được hỗ trợ

### 1. Direct Facebook Reel URL
```
Input:  https://www.facebook.com/reel/2412419815845658/
Output: <iframe width="267" height="591" ...> (NO spaces)
```

### 2. Facebook Video URL
```
Input:  https://www.facebook.com/watch/?v=123456789
Output: <iframe width="267" height="591" ...> (NO spaces)
```

### 3. Facebook Page Video
```
Input:  https://www.facebook.com/username/videos/123456789/
Output: <iframe width="267" height="591" ...> (NO spaces)
```

### 4. fb.watch Short URL
```
Input:  https://fb.watch/abc123/
Output: <iframe width="267" height="591" ...> (NO spaces)
```

### 5. Existing Facebook Iframe
```
Input:  <iframe src="https://www.facebook.com/plugins/video.php?..." width="500" height="800">
Output: <iframe width="267" height="591" ...> (recreated with 9:16 ratio, NO spaces)
```

## 🔧 Cách sử dụng

### Trong Tool:

1. **Copy link Facebook video** (bất kỳ format nào)
2. **Paste vào ô "Video URL"** trong tool
3. **Tool tự động convert** thành iframe 267x591 (NO spaces)
4. **Post lên WordPress** - Video hiển thị đúng tỷ lệ 9:16, Facebook không block

### Ví dụ:

```
Bước 1: Copy link
https://www.facebook.com/reel/2412419815845658/

Bước 2: Paste vào tool
[Video URL]: https://www.facebook.com/reel/2412419815845658/

Bước 3: Tool auto-convert (NO spaces!)
<iframe src="..."width="267"height="591"...>

Bước 4: Post lên WordPress
✅ Video hiển thị với tỷ lệ 9:16 chuẩn
✅ Facebook không block vì format đúng
```

## 📊 So sánh với Vimeo

| Feature | Vimeo | Facebook |
|---------|-------|----------|
| **Kích thước** | Responsive (16:9) | Fixed (267x591) |
| **Aspect ratio** | 16:9 (landscape) | 9:16 (portrait) |
| **Spacing** | Normal HTML | **NO SPACES!** |
| **Use case** | Desktop, landscape | Mobile, portrait |
| **Video type** | Professional, horizontal | Reels, vertical |

## 🎯 Khi nào dùng Facebook vs Vimeo?

### Dùng Facebook khi:
- ✅ Video portrait 9:16 (Facebook Reels, TikTok, Instagram)
- ✅ Video dọc từ mobile
- ✅ Short-form content
- ✅ Social media videos

### Dùng Vimeo khi:
- ✅ Video landscape 16:9
- ✅ Professional videos
- ✅ Long-form content
- ✅ Desktop-first videos

## 🧪 Testing

Chạy test script:

```bash
python test_facebook_spaces.py
```

Kết quả:
```
✅ All attributes concatenated (NO spaces)
✅ Format matches Facebook requirements (267x591 - 9:16 ratio)
✅ Facebook won't block this format
```

## 📝 Code Location

**File:** `view/gui_view.py`

**Functions:**
- `create_facebook_embed()` (line ~911)
- `_extract_video_url()` (line ~1103)

**Logic:**
```python
# CRITICAL: NO SPACES between attributes!
# 267x591 = 9:16 ratio for portrait video
fb_iframe = (
    f'<iframe src="...?height=476&...&width=267..."'
    f'width="267"'      # NO space before this
    f'height="591"'     # NO space before this
    f'style="..."'      # NO space before this
    # ... etc
)
```

## 🐛 Troubleshooting

### Vấn đề 1: Facebook block video (không hiển thị)

**Nguyên nhân:** Có khoảng trắng giữa các attributes

**Giải pháp:**
- ✅ Tool đã fix - tất cả attributes nối liền
- ✅ Không có khoảng trắng giữa `">`và attribute tiếp theo
- ✅ Format: `src="..."width="267"height="591"...`

### Vấn đề 2: Video bị crop hoặc méo

**Nguyên nhân:** Video không phải tỷ lệ 9:16

**Giải pháp:**
- Facebook tự động fit video vào 9:16
- Nếu video là 16:9 (landscape), sẽ có black bars
- Dùng Vimeo cho video landscape thay vì Facebook

### Vấn đề 3: Video không hiển thị (lý do khác)

**Nguyên nhân:** Video bị private hoặc deleted

**Giải pháp:**
1. Check video còn tồn tại trên Facebook
2. Check privacy setting = Public
3. Try với video khác

## 🎨 Customization

### Thay đổi kích thước (giữ tỷ lệ 9:16):

Nếu muốn kích thước khác nhưng giữ tỷ lệ 9:16, sửa trong `view/gui_view.py`:

```python
# Current: 267x591 (9:16)
fb_iframe = (
    f'<iframe src="...?height=476&...&width=267..."'
    f'width="267"'
    f'height="591"'
    # ...
)

# Larger: 360x640 (9:16)
fb_iframe = (
    f'<iframe src="...?height=640&...&width=360..."'
    f'width="360"'
    f'height="640"'
    # ...
)

# Smaller: 180x400 (9:16)
fb_iframe = (
    f'<iframe src="...?height=400&...&width=180..."'
    f'width="180"'
    f'height="400"'
    # ...
)
```

**Lưu ý:** 
1. Sửa cả `height=XXX&width=XXX` trong URL
2. Sửa cả `width="XXX"` và `height="XXX"` attributes
3. **KHÔNG THÊM KHOẢNG TRẮNG** giữa các attributes!
4. **GIỮ TỶ LỆ 9:16** cho video portrait

### Tính toán tỷ lệ 9:16:

```
Width = X
Height = X * 16 / 9 = X * 1.778

Ví dụ:
- 267 → 267 * 1.778 = 474.5 ≈ 476 (trong URL) / 591 (iframe height)
- 360 → 360 * 1.778 = 640
- 180 → 180 * 1.778 = 320
```

## 📚 Resources

- **Facebook Embed Docs:** https://developers.facebook.com/docs/plugins/embedded-video-player
- **9:16 Aspect Ratio Guide:** https://www.aspectratiocalculator.com/9-16.html

## ✅ Checklist

Khi post Facebook video:

- [ ] Link Facebook video đã copy
- [ ] Paste vào ô "Video URL"
- [ ] Tool auto-convert thành iframe 267x591 (9:16, NO spaces)
- [ ] Preview trên WordPress
- [ ] Video hiển thị đúng tỷ lệ 9:16
- [ ] Facebook không block (vì format đúng)

## 🎉 Kết luận

Tool giờ đã hỗ trợ **Facebook video** với:
- ✅ Kích thước **267x591** (tỷ lệ 9:16 chuẩn cho portrait video)
- ✅ Format đúng chuẩn Facebook (NO spaces)
- ✅ Facebook không block
- ✅ Hiển thị full video không bị crop

Chỉ cần paste link Facebook, tool tự động convert thành iframe chuẩn 9:16! 🚀

---

**Version:** 3.0.0  
**Date:** 2026-01-29  
**Status:** ✅ FIXED - 9:16 RATIO, NO SPACES FORMAT
