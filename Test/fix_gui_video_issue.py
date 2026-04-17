#!/usr/bin/env python3
"""
Fix để GUI xử lý video embed đúng cách
"""

# VẤN ĐỀ HIỆN TẠI:
# 1. User nhập video URL vào field "Video URL" 
# 2. User có thể gõ text vào field "Nội dung bài viết (HTML)"
# 3. Controller lấy content từ field đó làm raw_content
# 4. Nếu có raw_content → Tool BỎ QUA video generation
# 5. Kết quả: Chỉ có text, không có video

# GIẢI PHÁP 1: Sửa controller để xử lý đúng
def fixed_process_post(self, data, is_batch=False):
    """
    Fixed version của _process_post trong controller
    """
    try:
        from model.wp_model import BlogPost
        
        # 1. Kiểm tra nếu content chỉ là whitespace → Coi như trống
        content = data.content.strip() if data.content else ""
        
        # 2. Nếu có video URL nhưng content trống → Để auto-generate
        if data.video_url and not content:
            raw_content = ""  # Để trống để auto-generate
        else:
            raw_content = content  # Dùng content user nhập
        
        # 3. Create Post Object
        post = BlogPost(data.title, data.video_url, data.image_url, raw_content)
        post.generate_seo_content()
        
        # ... rest of the method
        
    except Exception as e:
        print(f"Error: {e}")

# GIẢI PHÁP 2: Thêm checkbox "Auto-generate content"
def add_auto_generate_checkbox():
    """
    Thêm checkbox để user chọn auto-generate hay dùng custom content
    """
    # Trong GUI:
    # self.chk_auto_generate = ctk.CTkCheckBox(frm, text="Auto-generate content với video", font=("Segoe UI", 12))
    # self.chk_auto_generate.pack(pady=5, padx=30, anchor="w")
    # self.chk_auto_generate.select()  # Default: checked
    
    # Trong get_post_data():
    # if self.chk_auto_generate.get():
    #     data.content = ""  # Force auto-generate
    # else:
    #     data.content = self.textbox_content.get("1.0", "end")
    pass

print("🎯 HƯỚNG DẪN SỬA LỖI:")
print("1. Để trống field 'Nội dung bài viết (HTML)'")
print("2. Chỉ điền Video URL")
print("3. Tool sẽ tự động tạo content với video")
print()
print("HOẶC:")
print("1. Sửa code controller như trong file này")
print("2. Thêm checkbox auto-generate")