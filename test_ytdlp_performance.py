"""
Test Enhanced YT-DLP với nhiều videos
Để test xem có bị chậm lại sau 200 videos không
"""

from model.enhanced_ytdlp import EnhancedYTDLP
import time

def test_small_batch():
    """Test với batch nhỏ (10 videos)"""
    print("\n" + "="*60)
    print("TEST 1: Small Batch (10 videos)")
    print("="*60 + "\n")
    
    ytdlp = EnhancedYTDLP(
        cookies_file="facebook_cookies.txt",
        max_workers=8,
        request_delay=0.3,
        timeout=20
    )
    
    # Test URLs (thay bằng URLs thật của bạn)
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=9bZkp7q19f0",
        "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
        "https://www.youtube.com/watch?v=fJ9rUzIMcZQ",
        "https://www.youtube.com/watch?v=2Vv-BfVoq4g",
        "https://www.youtube.com/watch?v=60ItHLz5WEA",
        "https://www.youtube.com/watch?v=ZZ5LpwO-An4",
        "https://www.youtube.com/watch?v=hT_nvWreIhg",
        "https://www.youtube.com/watch?v=L_jWHffIx5E",
        "https://www.youtube.com/watch?v=YQHsXMglC9A",
    ]
    
    start = time.time()
    results = ytdlp.batch_get_videos(test_urls)
    elapsed = time.time() - start
    
    success = sum(1 for r in results if r['success'])
    print(f"\n✅ Results: {success}/{len(test_urls)} successful in {elapsed:.1f}s")
    print(f"⏱️ Average: {elapsed/len(test_urls):.2f}s per video")


def test_medium_batch():
    """Test với batch trung bình (50 videos)"""
    print("\n" + "="*60)
    print("TEST 2: Medium Batch (50 videos)")
    print("="*60 + "\n")
    
    ytdlp = EnhancedYTDLP(
        cookies_file="facebook_cookies.txt",
        max_workers=5,
        request_delay=0.5,
        timeout=30
    )
    
    # Đọc URLs từ file (nếu có)
    try:
        with open('test_urls_50.txt', 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()][:50]
    except FileNotFoundError:
        print("⚠️ File test_urls_50.txt không tồn tại, skip test này")
        return
    
    if len(urls) < 10:
        print("⚠️ Cần ít nhất 10 URLs trong file, skip test này")
        return
    
    start = time.time()
    results = ytdlp.batch_get_videos(urls)
    elapsed = time.time() - start
    
    success = sum(1 for r in results if r['success'])
    print(f"\n✅ Results: {success}/{len(urls)} successful in {elapsed:.1f}s")
    print(f"⏱️ Average: {elapsed/len(urls):.2f}s per video")


def test_large_batch_with_batching():
    """Test với batch lớn (200+ videos) - Chia nhỏ thành batches"""
    print("\n" + "="*60)
    print("TEST 3: Large Batch (200+ videos) - With Batching")
    print("="*60 + "\n")
    
    ytdlp = EnhancedYTDLP(
        cookies_file="facebook_cookies.txt",
        max_workers=3,
        request_delay=1.0,
        timeout=45
    )
    
    # Đọc URLs từ file
    try:
        with open('test_urls_200.txt', 'r', encoding='utf-8') as f:
            all_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("⚠️ File test_urls_200.txt không tồn tại, skip test này")
        return
    
    if len(all_urls) < 50:
        print("⚠️ Cần ít nhất 50 URLs trong file, skip test này")
        return
    
    print(f"📊 Total URLs: {len(all_urls)}")
    
    # Chia thành batches 50 videos
    batch_size = 50
    all_results = []
    total_start = time.time()
    
    for i in range(0, len(all_urls), batch_size):
        batch_num = i // batch_size + 1
        batch = all_urls[i:i+batch_size]
        
        print(f"\n{'='*60}")
        print(f"🚀 Processing Batch {batch_num}/{(len(all_urls)-1)//batch_size + 1}")
        print(f"{'='*60}\n")
        
        batch_start = time.time()
        results = ytdlp.batch_get_videos(batch, use_cache=True)
        batch_elapsed = time.time() - batch_start
        
        all_results.extend(results)
        
        success = sum(1 for r in results if r['success'])
        print(f"\n📊 Batch {batch_num}: {success}/{len(batch)} successful in {batch_elapsed:.1f}s")
        
        # Chờ giữa các batch (trừ batch cuối)
        if i + batch_size < len(all_urls):
            wait_time = 30
            print(f"⏸️ Waiting {wait_time}s before next batch...\n")
            time.sleep(wait_time)
    
    total_elapsed = time.time() - total_start
    total_success = sum(1 for r in all_results if r['success'])
    
    print(f"\n{'='*60}")
    print(f"✅ FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Total: {total_success}/{len(all_urls)} successful")
    print(f"Time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} minutes)")
    print(f"Average: {total_elapsed/len(all_urls):.2f}s per video")
    print(f"{'='*60}\n")


def test_cache_performance():
    """Test hiệu suất của cache"""
    print("\n" + "="*60)
    print("TEST 4: Cache Performance")
    print("="*60 + "\n")
    
    ytdlp = EnhancedYTDLP(
        cookies_file="facebook_cookies.txt",
        max_workers=5,
        request_delay=0.5,
        timeout=30
    )
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=9bZkp7q19f0",
        "https://www.youtube.com/watch?v=kJQP7kiw5Fk",
    ]
    
    # First run (no cache)
    print("🔵 First run (no cache):")
    start = time.time()
    results1 = ytdlp.batch_get_videos(test_urls, use_cache=True)
    time1 = time.time() - start
    print(f"⏱️ Time: {time1:.1f}s\n")
    
    # Second run (with cache)
    print("🟢 Second run (with cache):")
    start = time.time()
    results2 = ytdlp.batch_get_videos(test_urls, use_cache=True)
    time2 = time.time() - start
    print(f"⏱️ Time: {time2:.1f}s\n")
    
    speedup = time1 / time2 if time2 > 0 else 0
    print(f"🚀 Speedup: {speedup:.1f}x faster with cache!")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 ENHANCED YT-DLP PERFORMANCE TESTS")
    print("="*60)
    
    # Chạy các tests
    try:
        # Test 1: Small batch (luôn chạy)
        test_small_batch()
        
        # Test 2: Medium batch (nếu có file)
        test_medium_batch()
        
        # Test 3: Large batch (nếu có file)
        test_large_batch_with_batching()
        
        # Test 4: Cache performance
        test_cache_performance()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ TESTS COMPLETE")
    print("="*60 + "\n")
