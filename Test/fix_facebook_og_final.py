"""
Final Solution: Inject OG Image Tag After Posting
This ensures Facebook gets the correct featured image, not Vimeo thumbnail
"""

def inject_og_image_to_post(selenium_client, post_url, featured_image_url):
    """
    Inject OG image meta tag to WordPress post after publishing
    This forces Facebook to use featured image instead of Vimeo thumbnail
    
    Args:
        selenium_client: Selenium WordPress client
        post_url: URL of published post
        featured_image_url: URL of uploaded featured image
    """
    try:
        print(f"[OG_FIX] Injecting OG image tag to post...")
        
        # Navigate to post edit page
        post_id = post_url.split('/')[-2]  # Extract post ID from URL
        edit_url = f"{selenium_client.site_url}/wp-admin/post.php?post={post_id}&action=edit"
        
        selenium_client.driver.get(edit_url)
        time.sleep(2)
        
        # Switch to Text/HTML editor
        try:
            # Try Gutenberg code editor
            selenium_client.driver.execute_script("""
                // Open code editor in Gutenberg
                wp.data.dispatch('core/edit-post').switchEditorMode('text');
            """)
            time.sleep(1)
        except:
            # Try Classic editor
            try:
                text_tab = selenium_client.driver.find_element(By.ID, "content-html")
                text_tab.click()
                time.sleep(1)
            except:
                print("[OG_FIX] Could not switch to HTML editor")
                return False
        
        # Get current content
        try:
            # Gutenberg
            content_area = selenium_client.driver.find_element(By.CSS_SELECTOR, ".editor-post-text-editor")
            current_content = content_area.get_attribute('value')
        except:
            # Classic
            content_area = selenium_client.driver.find_element(By.ID, "content")
            current_content = content_area.get_attribute('value')
        
        # Inject OG meta tag at the beginning
        og_tag = f'''<!-- Facebook OG Image Override -->
<meta property="og:image" content="{featured_image_url}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:secure_url" content="{featured_image_url}" />

'''
        
        new_content = og_tag + current_content
        
        # Update content
        selenium_client.driver.execute_script(
            "arguments[0].value = arguments[1];",
            content_area,
            new_content
        )
        
        # Save/Update post
        try:
            # Gutenberg
            selenium_client.driver.execute_script("""
                wp.data.dispatch('core/editor').savePost();
            """)
        except:
            # Classic
            update_btn = selenium_client.driver.find_element(By.ID, "publish")
            update_btn.click()
        
        time.sleep(2)
        print(f"[OG_FIX] ✅ OG image tag injected successfully!")
        return True
        
    except Exception as e:
        print(f"[OG_FIX] ❌ Error injecting OG tag: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_featured_image_url_from_wordpress(selenium_client, post_url):
    """
    Get the featured image URL from WordPress post
    
    Args:
        selenium_client: Selenium WordPress client
        post_url: URL of published post
        
    Returns:
        str: Featured image URL or None
    """
    try:
        # Navigate to post
        selenium_client.driver.get(post_url)
        time.sleep(2)
        
        # Try to find featured image
        try:
            # Method 1: wp-post-image class
            img = selenium_client.driver.find_element(By.CSS_SELECTOR, "img.wp-post-image")
            return img.get_attribute('src')
        except:
            pass
        
        try:
            # Method 2: attachment-post-thumbnail
            img = selenium_client.driver.find_element(By.CSS_SELECTOR, "img.attachment-post-thumbnail")
            return img.get_attribute('src')
        except:
            pass
        
        try:
            # Method 3: First image in article
            img = selenium_client.driver.find_element(By.CSS_SELECTOR, "article img")
            return img.get_attribute('src')
        except:
            pass
        
        print("[OG_FIX] Could not find featured image URL")
        return None
        
    except Exception as e:
        print(f"[OG_FIX] Error getting featured image URL: {e}")
        return None


# Alternative: Use WordPress REST API to update post meta
def inject_og_via_rest_api(site_url, username, password, post_id, featured_image_url):
    """
    Inject OG meta using WordPress REST API
    """
    import requests
    from requests.auth import HTTPBasicAuth
    
    try:
        # Get post content
        api_url = f"{site_url}/wp-json/wp/v2/posts/{post_id}"
        response = requests.get(api_url, auth=HTTPBasicAuth(username, password))
        
        if response.status_code == 200:
            post_data = response.json()
            current_content = post_data['content']['raw']
            
            # Inject OG tag
            og_tag = f'''<!-- Facebook OG Image Override -->
<meta property="og:image" content="{featured_image_url}" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />

'''
            new_content = og_tag + current_content
            
            # Update post
            update_data = {
                'content': new_content
            }
            
            update_response = requests.post(
                api_url,
                json=update_data,
                auth=HTTPBasicAuth(username, password)
            )
            
            if update_response.status_code == 200:
                print("[OG_FIX] ✅ OG tag injected via REST API!")
                return True
            else:
                print(f"[OG_FIX] REST API update failed: {update_response.status_code}")
                return False
        else:
            print(f"[OG_FIX] REST API get failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[OG_FIX] REST API error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("FACEBOOK OG IMAGE FIX - FINAL SOLUTION")
    print("=" * 60)
    print()
    print("Vấn đề: Facebook lấy Vimeo thumbnail thay vì featured image")
    print()
    print("Giải pháp:")
    print("1. Upload featured image TRƯỚC content images")
    print("2. Sau khi đăng bài, inject OG meta tag vào đầu content")
    print("3. OG tag chứa URL featured image đã upload")
    print("4. Facebook sẽ lấy OG tag này thay vì Vimeo thumbnail")
    print()
    print("=" * 60)
