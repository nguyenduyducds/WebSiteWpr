# Facebook SDK Bypass Method

## 🎯 Khi nào dùng?

Nếu **iframe method bị Facebook block**, dùng **Facebook SDK method** để bypass.

## 🔄 2 Methods

### Method 1: Direct Iframe (Default - Nhanh hơn)

```html
<iframe src="https://www.facebook.com/plugins/video.php?height=476&href=...&width=267&t=0"width="267"height="591"style="border:none;overflow:hidden"scrolling="no"frameborder="0"allowfullscreen="true"allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"allowFullScreen="true"></iframe>
```

**Ưu điểm:**
- ✅ Nhanh, không cần load thêm script
- ✅ Kích thước cố định 267x591 (9:16)
- ✅ Hoạt động với hầu hết sites

**Nhược điểm:**
- ❌ Có thể bị Facebook block nếu site có security strict
- ❌ Cần format NO SPACES giữa attributes

---

### Method 2: Facebook SDK (Bypass Security)

**Bước 1: Load Facebook SDK Script**
```html
<script>
window.fbAsyncInit = function() {
    FB.init({
        appId      : 'YOUR_APP_ID',
        xfbml      : true,
        version    : 'v12.0'
    });
};

(function(d, s, id){
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {return;}
    js = d.createElement(s); js.id = id;
    js.src = "https://connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));
</script>
```

**Bước 2: Dùng HTML Facebook chuẩn**
```html
<div class="fb-video" data-href="https://www.facebook.com/reel/2412419815845658/" data-width="267"></div>
```

**Ưu điểm:**
- ✅ Bypass Facebook security
- ✅ Official Facebook method
- ✅ Tự động responsive
- ✅ Không bị block

**Nhược điểm:**
- ❌ Chậm hơn (phải load SDK script)
- ❌ Cần Facebook App ID (hoặc dùng default)
- ❌ Kích thước không cố định (tự động adjust)

---

## 🔧 Cách bật Facebook SDK Method

### Option 1: Sửa config.json

```json
{
    "site_url": "yoursite.com/wp-admin",
    "username": "admin",
    "password": "password",
    "facebook_use_sdk": true
}
```

**Giá trị:**
- `false` (default) - Dùng iframe method (nhanh)
- `true` - Dùng SDK method (bypass security)

### Option 2: Code

```python
# Trong view/gui_view.py
embed_code = self.create_facebook_embed(fb_url, use_sdk=True)
```

---

## 📊 So sánh 2 Methods

| Feature | Iframe Method | SDK Method |
|---------|---------------|------------|
| **Tốc độ** | ⚡ Nhanh | 🐌 Chậm hơn |
| **Security** | ⚠️ Có thể bị block | ✅ Bypass được |
| **Kích thước** | 267x591 cố định | Tự động responsive |
| **Format** | NO SPACES required | Normal HTML |
| **Setup** | Không cần | Cần load SDK |
| **App ID** | Không cần | Cần (hoặc default) |

---

## 🧪 Testing

### Test Iframe Method (Default):

```bash
# config.json
"facebook_use_sdk": false
```

Output:
```html
<iframe src="..."width="267"height="591"...></iframe>
```

### Test SDK Method:

```bash
# config.json
"facebook_use_sdk": true
```

Output:
```html
<script>window.fbAsyncInit = function() {...}</script>
<div class="fb-video" data-href="..." data-width="267"></div>
```

---

## 🎯 Khuyến nghị

### Dùng Iframe Method (Default) khi:
- ✅ Site WordPress bình thường
- ✅ Không bị Facebook block
- ✅ Muốn tốc độ nhanh
- ✅ Muốn kích thước cố định 267x591

### Dùng SDK Method khi:
- ✅ Iframe bị Facebook block
- ✅ Site có security plugin strict
- ✅ Muốn official Facebook method
- ✅ Không quan tâm tốc độ load

---

## 🔒 Facebook App ID

### Không có App ID?

Có thể dùng **default** hoặc **bỏ trống**:

```javascript
FB.init({
    appId      : 'YOUR_APP_ID',  // Có thể bỏ trống hoặc dùng default
    xfbml      : true,
    version    : 'v12.0'
});
```

Facebook SDK vẫn hoạt động mà không cần App ID, nhưng:
- ⚠️ Có thể bị rate limit
- ⚠️ Không có analytics
- ⚠️ Không có advanced features

### Tạo Facebook App ID (Optional):

1. Vào https://developers.facebook.com/apps/
2. Create New App
3. Copy App ID
4. Paste vào code: `appId: 'YOUR_APP_ID'`

---

## 📝 Code Location

**File:** `view/gui_view.py`

**Function:** `create_facebook_embed(fb_url, use_sdk=False)`

**Lines:** ~911-960

**Logic:**
```python
if use_sdk:
    # SDK Method
    embed_code = (
        f'<script>window.fbAsyncInit = function() {{...}}</script>'
        f'<div class="fb-video" data-href="{clean_url}" data-width="267"></div>'
    )
else:
    # Iframe Method (default)
    embed_code = (
        f'<iframe src="..."width="267"height="591"...></iframe>'
    )
```

---

## 🐛 Troubleshooting

### Vấn đề 1: SDK không load

**Nguyên nhân:** Script bị block bởi ad blocker hoặc CSP

**Giải pháp:**
1. Tắt ad blocker
2. Check WordPress CSP settings
3. Whitelist `connect.facebook.net`

### Vấn đề 2: Video không hiển thị (SDK method)

**Nguyên nhân:** SDK chưa load xong

**Giải pháp:**
- SDK tự động load async
- Đợi vài giây để SDK init
- Check console log có error không

### Vấn đề 3: Kích thước không đúng (SDK method)

**Nguyên nhân:** SDK tự động responsive

**Giải pháp:**
```css
/* Force width */
.fb-video {
    width: 267px !important;
}
```

---

## ✅ Checklist

Khi dùng SDK Method:

- [ ] Set `facebook_use_sdk: true` trong config.json
- [ ] Load SDK script trước `<div class="fb-video">`
- [ ] Dùng `data-href` với full Facebook URL
- [ ] Set `data-width="267"` cho kích thước
- [ ] Check console log có error không
- [ ] Test video có play được không

---

## 🎉 Kết luận

Tool giờ hỗ trợ **2 methods** cho Facebook video:

1. **Iframe Method** (default) - Nhanh, 267x591 cố định, NO SPACES
2. **SDK Method** (bypass) - Chậm hơn, responsive, bypass security

Chỉ cần set `facebook_use_sdk: true` trong config.json để bật SDK method! 🚀

---

**Version:** 3.0.0  
**Date:** 2026-01-29  
**Status:** ✅ IMPLEMENTED - 2 METHODS AVAILABLE
