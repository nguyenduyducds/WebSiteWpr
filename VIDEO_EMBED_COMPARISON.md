# So sánh Vimeo vs Facebook Video Embed

## 🎯 Tổng quan

Tool xử lý **Vimeo** và **Facebook** video khác nhau để phù hợp với từng loại video.

---

## 📊 Bảng so sánh

| Feature | Vimeo | Facebook |
|---------|-------|----------|
| **Aspect Ratio** | 16:9 (Landscape) | 9:16 (Portrait) |
| **Layout** | Responsive | Fixed Size |
| **Width** | 100% (responsive) | 500px (fixed) |
| **Height** | Auto (56.25% padding) | 800px (fixed) |
| **Wrapper** | `<div>` + `<script>` | `<div>` center wrapper |
| **Use Case** | Desktop, landscape videos | Mobile, portrait videos |

---

## 🎬 Vimeo Embed

### Input:
```
https://player.vimeo.com/video/123456789
```

hoặc full embed code:
```html
<div style="padding:56.25% 0 0 0;position:relative;">
    <iframe src="https://player.vimeo.com/video/123456789..." 
            style="position:absolute;top:0;left:0;width:100%;height:100%;">
    </iframe>
</div>
<script src="https://player.vimeo.com/api/player.js"></script>
```

### Output:
Tool **GIỮ NGUYÊN** full embed code (nếu có) hoặc chỉ trả về URL.

### Đặc điểm:
- ✅ **Responsive** - Tự động scale theo màn hình
- ✅ **16:9 aspect ratio** - Phù hợp video landscape
- ✅ **Full width** - Chiếm toàn bộ chiều rộng container
- ✅ **Professional** - Không có branding (nếu dùng Vimeo Pro)

### Khi nào dùng:
- Video quay ngang (landscape)
- Video chuyên nghiệp
- Desktop viewing
- Full-width content area

---

## 📱 Facebook Embed

### Input:
```
https://www.facebook.com/reel/2412419815845658/
```

hoặc:
```
https://www.facebook.com/watch/?v=123456789
```

### Output:
```html
<div style="max-width:500px;margin:0 auto;">
    <iframe src="https://www.facebook.com/plugins/video.php?height=800&href=...&width=500..." 
            width="500" 
            height="800" 
            style="border:none;overflow:hidden">
    </iframe>
</div>
```

### Đặc điểm:
- ✅ **Fixed size** - 500x800px cố định
- ✅ **9:16 aspect ratio** - Phù hợp video portrait
- ✅ **Center aligned** - Tự động căn giữa
- ✅ **Mobile-friendly** - Tối ưu cho mobile

### Khi nào dùng:
- Facebook Reels
- Video quay dọc (portrait)
- Mobile-first content
- Sidebar widgets

---

## 🔄 Auto-Detection

Tool **TỰ ĐỘNG PHÁT HIỆN** loại video:

```python
# Vimeo detection
if '<div style="padding:' in input_text and 'player.vimeo.com' in input_text:
    # → Use Vimeo responsive embed
    return vimeo_embed

# Facebook detection
if 'facebook.com' in input_text or 'fb.watch' in input_text:
    # → Use Facebook fixed-size embed
    return facebook_embed
```

---

## 📐 Kích thước chi tiết

### Vimeo (Responsive):
```css
/* Container */
div {
    padding: 56.25% 0 0 0;  /* 16:9 ratio */
    position: relative;
}

/* Iframe */
iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}
```

**Kết quả:**
- Desktop (1200px): Video = 1200px × 675px
- Tablet (768px): Video = 768px × 432px
- Mobile (375px): Video = 375px × 211px

### Facebook (Fixed):
```css
/* Container */
div {
    max-width: 500px;
    margin: 0 auto;
}

/* Iframe */
iframe {
    width: 500px;
    height: 800px;
}
```

**Kết quả:**
- Desktop: Video = 500px × 800px
- Tablet: Video = 500px × 800px
- Mobile: Video = 500px × 800px (may scroll)

---

## 🎨 Styling

### Vimeo - Responsive wrapper:
```html
<!-- Vimeo tự động scale -->
<div style="padding:56.25% 0 0 0;position:relative;">
    <iframe style="position:absolute;top:0;left:0;width:100%;height:100%;"></iframe>
</div>
```

### Facebook - Center wrapper:
```html
<!-- Facebook center align với max-width -->
<div style="max-width:500px;margin:0 auto;">
    <iframe width="500" height="800"></iframe>
</div>
```

---

## 🧪 Test Cases

### Test Vimeo:
```python
Input:  "https://player.vimeo.com/video/123456789"
Output: "https://player.vimeo.com/video/123456789"  # Giữ nguyên

Input:  "<div style='padding:56.25%...'><iframe...></div><script...>"
Output: "<div style='padding:56.25%...'><iframe...></div><script...>"  # Giữ nguyên
```

### Test Facebook:
```python
Input:  "https://www.facebook.com/reel/123456789/"
Output: "<div style='max-width:500px...'><iframe width='500' height='800'...></iframe></div>"

Input:  "https://fb.watch/abc123/"
Output: "<div style='max-width:500px...'><iframe width='500' height='800'...></iframe></div>"
```

---

## 💡 Best Practices

### Cho Vimeo:
1. ✅ Dùng full embed code (với `<div>` wrapper)
2. ✅ Để responsive - không set fixed width
3. ✅ Upload video landscape (16:9)
4. ✅ Dùng cho content area chính

### Cho Facebook:
1. ✅ Dùng direct link (tool tự convert)
2. ✅ Để fixed size 500x800
3. ✅ Upload video portrait (9:16)
4. ✅ Dùng cho sidebar hoặc mobile content

---

## 🔧 Customization

### Thay đổi kích thước Facebook:

Nếu muốn kích thước khác, sửa trong `view/gui_view.py`:

```python
# Current: 500x800
fb_iframe = (
    f'<div style="max-width:500px;margin:0 auto;">'
    f'<iframe ... width="500" height="800" ...'
)

# Custom: 400x700
fb_iframe = (
    f'<div style="max-width:400px;margin:0 auto;">'
    f'<iframe ... width="400" height="700" ...'
)
```

**Lưu ý:** Cũng phải sửa trong URL:
```python
f'...video.php?height=700&...&width=400...'
```

### Thay đổi Vimeo aspect ratio:

Vimeo mặc định 16:9 (56.25% padding). Nếu muốn 4:3:

```python
# 16:9 (current)
padding: 56.25%

# 4:3
padding: 75%

# 21:9 (ultrawide)
padding: 42.86%
```

---

## 📚 Summary

| | Vimeo | Facebook |
|---|-------|----------|
| **Format** | Responsive | Fixed |
| **Ratio** | 16:9 | 9:16 |
| **Width** | 100% | 500px |
| **Height** | Auto | 800px |
| **Best for** | Desktop, landscape | Mobile, portrait |

**Kết luận:** Tool xử lý 2 loại video khác nhau để tối ưu cho từng use case! 🎯

---

**Version:** 3.0.0  
**Date:** 2026-01-29  
**Status:** ✅ VERIFIED
