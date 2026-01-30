#!/usr/bin/env python3
"""
Hướng dẫn sử dụng đúng cách để video embed hoạt động
"""

# ❌ SAI - raw_content có nội dung sẽ bỏ qua video generation
post_wrong = BlogPost(
    title="Test Video",
    video_url="https://youtube.com/watch?v=abc123",
    image_url="",
    raw_content="Nội dung tự viết"  # ← SAI: Sẽ chỉ dùng text này
)

# ✅ ĐÚNG - raw_content trống sẽ auto-generate với video
post_correct = BlogPost(
    title="Test Video", 
    video_url="https://youtube.com/watch?v=abc123",
    image_url="",
    raw_content=""  # ← ĐÚNG: Để trống để auto-generate
)

print("🎯 Cách sử dụng đúng:")
print("1. Để raw_content = '' (trống)")
print("2. Chỉ điền video_url")
print("3. Tool sẽ tự động tạo content + embed video")
print("4. Kiểm tra website có hiển thị video không")