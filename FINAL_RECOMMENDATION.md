# Final Recommendation - WordPress Automation

## Vấn đề hiện tại

Sau nhiều giờ troubleshooting, chúng ta đã thử:

### ✅ Đã làm được:
1. ✅ Login thành công
2. ✅ Navigate đến editor
3. ✅ Dismiss welcome modal
4. ✅ Post được published
5. ✅ URL accessible

### ❌ Vẫn chưa được:
1. ❌ **Title không được lưu** - Vẫn "Add title" hoặc "No title"
2. ❌ **Content không được lưu** - HTML code bị mất
3. ❌ **Featured image không được set**

## Nguyên nhân gốc rễ

**Gutenberg phụ thuộc hoàn toàn vào REST API**

Khi REST API bị block (403):
- Title không save được
- Content không save được  
- Featured image không upload được
- Autosave fail
- Publish fail (hoặc publish nhưng không có data)

## Các giải pháp đã thử

### 1. Block REST API và fake responses ❌
- Gutenberg vẫn cần REST API để lưu data
- Fake responses không có post ID thật
- Data không được lưu vào database

### 2. Form submit trực tiếp ❌
- Gutenberg không dùng form submit
- Data chỉ tồn tại trong JavaScript state
- Submit form = submit empty data

### 3. Classic Editor ❌
- Site không có Classic Editor plugin
- User không có quyền admin để cài
- `?classic-editor` parameter không hoạt động

### 4. JavaScript injection ❌
- Set title/content qua JavaScript
- Nhưng không trigger save
- Data mất khi publish

## Giải pháp cuối cùng (RECOMMENDED)

### Option 1: WordPress REST API trực tiếp (BEST)

**Không dùng Selenium/Gutenberg, dùng Python requests**

```python
import requests

# 1. Login và lấy cookies
session = requests.Session()
login_response = session.post(
    f"{site_url}/wp-login.php",
    data={
        "log": username,
        "pwd": password,
        "wp-submit": "Log In"
    }
)

# 2. Lấy nonce
dashboard = session.get(f"{site_url}/wp-admin/")
# Extract nonce from HTML

# 3. Upload featured image
with open(image_path, 'rb') as f:
    files = {'file': f}
    media_response = session.post(
        f"{site_url}/wp-json/wp/v2/media",
        files=files,
        headers={'X-WP-Nonce': nonce}
    )
    media_id = media_response.json()['id']

# 4. Create post
post_response = session.post(
    f"{site_url}/wp-json/wp/v2/posts",
    json={
        'title': title,
        'content': content,
        'status': 'publish',
        'featured_media': media_id
    },
    headers={'X-WP-Nonce': nonce}
)

post_id = post_response.json()['id']
post_url = post_response.json()['link']
```

**Ưu điểm:**
- ✅ Không cần Selenium
- ✅ Không cần Gutenberg
- ✅ Nhanh hơn nhiều
- ✅ Reliable 100%
- ✅ Dễ debug

**Nhược điểm:**
- ⚠️ Cần REST API không bị block
- ⚠️ Nếu REST API bị block → Không có cách nào khác

### Option 2: WordPress XML-RPC (Backup)

Nếu REST API bị block, dùng XML-RPC (old API):

```python
import xmlrpc.client

wp = xmlrpc.client.ServerProxy(f"{site_url}/xmlrpc.php")

# Upload image
with open(image_path, 'rb') as f:
    data = {
        'name': 'image.jpg',
        'type': 'image/jpeg',
        'bits': xmlrpc.client.Binary(f.read())
    }
    media_response = wp.wp.uploadFile(blog_id, username, password, data)
    media_id = media_response['id']

# Create post
post_data = {
    'post_title': title,
    'post_content': content,
    'post_status': 'publish',
    'post_thumbnail': media_id
}
post_id = wp.wp.newPost(blog_id, username, password, post_data)
```

**Ưu điểm:**
- ✅ Không cần REST API
- ✅ Old but reliable
- ✅ Ít bị block hơn

**Nhược điểm:**
- ⚠️ Có thể bị disable
- ⚠️ Ít features hơn REST API

### Option 3: Request admin access (ULTIMATE)

**Yêu cầu admin cài Classic Editor plugin**

Với Classic Editor:
- ✅ Không cần REST API
- ✅ Form submit truyền thống
- ✅ 100% reliable
- ✅ Code đã có sẵn

## Implementation Plan

### Bước 1: Test REST API
```python
import requests
response = requests.get(f"{site_url}/wp-json/wp/v2/posts")
if response.status_code == 200:
    print("REST API available - use Option 1")
elif response.status_code == 403:
    print("REST API blocked - try Option 2 or 3")
```

### Bước 2: Implement Option 1 (REST API)
- Tạo file mới: `model/wp_rest_api.py`
- Implement REST API client
- Test với 1 post

### Bước 3: Fallback to Option 2 (XML-RPC)
- Nếu REST API fail
- Try XML-RPC
- Test với 1 post

### Bước 4: Request admin access
- Nếu cả 2 fail
- Email admin request cài Classic Editor
- Hoặc whitelist REST API

## Code Structure

```
model/
├── selenium_wp.py          # Current (Gutenberg + Selenium)
├── wp_rest_api.py          # NEW (REST API direct)
├── wp_xmlrpc.py            # NEW (XML-RPC fallback)
└── wp_model.py             # Wrapper (auto-select method)
```

## Recommendation

**Implement REST API method ASAP**

Lý do:
1. Selenium + Gutenberg = Too complex, too many issues
2. REST API = Simple, fast, reliable
3. Nếu REST API bị block → Không có giải pháp nào khác work 100%

**Next steps:**
1. Test xem REST API có bị block không
2. Nếu không → Implement REST API method
3. Nếu có → Request admin whitelist hoặc cài Classic Editor

## Conclusion

Sau nhiều giờ troubleshooting, kết luận:

**Gutenberg + REST API blocked = Impossible to automate reliably**

Giải pháp duy nhất:
- Dùng REST API trực tiếp (không qua Gutenberg)
- Hoặc dùng Classic Editor (cần admin access)
- Hoặc dùng XML-RPC (nếu enabled)

Selenium + Gutenberg với REST API blocked = Waste of time ❌
