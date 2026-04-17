
import customtkinter as ctk
from tkinter import messagebox
import pyperclip  # Requires: pip install pyperclip (usually available or use root.clipboard_clear/append)
from model.key_storage import KeyStorage

class AdminKeyManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Config ---
        self.title("LVC MEDIA - Quản Lý Key")
        self.geometry("900x600")
        
        # --- Theme ---
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.colors = {
            'primary': '#F59E0B',
            'primary_hover': '#B45309',
            'bg_light': '#FFFBEB',
            'text_main': '#111827'
        }

        # Data Logic
        self.storage = KeyStorage()
        
        # GitHub Auto-Push/Pull
        self.github_auto_push = True  # Set to False to disable

        # UI Layout
        self.create_layout()
        self.refresh_table()
        
        # Async initial pull
        import threading
        threading.Thread(target=self.initial_pull, daemon=True).start()

    def initial_pull(self):
        self.after(0, lambda: self.refresh_btn.configure(text="Đang tải...", state="disabled"))
        self.auto_pull_from_github()
        self.after(0, self.refresh_table)
        self.after(0, lambda: self.refresh_btn.configure(text="🔄 Làm mới (Từ GitHub)", state="normal"))

    def create_layout(self):
        # 1. Header Section
        self.header_frame = ctk.CTkFrame(self, height=80, fg_color="white")
        self.header_frame.pack(fill="x", padx=10, pady=5)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Danh sách key đã kích hoạt", 
            font=("Segoe UI", 20, "bold"),
            text_color=self.colors['primary']
        )
        self.title_label.pack(side="left", padx=20)
        
        self.refresh_btn = ctk.CTkButton(
            self.header_frame,
            text="🔄 Làm mới (Từ GitHub)",
            width=150,
            fg_color="#10B981",
            hover_color="#059669",
            command=self.manual_refresh
        )
        self.refresh_btn.pack(side="right", padx=20)
        
        self.search_entry = ctk.CTkEntry(
            self.header_frame,
            placeholder_text="🔍 Tìm kiếm (Key, Note, IP...)",
            width=250
        )
        self.search_entry.pack(side="right", padx=10)
        self.search_entry.bind("<KeyRelease>", lambda event: self.refresh_table())

        # 2. Action Section (Left Panel)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Left: Generate Form
        self.left_panel = ctk.CTkFrame(self.content_frame, width=250, fg_color="white")
        self.left_panel.pack(side="left", fill="y", padx=(0, 10))

        ctk.CTkLabel(self.left_panel, text="Thêm key mới", font=("Segoe UI", 14, "bold")).pack(pady=15)

        self.note_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Tên khách hàng")
        self.note_entry.pack(pady=(10, 5), padx=15, fill="x")

        self.hwid_entry = ctk.CTkEntry(self.left_panel, placeholder_text="ID máy")
        self.hwid_entry.pack(pady=5, padx=15, fill="x")

        self.qty_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Số lượng (Mặc định: 1)")
        self.qty_entry.pack(pady=5, padx=15, fill="x")

        self.gen_btn = ctk.CTkButton(
            self.left_panel, 
            text="Thêm key", 
            fg_color=self.colors['primary'], 
            hover_color=self.colors['primary_hover'],
            command=self.on_generate
        )
        self.gen_btn.pack(pady=10, padx=15, fill="x")

        # --- Notepad Section ---
        ctk.CTkFrame(self.left_panel, height=2, fg_color="#E5E7EB").pack(fill="x", pady=10, padx=15)
        ctk.CTkLabel(self.left_panel, text="📝 Notepad (Ghi chú nhanh)", font=("Segoe UI", 12, "bold"), text_color=self.colors['primary']).pack(pady=(0, 5))
        self.notepad = ctk.CTkTextbox(self.left_panel, width=220, fg_color="#F9FAFB", border_width=1, border_color="#D1D5DB")
        self.notepad.pack(pady=(0, 15), padx=15, fill="both", expand=True)

        # Right: Key List (Table)
        self.right_panel = ctk.CTkFrame(self.content_frame, fg_color="white")
        self.right_panel.pack(side="right", fill="both", expand=True)

        # Scrollable Frame for items
        self.scroll_frame = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header for Table
        self.build_table_header()

    def build_table_header(self):
        # Header Row inside the scroll frame might be tricky if scrolled. 
        # Better to put header outside.
        pass 

    def refresh_table(self):
        # Clear old widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        keys = self.storage.get_all_keys()
        
        # Apply search filter
        if hasattr(self, 'search_entry'):
            search_query = self.search_entry.get().strip().lower()
            if search_query:
                filtered_keys = []
                for k in keys:
                    if (search_query in k.get('key', '').lower() or
                        search_query in str(k.get('note', '')).lower() or
                        search_query in str(k.get('activated_ip', '')).lower() or
                        search_query in str(k.get('hwid_lock', '')).lower()):
                        filtered_keys.append(k)
                keys = filtered_keys
        
        if not keys:
            ctk.CTkLabel(self.scroll_frame, text="Không có dữ liệu.").pack(pady=20)
            return

        # Header
        h_frame = ctk.CTkFrame(self.scroll_frame, height=40, fg_color="#E5E7EB")
        h_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(h_frame, text="KEY", width=250, anchor="w", font=("Consolas", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(h_frame, text="NOTE", width=120, anchor="w", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(h_frame, text="LOCKED TO", width=110, anchor="w", font=("Segoe UI", 13, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(h_frame, text="IP ADDR", width=120, anchor="w", font=("Segoe UI", 13, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(h_frame, text="DATE", width=140, anchor="w", font=("Segoe UI", 13, "bold")).pack(side="left", padx=5)
        ctk.CTkLabel(h_frame, text="ACTION", width=330, anchor="center", font=("Segoe UI", 12, "bold")).pack(side="right", padx=10)

        # Rows
        for item in keys:
            self.create_row(item)

    def create_row(self, item):
        row = ctk.CTkFrame(self.scroll_frame, height=50, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        # Key
        key_lbl = ctk.CTkEntry(row, width=250, font=("Consolas", 12))
        key_lbl.insert(0, item['key'])
        key_lbl.configure(state="readonly")
        key_lbl.pack(side="left", padx=5)
        
        # Note
        ctk.CTkLabel(row, text=item.get('note', ''), width=120, anchor="w").pack(side="left", padx=5)
        
        # Locked To
        lock_val = item.get('hwid_lock', 'GLOBAL')
        lock_color = "#10B981" if lock_val == "GLOBAL" else "#EF4444"
        ctk.CTkLabel(row, text=lock_val, width=110, anchor="w", text_color=lock_color, font=("Consolas", 13, "bold")).pack(side="left", padx=5)

        # IP
        ip_val = item.get('activated_ip', '---')
        ctk.CTkLabel(row, text=ip_val if ip_val else "---", width=120, anchor="w", font=("Consolas", 12)).pack(side="left", padx=5)

        # Date
        ctk.CTkLabel(row, text=item.get('created_at', ''), width=140, anchor="w", font=("Segoe UI", 12)).pack(side="left", padx=5)
        
        # Actions
        # Pack right-to-left
        del_btn = ctk.CTkButton(
            row, text="XOÁ", width=50, fg_color="#EF4444", hover_color="#DC2626",
            command=lambda k=item['key']: self.on_delete(k)
        )
        del_btn.pack(side="right", padx=(5, 10))

        renew_btn = ctk.CTkButton(
            row, text="GIA HẠN", width=70, fg_color="#3B82F6", hover_color="#2563EB",
            command=lambda k=item['key']: self.on_regenerate(k)
        )
        renew_btn.pack(side="right", padx=5)

        reset_btn = ctk.CTkButton(
            row, text="RS MÁY", width=60, fg_color="#8B5CF6", hover_color="#7C3AED",
            command=lambda k=item['key']: self.on_reset(k)
        )
        reset_btn.pack(side="right", padx=5)

        edit_btn = ctk.CTkButton(
            row, text="SỬA", width=50, fg_color="#F59E0B", hover_color="#D97706",
            command=lambda k=item['key'], n=item.get('note',''), h=item.get('hwid_lock','GLOBAL'): self.on_edit(k, n, h)
        )
        edit_btn.pack(side="right", padx=5)

        copy_btn = ctk.CTkButton(
            row, text="COPY", width=50, fg_color="#10B981", hover_color="#059669",
            command=lambda k=item['key']: self.on_copy(k)
        )
        copy_btn.pack(side="right", padx=5)

    def on_generate(self):
        note = self.note_entry.get().strip()
        hwid = self.hwid_entry.get().strip()
        qty_str = self.qty_entry.get().strip()
        
        qty = 1
        if qty_str.isdigit() and int(qty_str) > 0:
            qty = int(qty_str)
            
        generated_records = []
        for _ in range(qty):
            record = self.storage.create_new_key(note, hwid if hwid else None)
            generated_records.append(record)
        
        self.note_entry.delete(0, 'end')
        self.hwid_entry.delete(0, 'end')
        self.qty_entry.delete(0, 'end')
        self.refresh_table()
        
        if len(generated_records) > 0:
            self.show_generated_keys(generated_records)
            
        import threading
        threading.Thread(target=self.auto_push_to_github, daemon=True).start()

    def show_generated_keys(self, records):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Notepad - Đã tạo {len(records)} key mới")
        dialog.geometry("500x420")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text=f"📝 Bạn có thể ghi chú thêm trước khi Copy (như Notepad):", font=("Segoe UI", 13, "bold"), text_color=self.colors['primary']).pack(pady=15)
        
        textbox = ctk.CTkTextbox(dialog, height=250, font=("Consolas", 12))
        textbox.pack(padx=20, pady=5, fill="both", expand=True)
        
        keys_text = "\n".join([r['key'] for r in records])
        textbox.insert("0.0", keys_text)
        
        def copy_all():
            current_text = textbox.get("0.0", "end-1c")
            self.clipboard_clear()
            self.clipboard_append(current_text)
            self.update()
            dialog.focus_force() # Keep dialog focused 
            # Show info but it might hide behind, keep attributes topmost
            messagebox.showinfo("Đã copy", "Đã copy nội dung Notepad vào clipboard!", parent=dialog)
            
        ctk.CTkButton(
            dialog, 
            text="COPY TẤT CẢ (VÀO CLIPBOARD)", 
            fg_color=self.colors['primary'], 
            hover_color=self.colors['primary_hover'],
            command=copy_all
        ).pack(pady=15)
        
        # Bring to front after a small delay
        dialog.after(100, lambda: dialog.lift())

    def on_copy(self, key):
        self.clipboard_clear()
        self.clipboard_append(key)
        self.update() # Required to keep clipboard after app closes? (Not always, but good practice if short lived)
        messagebox.showinfo("Copied", f"Key copied to clipboard:\n{key}")

    def on_edit(self, key, current_note, current_hwid):
        # Create a small popup for editing
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Key Info")
        dialog.geometry("300x250")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="Edit Note:", anchor="w").pack(pady=(10,0), padx=20, fill="x")
        note_entry = ctk.CTkEntry(dialog)
        note_entry.insert(0, current_note)
        note_entry.pack(pady=5, padx=20, fill="x")
        
        ctk.CTkLabel(dialog, text="Edit HWID (Leave 'GLOBAL' to keep global):", anchor="w").pack(pady=(10,0), padx=20, fill="x")
        hwid_entry = ctk.CTkEntry(dialog)
        hwid_entry.insert(0, current_hwid)
        hwid_entry.pack(pady=5, padx=20, fill="x")
        
        def save():
            new_note = note_entry.get().strip()
            new_hwid = hwid_entry.get().strip()
            if new_hwid == "GLOBAL": new_hwid = None
            
            if self.storage.update_key(key, new_note, new_hwid):
                self.refresh_table()
                dialog.destroy()
                messagebox.showinfo("Updated", "Key info updated successfully!")
                import threading
                threading.Thread(target=self.auto_push_to_github, daemon=True).start()
            else:
                messagebox.showerror("Error", "Failed to update key!")
                
        ctk.CTkButton(dialog, text="SAVE CHANGES", command=save, fg_color=self.colors['primary']).pack(pady=20)

    def on_regenerate(self, key):
        if messagebox.askyesno("Confirm Renew", f"Are you sure you want to RE-GENERATE this key?\n\nThe OLD key will stop working.\nA NEW key will be created for this user."):
            new_key = self.storage.regenerate_key(key)
            if new_key:
                self.refresh_table()
                messagebox.showinfo("Success", f"Key Regenerated!\n\nNew Key:\n{new_key}")
                import threading
                threading.Thread(target=self.auto_push_to_github, daemon=True).start()
            else:
                messagebox.showerror("Error", "Could not find key to regenerate.")

    def on_reset(self, key):
        if messagebox.askyesno("Confirm Reset", "Bạn có chắc chắn muốn reset thiết bị và IP của key này?\nKey sẽ có thể đăng nhập trên máy mới (máy đầu tiên sử dụng)."):
            if hasattr(self.storage, 'reset_key') and self.storage.reset_key(key):
                self.refresh_table()
                messagebox.showinfo("Thành công", "Đã reset thiết bị cho key thành công!")
                import threading
                threading.Thread(target=self.auto_push_to_github, daemon=True).start()
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy key để reset.")

    def on_delete(self, key):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this key record?"):
            self.storage.delete_key(key)
            self.refresh_table()
            import threading
            threading.Thread(target=self.auto_push_to_github, daemon=True).start()
            
    def auto_push_to_github(self):
        """Automatically push license_keys_db.json to GitHub using API"""
        if not self.github_auto_push:
            return
            
        try:
            from model.github_uploader import GitHubUploader
            from model.key_storage import KEYS_DB_FILE
            import github_config
            
            # Check if token is configured
            if github_config.GITHUB_TOKEN == "ghp_YOUR_TOKEN_HERE":
                print("[GITHUB] ⚠️ Chưa cấu hình GitHub token trong github_config.py")
                return False
            
            # Upload using API
            uploader = GitHubUploader(
                github_config.GITHUB_TOKEN,
                github_config.GITHUB_REPO_OWNER,
                github_config.GITHUB_REPO_NAME
            )
            
            success, message = uploader.upload_file(KEYS_DB_FILE, "Cập nhật danh sách license keys")
            
            if success:
                print("[GITHUB] ✅ Đã đồng bộ lên GitHub thành công")
                return True
            else:
                print(f"[GITHUB] ❌ Upload thất bại: {message}")
                return False
            
        except Exception as e:
            print(f"[GITHUB] ⚠️ Lỗi khi đồng bộ: {e}")
            return False

    def auto_pull_from_github(self):
        """Automatically pull license_keys_db.json from GitHub using API"""
        if not self.github_auto_push:
            return False
            
        try:
            from model.github_uploader import GitHubUploader
            from model.key_storage import KEYS_DB_FILE
            import github_config
            
            if github_config.GITHUB_TOKEN == "ghp_YOUR_TOKEN_HERE":
                return False
            
            uploader = GitHubUploader(
                github_config.GITHUB_TOKEN,
                github_config.GITHUB_REPO_OWNER,
                github_config.GITHUB_REPO_NAME
            )
            
            success, message = uploader.download_file(KEYS_DB_FILE)
            if success:
                print(f"[GITHUB] ✅ Đã tải dữ liệu mới nhất từ GitHub")
                # Reload data in memory
                self.storage.load_keys()
                return True
            else:
                print(f"[GITHUB] ❌ Lỗi khi tải dữ liệu: {message}")
                return False
                
        except Exception as e:
            print(f"[GITHUB] ⚠️ Lỗi khi pull dữ liệu: {e}")
            return False

    def manual_refresh(self):
        self.refresh_btn.configure(text="Đang làm mới...", state="disabled")
        
        def pull_worker():
            pulled = self.auto_pull_from_github()
            
            self.after(0, self.refresh_table)
            self.after(0, lambda: self.refresh_btn.configure(text="🔄 Làm mới (Từ GitHub)", state="normal"))
            
            if pulled:
                self.after(0, lambda: messagebox.showinfo("Thành công", "Đã tải dữ liệu mới nhất từ GitHub!"))
            else:
                self.after(0, lambda: messagebox.showwarning("Lỗi", "Không thể tải dữ liệu mới từ GitHub."))
                
        import threading
        threading.Thread(target=pull_worker, daemon=True).start()

if __name__ == "__main__":
    app = AdminKeyManager()
    app.mainloop()
