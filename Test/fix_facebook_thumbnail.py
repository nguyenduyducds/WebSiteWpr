"""
Fix Facebook Thumbnail Issue
Add Open Graph meta tags to WordPress posts
"""

def add_og_meta_tags_script():
    """
    JavaScript to inject Open Graph meta tags into WordPress post
    This ensures Facebook picks up the correct featured image
    """
    return """
    // Add Open Graph meta tags for Facebook sharing
    (function() {
        // Get featured image URL
        var featuredImg = document.querySelector('.wp-post-image, .attachment-post-thumbnail, article img');
        var imgUrl = featuredImg ? featuredImg.src : '';
        
        // Get post title
        var title = document.querySelector('h1.entry-title, h1.post-title, article h1');
        var titleText = title ? title.textContent.trim() : document.title;
        
        // Get post excerpt/description
        var excerpt = document.querySelector('.entry-excerpt, .post-excerpt, article p');
        var excerptText = excerpt ? excerpt.textContent.trim().substring(0, 200) : '';
        
        // Get current URL
        var url = window.location.href;
        
        // Remove existing OG tags if any
        var existingOgTags = document.querySelectorAll('meta[property^="og:"]');
        existingOgTags.forEach(function(tag) {
            tag.remove();
        });
        
        // Add OG tags
        var ogTags = [
            { property: 'og:type', content: 'article' },
            { property: 'og:url', content: url },
            { property: 'og:title', content: titleText },
            { property: 'og:description', content: excerptText },
            { property: 'og:image', content: imgUrl },
            { property: 'og:image:width', content: '1200' },
            { property: 'og:image:height', content: '630' },
            { property: 'og:site_name', content: document.title.split('|')[0].trim() }
        ];
        
        // Add Twitter Card tags
        var twitterTags = [
            { name: 'twitter:card', content: 'summary_large_image' },
            { name: 'twitter:title', content: titleText },
            { name: 'twitter:description', content: excerptText },
            { name: 'twitter:image', content: imgUrl }
        ];
        
        var head = document.head || document.getElementsByTagName('head')[0];
        
        // Inject OG tags
        ogTags.forEach(function(tag) {
            if (tag.content) {
                var meta = document.createElement('meta');
                meta.setAttribute('property', tag.property);
                meta.setAttribute('content', tag.content);
                head.appendChild(meta);
            }
        });
        
        // Inject Twitter tags
        twitterTags.forEach(function(tag) {
            if (tag.content) {
                var meta = document.createElement('meta');
                meta.setAttribute('name', tag.name);
                meta.setAttribute('content', tag.content);
                head.appendChild(meta);
            }
        });
        
        console.log('[OG_META] Added Open Graph tags for Facebook sharing');
        console.log('[OG_META] Featured Image:', imgUrl);
    })();
    """


def get_facebook_debug_url(post_url):
    """
    Get Facebook Sharing Debugger URL to clear cache
    """
    return f"https://developers.facebook.com/tools/debug/?q={post_url}"


def clear_facebook_cache_instructions(post_url):
    """
    Instructions to clear Facebook cache for a post
    """
    debug_url = get_facebook_debug_url(post_url)
    
    return f"""
    🔧 CÁCH XÓA CACHE FACEBOOK CHO THUMBNAIL

    Vấn đề: Facebook cache ảnh cũ, không lấy featured image mới
    
    Giải pháp:
    
    1. Mở Facebook Sharing Debugger:
       {debug_url}
    
    2. Click "Scrape Again" để Facebook lấy lại ảnh mới
    
    3. Kiểm tra preview - ảnh đã đúng chưa
    
    4. Share lại link lên Facebook
    
    ---
    
    HOẶC:
    
    1. Thêm ?v=1 vào cuối URL khi share:
       {post_url}?v=1
    
    2. Facebook sẽ coi đây là URL mới và lấy ảnh mới
    
    3. Mỗi lần share, tăng số: ?v=2, ?v=3, ...
    
    ---
    
    LƯU Ý:
    - Facebook cache ảnh trong 24-48 giờ
    - Phải dùng Debugger để xóa cache ngay lập tức
    - Hoặc đợi 1-2 ngày Facebook tự update
    """


if __name__ == "__main__":
    print("=" * 60)
    print("FIX FACEBOOK THUMBNAIL ISSUE")
    print("=" * 60)
    
    # Example post URL
    example_url = "https://spotlight.tfvp.org/14490/30/"
    
    print("\n📋 Open Graph Meta Tags Script:")
    print("-" * 60)
    print(add_og_meta_tags_script())
    
    print("\n" + "=" * 60)
    print(clear_facebook_cache_instructions(example_url))
    print("=" * 60)
    
    print("\n✅ Script này sẽ được tự động inject vào WordPress post")
    print("✅ Đảm bảo Facebook lấy đúng featured image")
