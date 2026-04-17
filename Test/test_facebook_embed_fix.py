
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.seo_content_generator import SEOContentGenerator
from model.theme_manager import ThemeManager
from model.wp_model import BlogPost

def test_seo_generator():
    print("\n--- Testing SEOContentGenerator ---")
    generator = SEOContentGenerator()
    
    # Test Reel URL
    url = "https://www.facebook.com/reel/896240026390242/"
    html = generator.generate_video_embed(url)
    print(f"Reel Input: {url}")
    print(f"Output:\n{html}")
    
    assert "plugins/video.php" in html
    assert "href=https%3A%2F%2Fwww.facebook.com%2Freel%2F896240026390242%2F" in html
    assert 'width="267"' in html
    assert 'height="476"' in html
    assert 'scrolling="no"' in html
    
    # Test Standard Video URL
    url2 = "https://www.facebook.com/watch/?v=123456789"
    html2 = generator.generate_video_embed(url2)
    print(f"\nStandard Input: {url2}")
    print(f"Output:\n{html2}")
    assert "width=560" in html2 or 'width="560"' in html2

def test_theme_manager():
    print("\n--- Testing ThemeManager ---")
    manager = ThemeManager()
    
    url = "https://www.facebook.com/reel/896240026390242/"
    # Calling internal method for direct verification
    html = manager.generate_video_embed(url)
    print(f"Reel Input: {url}")
    print(f"Output:\n{html}")
    
    assert "plugins/video.php" in html
    assert "display: flex" in html

def test_wp_model():
    print("\n--- Testing WPModel ---")
    # Mocking basic wp_model behavior
    post = BlogPost("Test Title", video_url="https://www.facebook.com/reel/896240026390242/", raw_content="Content")
    
    # Access private method for testing
    block = post._generate_video_block(post.video_url)
    print(f"Reel Input: {post.video_url}")
    print(f"Output:\n{block}")
    
    assert "plugins/video.php" in block
    assert "fb-video-container" in block
    assert "width=267" in block

if __name__ == "__main__":
    try:
        test_seo_generator()
        test_theme_manager()
        test_wp_model()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
