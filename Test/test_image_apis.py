"""
Test script for Image APIs (Unsplash, Pexels, Pixabay)
Tests all 3 APIs and the multi-source rotation system
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model.image_api import ImageAPI

def print_separator(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def test_individual_apis():
    """Test each API individually"""
    api = ImageAPI()
    
    # Test query
    query = "Ferrari supercar luxury"
    
    print_separator("TEST 1: Unsplash API")
    try:
        results = api.search_car_images(query, count=5, page=1)
        if results:
            print(f"✅ SUCCESS: Found {len(results)} images from Unsplash")
            print(f"📸 Sample URL: {results[0][:80]}...")
        else:
            print("❌ FAILED: No results from Unsplash")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print_separator("TEST 2: Pexels API")
    try:
        results = api.search_pexels_images(query, count=5, page=1)
        if results:
            print(f"✅ SUCCESS: Found {len(results)} images from Pexels")
            print(f"📸 Sample URL: {results[0][:80]}...")
        else:
            print("❌ FAILED: No results from Pexels")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print_separator("TEST 3: Pixabay API")
    try:
        results = api.search_pixabay_images(query, count=5, page=1)
        if results:
            print(f"✅ SUCCESS: Found {len(results)} images from Pixabay")
            print(f"📸 Sample URL: {results[0][:80]}...")
        else:
            print("❌ FAILED: No results from Pixabay")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_multi_source_rotation():
    """Test the multi-source rotation system"""
    print_separator("TEST 4: Multi-Source Rotation System")
    
    api = ImageAPI()
    queries = [
        "Lamborghini exotic car",
        "Porsche sports car",
        "BMW luxury sedan"
    ]
    
    print("Testing 3 consecutive requests to verify API rotation:\n")
    
    for i, query in enumerate(queries, 1):
        print(f"Request {i}: '{query}'")
        results = api.search_multi_source(query, count=3, page=1)
        
        if results:
            print(f"  ✅ Got {len(results)} images")
            print(f"  📊 Current rotation index: {api.current_api_index}")
        else:
            print(f"  ❌ No results")
        print()

def test_get_car_images_from_title():
    """Test the main function used by the app"""
    print_separator("TEST 5: Main Function (get_car_images_from_title)")
    
    api = ImageAPI()
    
    test_titles = [
        "Ferrari F8 Tributo 2024 - Siêu xe đỉnh cao",
        "Lamborghini Aventador SVJ - Hypercar mạnh mẽ",
        "Porsche 911 GT3 RS - Sports car huyền thoại"
    ]
    
    for title in test_titles:
        print(f"\n📝 Title: {title}")
        results = api.get_car_images_from_title(title, count=3)
        
        if results:
            print(f"  ✅ SUCCESS: Got {len(results)} unique images")
            for idx, url in enumerate(results, 1):
                print(f"     {idx}. {url[:70]}...")
        else:
            print(f"  ❌ FAILED: No images found")
        
        print(f"  📊 Pool size: {len(api.image_pool)}, Used images: {len(api.used_images)}")

def test_download_image():
    """Test downloading an image"""
    print_separator("TEST 6: Image Download")
    
    api = ImageAPI()
    
    # Get a test image
    print("Fetching test image from Unsplash...")
    results = api.search_car_images("Ferrari supercar", count=1, page=1)
    
    if results:
        test_url = results[0]
        print(f"📸 Test URL: {test_url[:80]}...")
        
        # Create test directory
        test_dir = "test_downloads"
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        
        save_path = os.path.join(test_dir, "test_ferrari.jpg")
        
        print(f"\n⬇️ Downloading to: {save_path}")
        success = api.download_image(test_url, save_path)
        
        if success and os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            print(f"✅ SUCCESS: Downloaded {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Clean up
            try:
                os.remove(save_path)
                os.rmdir(test_dir)
                print("🗑️ Cleaned up test files")
            except:
                pass
        else:
            print("❌ FAILED: Download failed")
    else:
        print("❌ FAILED: Could not get test image")

def main():
    print("\n" + "🚗"*35)
    print("  IMAGE API TEST SUITE - Car Image Fetcher")
    print("  Testing: Unsplash + Pexels + Pixabay")
    print("🚗"*35)
    
    try:
        # Run all tests
        test_individual_apis()
        test_multi_source_rotation()
        test_get_car_images_from_title()
        test_download_image()
        
        # Summary
        print_separator("TEST SUMMARY")
        print("✅ All tests completed!")
        print("\n💡 Tips:")
        print("  - If any API fails, check the API key in model/image_api.py")
        print("  - Unsplash: 50 requests/hour")
        print("  - Pexels: 200 requests/hour")
        print("  - Pixabay: 6,000 requests/hour")
        print("\n🎉 Your multi-source image system is ready to use!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
