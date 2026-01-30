"""
Script to check WordPress post status
Helps diagnose why posts are not visible on frontend
"""

import sys
from model.selenium_wp import SeleniumWPClient
import time

def check_post_status(site_url, username, password, post_id):
    """Check the status of a specific post"""
    
    print(f"🔍 Checking post status for ID: {post_id}")
    print(f"Site: {site_url}\n")
    
    client = SeleniumWPClient(site_url, username, password)
    
    try:
        # Initialize driver (visible mode to see what's happening)
        print("🌐 Opening browser...")
        client.init_driver(headless=False)
        
        # Login
        print("🔐 Logging in...")
        client.login()
        
        # Navigate to post edit page
        base_url = site_url.rstrip('/')
        
        # Clean URL - ensure it has protocol
        if not base_url.startswith('http://') and not base_url.startswith('https://'):
            base_url = 'https://' + base_url
        
        # Remove /wp-admin if present
        if base_url.endswith('/wp-admin'):
            base_url = base_url[:-9]
        
        edit_url = f"{base_url}/wp-admin/post.php?post={post_id}&action=edit"
        print(f"📝 Opening post editor: {edit_url}")
        client.driver.get(edit_url)
        time.sleep(3)
        
        # Check if post exists
        if "post.php" not in client.driver.current_url:
            print(f"❌ ERROR: Post {post_id} does not exist!")
            return
        
        # Get post title
        try:
            title_elem = client.driver.find_element("css selector", "h1.wp-block-post-title, .editor-post-title__input")
            title = title_elem.text or title_elem.get_attribute("value") or "Unknown"
            print(f"📌 Post Title: {title}")
        except:
            print("⚠️ Could not get post title")
        
        # Check post status
        print("\n🔍 Checking post status...")
        
        try:
            # Method 1: Check status in toolbar
            status_elem = client.driver.find_element("xpath", "//button[contains(@class, 'editor-post-publish-button__button')]")
            status_text = status_elem.text.strip()
            print(f"Status Button Text: {status_text}")
            
            if "Publish" in status_text or "Đăng" in status_text:
                print("❌ STATUS: DRAFT (Not published yet!)")
                print("\n💡 Solution: Click the Publish button to publish the post")
            elif "Update" in status_text or "Cập nhật" in status_text:
                print("✅ STATUS: PUBLISHED")
            else:
                print(f"⚠️ STATUS: Unknown ({status_text})")
        except Exception as e:
            print(f"⚠️ Could not determine status from button: {e}")
            
            # Method 2: Check URL bar status indicator
            try:
                # Look for status in post info panel
                client.driver.execute_script("document.querySelector('.editor-post-publish-panel__toggle').click();")
                time.sleep(1)
                
                status_labels = client.driver.find_elements("css selector", ".components-panel__body-title")
                for label in status_labels:
                    if "Status" in label.text or "Trạng thái" in label.text:
                        print(f"Status Label: {label.text}")
            except:
                pass
        
        # Check visibility
        print("\n🔍 Checking visibility settings...")
        try:
            # Open settings panel if not open
            try:
                settings_btn = client.driver.find_element("css selector", "button[aria-label='Settings'][aria-pressed='false']")
                settings_btn.click()
                time.sleep(0.5)
            except:
                pass
            
            # Look for visibility setting
            visibility_btns = client.driver.find_elements("xpath", "//button[contains(., 'Public') or contains(., 'Private') or contains(., 'Password')]")
            for btn in visibility_btns:
                if btn.is_displayed():
                    print(f"Visibility: {btn.text}")
                    break
        except Exception as e:
            print(f"⚠️ Could not check visibility: {e}")
        
        # Get permalink
        print("\n🔗 Getting permalink...")
        try:
            # Try to find permalink in editor
            permalink_elem = client.driver.find_element("css selector", ".editor-post-permalink__link, .components-external-link")
            permalink = permalink_elem.get_attribute("href")
            print(f"Permalink: {permalink}")
            
            # Test if permalink works
            print("\n🧪 Testing if post is accessible...")
            client.driver.execute_script(f"window.open('{permalink}', '_blank');")
            time.sleep(2)
            
            windows = client.driver.window_handles
            if len(windows) > 1:
                client.driver.switch_to.window(windows[-1])
                time.sleep(2)
                
                page_title = client.driver.title
                page_body = client.driver.find_element("tag name", "body").text
                
                if "404" in page_title or "Not Found" in page_title or "Page Not Found" in page_body:
                    print("❌ Post returns 404 - NOT ACCESSIBLE!")
                    print("\n💡 Possible reasons:")
                    print("   1. Post is still in Draft status")
                    print("   2. Post is set to Private")
                    print("   3. WordPress permalinks need to be flushed")
                    print("   4. Post was deleted")
                else:
                    print(f"✅ Post is accessible! Title: {page_title}")
                
                client.driver.switch_to.window(windows[0])
        except Exception as e:
            print(f"⚠️ Could not get/test permalink: {e}")
        
        print("\n" + "="*60)
        print("✅ Check complete! Review the information above.")
        print("\nPress Enter to close browser...")
        input()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    # Load config
    from model.config_manager import ConfigManager
    config = ConfigManager().load_config()
    
    site_url = config.get("site_url", "")
    username = config.get("username", "")
    password = config.get("password", "")
    
    if not all([site_url, username, password]):
        print("❌ Error: Missing credentials in config.json")
        print("Please run the main tool first to save credentials.")
        sys.exit(1)
    
    # Get post ID from command line or prompt
    if len(sys.argv) > 1:
        post_id = sys.argv[1]
    else:
        post_id = input("Enter Post ID to check: ").strip()
    
    if not post_id.isdigit():
        print("❌ Error: Post ID must be a number")
        sys.exit(1)
    
    check_post_status(site_url, username, password, post_id)
