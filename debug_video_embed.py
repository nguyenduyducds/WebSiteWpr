#!/usr/bin/env python3
"""
Debug script để kiểm tra vấn đề video embed không hiển thị trên WordPress
"""

import sys
import os
sys.path.append('.')

from model.wp_model import BlogPost, WordPressClient
from model.config_manager import ConfigManager

def test_video_embed_generation():
    """Test tạo video embed code"""
    print("🧪 Testing Video Embed Generation...")
    
    # Test cases
    test_cases = [
        {
            "name": "YouTube URL",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "expected": "youtube"
        },
        {
            "name": "Vimeo URL", 
            "url": "https://vimeo.com/123456789",
            "expected": "vimeo"
        },
        {
            "name": "Facebook URL",
            "url": "https://www.facebook.com/watch/?v=123456789",
            "expected": "facebook"
        },
        {
            "name": "Raw Embed Code",
            "url": '<iframe src="https://player.vimeo.com/video/123456789" width="640" height="360"></iframe>',
            "expected": "iframe"
        }
    ]
    
    for test in test_cases:
        print(f"\n📹 Testing {test['name']}: {test['url'][:50]}...")
        
        # Tạo BlogPost với video URL
        post = BlogPost(
            title=f"Test {test['name']}", 
            video_url=test['url'],
            image_url="",
            raw_content=""
        )
        
        # Generate content
        content = post.generate_seo_content()
        
        # Kiểm tra kết quả
        if test['expected'] in content.lower():
            print(f"✅ {test['name']} embed generated successfully")
            
            # Hiển thị một phần content để debug
            lines = content.split('\n')
            video_lines = [line for line in lines if 'iframe' in line or 'embed' in line or 'video' in line][:3]
            for line in video_lines:
                print(f"   📄 {line.strip()[:100]}...")
        else:
            print(f"❌ {test['name']} embed generation failed")
            print(f"   Expected: {test['expected']}")
            print(f"   Content length: {len(content)}")

def test_wordpress_connection():
    """Test kết nối WordPress"""
    print("\n🔗 Testing WordPress Connection...")
    
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        site_url = config.get("site_url", "")
        username = config.get("username", "")
        password = config.get("password", "")
        
        if not all([site_url, username, password]):
            print("❌ Missing WordPress credentials in config.json")
            return False
            
        # Clean site URL
        clean_url = site_url.strip().rstrip('/')
        if clean_url.endswith('/wp-admin'):
            clean_url = clean_url[:-9]
        if not clean_url.startswith('http'):
            clean_url = 'https://' + clean_url
            
        print(f"   🌐 Site: {clean_url}")
        print(f"   👤 User: {username}")
        
        # Test XML-RPC connection
        client = WordPressClient(clean_url, username, password)
        
        # Tạo test post đơn giản
        test_post = BlogPost(
            title="🧪 Video Embed Test Post",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", 
            image_url="",
            raw_content="This is a test post to check video embedding."
        )
        test_post.generate_seo_content()
        
        print(f"   📝 Generated content length: {len(test_post.content)} chars")
        
        # Kiểm tra có video block không
        if "iframe" in test_post.content or "embed" in test_post.content:
            print("   ✅ Video embed code found in content")
        else:
            print("   ❌ No video embed code found in content")
            
        return True
        
    except Exception as e:
        print(f"❌ WordPress connection test failed: {e}")
        return False

def analyze_content_structure():
    """Phân tích cấu trúc content được tạo"""
    print("\n📊 Analyzing Content Structure...")
    
    post = BlogPost(
        title="Test Video Post",
        video_url="https://vimeo.com/123456789",
        image_url="",
        raw_content=""
    )
    
    content = post.generate_seo_content()
    
    # Phân tích các thành phần
    components = {
        "CSS Styles": content.count("<style>"),
        "HTML Blocks": content.count("<!-- wp:html -->"),
        "Video Containers": content.count("video-container"),
        "Iframes": content.count("<iframe"),
        "Embeds": content.count("wp:embed"),
        "Paragraphs": content.count("wp:paragraph"),
        "Headings": content.count("wp:heading")
    }
    
    print("   📈 Content Components:")
    for component, count in components.items():
        status = "✅" if count > 0 else "❌"
        print(f"   {status} {component}: {count}")
    
    # Tìm video block
    lines = content.split('\n')
    video_block_start = -1
    video_block_end = -1
    
    for i, line in enumerate(lines):
        if 'iframe' in line and 'vimeo' in line:
            video_block_start = max(0, i-2)
            video_block_end = min(len(lines), i+3)
            break
    
    if video_block_start >= 0:
        print(f"\n   🎬 Video Block Found (lines {video_block_start}-{video_block_end}):")
        for i in range(video_block_start, video_block_end):
            if i < len(lines):
                print(f"   {i:3d}: {lines[i]}")
    else:
        print("   ❌ No video block found in content")

def check_wordpress_capabilities():
    """Kiểm tra khả năng của WordPress site"""
    print("\n🔧 Checking WordPress Capabilities...")
    
    suggestions = [
        "1. Kiểm tra Theme có hỗ trợ video embeds không",
        "2. Tắt tất cả plugins và test lại", 
        "3. Kiểm tra WordPress settings > Media > Auto-embeds",
        "4. Thử đăng manual một video embed để test",
        "5. Kiểm tra Console browser có lỗi JavaScript không",
        "6. Verify theme không strip iframe tags"
    ]
    
    print("   💡 Troubleshooting Suggestions:")
    for suggestion in suggestions:
        print(f"   {suggestion}")

def main():
    """Chạy tất cả tests"""
    print("🚀 WordPress Video Embed Debug Tool")
    print("=" * 50)
    
    tests = [
        test_video_embed_generation,
        test_wordpress_connection, 
        analyze_content_structure,
        check_wordpress_capabilities
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed: {e}")
        print()
    
    print("🏁 Debug completed! Check the results above.")
    print("\n💡 Next Steps:")
    print("1. Nếu embed code được tạo đúng → Vấn đề ở WordPress/Theme")
    print("2. Nếu embed code không có → Vấn đề ở code generation")
    print("3. Test manual post một video embed trực tiếp vào WordPress")

if __name__ == "__main__":
    main()