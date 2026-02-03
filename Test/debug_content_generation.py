#!/usr/bin/env python3
"""
Debug content generation để tìm vấn đề
"""

import sys
import os
sys.path.append('.')

from model.wp_model import BlogPost

def test_content_generation():
    """Test chi tiết quá trình tạo content"""
    print("🔍 Debug Content Generation...")
    
    # Test case 1: Không có raw_content
    print("\n📝 Test 1: Auto-generated content (no raw_content)")
    post1 = BlogPost(
        title="Test Video Post",
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        image_url="",
        raw_content=""  # Empty raw_content
    )
    
    print(f"   Raw content: '{post1.raw_content}'")
    print(f"   Raw content stripped: '{post1.raw_content.strip()}'")
    print(f"   Has raw content: {bool(post1.raw_content and post1.raw_content.strip())}")
    
    content1 = post1.generate_seo_content()
    print(f"   Generated content length: {len(content1)}")
    
    # Tìm video block
    if "youtube" in content1.lower() or "iframe" in content1.lower():
        print("   ✅ Video block found in content")
        
        # Hiển thị video block
        lines = content1.split('\n')
        for i, line in enumerate(lines):
            if 'youtube' in line.lower() or ('iframe' in line.lower() and 'youtube' in line.lower()):
                print(f"   🎬 Video line {i}: {line[:100]}...")
                break
    else:
        print("   ❌ No video block found")
    
    # Test case 2: Có raw_content
    print("\n📝 Test 2: With raw_content")
    post2 = BlogPost(
        title="Test Video Post 2",
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        image_url="",
        raw_content="This is custom content."
    )
    
    print(f"   Raw content: '{post2.raw_content}'")
    print(f"   Has raw content: {bool(post2.raw_content and post2.raw_content.strip())}")
    
    content2 = post2.generate_seo_content()
    print(f"   Generated content length: {len(content2)}")
    print(f"   Content: '{content2}'")
    
    # Test case 3: Raw content empty nhưng có spaces
    print("\n📝 Test 3: Raw content with spaces only")
    post3 = BlogPost(
        title="Test Video Post 3",
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        image_url="",
        raw_content="   "  # Spaces only
    )
    
    print(f"   Raw content: '{post3.raw_content}'")
    print(f"   Raw content stripped: '{post3.raw_content.strip()}'")
    print(f"   Has raw content: {bool(post3.raw_content and post3.raw_content.strip())}")
    
    content3 = post3.generate_seo_content()
    print(f"   Generated content length: {len(content3)}")

def test_video_block_generation():
    """Test riêng phần tạo video block"""
    print("\n🎬 Testing Video Block Generation...")
    
    post = BlogPost(
        title="Video Block Test",
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        image_url="",
        raw_content=""
    )
    
    # Gọi generate_seo_content và debug từng bước
    print("   Calling generate_seo_content()...")
    
    # Simulate the method logic
    if post.raw_content and post.raw_content.strip():
        print("   → Taking raw_content path")
        content = post.raw_content
    else:
        print("   → Taking auto-generation path")
        print(f"   → Video URL: {post.video_url}")
        
        # Test video block generation logic
        video_block = ""
        if post.video_url:
            print(f"   → Processing video URL: {post.video_url}")
            
            if "youtube.com" in post.video_url or "youtu.be" in post.video_url:
                print("   → Detected YouTube URL")
                video_block = f"""
<!-- wp:embed {{"url":"{post.video_url}","type":"video","providerNameSlug":"youtube","responsive":true,"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"}} -->
<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio">
    <div class="wp-block-embed__wrapper">
        {post.video_url}
    </div>
</figure>
<!-- /wp:embed -->"""
                print(f"   → Generated video block: {len(video_block)} chars")
                print(f"   → Video block preview: {video_block[:100]}...")
            else:
                print("   → Not a YouTube URL")
        else:
            print("   → No video URL provided")
        
        # Test full content generation
        full_content = post.generate_seo_content()
        print(f"   → Full content length: {len(full_content)}")
        
        # Check if video block is in full content
        if video_block.strip() and video_block.strip() in full_content:
            print("   ✅ Video block found in full content")
        elif "youtube" in full_content.lower():
            print("   ⚠️ YouTube reference found but not exact video block")
        else:
            print("   ❌ Video block NOT found in full content")

def main():
    """Chạy debug tests"""
    print("🚀 Content Generation Debug")
    print("=" * 40)
    
    test_content_generation()
    test_video_block_generation()
    
    print("\n" + "=" * 40)
    print("🎯 Kết luận:")
    print("- Nếu Test 1 tạo content dài → Logic OK")
    print("- Nếu Test 1 tạo content ngắn → Bug trong generate_seo_content")
    print("- Nếu Test 2 chỉ return raw_content → Logic đúng")
    print("- Kiểm tra video block có được tạo đúng không")

if __name__ == "__main__":
    main()