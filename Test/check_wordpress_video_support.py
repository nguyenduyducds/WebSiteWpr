#!/usr/bin/env python3
"""
Kiểm tra WordPress có hỗ trợ video embed không
"""

import sys
import os
import time
sys.path.append('.')

from model.selenium_wp import SeleniumWPClient
from model.config_manager import ConfigManager

def check_wordpress_admin():
    """Kiểm tra bài viết trong WordPress Admin"""
    print("🔍 Checking WordPress Admin...")
    
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        site_url = config.get("site_url", "")
        username = config.get("username", "")
        password = config.get("password", "")
        
        selenium_client = SeleniumWPClient(site_url, username, password)
        selenium_client.init_driver(headless=False)
        
        if not selenium_client.login():
            print("❌ Login failed!")
            return False
        
        print("✅ Login successful!")
        
        # Vào Posts list
        base_url = site_url.replace('/wp-admin', '').replace('https://', 'https://').replace('http://', 'https://')
        posts_url = f"{base_url}/wp-admin/edit.php"
        
        print(f"📋 Navigating to Posts: {posts_url}")
        selenium_client.driver.get(posts_url)
        time.sleep(3)
        
        # Tìm bài viết mới nhất
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Tìm link "Edit" đầu tiên (bài mới nhất)
            edit_links = selenium_client.driver.find_elements(By.XPATH, "//a[contains(@aria-label, 'Edit') or contains(text(), 'Edit')]")
            
            if edit_links:
                print(f"📝 Found {len(edit_links)} edit links")
                
                # Click edit link đầu tiên
                edit_links[0].click()
                time.sleep(3)
                
                print("📝 Opened post editor")
                
                # Switch to Code Editor để xem raw HTML
                try:
                    # Try keyboard shortcut first
                    from selenium.webdriver.common.action_chains import ActionChains
                    from selenium.webdriver.common.keys import Keys
                    
                    ActionChains(selenium_client.driver).key_down(Keys.CONTROL).key_down(Keys.SHIFT).key_down(Keys.ALT).send_keys('m').key_up(Keys.ALT).key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()
                    time.sleep(2)
                    
                    # Tìm textarea content
                    textareas = selenium_client.driver.find_elements(By.TAG_NAME, "textarea")
                    visible_textareas = [t for t in textareas if t.is_displayed()]
                    
                    if visible_textareas:
                        content_area = visible_textareas[-1]  # Usually the last one is content
                        raw_content = content_area.get_attribute("value")
                        
                        print(f"📄 Raw content length: {len(raw_content)}")
                        
                        # Kiểm tra iframe
                        if "iframe" in raw_content:
                            print("✅ IFRAME FOUND in WordPress content!")
                            
                            # Count iframes
                            iframe_count = raw_content.count("<iframe")
                            print(f"   📊 Iframe count: {iframe_count}")
                            
                            # Show iframe lines
                            lines = raw_content.split('\n')
                            iframe_lines = [i for i, line in enumerate(lines) if 'iframe' in line.lower()]
                            
                            print(f"   🎬 Iframe at lines: {iframe_lines[:3]}")  # Show first 3
                            for line_num in iframe_lines[:2]:
                                if line_num < len(lines):
                                    print(f"   {line_num:3d}: {lines[line_num][:100]}...")
                            
                            print("\n✅ KẾT LUẬN: Tool hoạt động OK!")
                            print("   → Iframe được inject thành công vào WordPress")
                            print("   → Vấn đề là Theme/Plugin đang block hiển thị")
                            
                        else:
                            print("❌ NO IFRAME found in WordPress content!")
                            print("   → Tool có vấn đề trong việc inject content")
                            
                            # Show what's actually there
                            if len(raw_content) < 500:
                                print(f"   Actual content: {raw_content}")
                            else:
                                print(f"   Content preview: {raw_content[:300]}...")
                        
                        # Giữ browser mở để user kiểm tra
                        print(f"\n⏳ Keeping browser open for 20 seconds...")
                        print(f"   Bạn có thể kiểm tra trực tiếp trong Code Editor")
                        time.sleep(20)
                        
                    else:
                        print("❌ No textarea found in Code Editor")
                        
                except Exception as e:
                    print(f"❌ Error checking content: {e}")
                    
            else:
                print("❌ No edit links found")
                
        except Exception as e:
            print(f"❌ Error navigating posts: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            selenium_client.close()
        except:
            pass

def create_simple_test_post():
    """Tạo bài test đơn giản để kiểm tra"""
    print("\n🧪 Creating Simple Test Post...")
    
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        site_url = config.get("site_url", "")
        username = config.get("username", "")
        password = config.get("password", "")
        
        selenium_client = SeleniumWPClient(site_url, username, password)
        selenium_client.init_driver(headless=False)
        
        if not selenium_client.login():
            print("❌ Login failed!")
            return False
        
        # Tạo bài viết với HTML đơn giản nhất
        from model.wp_model import BlogPost
        
        simple_post = BlogPost(
            title=f"🔍 Simple Video Test - {int(time.time())}",
            video_url="",  # Không dùng auto-generation
            image_url="",
            raw_content=""
        )
        
        # Set content trực tiếp - chỉ có iframe thuần
        simple_post.content = '''<!-- wp:html -->
<h2>Test Video Embed</h2>
<p>Video phía dưới:</p>
<iframe title="vimeo-player" src="https://player.vimeo.com/video/1152744141?h=bfb456b5d0" width="640" height="360" frameborder="0" allowfullscreen></iframe>
<p>Nếu thấy video → Theme hỗ trợ iframe</p>
<p>Nếu không thấy → Theme/Plugin block iframe</p>
<!-- /wp:html -->'''
        
        print("📤 Posting simple test...")
        success, result = selenium_client.post_article(simple_post)
        
        if success:
            print(f"✅ Simple test posted!")
            print(f"🔗 Link: {result}")
            print(f"\n💡 Kiểm tra link này:")
            print(f"   {result}")
            print(f"\n🎯 Nếu thấy video → Theme OK, vấn đề ở tool")
            print(f"   Nếu không thấy → Theme/Plugin block iframe")
            
            time.sleep(10)
            return True
        else:
            print(f"❌ Simple test failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Simple test error: {e}")
        return False
    finally:
        try:
            selenium_client.close()
        except:
            pass

def main():
    """Chạy kiểm tra WordPress"""
    print("🚀 WordPress Video Support Check")
    print("=" * 50)
    
    # Test 1: Kiểm tra WordPress Admin
    check_wordpress_admin()
    
    # Test 2: Tạo bài test đơn giản
    create_simple_test_post()
    
    print("\n" + "=" * 50)
    print("📊 HƯỚNG DẪN TIẾP THEO:")
    print()
    print("✅ NẾU THẤY IFRAME trong WordPress Admin:")
    print("   → Tool hoạt động OK")
    print("   → Vấn đề: Theme/Plugin block video")
    print("   → Giải pháp: Tắt plugins, đổi theme")
    print()
    print("❌ NẾU KHÔNG THẤY IFRAME trong WordPress Admin:")
    print("   → Tool có vấn đề inject content")
    print("   → Cần debug thêm code injection")
    print()
    print("🔧 CÁCH SỬA:")
    print("1. Tắt tất cả plugins WordPress")
    print("2. Đổi theme về Twenty Twenty-Four")
    print("3. Test lại")
    print("4. Nếu vẫn không có → Liên hệ hosting support")

if __name__ == "__main__":
    main()