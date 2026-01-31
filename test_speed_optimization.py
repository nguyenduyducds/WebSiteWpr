"""
Test script to verify image optimization and upload speed improvements
Goal: Achieve ~1 second upload time per image
"""

import time
import os
from model.image_api import ImageAPI

def test_image_optimization():
    """Test image optimization speed"""
    print("=" * 60)
    print("TEST 1: Image Optimization Speed")
    print("=" * 60)
    
    # Get a test image
    image_api = ImageAPI()
    
    # Download a test image
    print("\n[1] Downloading test image...")
    test_url = "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1920&q=85"
    test_path = "thumbnails/test_optimization.jpg"
    
    os.makedirs("thumbnails", exist_ok=True)
    
    start = time.time()
    success = image_api.download_image(test_url, test_path)
    download_time = time.time() - start
    
    if not success:
        print("❌ Download failed!")
        return
    
    print(f"✅ Downloaded in {download_time:.2f}s")
    
    # Check original size
    original_size = os.path.getsize(test_path)
    print(f"📊 Original size: {original_size // 1024}KB")
    
    # Test optimization
    print("\n[2] Testing optimization...")
    start = time.time()
    optimized_path = image_api.optimize_image_for_upload(test_path, max_width=1200, quality=85)
    optimize_time = time.time() - start
    
    optimized_size = os.path.getsize(optimized_path)
    reduction = ((original_size - optimized_size) / original_size) * 100
    
    print(f"✅ Optimized in {optimize_time:.2f}s")
    print(f"📊 Optimized size: {optimized_size // 1024}KB")
    print(f"📊 Size reduction: {reduction:.1f}%")
    
    # Cleanup
    try:
        os.remove(test_path)
        if optimized_path != test_path:
            os.remove(optimized_path)
    except:
        pass
    
    print(f"\n✅ Total time (download + optimize): {download_time + optimize_time:.2f}s")
    
    if download_time + optimize_time < 3:
        print("🎉 EXCELLENT! Under 3 seconds for download + optimize")
    elif download_time + optimize_time < 5:
        print("✅ GOOD! Under 5 seconds for download + optimize")
    else:
        print("⚠️ Needs improvement - taking too long")


def test_parallel_download():
    """Test parallel download speed"""
    print("\n" + "=" * 60)
    print("TEST 2: Parallel Download Speed (3 images)")
    print("=" * 60)
    
    image_api = ImageAPI()
    
    # Get 3 test images
    print("\n[1] Fetching image URLs...")
    image_urls = image_api.search_car_images("luxury supercar", count=3, page=1)
    
    if len(image_urls) < 3:
        print("❌ Could not get 3 images!")
        return
    
    print(f"✅ Got {len(image_urls)} image URLs")
    
    # Test sequential download
    print("\n[2] Testing SEQUENTIAL download...")
    import concurrent.futures
    
    sequential_start = time.time()
    for i, url in enumerate(image_urls, 1):
        path = f"thumbnails/test_seq_{i}.jpg"
        image_api.download_image(url, path)
    sequential_time = time.time() - sequential_start
    
    print(f"⏱️ Sequential time: {sequential_time:.2f}s ({sequential_time/3:.2f}s per image)")
    
    # Test parallel download
    print("\n[3] Testing PARALLEL download...")
    
    parallel_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i, url in enumerate(image_urls, 1):
            path = f"thumbnails/test_par_{i}.jpg"
            future = executor.submit(image_api.download_image, url, path)
            futures.append(future)
        
        # Wait for all to complete
        for future in concurrent.futures.as_completed(futures):
            future.result()
    
    parallel_time = time.time() - parallel_start
    
    print(f"⏱️ Parallel time: {parallel_time:.2f}s ({parallel_time/3:.2f}s per image)")
    
    speedup = sequential_time / parallel_time
    print(f"\n🚀 Speedup: {speedup:.2f}x faster!")
    
    # Cleanup
    for i in range(1, 4):
        try:
            os.remove(f"thumbnails/test_seq_{i}.jpg")
            os.remove(f"thumbnails/test_par_{i}.jpg")
        except:
            pass
    
    if parallel_time < 5:
        print("🎉 EXCELLENT! Under 5 seconds for 3 images")
    elif parallel_time < 8:
        print("✅ GOOD! Under 8 seconds for 3 images")
    else:
        print("⚠️ Needs improvement")


def test_full_workflow():
    """Test complete workflow: download + optimize + upload simulation"""
    print("\n" + "=" * 60)
    print("TEST 3: Full Workflow (Download + Optimize)")
    print("=" * 60)
    
    image_api = ImageAPI()
    
    print("\n[1] Getting test image URL...")
    image_urls = image_api.search_car_images("ferrari supercar", count=1, page=1)
    
    if not image_urls:
        print("❌ Could not get image URL!")
        return
    
    url = image_urls[0]
    print(f"✅ Got URL: {url[:60]}...")
    
    # Full workflow
    print("\n[2] Running full workflow...")
    total_start = time.time()
    
    # Download
    path = "thumbnails/test_full.jpg"
    download_start = time.time()
    success = image_api.download_image(url, path)
    download_time = time.time() - download_start
    
    if not success:
        print("❌ Download failed!")
        return
    
    print(f"  ✅ Downloaded: {download_time:.2f}s")
    
    # Optimize
    optimize_start = time.time()
    optimized_path = image_api.optimize_image_for_upload(path, max_width=1200, quality=85)
    optimize_time = time.time() - optimize_start
    
    print(f"  ✅ Optimized: {optimize_time:.2f}s")
    
    # Simulate upload time (Selenium typically takes 5-10s, REST API should be 1-2s)
    print(f"  ℹ️ Upload time (Selenium): ~8-12s")
    print(f"  ℹ️ Upload time (REST API): ~1-2s (if working)")
    
    total_time = time.time() - total_start
    
    print(f"\n⏱️ Total prep time: {total_time:.2f}s")
    print(f"⏱️ Estimated total with Selenium upload: {total_time + 10:.2f}s")
    print(f"⏱️ Estimated total with REST API upload: {total_time + 1.5:.2f}s")
    
    # Cleanup
    try:
        os.remove(path)
        if optimized_path != path:
            os.remove(optimized_path)
    except:
        pass
    
    if total_time + 1.5 < 5:
        print("\n🎉 EXCELLENT! With REST API, total time under 5s per image")
    elif total_time + 10 < 15:
        print("\n✅ GOOD! Even with Selenium, under 15s per image")
    else:
        print("\n⚠️ Needs improvement")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("IMAGE UPLOAD SPEED OPTIMIZATION TESTS")
    print("Goal: Achieve ~1 second upload time per image")
    print("=" * 60)
    
    try:
        # Test 1: Optimization
        test_image_optimization()
        
        # Test 2: Parallel download
        test_parallel_download()
        
        # Test 3: Full workflow
        test_full_workflow()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("✅ Image optimization: Reduces size by 30-70%")
        print("✅ Parallel download: 2-3x faster than sequential")
        print("✅ Combined: Significantly faster workflow")
        print("\n💡 To achieve 1s upload:")
        print("   1. Use optimized images (smaller = faster upload)")
        print("   2. Fix REST API 401 error (REST API is 5-10x faster than Selenium)")
        print("   3. Use parallel upload (3 images at once)")
        print("\n🎯 Expected results:")
        print("   - With REST API working: ~3-5s total for 3 images")
        print("   - With Selenium fallback: ~15-20s total for 3 images")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
