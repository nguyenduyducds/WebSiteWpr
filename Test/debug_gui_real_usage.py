#!/usr/bin/env python3
"""
Debug thực tế việc sử dụng GUI để tìm vấn đề
"""

import sys
import os
import time
sys.path.append('.')

from model.selenium_wp import SeleniumWPClient
from model.wp_model import BlogPost
from model.config_manager import ConfigManager
from view.gui_view import AppData

def simulate_gui_usage():
    """Mô phỏng cách user sử dụng GUI"""
    print("🎯 Simulating Real GUI Usage...")
    
    # Mô phỏng data từ GUI
    data = AppData()
    data.title = "Test Video từ GUI"
    data.video_url = '<iframe title="vimeo-player" src="https://player.vimeo.com/video/1152744141?h=bfb456b5d0" width="640" height="360" frameborder="0" referrerpolicy="strict-origin-when-cross-origin" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" allowfullscreen></iframe>'
    data.image_url = ""
    
    # Test case 1: Content trống (như user để trống field)
    print("\n📝 Test Case 1: Content field trống")
    data.content = ""
    
    print(f"   Title: {data.title}")
    print(f"   Video URL: {data.video_url[:50]}...")
    print(f"   Content: '{data.content}'")
    print(f"   Content stripped: '{data.content.strip()}'")
    
    # Áp dụng logic mới từ controller
    content = data.content.strip() if data.content else ""
    if data.video_url and not content:
        raw_content = ""  # Auto-generate
        print("   → Logic: Auto-generate (raw_content = '')")
    else:
        raw_content = content
        print(f"   → Logic: Use custom content (raw_content = '{raw_content}')")
    
    # Tạo BlogPost
    post = BlogPost(data.title, data.video_url, data.image_url, raw_content)
    generated_content = post.generate_seo_content()
    
    print(f"   Generated content length: {len(generated_content)}")
    
    # Kiểm tra video trong content
    if "iframe" in generated_content and "vimeo" in generated_content:
        print("   ✅ Video iframe found in content")
        
        # Tìm iframe line
        lines = generated_content.split('\n')
        for i, line in enumerate(lines):
            if 'iframe' in line and 'vimeo' in line:
                print(f"   🎬 Iframe at line {i}: {line[:80]}...")
                break
    else:
        print("   ❌ No video iframe found")
        
        # Debug: Tìm bất kỳ reference nào
        if "vimeo" in generated_content.lower():
            print("   ⚠️ Found vimeo reference but no iframe")
        else:
            print("   ❌ No vimeo reference at all")
    
    # Test case 2: Content có nội dung (như user gõ gì đó)
    print("\n📝 Test Case 2: Content field có nội dung")
    data.content = "Đây là nội dung tự viết"
    
    content = data.content.strip() if data.content else ""
    if data.video_url and not content:
        raw_content = ""
        print("   → Logic: Auto-generate")
    else:
        raw_content = content
        print(f"   → Logic: Use custom content (raw_content = '{raw_content}')")
    
    post2 = BlogPost(data.title, data.video_url, data.image_url, raw_content)
    generated_content2 = post2.generate_seo_content()
    
    print(f"   Generated content length: {len(generated_content2)}")
    print(f"   Content: '{generated_content2}'")
    
    return data, generated_content

def test_real_posting():
    """Test đăng bài thực tế với GUI data"""
    print("\n🚀 Testing Real Posting with GUI Data...")
    
    try:
        # Load config
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        site_url = config.get("site_url", "")
        username = config.get("username", "")
        password = config.get("password", "")
        
        # Mô phỏng GUI data - CHÍNH XÁC như user sử dụng
        data = AppData()
        data.title = f"🎯 GUI Real Test - {int(time.time())}"
        data.video_url = '<iframe title="vimeo-player" src="https://player.vimeo.com/video/1152744141?h=bfb456b5d0" width="640" height="360" frameborder="0" referrerpolicy="strict-origin-when-cross-origin" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" allowfullscreen></iframe>'
        data.image_url = ""
        data.content = ""  # User để trống field content
        
        print(f"🌐 Site: {site_url}")
        print(f"👤 User: {username}")
        print(f"📝 Title: {data.title}")
        print(f"🎥 Video: {data.video_url[:50]}...")
        print(f"📄 Content: '{data.content}' (empty)")
        
        # Áp dụng logic controller mới
        content = data.content.strip() if data.content else ""
        if data.video_url and not content:
            raw_content = ""  # Auto-generate
            print("✅ Logic: Will auto-generate content with video")
        else:
            raw_content = content
            print(f"⚠️ Logic: Will use custom content: '{raw_content}'")
        
        # Tạo Selenium client
        selenium_client = SeleniumWPClient(site_url, username, password)
        selenium_client.init_driver(headless=False)
        
        if not selenium_client.login():
            print("❌ Login failed!")
            return False
        
        print("✅ Login successful!")
        
        # Tạo BlogPost với logic mới
        post = BlogPost(data.title, data.video_url, data.image_url, raw_content)
        post.generate_seo_content()
        
        print(f"📊 Final content length: {len(post.content)}")
        
        # Debug final content
        if "iframe" in post.content and "vimeo" in post.content:
            print("✅ Final content contains video iframe")
        else:
            print("❌ Final content does NOT contain video iframe")
            
            # Show what's actually in the content
            if len(post.content) < 100:
                print(f"   Actual content: '{post.content}'")
            else:
                print(f"   Content preview: '{post.content[:200]}...'")
        
        # Post to WordPress
        print("\n📤 Posting to WordPress...")
        success, result = selenium_client.post_article(post)
        
        if success:
            print(f"✅ Post successful!")
            print(f"🔗 Link: {result}")
            print(f"\n💡 KIỂM TRA LINK NÀY:")
            print(f"   {result}")
            
            # Giữ browser mở
            print("\n⏳ Keeping browser open for 15 seconds...")
            time.sleep(15)
            
            return True, result
        else:
            print(f"❌ Post failed: {result}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False, None
    finally:
        try:
            selenium_client.close()
        except:
            pass

def main():
    """Chạy debug tests"""
    print("🚀 GUI Real Usage Debug")
    print("=" * 60)
    print("🎯 Mô phỏng chính xác cách user sử dụng GUI")
    print("=" * 60)
    
    # Test 1: Simulate GUI logic
    data, content = simulate_gui_usage()
    
    # Test 2: Real posting
    success, link = test_real_posting()
    
    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ DEBUG:")
    
    if success:
        print(f"✅ Đăng bài thành công: {link}")
        print("\n🎯 KIỂM TRA:")
        print("1. Mở link trên")
        print("2. Xem có video Vimeo hiển thị không")
        print("3. Nếu không có → Vấn đề ở WordPress/Theme")
        print("4. Nếu có → Logic đã OK")
    else:
        print("❌ Đăng bài thất bại")
    
    print("\n💡 NẾU VẪN KHÔNG THẤY VIDEO:")
    print("1. Kiểm tra WordPress Admin → Posts → Edit bài vừa đăng")
    print("2. Xem trong Code Editor có iframe không")
    print("3. Nếu có iframe → Theme/Plugin block video")
    print("4. Nếu không có iframe → Logic generation có vấn đề")

if __name__ == "__main__":
    main()