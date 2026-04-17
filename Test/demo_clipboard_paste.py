#!/usr/bin/env python3
"""
Demo GUI with clipboard paste functionality
"""

import customtkinter as ctk
from PIL import ImageGrab, Image
import os
import time
from tkinter import messagebox

class ClipboardPasteDemo(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("🖼️ Clipboard Paste Demo")
        self.geometry("600x400")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Header
        header = ctk.CTkLabel(self, text="📋 Test Clipboard Paste", font=("Segoe UI", 24, "bold"))
        header.pack(pady=20)
        
        # Instructions
        instructions = ctk.CTkLabel(
            self, 
            text="Hướng dẫn:\n1. Chụp màn hình (PrtScn hoặc Win+Shift+S)\n2. Click vào ô bên dưới\n3. Nhấn Ctrl+V để paste ảnh",
            font=("Segoe UI", 12),
            text_color="gray"
        )
        instructions.pack(pady=10)
        
        # Input frame
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(input_frame, text="Link Ảnh Thumbnail:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # Hint
        hint = ctk.CTkLabel(
            input_frame, 
            text="💡 Nhấn Ctrl+V để paste ảnh từ clipboard!", 
            font=("Segoe UI", 10), 
            text_color="#10b981"
        )
        hint.pack(anchor="w", padx=10, pady=2)
        
        # Entry
        self.entry_image = ctk.CTkEntry(
            input_frame, 
            placeholder_text="Nhấn Ctrl+V để paste ảnh...", 
            height=40
        )
        self.entry_image.pack(fill="x", padx=10, pady=5)
        
        # Bind Ctrl+V
        self.entry_image.bind('<Control-v>', self.paste_image_from_clipboard)
        
        # Log area
        ctk.CTkLabel(self, text="📜 Log:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=30, pady=(10, 5))
        
        self.log_box = ctk.CTkTextbox(self, height=150)
        self.log_box.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        self.log("✅ Sẵn sàng! Hãy chụp màn hình và paste vào ô trên.")
    
    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime("[%H:%M:%S] ")
        self.log_box.insert("end", timestamp + message + "\n")
        self.log_box.see("end")
    
    def paste_image_from_clipboard(self, event=None):
        """Paste image from clipboard and save to thumbnails folder"""
        try:
            self.log("🔍 Đang kiểm tra clipboard...")
            
            # Try to get image from clipboard
            img = ImageGrab.grabclipboard()
            
            if img is None:
                self.log("⚠️ Clipboard không chứa ảnh. Hãy chụp màn hình (PrtScn) trước!")
                return "break"
            
            # Check if it's an image
            if not isinstance(img, Image.Image):
                # Sometimes clipboard contains file paths
                if isinstance(img, list) and len(img) > 0:
                    file_path = img[0]
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp')):
                        self.entry_image.delete(0, "end")
                        self.entry_image.insert(0, file_path)
                        self.log(f"🖼️ Đã paste đường dẫn ảnh: {os.path.basename(file_path)}")
                        return "break"
                
                self.log("⚠️ Clipboard không chứa ảnh hợp lệ!")
                return "break"
            
            # Create thumbnails directory if not exists
            thumbnails_dir = os.path.join(os.getcwd(), "thumbnails")
            os.makedirs(thumbnails_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"pasted_thumb_{timestamp}.png"
            filepath = os.path.join(thumbnails_dir, filename)
            
            # Save image
            img.save(filepath, "PNG")
            
            # Update entry field
            self.entry_image.delete(0, "end")
            self.entry_image.insert(0, filepath)
            
            # Log success
            self.log(f"✅ Đã paste và lưu ảnh: {filename}")
            self.log(f"   📐 Kích thước: {img.width}x{img.height}")
            self.log(f"   📁 Đường dẫn: {filepath}")
            
            return "break"  # Prevent default paste behavior
            
        except Exception as e:
            self.log(f"❌ Lỗi khi paste ảnh: {e}")
            import traceback
            traceback.print_exc()
            return "break"

if __name__ == "__main__":
    app = ClipboardPasteDemo()
    app.mainloop()
