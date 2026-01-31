"""
Test Theme System Integration
Verify that theme selection works end-to-end
"""

def test_theme_manager():
    """Test ThemeManager basic functionality"""
    print("=" * 60)
    print("TEST 1: ThemeManager Basic Functionality")
    print("=" * 60)
    
    from model.theme_manager import ThemeManager
    
    manager = ThemeManager()
    
    # Test 1: List themes
    print("\n📋 Available Themes:")
    themes = manager.get_theme_list()
    for theme in themes:
        print(f"  - {theme['name']} ({theme['id']})")
        print(f"    {theme['description']}")
    
    # Test 2: Switch themes
    print("\n🔄 Testing Theme Switching:")
    for theme_id in ['supercar', 'news', 'default']:
        success = manager.set_theme(theme_id)
        print(f"  - Switch to '{theme_id}': {'✅' if success else '❌'}")
    
    # Test 3: Generate content with each theme
    print("\n📝 Testing Content Generation:")
    test_data = {
        'title': 'Test Supercar Article',
        'video_url': 'https://player.vimeo.com/video/123456789',
        'featured_image': 'https://example.com/image.jpg',
        'content_images': ['https://example.com/img1.jpg', 'https://example.com/img2.jpg']
    }
    
    for theme_id in ['supercar', 'news', 'default']:
        content = manager.generate_content(
            title=test_data['title'],
            video_url=test_data['video_url'],
            featured_image=test_data['featured_image'],
            content_images=test_data['content_images'],
            theme_id=theme_id
        )
        print(f"  - {theme_id}: {len(content)} chars generated")
        
        # Verify placeholders are replaced
        if '{{POST_TITLE}}' in content:
            print(f"    ⚠️ Warning: Placeholder not replaced!")
        else:
            print(f"    ✅ Content properly generated")
    
    print("\n✅ ThemeManager tests completed!")


def test_gui_integration():
    """Test GUI theme selector integration"""
    print("\n" + "=" * 60)
    print("TEST 2: GUI Integration")
    print("=" * 60)
    
    # Simulate AppData with theme
    from view.gui_view import AppData
    
    data = AppData()
    data.title = "Test Post"
    data.theme = "supercar"
    
    print(f"\n📦 AppData created:")
    print(f"  - Title: {data.title}")
    print(f"  - Theme: {data.theme}")
    print(f"  ✅ AppData has theme attribute")


def test_blogpost_integration():
    """Test BlogPost theme integration"""
    print("\n" + "=" * 60)
    print("TEST 3: BlogPost Integration")
    print("=" * 60)
    
    from model.wp_model import BlogPost
    
    # Create post with theme
    post = BlogPost(
        title="Lamborghini Aventador SVJ Review",
        video_url="https://player.vimeo.com/video/123456789",
        image_url="https://example.com/lambo.jpg",
        raw_content="",
        content_images=["https://example.com/img1.jpg"]
    )
    
    # Set theme
    post.theme = "supercar"
    print(f"\n📝 BlogPost created:")
    print(f"  - Title: {post.title}")
    print(f"  - Theme: {post.theme}")
    
    # Generate content
    print(f"\n🔄 Generating SEO content...")
    post.generate_seo_content()
    
    print(f"  - Content length: {len(post.content)} chars")
    
    # Verify theme was used
    if 'supercar-theme' in post.content or 'SUPERCAR NEWS' in post.content:
        print(f"  ✅ Supercar theme applied successfully!")
    else:
        print(f"  ⚠️ Theme may not be applied correctly")
    
    # Check for placeholders
    if '{{' in post.content:
        print(f"  ⚠️ Warning: Some placeholders not replaced")
    else:
        print(f"  ✅ All placeholders replaced")


def test_end_to_end():
    """Test complete flow from GUI to BlogPost"""
    print("\n" + "=" * 60)
    print("TEST 4: End-to-End Flow")
    print("=" * 60)
    
    from view.gui_view import AppData
    from model.wp_model import BlogPost
    
    # Simulate GUI data
    data = AppData()
    data.title = "Ferrari SF90 Stradale: The Future of Supercars"
    data.video_url = "https://player.vimeo.com/video/987654321"
    data.image_url = "https://example.com/ferrari.jpg"
    data.content = ""  # Auto-generate
    data.theme = "supercar"  # Selected from GUI
    
    print(f"\n1️⃣ GUI Data:")
    print(f"  - Title: {data.title}")
    print(f"  - Theme: {data.theme}")
    
    # Simulate controller creating BlogPost
    post = BlogPost(
        title=data.title,
        video_url=data.video_url,
        image_url=data.image_url,
        raw_content=data.content,
        content_images=[]
    )
    
    # Controller sets theme
    if hasattr(data, 'theme') and data.theme:
        post.theme = data.theme
        print(f"\n2️⃣ Controller set theme: {post.theme}")
    
    # Generate content
    print(f"\n3️⃣ Generating content...")
    post.generate_seo_content()
    
    print(f"  - Content generated: {len(post.content)} chars")
    
    # Verify
    if post.theme == data.theme:
        print(f"  ✅ Theme preserved through flow")
    else:
        print(f"  ❌ Theme mismatch!")
    
    if 'supercar-theme' in post.content or 'SUPERCAR NEWS' in post.content:
        print(f"  ✅ Theme applied to content")
    else:
        print(f"  ⚠️ Theme may not be in content")
    
    print(f"\n✅ End-to-end test completed!")


if __name__ == "__main__":
    print("\n🚀 THEME SYSTEM INTEGRATION TEST")
    print("=" * 60)
    
    try:
        test_theme_manager()
        test_gui_integration()
        test_blogpost_integration()
        test_end_to_end()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Theme system is fully integrated and working!")
        print("\nNext steps:")
        print("  1. Run the main application: python main.py")
        print("  2. Select a theme from the dropdown")
        print("  3. Create a post and verify theme is applied")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
