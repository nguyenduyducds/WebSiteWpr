import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
import time
import threading
import os
import webbrowser
from tkinter import messagebox, filedialog
from PIL import ImageGrab, Image, ImageTk
import io

# Giả lập AppData nếu chưa có module model
class AppData:
    """Helper to store current input values."""
    def __init__(self):
        self.site_url = ""
        self.username = ""
        self.password = ""
        self.title = ""
        self.video_url = ""
        self.image_url = ""
        self.content_image = ""  # New: Image to insert in middle of content
        self.content = ""
        self.theme = "supercar"  # Default theme

class GUIView(ctk.CTk):
    def __init__(self, controller, initial_config=None):
        super().__init__()
        self.controller = controller
        self.initial_config = initial_config or {}
        
        # --- Cấu hình màu sắc cho Light Mode ---
        self.colors = {
            'primary': '#2563eb',       # Blue 600
            'primary_hover': '#1d4ed8', # Blue 700
            'success': '#059669',       # Green 600
            'success_hover': '#047857', # Green 700
            'warning': '#d97706',       # Orange 600
            'danger': '#dc2626',        # Red 600
            'bg_light': '#f9fafb',      # Gray 50 - Main background
            'bg_card': '#ffffff',       # White - Cards
            'bg_dark': '#f3f4f6',       # Gray 100 - Darker sections
            'text_primary': '#111827',  # Gray 900 - Main text
            'text_secondary': '#6b7280', # Gray 500 - Secondary text
            'border': '#e5e7eb'         # Gray 200 - Borders
        }
        
        # --- Cấu hình cửa sổ ---
        self.title("🚀 WP Auto Tool - Professional Edition")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Theme - LIGHT MODE mặc định
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        try:
            from version import get_version
            self.app_version = get_version()
        except ImportError:
            self.app_version = "2.0.3"

        # Biến dữ liệu
        self.login_frame = None
        self.main_frame = None
        self.post_queue = [] 
        
        # Initialize Update Checker
        try:
            from model.update_checker import UpdateChecker
            update_url = self.initial_config.get('update_url', "https://raw.githubusercontent.com/nguyenduyducds/WebSiteWpr/master/version.json");
            self.updater = UpdateChecker(self.app_version, update_url)
            self.after(3000, self.check_startup_update) # Check after 3s
        except Exception as e:
            print(f"Update init failed: {e}")
            
        self.content_pool = []
        self.batch_data = None
        self.published_links = []
        self.published_posts = []  # Store {title, link} pairs for copy function
        self.current_link = ""

        # Khởi tạo màn hình
        self.create_login_screen()

    def check_startup_update(self):
        """Check for updates silently on startup"""
        if hasattr(self, 'updater'):
            self.updater.check_for_updates(callback=self.on_update_found)
            
    def on_update_found(self, has_update, new_version, download_url):
        if has_update:
            msg = f"🔥 NGUYỄN DUY ĐỨC THÔNG BÁO:\n\nĐã có bản cập nhật v{new_version} !\n(Bản hiện tại: v{self.app_version})\n\n👉 Bấm OK để cập nhật ngay cho 'ngon' nhé!"
            if messagebox.askyesno("Nguyễn Duy Đức Thông Báo Update", msg):
                if download_url and download_url.endswith(".exe"):
                    # Start auto-update flow
                    self.perform_auto_update(download_url)
                elif download_url:
                    # Fallback for non-exe checks (e.g. zip)
                    webbrowser.open(download_url)
                else:
                    messagebox.showinfo("Thông tin", f"Vui lòng liên hệ Admin để nhận bản cập nhật v{new_version}.")

    def perform_auto_update(self, url):
        """Show progress window and download"""
        # Create Popup
        self.update_window = ctk.CTkToplevel(self)
        self.update_window.title("Đang cập nhật...")
        self.update_window.geometry("400x150")
        self.update_window.attributes("-topmost", True)
        
        ctk.CTkLabel(self.update_window, text="Đang tải bản cập nhật mới...", font=("Segoe UI", 14)).pack(pady=20)
        
        self.progress_bar = ctk.CTkProgressBar(self.update_window, width=300)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        self.lbl_progress = ctk.CTkLabel(self.update_window, text="0%")
        self.lbl_progress.pack(pady=5)
        
        # Start download
        self.updater.download_and_install(
            url, 
            progress_callback=self.on_update_progress,
            completion_callback=self.on_update_complete
        )

    def on_update_progress(self, current, total):
        try:
            percent = current / total
            self.progress_bar.set(percent)
            self.lbl_progress.configure(text=f"{int(percent*100)}%")
            self.update_window.update()
        except: pass

    def on_update_complete(self, success, result):
        if success:
            bat_path = result
            # Run batch file and exit
            try:
                import subprocess, sys
                subprocess.Popen([bat_path], shell=True)
                self.quit()
                sys.exit()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể khởi động lại: {e}")
        else:
            self.update_window.destroy()
            messagebox.showerror("Lỗi Cập Nhật", f"Tải xuống thất bại:\n{result}") 

    # =========================================================================
    # PHẦN 1: LOGIN SCREEN (Giữ nguyên vì đã ổn)
    # =========================================================================
    def create_login_screen(self):
        self.login_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.colors['bg_light'])
        self.login_frame.pack(fill="both", expand=True)

        # Center container with shadow effect
        center_box = ctk.CTkFrame(
            self.login_frame, 
            corner_radius=24, 
            fg_color=self.colors['bg_card'],
            border_width=2,
            border_color=self.colors['border']
        )
        center_box.place(relx=0.5, rely=0.5, anchor="center")

        # Header with gradient-like effect
        header_frame = ctk.CTkFrame(center_box, corner_radius=20, fg_color="transparent")
        header_frame.pack(pady=(40, 10), padx=40)
        
        ctk.CTkLabel(
            header_frame, 
            text="🚀", 
            font=("Segoe UI Emoji", 56)
        ).pack()
        
        ctk.CTkLabel(
            header_frame, 
            text="WordPress Automation", 
            font=("Segoe UI", 28, "bold"), 
            text_color=self.colors['primary']
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            header_frame, 
            text="Đăng nhập để bắt đầu tự động hóa", 
            font=("Segoe UI", 13), 
            text_color=self.colors['text_secondary']
        ).pack()

        # Inputs with better spacing
        input_frame = ctk.CTkFrame(center_box, fg_color="transparent")
        input_frame.pack(pady=20, padx=40, fill="x")
        
        self.entry_site = self.create_modern_input(
            input_frame, 
            "🌍 Site URL", 
            "https://yoursite.com/wp-admin", 
            self.initial_config.get("site_url", "")
        )
        
        self.entry_user = self.create_modern_input(
            input_frame, 
            "👤 Username", 
            "admin", 
            self.initial_config.get("username", "")
        )
        
        self.entry_pass = self.create_modern_input(
            input_frame, 
            "🔒 Password", 
            "••••••••", 
            self.initial_config.get("password", ""), 
            show="*"
        )

        # Checkbox with better styling
        checkbox_frame = ctk.CTkFrame(center_box, fg_color="transparent")
        checkbox_frame.pack(pady=15, padx=40, fill="x")
        
        self.chk_headless = ctk.CTkCheckBox(
            checkbox_frame, 
            text="⚡ Chạy ẩn (Headless Mode - Nhanh hơn)", 
            font=("Segoe UI", 12),
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover']
        )
        self.chk_headless.pack(anchor="w")

        # Button with gradient-like effect
        self.btn_login = ctk.CTkButton(
            center_box, 
            text="🚀 ĐĂNG NHẬP", 
            height=50, 
            width=340, 
            font=("Segoe UI", 15, "bold"),
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover'],
            corner_radius=12,
            command=self.on_login_click
        )
        self.btn_login.pack(pady=20, padx=40)

        self.lbl_status = ctk.CTkLabel(
            center_box, 
            text="", 
            font=("Segoe UI", 11), 
            text_color=self.colors['danger']
        )
        self.lbl_status.pack(pady=(0, 30))

    def create_modern_input(self, parent, label_text, placeholder, initial_value="", show=None):
        # Container for each input
        input_container = ctk.CTkFrame(parent, fg_color="transparent")
        input_container.pack(fill="x", pady=8)
        
        # Label
        ctk.CTkLabel(
            input_container, 
            text=label_text, 
            font=("Segoe UI", 13, "bold"), 
            anchor="w",
            text_color=self.colors['text_primary']
        ).pack(fill="x", pady=(0, 6))
        
        # Entry with better styling
        entry = ctk.CTkEntry(
            input_container, 
            placeholder_text=placeholder, 
            height=45, 
            width=340,
            font=("Segoe UI", 12),
            corner_radius=10,
            border_width=1,
            border_color=self.colors['border'],
            show=show
        )
        entry.pack(fill="x")
        
        if initial_value: 
            try:
                # Use after() to insert value asynchronously to avoid blocking
                self.after(10, lambda e=entry, v=initial_value: self._safe_insert(e, v))
            except Exception as e:
                print(f"[GUI] Error inserting initial value: {e}")
        return entry
    
    def create_form_input(self, parent, label_text, placeholder, initial_value="", show=None, height=45):
        """Create a modern form input with better styling"""
        # Container
        input_container = ctk.CTkFrame(parent, fg_color="transparent")
        input_container.pack(fill="x", pady=10)
        
        # Label
        ctk.CTkLabel(
            input_container, 
            text=label_text, 
            font=("Segoe UI", 13, "bold"), 
            anchor="w",
            text_color=self.colors['text_primary']
        ).pack(fill="x", pady=(0, 8))
        
        # Entry
        entry = ctk.CTkEntry(
            input_container, 
            placeholder_text=placeholder, 
            height=height,
            font=("Segoe UI", 12),
            corner_radius=12,
            border_width=2,
            border_color=self.colors['border'],
            fg_color=self.colors['bg_light'],
            text_color=self.colors['text_primary'],
            placeholder_text_color=self.colors['text_secondary'],
            show=show
        )
        entry.pack(fill="x")
        
        if initial_value:
            self.after(10, lambda e=entry, v=initial_value: self._safe_insert(e, v))
        
        return entry
    
    def create_image_input_section(self, parent):
        """Create image input section with paste support"""
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill="x", pady=10)
        
        # Label
        ctk.CTkLabel(
            section, 
            text="🖼️ Ảnh Thumbnail", 
            font=("Segoe UI", 13, "bold"), 
            anchor="w",
            text_color=self.colors['text_primary']
        ).pack(fill="x", pady=(0, 8))
        
        # Hint
        hint_frame = ctk.CTkFrame(section, fg_color="transparent")
        hint_frame.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(
            hint_frame, 
            text="💡 Tip: Chụp màn hình rồi nhấn Ctrl+V để paste ảnh trực tiếp!", 
            font=("Segoe UI", 11), 
            text_color=self.colors['success'], 
            anchor="w"
        ).pack(side="left")
    
    def _safe_insert(self, entry, value):
        """Safely insert value into entry without blocking"""
        try:
            entry.delete(0, "end")
            entry.insert(0, value)
        except Exception as e:
            print(f"[GUI] Error in safe insert: {e}")
    
    def _handle_title_paste(self, event=None):
        """Handle title paste asynchronously to prevent freeze with Unicode"""
        try:
            # Get clipboard content
            clipboard_text = self.clipboard_get()
            
            # Clear current content
            self.entry_title.delete(0, "end")
            
            # Insert asynchronously to prevent blocking
            self.after(10, lambda: self._safe_insert(self.entry_title, clipboard_text))
            
            # Prevent default paste behavior
            return "break"
        except Exception as e:
            print(f"[GUI] Error handling title paste: {e}")
            # Allow default behavior if our handler fails
            return None

    def on_theme_changed(self, choice):
        """Update theme description when user selects a theme"""
        descriptions = {
            "⚪ Không dùng theme (Raw HTML)": "💡 Không áp dụng CSS, chỉ post HTML thuần như cũ",
            "🏎️ Supercar News (Premium)": "💡 Premium automotive design with luxury styling (English content)",
            "📰 Breaking News": "💡 Modern news layout with breaking badge and trending style",
            "📝 Classic Blog": "💡 Clean and simple blog layout for general content",
            "✨ Minimal Clean": "💡 Ultra simple and elegant design with serif fonts",
            "💻 Tech Modern": "💡 Developer-friendly tech style with code support",
            "📖 Magazine": "💡 Editorial magazine style with drop cap",
            "💼 Business Pro": "💡 Professional business layout for corporate content",
            "🌸 Lifestyle": "💡 Warm and friendly blog style for lifestyle content",
            "🌙 Dark Mode": "💡 Modern dark theme for night reading"
        }
        
        desc = descriptions.get(choice, "")
        if hasattr(self, 'theme_desc_label'):
            self.theme_desc_label.configure(text=desc)
        
        print(f"[GUI] Theme changed to: {choice}")
    
    def get_selected_theme_id(self):
        """Convert theme display name to theme ID"""
        theme_map = {
            "⚪ Không dùng theme (Raw HTML)": "none",
            "🏎️ Supercar News (Premium)": "supercar",
            "📰 Breaking News": "news",
            "📝 Classic Blog": "default",
            "✨ Minimal Clean": "minimal",
            "💻 Tech Modern": "tech",
            "📖 Magazine": "magazine",
            "💼 Business Pro": "business",
            "🌸 Lifestyle": "lifestyle",
            "🌙 Dark Mode": "dark"
        }
        
        selected = self.theme_var.get() if hasattr(self, 'theme_var') else "⚪ Không dùng theme (Raw HTML)"
        return theme_map.get(selected, "none")  # Default to "none" instead of "supercar"

    
    def on_login_click(self):
        site = self.entry_site.get().strip()
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()
        if not all([site, user, pwd]):
            self.lbl_status.configure(text="⚠️ Vui lòng nhập đủ thông tin!")
            return
        
        self.btn_login.configure(state="disabled", text="🔄 Đang kết nối...")
        # Gọi controller (Giả lập)
        if self.controller:
            self.controller.handle_login(site, user, pwd, headless=bool(self.chk_headless.get()))
        else:
            self.after(1000, self.login_success) # Test only

    def login_success(self):
        self.lbl_status.configure(text="✅ Đăng nhập thành công!", text_color=self.colors['success'])
        self.after(500, self.switch_to_main_screen)

    def login_failed(self, message):
        self.lbl_status.configure(text=f"❌ Lỗi: {message}", text_color=self.colors['danger'])
        self.btn_login.configure(state="normal", text="🚀 ĐĂNG NHẬP")

    def switch_to_main_screen(self):
        self.login_frame.destroy()
        self.create_main_screen()

    # =========================================================================
    # PHẦN 2: MAIN SCREEN (Layout đã được làm sạch)
    # =========================================================================
    def create_main_screen(self):
        # Container chính
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Header (Thanh trên cùng)
        self.create_header()

        # 2. Nội dung Tab (Trung tâm)
        self.create_tabs()

        # 3. Status Bar (Thanh trạng thái dưới cùng)
        self.create_status_bar()

    def create_header(self):
        header = ctk.CTkFrame(
            self.main_frame, 
            height=80, 
            corner_radius=16, 
            fg_color=self.colors['bg_card'],
            border_width=2,
            border_color=self.colors['border']
        )
        header.pack(fill="x", pady=(0, 15))
        
        # Logo & Title with better spacing
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=25, pady=15)
        
        ctk.CTkLabel(
            title_frame, 
            text="� WP Auto Tool", 
            font=("Segoe UI", 22, "bold"), 
            text_color=self.colors['primary']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame, 
            text="Professional Automation Dashboard", 
            font=("Segoe UI", 12), 
            text_color=self.colors['text_secondary']
        ).pack(anchor="w", pady=(2, 0))
        
        # Version info
        version_text = f"v{self.app_version}"
        
        ctk.CTkLabel(
            title_frame,
            text=version_text,
            font=("Segoe UI", 10, "bold"),
            text_color=self.colors['primary'],
            fg_color=self.colors['bg_dark'],
            corner_radius=6,
            padx=10,
            pady=4
        ).pack(anchor="w", pady=(5, 0))

        # User Info & Logout with better styling
        user_frame = ctk.CTkFrame(header, fg_color="transparent")
        user_frame.pack(side="right", padx=25, pady=15)
        
        username = self.controller.username if hasattr(self.controller, 'username') else "Admin"
        
        # User badge
        user_badge = ctk.CTkFrame(
            user_frame, 
            fg_color=self.colors['bg_dark'],
            corner_radius=10,
            border_width=1,
            border_color=self.colors['border']
        )
        user_badge.pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(
            user_badge, 
            text=f"👤 {username}", 
            font=("Segoe UI", 13, "bold"),
            text_color=self.colors['text_primary']
        ).pack(padx=15, pady=8)
        
        # Logout button
        ctk.CTkButton(
            user_frame, 
            text="� Đăng Xuất", 
            width=100, 
            height=36, 
            font=("Segoe UI", 12, "bold"),
            fg_color=self.colors['danger'], 
            hover_color="#dc2626",
            corner_radius=10,
            command=self.logout
        ).pack(side="left")
        
        # About/Version button in header
        ctk.CTkButton(
            user_frame,
            text="ℹ️ Thông Tin",
            width=110,
            height=36,
            font=("Segoe UI", 11),
            fg_color=self.colors['bg_dark'],
            hover_color=self.colors['border'],
            text_color=self.colors['text_primary'],
            corner_radius=10,
            command=self.show_about_dialog
        ).pack(side="left", padx=(0, 10))

    def create_tabs(self):
        self.tabview = ctk.CTkTabview(
            self.main_frame, 
            corner_radius=16,
            border_width=2,
            border_color=self.colors['border'],
            fg_color=self.colors['bg_card'],
            segmented_button_fg_color=self.colors['bg_dark'],
            segmented_button_selected_color=self.colors['primary'],
            segmented_button_selected_hover_color=self.colors['primary_hover'],
            segmented_button_unselected_color=self.colors['bg_dark'],
            segmented_button_unselected_hover_color=self.colors['border'],
            text_color=self.colors['text_primary'],
            text_color_disabled=self.colors['text_secondary']
        )
        self.tabview.pack(fill="both", expand=True)

        # Định nghĩa các Tab với icons đẹp hơn
        self.tab_post = self.tabview.add("📝 Đăng Bài")
        self.tab_batch = self.tabview.add("📦 Hàng Chờ") 
        self.tab_upload = self.tabview.add("☁️ Upload")
        self.tab_vimeo = self.tabview.add("🎥 Vimeo")
        self.tab_images = self.tabview.add("🖼️ Ảnh")
        self.tab_data = self.tabview.add("📜 Logs")
        self.tab_settings = self.tabview.add("⚙️ Cài Đặt")

        # Xây dựng nội dung từng Tab
        self.create_post_tab_content()
        self.create_batch_tab_content()
        self.create_upload_tab_content()
        self.create_vimeo_tab_content()
        self.create_images_tab_content()
        self.create_data_tab_content()
        self.create_settings_tab_content()

    def create_status_bar(self):
        self.status_frame = ctk.CTkFrame(
            self.main_frame, 
            height=40, 
            corner_radius=12,
            fg_color=self.colors['bg_card'],
            border_width=2,
            border_color=self.colors['border']
        )
        self.status_frame.pack(fill="x", pady=(15, 0))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="✅ Sẵn sàng", 
            font=("Segoe UI", 12, "bold"), 
            text_color=self.colors['success']
        )
        self.status_label.pack(side="left", padx=20, pady=8)
        
        # Kill Chrome button
        ctk.CTkButton(
            self.status_frame,
            text="🔪 Kill Chrome",
            width=110,
            height=28,
            font=("Segoe UI", 10, "bold"),
            fg_color="#dc2626",
            hover_color="#b91c1c",
            text_color="white",
            corner_radius=8,
            command=self.kill_chrome_processes
        ).pack(side="left", padx=10, pady=8)
        
        # Connection indicator
        connection_frame = ctk.CTkFrame(self.status_frame, fg_color="transparent")
        connection_frame.pack(side="right", padx=20, pady=8)
        
        ctk.CTkLabel(
            connection_frame, 
            text="🟢", 
            font=("Segoe UI", 14)
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(
            connection_frame, 
            text="Connected", 
            font=("Segoe UI", 11), 
            text_color=self.colors['text_secondary']
        ).pack(side="left")

    # =========================================================================
    # TAB 1: ĐĂNG BÀI LẺ (Post Form) - WEB LAYOUT STYLE
    # =========================================================================
    def create_post_tab_content(self):
        container = ctk.CTkScrollableFrame(
            self.tab_post, 
            fg_color="transparent"
        )
        container.pack(fill="both", expand=True, padx=0, pady=0)

        # Header Title
        title_frame = ctk.CTkFrame(container, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(15, 10))
        ctk.CTkLabel(title_frame, text="📝 Soạn Thảo Bài Viết", font=("Segoe UI", 20, "bold")).pack(side="left")
        ctk.CTkLabel(title_frame, text=" | Editor Mode", font=("Segoe UI", 12), text_color="gray").pack(side="left", padx=5, pady=(5,0))

        # === GRID LAYOUT CONTAINER ===
        grid = ctk.CTkFrame(container, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Configure grid weights
        grid.columnconfigure(0, weight=3) # Left column (Main) 70%
        grid.columnconfigure(1, weight=1) # Right column (Sidebar) 30%

        # ================= LEFT COLUMN: MAIN CONTENT =================
        left_col = ctk.CTkFrame(grid, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # 1. Main Info Card
        main_card = ctk.CTkFrame(left_col, fg_color=self.colors['bg_card'], corner_radius=12, border_width=1, border_color=self.colors['border'])
        main_card.pack(fill="both", expand=True, pady=(0, 15))

        # Title Input
        input_container = ctk.CTkFrame(main_card, fg_color="transparent")
        input_container.pack(fill="x", padx=20, pady=20)
        
        self.entry_title = self.create_form_input(
            input_container, 
            "📌 Tiêu đề bài viết", 
            "Nhập tiêu đề hấp dẫn vào đây...",
            height=50
        )
        # Bind paste handlers
        self.entry_title.bind('<Control-v>', self._handle_title_paste)
        
        # Link Video (More space)
        vid_container = ctk.CTkFrame(main_card, fg_color="transparent")
        vid_container.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(vid_container, text="🎬 Link Video / Embed Code", font=("Segoe UI", 13, "bold"), text_color=self.colors['text_primary']).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(vid_container, text="Hỗ trợ nhiều dòng (Facebook, Youtube, Vimeo...)", font=("Segoe UI", 11), text_color="gray").pack(anchor="w", pady=(0, 5))

        self.entry_video = ctk.CTkTextbox(
            vid_container,
            height=120,
            font=("Consolas", 12),
            corner_radius=10,
            border_width=2,
            border_color=self.colors['border'],
            fg_color=self.colors['bg_light'],
            text_color=self.colors['text_primary'],
        )
        self.entry_video.pack(fill="x")
        
        # Content Editor
        content_container = ctk.CTkFrame(main_card, fg_color="transparent")
        content_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        ctk.CTkLabel(content_container, text="📝 Nội dung chi tiết (HTML)", font=("Segoe UI", 13, "bold"), text_color=self.colors['text_primary']).pack(anchor="w", pady=(0, 5))
        
        self.textbox_content = ctk.CTkTextbox(
            content_container, 
            height=250, # Taller for writing
            font=("Segoe UI", 12),
            corner_radius=10,
            border_width=2,
            border_color=self.colors['border']
        )
        self.textbox_content.pack(fill="both", expand=True)

        # Bulk Import Section (Bototm of Left Col)
        bulk_card = ctk.CTkFrame(left_col, fg_color=self.colors['bg_card'], corner_radius=12, border_width=1, border_color=self.colors['border'])
        bulk_card.pack(fill="x", pady=(0, 20))
        
        # Header for Bulk
        ctk.CTkLabel(bulk_card, text="🔌 Công cụ Import Facebook Hàng Loạt", font=("Segoe UI", 14, "bold"), text_color=self.colors['text_primary']).pack(anchor="w", padx=20, pady=15)
        
        bulk_content = ctk.CTkFrame(bulk_card, fg_color="transparent")
        bulk_content.pack(fill="x", padx=20, pady=(0, 20))
        
        # Layout for Bulk: Input Left, Options Right
        self.textbox_fb_links = ctk.CTkTextbox(bulk_content, height=150, font=("Consolas", 11))
        self.textbox_fb_links.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.textbox_fb_links.insert("1.0", "# Paste danh sách link FB vào đây (mỗi dòng 1 link)...\n")
        self.textbox_fb_links.bind("<KeyRelease>", self.update_link_count_display)

        bulk_actions = ctk.CTkFrame(bulk_content, fg_color="transparent")
        bulk_actions.pack(side="right", fill="y")
        
        self.lbl_link_count = ctk.CTkLabel(bulk_actions, text="(0 link)", text_color="#10b981", font=("Segoe UI", 12, "bold"))
        self.lbl_link_count.pack(anchor="e")
        
        self.chk_auto_title_fb = ctk.CTkCheckBox(bulk_actions, text="Auto-Title", font=("Segoe UI", 11))
        self.chk_auto_title_fb.pack(anchor="e", pady=5)
        self.chk_auto_title_fb.select()
        
        self.btn_import_fb = ctk.CTkButton(bulk_actions, text="⚡ Phân Tích & Lấy Embed", 
                                          height=40, width=180,
                                          fg_color="#d97706", hover_color="#b45309",
                                          font=("Segoe UI", 12, "bold"),
                                          command=self.import_fb_bulk)
        self.btn_import_fb.pack(anchor="e", pady=(10, 0))


        # ================= RIGHT COLUMN: SIDEBAR =================
        right_col = ctk.CTkFrame(grid, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(0, 0))
        
        # 1. Action Panel (Sticky Top)
        action_card = ctk.CTkFrame(right_col, fg_color=self.colors['bg_card'], corner_radius=12, border_width=1, border_color=self.colors['border'])
        action_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(action_card, text="🚀 Tác Vụ", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=15)
        
        self.btn_post = ctk.CTkButton(
            action_card, 
            text="ĐĂNG BÀI NGAY", 
            height=45,
            font=("Segoe UI", 13, "bold"),
            fg_color=self.colors['primary'], 
            hover_color=self.colors['primary_hover'],
            command=self.on_post_click
        )
        self.btn_post.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkButton(
            action_card, 
            text="➕ Thêm vào Queue", 
            height=35,
            font=("Segoe UI", 12, "bold"),
            fg_color=self.colors['warning'], 
            hover_color="#d97706", 
            text_color="white",
            command=self.add_to_queue
        ).pack(fill="x", padx=15, pady=(0, 15))

        # 2. Settings Card
        settings_card = ctk.CTkFrame(right_col, fg_color=self.colors['bg_card'], corner_radius=12, border_width=1, border_color=self.colors['border'])
        settings_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(settings_card, text="⚙️ Cấu Hình", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Theme
        ctk.CTkLabel(settings_card, text="Giao diện (Theme):", font=("Segoe UI", 12)).pack(anchor="w", padx=15, pady=(0, 5))
        
        self.theme_var = ctk.StringVar(value="⚪ Không dùng theme (Raw HTML)")
        theme_dropdown = ctk.CTkOptionMenu(
            settings_card,
            values=[ "⚪ Không dùng theme (Raw HTML)", "🏎️ Supercar News (Premium)", "📰 Breaking News", "📝 Classic Blog", "✨ Minimal Clean", "💻 Tech Modern", "📖 Magazine", "💼 Business Pro", "🌸 Lifestyle", "🌙 Dark Mode" ],
            variable=self.theme_var,
            height=35,
            font=("Segoe UI", 11),
            fg_color=self.colors['bg_dark'],
            button_color=self.colors['border'],
            button_hover_color=self.colors['primary'],
            text_color=self.colors['text_primary'],
            dropdown_fg_color=self.colors['bg_card'],
            dropdown_hover_color=self.colors['bg_dark'],
            command=self.on_theme_changed
        )
        theme_dropdown.pack(fill="x", padx=15, pady=(0, 5))
        
        self.theme_desc_label = ctk.CTkLabel(settings_card, text="💡 Basic HTML mode", font=("Segoe UI", 10), text_color="gray", anchor="w", wraplength=250)
        self.theme_desc_label.pack(fill="x", padx=15, pady=(0, 15))

        # 3. Media Card
        media_card = ctk.CTkFrame(right_col, fg_color=self.colors['bg_card'], corner_radius=12, border_width=1, border_color=self.colors['border'])
        media_card.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(media_card, text="🖼️ Media & Ảnh", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Thumbnail
        ctk.CTkLabel(media_card, text="Ảnh Đại Diện (Thumbnail):", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(0, 5))
        
        thumb_row = ctk.CTkFrame(media_card, fg_color="transparent")
        thumb_row.pack(fill="x", padx=15, pady=(0, 15)) 
        
        self.entry_image = ctk.CTkEntry(thumb_row, placeholder_text="URL hoặc Paste...", height=35)
        self.entry_image.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.entry_image.bind('<Control-v>', self.paste_image_from_clipboard)
        
        ctk.CTkButton(thumb_row, text="📂", width=40, height=35, command=self.browse_thumbnail).pack(side="right")
        
        # Content Images
        ctk.CTkLabel(media_card, text="Ảnh Content (Chèn giữa):", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=15, pady=(0, 5))
        
        self.chk_auto_fetch_images = ctk.CTkCheckBox(media_card, text="Tự động lấy ảnh API", font=("Segoe UI", 11), checkbox_height=18, checkbox_width=18)
        self.chk_auto_fetch_images.pack(anchor="w", padx=15, pady=(0, 8))
        
        # Helper to create mini image row
        def create_mini_img_input(parent, placeholder, bind_cmd, browse_cmd):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", padx=15, pady=(0, 8))
            e = ctk.CTkEntry(r, placeholder_text=placeholder, height=30, font=("Segoe UI", 11))
            e.pack(side="left", fill="x", expand=True, padx=(0, 5))
            e.bind('<Control-v>', bind_cmd)
            ctk.CTkButton(r, text="📂", width=35, height=30, command=browse_cmd).pack(side="right")
            return e

        self.entry_content_image = create_mini_img_input(media_card, "Ảnh 1...", lambda e: self.paste_image_from_clipboard_to_field(e, self.entry_content_image, "content1"), self.browse_content_image)
        self.entry_content_image2 = create_mini_img_input(media_card, "Ảnh 2...", lambda e: self.paste_image_from_clipboard_to_field(e, self.entry_content_image2, "content2"), self.browse_content_image2)
        self.entry_content_image3 = create_mini_img_input(media_card, "Ảnh 3...", lambda e: self.paste_image_from_clipboard_to_field(e, self.entry_content_image3, "content3"), self.browse_content_image3)
        
        ctk.CTkLabel(media_card, text="", height=5).pack() # Spacer

        # 4. Result List (Sidebar)
        # Re-using the result list idea but making it compact in sidebar
        res_card = ctk.CTkFrame(right_col, fg_color=self.colors['bg_card'], corner_radius=12, border_width=1, border_color=self.colors['border'])
        res_card.pack(fill="both", expand=True, pady=(0, 10))
        
        head = ctk.CTkFrame(res_card, fg_color="transparent")
        head.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(head, text="📊 Kết quả (Chờ xử lý)", font=("Segoe UI", 14, "bold")).pack(side="left")
        
        self.chk_select_all = ctk.CTkCheckBox(head, text="All", width=50, font=("Segoe UI", 11), command=self.toggle_select_all_results)
        self.chk_select_all.pack(side="right")
        
        ctk.CTkButton(head, text="➕ Thêm vào hàng chờ", 
                     width=140, 
                     height=28,
                     font=("Segoe UI", 11, "bold"),
                     fg_color=self.colors['warning'], 
                     hover_color="#d97706",
                     command=self.add_selected_results_to_queue).pack(side="right", padx=5)
        
        # Use existing name for compatibility
        self.results_scroll = ctk.CTkScrollableFrame(res_card, fg_color="transparent") 
        self.results_scroll.pack(fill="both", expand=True, padx=5, pady=5)


        # Result Area


    # =========================================================================
    # TAB 2: BATCH & QUEUE (Hợp nhất Logic Hàng chờ vào đây)
    # =========================================================================
    def create_batch_tab_content(self):
        # Chia làm 2 cột: Trái (Công cụ Import) - Phải (Danh sách Hàng Chờ)
        grid = ctk.CTkFrame(self.tab_batch, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- LEFT COLUMN: TOOLS ---
        left_col = ctk.CTkFrame(grid, width=350)
        left_col.pack(side="left", fill="both", padx=5, expand=False)
        
        ctk.CTkLabel(left_col, text="📂 Nhập Dữ Liệu", font=("Segoe UI", 14, "bold")).pack(pady=10)
        
        # CSV Section
        ctk.CTkLabel(left_col, text="Nhập từ CSV:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10)
        self.entry_csv = ctk.CTkEntry(left_col, placeholder_text="Chưa chọn file CSV...")
        self.entry_csv.pack(fill="x", padx=10, pady=5)
        
        btn_row_csv = ctk.CTkFrame(left_col, fg_color="transparent")
        btn_row_csv.pack(fill="x", padx=10)
        ctk.CTkButton(btn_row_csv, text="Chọn File", width=80, command=self.browse_csv).pack(side="left", padx=2)
        ctk.CTkButton(btn_row_csv, text="Tải Mẫu", width=80, fg_color="gray", command=self.create_example_csv).pack(side="right", padx=2)

        # TXT Folder Section
        ctk.CTkLabel(left_col, text="Nhập từ Folder TXT:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(20, 0))
        ctk.CTkButton(left_col, text="📂 Chọn Folder TXT", command=self.import_txt_folder).pack(fill="x", padx=10, pady=5)

        # Facebook Tools Section
        ctk.CTkLabel(left_col, text="Công cụ Facebook:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(20, 0))
        ctk.CTkLabel(left_col, text="💡 Nhập nhiều link FB trong tab 'Đăng Bài Lẻ'", 
                    font=("Segoe UI", 10), 
                    text_color="gray",
                    wraplength=300).pack(anchor="w", padx=10, pady=(5, 0))
        ctk.CTkButton(left_col, text="📱 Mở Tab Facebook Import", 
                     fg_color="#1877F2", 
                     command=lambda: self.tabview.set("📝 Đăng Bài Lẻ")).pack(fill="x", padx=10, pady=5)

        # --- RIGHT COLUMN: QUEUE LIST ---
        right_col = ctk.CTkFrame(grid)
        right_col.pack(side="right", fill="both", expand=True, padx=5)

        # Queue Header
        q_header = ctk.CTkFrame(right_col, height=40, fg_color="transparent")
        q_header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(q_header, text="📋 Danh sách Hàng Chờ", font=("Segoe UI", 14, "bold")).pack(side="left")
        self.lbl_queue_count = ctk.CTkLabel(q_header, text="(0 bài)", text_color="gray")
        self.lbl_queue_count.pack(side="left", padx=5)
        
        # Copy All Links button
        ctk.CTkButton(
            q_header, 
            text="📋 Copy Tất Cả Link", 
            width=130, 
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover'],
            command=self.copy_all_links_with_titles
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(q_header, text="🗑️ Xóa All", width=80, fg_color=self.colors['danger'], command=self.clear_queue).pack(side="right")

        # Listbox replacement with Scrollable Frame for Cards
        self.queue_scroll = ctk.CTkScrollableFrame(right_col, label_text="Danh sách Video đang chờ")
        self.queue_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        # self.queue_listbox = ctk.CTkTextbox(right_col, font=("Consolas", 12)) # Removed
        # self.queue_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        # self.queue_listbox.configure(state="disabled")

        # Action Button (Run Batch)
        self.btn_batch_post = ctk.CTkButton(right_col, text="▶️ CHẠY AUTO POST (HÀNG CHỜ)", height=50, 
                                            fg_color=self.colors['success'], 
                                            font=("Segoe UI", 13, "bold"),
                                            state="disabled",
                                            command=self.on_queue_post_click)
        self.btn_batch_post.pack(fill="x", padx=10, pady=10)

    # =========================================================================
    # TAB 3: UPLOAD VIDEO
    # =========================================================================
    def create_upload_tab_content(self):
        container = ctk.CTkFrame(self.tab_upload, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Upload Options
        options_frame = ctk.CTkFrame(container)
        options_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(options_frame, text="Tùy chọn Upload:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.chk_headless_upload = ctk.CTkCheckBox(options_frame, text="🚀 Chạy ẩn (Nhanh hơn)", font=("Segoe UI", 11))
        self.chk_headless_upload.pack(anchor="w", padx=20, pady=2)
        self.chk_headless_upload.select()  # Default to headless for speed
        
        self.chk_auto_add_queue = ctk.CTkCheckBox(options_frame, text="📝 Tự động thêm vào hàng chờ đăng bài", font=("Segoe UI", 11))
        self.chk_auto_add_queue.pack(anchor="w", padx=20, pady=2)
        self.chk_auto_add_queue.select()  # Default to auto-add
        
        # Input Area
        input_frame = ctk.CTkFrame(container)
        input_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(input_frame, text="Chọn Video Upload:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        row = ctk.CTkFrame(input_frame, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=5)
        
        self.entry_upload_path = ctk.CTkEntry(row, placeholder_text="Đường dẫn file video...")
        self.entry_upload_path.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="📂 Chọn File", width=100, command=self.browse_video_upload).pack(side="left", padx=5)
        
        self.btn_upload = ctk.CTkButton(input_frame, text="⬆️ Bắt đầu Upload", fg_color=self.colors['primary'], command=self.on_upload_click)
        self.btn_upload.pack(fill="x", padx=10, pady=10)

        # Upload Log/Result Area
        ctk.CTkLabel(container, text="Kết quả Upload (Link nhúng sẽ hiện ở đây):", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10,0))
        self.txt_upload_list = ctk.CTkTextbox(container, font=("Consolas", 11))
        self.txt_upload_list.pack(fill="both", expand=True, pady=5)

    # =========================================================================
    # TAB 4: VIMEO TOOLS
    # =========================================================================
    def create_vimeo_tab_content(self):
        frm = ctk.CTkFrame(self.tab_vimeo)
        frm.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frm, text="🎥 Công cụ Vimeo", font=("Segoe UI", 16, "bold")).pack(pady=10)
        
        # Cookie Login Test Section
        login_frame = ctk.CTkFrame(frm)
        login_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(login_frame, text="🔐 Test Cookie Login", font=("Segoe UI", 14, "bold")).pack(pady=5)
        
        self.chk_headless_test = ctk.CTkCheckBox(login_frame, text="🚀 Chạy ẩn (Nhanh hơn)", font=("Segoe UI", 11))
        self.chk_headless_test.pack(anchor="w", padx=20, pady=2)
        self.chk_headless_test.select()  # Default to headless
        
        self.btn_test_cookie = ctk.CTkButton(login_frame, text="🍪 Test Cookie Login", 
                                           height=40, fg_color=self.colors['success'], 
                                           command=self.test_vimeo_cookie_login)
        self.btn_test_cookie.pack(fill="x", padx=20, pady=5)
        
        # Account Creation Section
        reg_frame = ctk.CTkFrame(frm)
        reg_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(reg_frame, text="📝 Tạo Tài Khoản Vimeo Hàng Loạt", font=("Segoe UI", 14, "bold")).pack(pady=5)
        
        self.entry_vm_count = self.create_modern_input(reg_frame, "Số lượng tài khoản cần tạo:", "10")
        
        # Vimeo Options
        self.chk_headless_vimeo = ctk.CTkCheckBox(reg_frame, text="🚀 Chạy ẩn (Nhanh hơn)", font=("Segoe UI", 11))
        self.chk_headless_vimeo.pack(anchor="w", padx=30, pady=5)
        self.chk_headless_vimeo.select()  # Default to headless
        
        self.btn_vm_reg = ctk.CTkButton(reg_frame, text="🚀 Bắt đầu Tạo", height=50, 
                                      fg_color=self.colors['warning'], 
                                      command=self.on_vimeo_reg_click)
        self.btn_vm_reg.pack(fill="x", padx=30, pady=20)

        # Account List Section
        list_frame = ctk.CTkFrame(frm)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header_frame, text="📋 Danh sách Tài Khoản", font=("Segoe UI", 14, "bold")).pack(side="left")
        ctk.CTkButton(header_frame, text="🔄 Refresh", width=80, height=25, command=self.refresh_account_list).pack(side="right")
        
        # Scrollable list
        self.acc_scroll = ctk.CTkScrollableFrame(list_frame, label_text="Click 'Login' để mở trình duyệt")
        self.acc_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Initial load
        self.after(500, self.refresh_account_list)

        # Log Section
        ctk.CTkLabel(frm, text="📜 Nhật ký chạy:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=30, pady=(10,0))
        self.txt_vimeo_log = ctk.CTkTextbox(frm, font=("Consolas", 10), height=300)
        self.txt_vimeo_log.pack(fill="both", expand=True, padx=30, pady=10)
        self.txt_vimeo_log.configure(state="disabled")

    def refresh_account_list(self):
        """Read vimeo_accounts.txt and populate the scrollable list"""
        # Clear existing
        try:
            for widget in self.acc_scroll.winfo_children():
                widget.destroy()
        except:
            pass # Widget might not be ready
            
        try:
            if os.path.exists("vimeo_accounts.txt"):
                with open("vimeo_accounts.txt", "r", encoding="utf-8") as f:
                    lines = [l.strip() for l in f.readlines() if l.strip()]
                
                if not lines:
                    ctk.CTkLabel(self.acc_scroll, text="File tài khoản trống").pack(pady=10)
                    return

                for idx, line in enumerate(lines):
                    if "|" in line:
                        parts = line.split("|")
                        if len(parts) >= 2:
                            email = parts[0].strip()
                            pwd = parts[1].strip()
                            
                            row = ctk.CTkFrame(self.acc_scroll)
                            row.pack(fill="x", pady=2, padx=2)
                            
                            # Login Button (Pack FIRST to ensure visibility)
                            btn = ctk.CTkButton(row, text="Login 🚀", width=80, height=24,
                                              fg_color=self.colors['primary'],
                                              command=lambda e=email, p=pwd: self.start_vimeo_session(e, p))
                            btn.pack(side="right", padx=10, pady=2)

                            # Info (Pack SECOND to take remaining space)
                            info_text = f"{idx+1}. {email} | {pwd}"
                            ctk.CTkLabel(row, text=info_text, font=("Consolas", 12), anchor="w").pack(side="left", padx=10, fill="x", expand=True)
            else:
                ctk.CTkLabel(self.acc_scroll, text="Không tìm thấy file vimeo_accounts.txt\nTạo file này với định dạng: email|password").pack(pady=20)
                
        except Exception as e:
            print(f"Error loading accounts: {e}")

    def start_vimeo_session(self, email, pwd):
        """Launch browser and auto-login"""
        import threading
        from model.vimeo_helper import VimeoHelper
        
        if hasattr(self, 'txt_vimeo_log'):
            self.txt_vimeo_log.configure(state="normal")
            self.txt_vimeo_log.insert("end", f"\n[SYSTEM] 🚀 Đang mở trình duyệt cho: {email}...\n")
            self.txt_vimeo_log.see("end")
            self.txt_vimeo_log.configure(state="disabled")
            
        def _run():
            helper = VimeoHelper()
            try:
                helper.login_interactive(email, pwd)
            except Exception as e:
                print(f"Login error: {e}")
                
        # Run in thread so GUI doesn't freeze
        threading.Thread(target=_run, daemon=True).start()

    # =========================================================================
    # TAB 4.5: IMAGE MANAGEMENT (Quản lý ảnh API car)
    # =========================================================================
    def create_images_tab_content(self):
        """Tab to manage car API images - save and delete"""
        container = ctk.CTkScrollableFrame(self.tab_images, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_frame, text="Ảnh Đã Up Lên Web", font=("Segoe UI", 18, "bold")).pack(side="left")
        ctk.CTkButton(header_frame, text="🔄 Làm Mới", width=100, command=self.refresh_image_lists).pack(side="right", padx=5)
        
        # Description
        ctk.CTkLabel(container, 
                    text="💡 Ảnh xe sẽ tự động lưu vào thư viện sau khi upload lên WordPress thành công",
                    font=("Segoe UI", 11),
                    text_color="gray",
                    wraplength=800).pack(anchor="w", pady=(0, 20))
        
        # ===== SECTION: SAVED LIBRARY (Thư viện ảnh xe từ API) =====
        saved_section = ctk.CTkFrame(container)
        saved_section.pack(fill="both", expand=True)
        
        ctk.CTkLabel(saved_section, text=" Thư Viện Ảnh ", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        ctk.CTkLabel(saved_section, 
                    text="Ảnh xe đã upload lên WordPress. Tự động lưu sau mỗi lần đăng bài thành công.",
                    font=("Segoe UI", 10),
                    text_color="gray").pack(anchor="w", padx=20, pady=(0, 10))
        
        # Saved list with scrollbar
        saved_list_frame = ctk.CTkFrame(saved_section)
        saved_list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        self.saved_listbox = tk.Listbox(
            saved_list_frame,
            font=("Consolas", 10),
            bg="#2b2b2b",
            fg="white",
            selectbackground="#10b981",
            height=8
        )
        self.saved_listbox.pack(side="left", fill="both", expand=True)
        
        saved_scrollbar = ctk.CTkScrollbar(saved_list_frame, command=self.saved_listbox.yview)
        saved_scrollbar.pack(side="right", fill="y")
        self.saved_listbox.configure(yscrollcommand=saved_scrollbar.set)
        
        # Saved actions
        saved_actions = ctk.CTkFrame(saved_section, fg_color="transparent")
        saved_actions.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkButton(saved_actions, text="📋 Copy Đường Dẫn", 
                     fg_color=self.colors['primary'], 
                     width=150,
                     command=self.copy_saved_image_path).pack(side="left", padx=5)
        
        ctk.CTkButton(saved_actions, text="🗑️ Xoá Khỏi Thư Viện", 
                     fg_color=self.colors['danger'], 
                     width=150,
                     command=self.delete_selected_saved).pack(side="left", padx=5)
        
        ctk.CTkButton(saved_actions, text="👁️ Xem Ảnh", 
                     fg_color="gray", 
                     width=100,
                     command=self.view_selected_saved).pack(side="left", padx=5)
        
        ctk.CTkButton(saved_actions, text="📂 Mở Thư Mục", 
                     fg_color="gray", 
                     width=120,
                     command=lambda: self.open_folder("saved_car_images")).pack(side="left", padx=5)
        
        self.lbl_saved_count = ctk.CTkLabel(saved_actions, text="(0 ảnh)", text_color="gray")
        self.lbl_saved_count.pack(side="right", padx=10)
        
        # Load initial data
        self.refresh_image_lists()
    
    def refresh_image_lists(self):
        """Refresh saved car images from API"""
        try:
            from model.image_api import ImageAPI
            image_api = ImageAPI()
            
            # Get saved images
            saved_images = image_api.get_saved_images()
            self.saved_listbox.delete(0, tk.END)
            for img_path in saved_images:
                filename = os.path.basename(img_path)
                size_kb = os.path.getsize(img_path) // 1024
                self.saved_listbox.insert(tk.END, f"{filename} ({size_kb} KB)")
            
            self.lbl_saved_count.configure(text=f"({len(saved_images)} ảnh)")
            
            self.log(f"🔄 Đã làm mới thư viện: {len(saved_images)} ảnh xe từ API")
            
        except Exception as e:
            self.log(f"❌ Lỗi làm mới danh sách ảnh: {e}")
    
    
    def delete_selected_saved(self):
        """Delete selected saved image"""
        try:
            selection = self.saved_listbox.curselection()
            if not selection:
                messagebox.showwarning("Chưa chọn ảnh", "Vui lòng chọn ảnh cần xoá!")
                return
            
            # Confirm deletion
            if not messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xoá ảnh này khỏi thư viện?"):
                return
            
            from model.image_api import ImageAPI
            image_api = ImageAPI()
            
            # Get selected image path
            saved_images = image_api.get_saved_images()
            selected_idx = selection[0]
            
            if selected_idx >= len(saved_images):
                messagebox.showerror("Lỗi", "Không tìm thấy ảnh!")
                return
            
            image_path = saved_images[selected_idx]
            
            # Delete image
            if image_api.delete_image(image_path):
                self.log(f"🗑️ Đã xoá ảnh khỏi thư viện: {os.path.basename(image_path)}")
                messagebox.showinfo("Thành công", "Đã xoá ảnh khỏi thư viện!")
                self.refresh_image_lists()
            else:
                messagebox.showerror("Lỗi", "Không thể xoá ảnh!")
                
        except Exception as e:
            self.log(f"❌ Lỗi xoá ảnh: {e}")
            messagebox.showerror("Lỗi", f"Lỗi xoá ảnh: {e}")
    
    
    def view_selected_saved(self):
        """Open selected saved image in default image viewer"""
        try:
            selection = self.saved_listbox.curselection()
            if not selection:
                messagebox.showwarning("Chưa chọn ảnh", "Vui lòng chọn ảnh cần xem!")
                return
            
            from model.image_api import ImageAPI
            image_api = ImageAPI()
            
            saved_images = image_api.get_saved_images()
            selected_idx = selection[0]
            
            if selected_idx >= len(saved_images):
                return
            
            image_path = saved_images[selected_idx]
            
            # Open with default viewer
            import subprocess
            subprocess.Popen(['start', '', image_path], shell=True)
            
        except Exception as e:
            self.log(f"❌ Lỗi mở ảnh: {e}")
    
    def copy_saved_image_path(self):
        """Copy selected saved image path to clipboard"""
        try:
            selection = self.saved_listbox.curselection()
            if not selection:
                messagebox.showwarning("Chưa chọn ảnh", "Vui lòng chọn ảnh!")
                return
            
            from model.image_api import ImageAPI
            image_api = ImageAPI()
            
            saved_images = image_api.get_saved_images()
            selected_idx = selection[0]
            
            if selected_idx >= len(saved_images):
                return
            
            image_path = saved_images[selected_idx]
            
            # Copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(os.path.abspath(image_path))
            
            self.log(f"📋 Đã copy đường dẫn: {image_path}")
            messagebox.showinfo("Thành công", f"Đã copy đường dẫn!\n{os.path.abspath(image_path)}")
            
        except Exception as e:
            self.log(f"❌ Lỗi copy đường dẫn: {e}")
    
    def open_folder(self, folder_name):
        """Open folder in file explorer"""
        try:
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            
            import subprocess
            subprocess.Popen(['explorer', os.path.abspath(folder_name)])
            
        except Exception as e:
            self.log(f"❌ Lỗi mở thư mục: {e}")

    # =========================================================================
    # TAB 5: DATA & LOGS (Thay thế cho Bottom UI cũ)
    # =========================================================================
    def create_data_tab_content(self):
        tabview_logs = ctk.CTkTabview(self.tab_data)
        tabview_logs.pack(fill="both", expand=True, padx=5, pady=5)
        
        tab_sys_log = tabview_logs.add("🖥️ System Log")
        tab_history = tabview_logs.add("✅ Lịch sử Link")
        
        # System Log
        self.textbox_log = ctk.CTkTextbox(tab_sys_log, font=("Consolas", 11))
        self.textbox_log.pack(fill="both", expand=True)
        self.textbox_log.configure(state="disabled")
        
        # History
        hist_toolbar = ctk.CTkFrame(tab_history, height=40)
        hist_toolbar.pack(fill="x", pady=5)
        ctk.CTkButton(hist_toolbar, text="📋 Copy Tất Cả Link", command=self.copy_history_links).pack(side="right", padx=10)
        ctk.CTkButton(hist_toolbar, text="🗑️ Xóa Lịch Sử", command=self.clear_history, fg_color="red").pack(side="right", padx=10)
        
        # Use tkinter Text widget instead of CTkTextbox for better link handling
        import tkinter as tk
        history_frame = ctk.CTkFrame(tab_history)
        history_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.history_textbox = tk.Text(
            history_frame, 
            font=("Segoe UI", 11),
            bg="#2b2b2b",
            fg="white",
            insertbackground="white",
            wrap="word",
            cursor="arrow"
        )
        self.history_textbox.pack(fill="both", expand=True)
        self.history_textbox.configure(state="disabled")
        
        # Configure tag for clickable links
        self.history_textbox.tag_config("link", foreground="#3b82f6", underline=True)
        self.history_textbox.tag_bind("link", "<Button-1>", self._on_link_click)
        self.history_textbox.tag_bind("link", "<Enter>", lambda e: self.history_textbox.config(cursor="hand2"))
        self.history_textbox.tag_bind("link", "<Leave>", lambda e: self.history_textbox.config(cursor="arrow"))

    # Method removed (using the one defined later which correctly clears self.published_links)

    # =========================================================================
    # TAB 6: SETTINGS
    # =========================================================================
    def create_settings_tab_content(self):
        frm = ctk.CTkFrame(self.tab_settings)
        frm.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- UI Settings ---
        ctk.CTkLabel(frm, text="Cài đặt giao diện", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=10)
        ctk.CTkOptionMenu(frm, values=["Dark", "Light", "System"], command=lambda v: ctk.set_appearance_mode(v)).pack(padx=20, anchor="w")
        
        # --- Facebook Cookie Settings ---
        ctk.CTkLabel(frm, text="Facebook Cookies (Fix lỗi Reel/Video)", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(30, 10))
        
        cookie_frame = ctk.CTkFrame(frm, fg_color="transparent")
        cookie_frame.pack(anchor="w", padx=20, fill="x")
        
        # Status Label
        self.lbl_fb_cookie_status = ctk.CTkLabel(cookie_frame, text="Checking...", font=("Segoe UI", 12))
        self.lbl_fb_cookie_status.pack(side="left", padx=(0, 15))
        
        # Import Button
        ctk.CTkButton(
            cookie_frame, 
            text="📂 Chọn File Cookie (.txt)", 
            command=self.browse_fb_cookie,
            fg_color="#3b82f6",
            width=150
        ).pack(side="left")
        
        # Paste Button (NEW)
        ctk.CTkButton(
            cookie_frame, 
            text="📋 Paste từ Clipboard", 
            command=self.paste_fb_cookie_from_clipboard,
            fg_color="#8b5cf6", # Purple
            width=150
        ).pack(side="left", padx=10)
        
        # Help Text
        ctk.CTkLabel(
            frm, 
            text="💡 Hướng dẫn: Dùng extension 'Get cookies.txt LOCALLY' -> Copy -> Bấm nút Paste ở trên.",
            text_color="gray",
            font=("Segoe UI", 11)
        ).pack(anchor="w", padx=20, pady=5)
        
        # Initial check
        self.check_fb_cookie_status()
        
        ctk.CTkLabel(frm, text="Thông tin phiên bản: v2.0 Refactored", text_color="gray").pack(side="bottom", pady=20)

    def check_fb_cookie_status(self):
        if hasattr(self, 'lbl_fb_cookie_status'):
             if os.path.exists("facebook_cookies.txt"):
                 self.lbl_fb_cookie_status.configure(text="✅ Đã có cookie", text_color="#4ade80") # Green
             else:
                 self.lbl_fb_cookie_status.configure(text="❌ Chưa có cookie", text_color="#ef4444") # Red

    def browse_fb_cookie(self):
        filename = filedialog.askopenfilename(title="Chọn file cookie Facebook", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            try:
                import shutil
                shutil.copy2(filename, "facebook_cookies.txt")
                self.log(f"✅ Đã import cookie từ: {os.path.basename(filename)}")
                self.check_fb_cookie_status()
                messagebox.showinfo("Thành công", "Đã nạp Facebook Cookie thành công!")
            except Exception as e:
                self.log(f"❌ Lỗi copy cookie: {e}")
                
    def paste_fb_cookie_from_clipboard(self):
        try:
            content = self.clipboard_get()
            if not content or len(content) < 10:
                messagebox.showwarning("Clipboard Trống", "Vui lòng copy nội dung cookie trước!")
                return
            
            # Simple check for netscape format
            if ".facebook.com" not in content and "c_user" not in content:
                res = messagebox.askyesno("Cảnh báo", "Nội dung không giống cookie Facebook. Bạn có chắc muốn lưu?")
                if not res: return
                
            with open("facebook_cookies.txt", "w", encoding="utf-8") as f:
                f.write(content)
                
            self.check_fb_cookie_status()
            self.log("✅ Đã paste cookie từ clipboard.")
            messagebox.showinfo("Thành công", "Đã lưu nội dung cookie!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lấy nội dung clipboard: {e}")

    # =========================================================================
    # LOGIC HELPERS & EVENT HANDLERS
    # =========================================================================

    def log(self, message):
        """Unified logging method"""
        # 1. Update Log tab
        if hasattr(self, 'textbox_log'):
            self.textbox_log.configure(state="normal")
            timestamp = time.strftime("[%H:%M:%S] ")
            self.textbox_log.insert("end", timestamp + str(message) + "\n")
            self.textbox_log.see("end")
            self.textbox_log.configure(state="disabled")
        
        # 2. Update Status Bar (short msg)
        if hasattr(self, 'status_label'):
            short_msg = str(message).split('\n')[0][:50]
            self.status_label.configure(text=short_msg)
            
        print(message) # Console fallback

    def browse_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            self.entry_csv.delete(0, "end")
            self.entry_csv.insert(0, path)
            # Load data logic here
            try:
                from model.batch_helper import BatchPostData
                self.batch_data = BatchPostData(path)
                self.log(f"Đã load {self.batch_data.total_posts()} bài từ CSV.")
                self.btn_batch_post.configure(state="normal")
            except:
                self.log("Lỗi load CSV (Giả lập: File OK)")
                self.btn_batch_post.configure(state="normal")

    def create_example_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="mau_bai_viet.csv")
        if path:
            with open(path, "w", encoding="utf-8-sig") as f:
                f.write("title,video_url,image_url,content\nBai 1,http://video,,Noi dung 1")
            self.log(f"Đã tạo file mẫu: {path}")

    def import_txt_folder(self):
        """Import content from TXT files to be used as body content for video posts"""
        folder = filedialog.askdirectory(title="Chọn folder chứa file TXT (nội dung body)")
        if not folder: 
            return
        
        try:
            # Get all .txt files
            files = [f for f in os.listdir(folder) if f.endswith(".txt")]
            
            if not files:
                self.log("❌ Không tìm thấy file .txt nào trong folder!")
                return
            
            # Store content in a pool for later use
            if not hasattr(self, 'content_pool'):
                self.content_pool = []
            
            imported_count = 0
            for filename in files:
                try:
                    file_path = os.path.join(folder, filename)
                    
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    # Skip empty files
                    if not content:
                        self.log(f"⚠️ Bỏ qua file trống: {filename}")
                        continue
                    
                    # Add to content pool WITH file path for later deletion
                    self.content_pool.append({
                        'filename': filename,
                        'filepath': file_path,  # Store full path for deletion
                        'content': content
                    })
                    
                    imported_count += 1
                    self.log(f"✅ Đã đọc: {filename} ({len(content)} ký tự)")
                    
                except Exception as e:
                    self.log(f"❌ Lỗi đọc file {filename}: {e}")
                    continue
            
            self.log(f"🎉 Đã load {imported_count} file nội dung vào bộ nhớ.")
            self.log(f"💡 Tip: Upload video để tự động ghép với nội dung này!")
            
        except Exception as e:
            self.log(f"❌ Lỗi import folder: {e}")

    def add_result_card(self, idx, title, embed_code, image_url, analysis_text):
        """Add a result card to the scrollable list"""
        try:
            # Card Frame
            card = ctk.CTkFrame(self.results_scroll, fg_color="#2b2b2b", corner_radius=8, border_width=1, border_color="#404040")
            card.pack(fill="x", pady=5, padx=5)
            
            # STORE DATA ON CARD FOR BULK ACTIONS
            card.data = {
                'title': title,
                'embed_code': embed_code,
                'image_url': image_url
            }
            
            # Checkbox (Left)
            card.checkbox = ctk.CTkCheckBox(card, text="", width=24, checkbox_width=20, checkbox_height=20)
            card.checkbox.pack(side="left", padx=(10, 0))
            # Auto-select if face detected (Optional smart feature? maybe just leave unchecked)
            # card.checkbox.select() 
            
            # --- Layout: Image Left, Info Right ---
            # Image Placeholder/Canvas
            img_frame = ctk.CTkFrame(card, width=100, height=100, fg_color="#1a1a1a")
            img_frame.pack(side="left", padx=5, pady=5)
            img_frame.pack_propagate(False) # Fixed size
            
            # Load Image
            if image_url and os.path.exists(image_url):
                 try:
                    from PIL import Image, ImageTk
                    pil_img = Image.open(image_url)
                    pil_img.thumbnail((100, 100))
                    ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                    ctk.CTkLabel(img_frame, text="", image=ctk_img).pack(expand=True)
                 except:
                    ctk.CTkLabel(img_frame, text="No Image").pack(expand=True)
            else:
                 ctk.CTkLabel(img_frame, text="No Image").pack(expand=True)

            # Info Frame
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
            
            # Title
            ctk.CTkLabel(info_frame, text=f"{idx}. {title}", font=("Segoe UI", 12, "bold"), text_color="white", anchor="w").pack(fill="x")
            
            # AI Analysis Result
            ai_color = "#9ca3af" # default light gray for neutral/error
            if "Phát hiện" in analysis_text or "Face Detected" in analysis_text: ai_color = "#4ade80" # Screen Green (Brighter)
            elif "No Image" in analysis_text or "Failed" in analysis_text: ai_color = "#ef4444" # Red for obvious error
            
            ctk.CTkLabel(info_frame, text=f"🧠 AI: {analysis_text}", font=("Segoe UI", 11), text_color=ai_color, anchor="w").pack(fill="x")
            
            # Embed Code (Entry for easy copying)
            embed_entry = ctk.CTkEntry(info_frame, font=("Consolas", 10), height=25, text_color="white", fg_color="#374151")
            embed_entry.pack(fill="x", pady=2)
            embed_entry.insert(0, embed_code)
            
            # Add to Queue Button
            ctk.CTkButton(info_frame, text="⬇ Thêm vào Queue", 
                         width=100, height=24, 
                         fg_color="#3b82f6", font=("Segoe UI", 10),
                         command=lambda c=card: self.add_single_result_to_queue(c)).pack(anchor="e", pady=2)
            
        except Exception as e:
            print(f"Error adding card: {e}")

    def toggle_select_all_results(self):
        """Select or deselect all cards"""
        state = self.chk_select_all.get()
        for widget in self.results_scroll.winfo_children():
            if hasattr(widget, 'checkbox'):
                if state: widget.checkbox.select()
                else: widget.checkbox.deselect()

    def add_single_result_to_queue(self, card):
        """Add a single card's data to the queue"""
        try:
            data = card.data
            # Create post data
            post_data = {
                'title': data['title'],
                'video_url': data['embed_code'],
                'image_url': data['image_url'],
                'content': '',
                'needs_body_content': True,
                'theme': self.get_selected_theme_id()
            }
            self.post_queue.append(post_data)
            self.update_queue_display()
            self.log(f"✅ Đã thêm '{data['title']}' vào hàng chờ.")
        except Exception as e:
            self.log(f"❌ Lỗi thêm bài: {e}")

    def add_selected_results_to_queue(self):
        """Add all checked cards to queue"""
        added_count = 0
        for widget in self.results_scroll.winfo_children():
            if hasattr(widget, 'checkbox') and widget.checkbox.get() == 1:
                self.add_single_result_to_queue(widget)
                added_count += 1
        
        if added_count > 0:
            self.log(f"🎉 Đã thêm {added_count} video đã chọn vào hàng chờ!")
        else:
            self.log("⚠️ Chưa chọn video nào!")

    def update_link_count_display(self, event=None):
        """Update the link count label based on textbox content"""
        try:
            if not hasattr(self, 'textbox_fb_links') or not hasattr(self, 'lbl_link_count'):
                return
                
            text = self.textbox_fb_links.get("1.0", "end").strip()
            if not text:
                count = 0
            else:
                lines = text.split('\n')
                # Count non-empty non-comment lines
                count = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
            
            self.lbl_link_count.configure(text=f"({count} link)")
        except:
            pass

    def import_fb_bulk(self):
        """Import multiple video links, generate embeds, and SHOW RESULT in List"""
        try:
            # Get text from textbox
            fb_text = self.textbox_fb_links.get("1.0", "end").strip()
            
            if not fb_text:
                self.log("❌ Chưa nhập link Video nào!")
                return
            
            # Split by lines and filter out comments and empty lines
            lines = fb_text.split('\n')
            video_links = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'): continue
                if any(domain in line for domain in ['facebook.com', 'fb.watch', 'vimeo.com', 'youtube.com', 'youtu.be']):
                    video_links.append(line)
            
            if not video_links:
                self.log("❌ Không tìm thấy link Video hợp lệ!")
                return
            
            self.log(f"📱 Bắt đầu xử lý {len(video_links)} link Video (AI Analysis)...")
            self.btn_import_fb.configure(state="disabled", text="⏳ Đang phân tích...")
            
            # Clear previous results in scrollable frame
            for widget in self.results_scroll.winfo_children():
                widget.destroy()
            
            # Process in thread
            import threading
            import requests 
            from bs4 import BeautifulSoup
            import cv2
            import numpy as np
            import urllib.request

            def _get_meta(url):
                title = None
                img_url = None
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    resp = requests.get(url, headers=headers, timeout=5)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        # Title
                        og_title = soup.find("meta", property="og:title")
                        if og_title: title = og_title.get("content")
                        if not title and soup.title: title = soup.title.string
                        # Image
                        og_image = soup.find("meta", property="og:image")
                        if og_image: img_url = og_image.get("content")
                except: pass
                return title, img_url
            
            def _analyze_face(img_path):
                try:
                    # Import here to avoid global crash if missing
                    try:
                        import cv2
                        import numpy as np
                    except ImportError:
                        return "OpenCV Missing"

                    # Check file exists
                    if not os.path.exists(img_path):
                        return "Image Missing"

                    # Load Haar Cascade (Fastest)
                    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    
                    # Read image with error handling (supports unicode paths better via frombuffer if needed, but imread is default)
                    # Use standard imread for now
                    img = cv2.imread(img_path)
                    
                    if img is None:
                        return "Read Error"
                        
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    
                    if len(faces) > 0:
                        return f"Face Detected ({len(faces)})"
                    return "No Face"
                    
                except Exception as e:
                    return f"Analysis Error: {str(e)[:20]}"

            def _process_links():
                processed_count = 0
                shared_driver = None
                
                # Check for FB links to init One Shared Driver
                has_fb = any(('facebook.com' in x or 'fb.watch' in x) for x in video_links)
                
                if has_fb:
                    try:
                        self.log("🚀 Đang khởi động trình duyệt ẩn danh (Shared) để quét Facebook...")
                        import undetected_chromedriver as uc
                        options = uc.ChromeOptions()
                        
                        # Re-enable Headless to avoid annoying popups
                        options.add_argument("--headless=new") 
                        
                        # Use Mobile User Agent
                        options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1')
                        
                        options.add_argument("--disable-gpu")
                        options.add_argument("--mute-audio")
                        options.add_argument("--window-size=375,812") # Mobile dimensions
                        
                        chrome_path = os.path.join(os.getcwd(), "chrome_portable", "chrome.exe")
                        if os.path.exists(chrome_path): options.binary_location = chrome_path
                        
                        shared_driver = uc.Chrome(options=options, version_main=None)
                        shared_driver.set_page_load_timeout(45)
                    except Exception as e:
                        print(f"Failed to init shared driver: {e}")

                try:
                    for idx, link in enumerate(video_links):
                        try:
                            title = None
                            img_remote = None
                            video_url_final = link
                            platform = "Video"

                            # 1. FACEBOOK
                            if 'facebook.com' in link or 'fb.watch' in link:
                                platform = "Facebook"
                                self.after(0, lambda i=idx: self.log(f"   🔍 [{i+1}] FB: Đang lấy dữ liệu..."))
                                
                                # Use shared driver!
                                title = self.get_facebook_title(link, driver=shared_driver)
                                
                                # Get Image (Prefer cached from get_facebook_title, fallback to _get_meta)
                                img_remote = None
                                if hasattr(self, '_last_fb_image') and self._last_fb_image:
                                    img_remote = self._last_fb_image
                                else:
                                    _, img_remote = _get_meta(link)
                                
                                # Convert to embed (Iframe)
                                video_url_final = self.create_facebook_embed(link, use_sdk=False)
                            
                            # 2. YOUTUBE
                            elif 'youtube.com' in link or 'youtu.be' in link:
                                platform = "YouTube"
                                self.after(0, lambda i=idx: self.log(f"   🔍 [{i+1}] YT: Đang lấy dữ liệu..."))
                                
                                # Get ID
                                import re
                                vid_id = None
                                if 'youtu.be' in link:
                                    match = re.search(r'youtu\.be/([\w-]+)', link)
                                    if match: vid_id = match.group(1)
                                else:
                                    match = re.search(r'v=([\w-]+)', link)
                                    if match: vid_id = match.group(1)
                                
                                if vid_id:
                                    # Embed Code
                                    video_url_final = f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{vid_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
                                    
                                    # Thumbnail (High Quality)
                                    img_remote = f"https://img.youtube.com/vi/{vid_id}/maxresdefault.jpg"
                                    
                                    # Title via oEmbed
                                    try:
                                        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid_id}&format=json"
                                        res = requests.get(oembed_url, timeout=3)
                                        if res.status_code == 200:
                                            title = res.json().get('title')
                                    except: pass
                                
                                if not title:
                                    title, _ = _get_meta(link) # Fallback

                            # 3. VIMEO
                            elif 'vimeo.com' in link:
                                platform = "Vimeo"
                                self.after(0, lambda i=idx: self.log(f"   🔍 [{i+1}] Vimeo: Đang lấy dữ liệu..."))
                                
                                # Convert to Player URL / Embed
                                # Default to keeping it as is, but we will try to make it an embed if possible
                                video_url_final = link 
                                
                                # Extract ID
                                import re
                                vid_id = None
                                match = re.search(r'vimeo\.com/(\d+)', link)
                                if match:
                                    vid_id = match.group(1)
                                    # Use helper function for proper aspect ratio
                                    video_url_final = self.create_vimeo_embed(vid_id, title or "Vimeo Video")
                                    
                                    # Fetch oEmbed Title
                                    try:
                                        oembed_url = f"https://vimeo.com/api/oembed.json?url=https://vimeo.com/{vid_id}"
                                        res = requests.get(oembed_url, timeout=3)
                                        if res.status_code == 200:
                                            data = res.json()
                                            title = data.get('title')
                                            img_remote = data.get('thumbnail_url')
                                    except: pass
                                
                                if not title:
                                    title, img_remote_meta = _get_meta(link)
                                    if not img_remote: img_remote = img_remote_meta

                            # 4. OTHERS
                            else:
                                self.after(0, lambda i=idx: self.log(f"   🔍 [{i+1}] Đang lấy dữ liệu..."))
                                title, img_remote = _get_meta(link)
                                video_url_final = link

                            if not title: title = f"Video {idx+1}"

                            # Download Image for Analysis
                            local_img_path = None
                            analysis_result = "No Image"
                            
                            if img_remote:
                                try:
                                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                                    if not os.path.exists("temp_analysis"): os.makedirs("temp_analysis")
                                    local_img_path = f"temp_analysis/thumb_{timestamp}_{idx}.jpg"
                                    urllib.request.urlretrieve(img_remote, local_img_path)
                                    
                                    # Analyze
                                    analysis_result = _analyze_face(local_img_path)
                                except:
                                    analysis_result = "Download Failed"

                            # Add card to UI
                            self.after(0, lambda i=idx+1, t=title, e=video_url_final, img=local_img_path, a=analysis_result: 
                                       self.add_result_card(i, t, e, img, a))
                            
                            processed_count += 1
                            
                        except Exception as e:
                            print(e)
                            continue
                finally:
                    # Clean up shared driver
                    if shared_driver:
                        try:
                            shared_driver.quit()
                        except: pass
                
                self.after(0, lambda: self.log(f"🏁 Hoàn tất phân tích {processed_count} link."))
                self.after(0, lambda: self.btn_import_fb.configure(state="normal", text="🚀 Phân Tích & Lấy Embed"))


            # Start thread
            threading.Thread(target=_process_links, daemon=True).start()

        except Exception as e:
            self.log(f"❌ Lỗi xử lý: {e}")
            self.btn_import_fb.configure(state="normal", text="🚀 Phân Tích & Lấy Embed")

    def get_facebook_title(self, fb_url, driver=None):
        """Get title from Facebook video page using undetected_chromedriver to bypass detection"""
        fetched_title = None
        self._last_fb_image = None # Reset image cache
        
        # --- Method 1: Try yt-dlp Dictionary / Library (Python Native) ---
        # Đây là cách TỐT NHẤT & CHUẨN NHẤT như bạn yêu cầu 
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'simulate': True,
                'extract_flat': False,
                'noplaylist': True,
                'ignoreerrors': True,
                # FIX CHÍNH: Dùng 'chrome' để auto-pick version mới nhất khớp với curl-cffi
                'impersonate': 'chrome', 
                'extractor_args': {'facebook': {'impersonate': 'chrome'}},
            }
            
            # --- COOKIE SUPPORT (Tính năng mới) ---
            # Nếu có file facebook_cookies.txt, load vào để đăng nhập & lấy tin chuẩn 100%
            cookie_path = "facebook_cookies.txt"
            if os.path.exists(cookie_path):
                ydl_opts['cookiefile'] = cookie_path
                print(f"[FB] 🍪 Đã tìm thấy facebook_cookies.txt -> Đang sử dụng cookie!")
            else:
                print(f"[FB] ℹ️ Không thấy facebook_cookies.txt -> Chạy chế độ Guest (có thể bị hạn chế)")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Tải metadata
                info = ydl.extract_info(fb_url, download=False)
                
                # Trích xuất thông tin (info có thể None nếu lỗi)
                if info:
                    title = info.get('title')
                    if title:
                        fetched_title = title.strip()
                        self._last_fb_image = info.get('thumbnail')
                        print(f"[FB] yt_dlp Lib extracted: {fetched_title[:50]}...")
                        return fetched_title

        except ImportError:
            print("[FB] Python module 'yt_dlp' lỗi import.")
        except Exception as e:
            # Lỗi này thường do FB đổi cấu trúc, không sao cả -> fallback
            print(f"[FB] yt-dlp chưa support video này, đang chuyển sang chạy Browser... ({e})")

        # --- Method 1.5: Try yt-dlp Subprocess (Fallback nếu không import được lib) ---
        try:
            import subprocess
            import json
            
            cmd = ['yt-dlp', '--dump-json', '--no-download', '--no-warnings', '--quiet', fb_url]
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, startupinfo=startupinfo)
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                title = data.get('title') or data.get('fulltitle')
                if title and title.strip():
                    fetched_title = title.strip()
                    self._last_fb_image = data.get('thumbnail') 
                    print(f"[FB] yt-dlp.exe extracted: {fetched_title[:50]}...")
                    return fetched_title
        except: pass
        
        # --- Method 2: Requests (Only if no driver provided) ---
        if not driver:
            try:
                import requests
                from bs4 import BeautifulSoup
                
                headers = {
                    'User-Agent': 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
                
                response = requests.get(fb_url, headers=headers, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    t = None
                    og_title = soup.find('meta', property='og:title')
                    if og_title: t = og_title.get('content')
                    
                    invalid_titles = ['facebook', 'watch', 'video', 'log into facebook', 'login', 'log in', 
                                     'this page isn', 'content not found', 'unavailable', 'facebook video']
                    
                    if t:
                        is_invalid = any(inv in t.lower() for inv in invalid_titles)
                        if not is_invalid:
                            fetched_title = t.strip()
                            og_image = soup.find('meta', property='og:image')
                            if og_image: self._last_fb_image = og_image.get('content')
            except: pass

        # --- Method 2: undetected_chromedriver (Fallback Mạnh Mẽ) ---
        invalid_titles = ["facebook video", "facebook", "log into facebook", "log in", "login", "watch",
                         "this page isn", "content not found", "page not found", "unavailable"]
        
        is_invalid_title = False
        if fetched_title:
             is_invalid_title = any(inv in fetched_title.lower() for inv in invalid_titles)
             
        if not fetched_title or is_invalid_title:
            print("[FB] Using undetected_chromedriver for title extraction...")
            
            # Helper for safe import
            try:
                import undetected_chromedriver as uc
            except ImportError:
                print("[FB] Could not import undetected_chromedriver")
                return "Facebook Video"

            use_driver = None
            should_quit = False
            
            # Reuse driver if possible
            if driver and isinstance(driver, uc.Chrome):
                use_driver = driver
                print("[FB] Reusing existing driver")
            else:
                try:
                    # import undetected_chromedriver as uc # Already imported above
                    options = uc.ChromeOptions()
                    # Re-enable Headless
                    options.add_argument("--headless=new") 
                    
                    # Mobile UA
                    options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1')
                    
                    options.add_argument("--disable-gpu")
                    options.add_argument("--mute-audio")
                    options.add_argument("--window-size=375,812") 
                    # Chống detect bot
                    options.add_argument("--disable-blink-features=AutomationControlled")
                    
                    chrome_path = os.path.join(os.getcwd(), "chrome_portable", "chrome.exe")
                    if os.path.exists(chrome_path): options.binary_location = chrome_path
                    
                    use_driver = uc.Chrome(options=options, version_main=None)
                    use_driver.set_page_load_timeout(45)
                    should_quit = True
                    
                    # --- LOAD COOKIES INTO DRIVER ---
                    if os.path.exists(cookie_path):
                        try:
                            # Use mobile site for cookies too
                            use_driver.get("https://m.facebook.com/")
                            with open(cookie_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if line.strip() and not line.strip().startswith('#'):
                                        parts = line.split('\t')
                                        if len(parts) >= 7:
                                            cookie = {
                                                'name': parts[5],
                                                'value': parts[6].strip(),
                                                'domain': parts[0],
                                                'path': parts[2]
                                            }
                                            try: use_driver.add_cookie(cookie)
                                            except: pass
                            print("[FB] 🍪 Đã nạp Cookies vào Browser Fallback!")
                            time.sleep(1) # Chờ cookie ăn
                        except Exception as e:
                            print(f"[FB] Lỗi nạp cookie: {e}")

                except Exception as e:
                    print(f"[FB] Failed to create driver: {e}")
                    return "Facebook Video" 

            try:
                use_driver.get(fb_url)
                
                # Scroll nhẹ
                try: use_driver.execute_script("window.scrollTo(0, 300);")
                except: pass
                
                # --- NEW: Dùng WebDriverWait thay vì sleep cứng ---
                from selenium.webdriver.common.by import By # Ensure imports
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                wait = WebDriverWait(use_driver, 15) # Chờ tối đa 15s
                
                # 1. Image Strategy (Wait for og:image)
                try:
                    # Chờ thẻ meta og:image xuất hiện
                    og_img_el = wait.until(EC.presence_of_element_located((By.XPATH, "//meta[@property='og:image']")))
                    if og_img_el:
                        img_url = og_img_el.get_attribute("content")
                        if img_url:
                            self._last_fb_image = img_url
                            print(f"[FB] Selenium found og:image: {img_url[:30]}...")
                except: 
                    # Last resort: Ảnh to nhất
                    if not self._last_fb_image:
                        try:
                            largest_img = use_driver.execute_script("""
                                let maxArea = 0; let bestSrc = null;
                                document.querySelectorAll('img').forEach(img => {
                                    let rect = img.getBoundingClientRect();
                                    let area = rect.width * rect.height;
                                    if (area > maxArea && rect.width > 200) { maxArea = area; bestSrc = img.src; }
                                });
                                return bestSrc;
                            """)
                            if largest_img: self._last_fb_image = largest_img
                        except: pass

                # 2. Title Strategy
                try:
                    # a. Thử lấy og:title (Title chuẩn của bài post)
                    og_title_el = use_driver.find_elements(By.XPATH, "//meta[@property='og:title']")
                    if og_title_el:
                        og_title = og_title_el[0].get_attribute("content")
                        if og_title and "Facebook" not in og_title:
                            fetched_title = og_title
                            print(f"[FB] Selenium found og:title: {fetched_title}")
                    
                    # b. Nếu không có, thử lấy Page Title
                except Exception as e:
                    print(f"[FB] Selenium getting og:title error: {e}")

                try:
                    # Wait for title in <title> tag
                    import time
                    time.sleep(3)
                    
                    # Try getting title from document.title
                    t = use_driver.title
                    
                    # Clean up title
                    if t:
                        if "Log in" in t or "Đăng nhập" in t:
                             self.log("⚠️ Facebook yêu cầu đăng nhập (Login Wall) - Vui lòng nhập Cookie!")
                             fetched_title = "Facebook Login Required"
                        else:
                             t = t.replace(" | Facebook", "").replace("Facebook", "").strip()
                    
                    # If empty or generic, try finding h1 or video label
                    if not t or len(t) < 5:
                         try:
                             # Try to find user status/caption
                             # Ensure uc is imported for By if not already in scope
                             if 'uc' not in locals() and 'uc' not in globals():
                                 import undetected_chromedriver as uc
                             elem = use_driver.find_element(uc.By.CSS_SELECTOR, 'div[data-ad-preview="message"]')
                             if elem: t = elem.text
                         except: pass

                    if t and len(t) > 3:
                        fetched_title = t
                        print(f"[FB] Browser extracted: {fetched_title[:50]}...")
                    else:
                        fetched_title = "Facebook Video"

                except Exception as e:
                     print(f"[FB] Browser error: {e}")
                     fetched_title = "Facebook Video"
                
            except Exception as e:
                print(f"[FB] Driver fallback error: {e}")
            finally:
                if should_quit and use_driver:
                    try: 
                        use_driver.quit()
                    except: pass


        if fetched_title:
            fetched_title = fetched_title.replace(' | Facebook', '').replace('Facebook', '').strip()
            if any(inv in fetched_title.lower() for inv in invalid_titles): fetched_title = None

        return fetched_title or "Facebook Video"
    
    def create_vimeo_embed(self, video_id, title="Vimeo Video"):
        """
        Create Vimeo embed code with automatic aspect ratio detection
        
        Args:
            video_id: Vimeo video ID
            title: Video title for accessibility
            
        Returns:
            str: HTML embed code with responsive wrapper
        """
        try:
            import requests
            
            # Get video info from Vimeo oEmbed API
            oembed_url = f"https://vimeo.com/api/oembed.json?url=https://vimeo.com/{video_id}"
            response = requests.get(oembed_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                width = data.get('width', 640)
                height = data.get('height', 360)
                
                # Calculate aspect ratio
                aspect_ratio = width / height if height > 0 else 16/9
                
                # Determine if vertical (9:16) or horizontal (16:9)
                is_vertical = aspect_ratio < 1  # width < height
                
                if is_vertical:
                    # Vertical video (9:16) - Use max-width and center
                    padding_percent = (height / width) * 100  # e.g., 177.78% for 9:16
                    
                    embed_code = f'''<div style="max-width:400px;margin:0 auto;">
<div style="padding:{padding_percent:.2f}% 0 0 0;position:relative;">
<iframe src="https://player.vimeo.com/video/{video_id}?badge=0&autopause=0&player_id=0&app_id=58479" 
frameborder="0" 
allow="autoplay; fullscreen; picture-in-picture; clipboard-write" 
style="position:absolute;top:0;left:0;width:100%;height:100%;" 
title="{title}"></iframe>
</div>
</div>
<script src="https://player.vimeo.com/api/player.js"></script>'''
                    
                    print(f"[VIMEO] 📱 Vertical video detected: {width}x{height} (aspect: {aspect_ratio:.2f})")
                else:
                    # Horizontal video (16:9) - Full width responsive
                    padding_percent = (height / width) * 100  # e.g., 56.25% for 16:9
                    
                    embed_code = f'''<div style="padding:{padding_percent:.2f}% 0 0 0;position:relative;">
<iframe src="https://player.vimeo.com/video/{video_id}?badge=0&autopause=0&player_id=0&app_id=58479" 
frameborder="0" 
allow="autoplay; fullscreen; picture-in-picture; clipboard-write" 
style="position:absolute;top:0;left:0;width:100%;height:100%;" 
title="{title}"></iframe>
</div>
<script src="https://player.vimeo.com/api/player.js"></script>'''
                    
                    print(f"[VIMEO] 🖥️ Horizontal video detected: {width}x{height} (aspect: {aspect_ratio:.2f})")
                
                return embed_code
            else:
                print(f"[VIMEO] ⚠️ Could not fetch video info, using default 16:9")
                
        except Exception as e:
            print(f"[VIMEO] ❌ Error detecting aspect ratio: {e}")
        
        # Fallback to standard 16:9 embed
        return f'''<div style="padding:56.25% 0 0 0;position:relative;">
<iframe src="https://player.vimeo.com/video/{video_id}?badge=0&autopause=0&player_id=0&app_id=58479" 
frameborder="0" 
allow="autoplay; fullscreen; picture-in-picture; clipboard-write" 
style="position:absolute;top:0;left:0;width:100%;height:100%;" 
title="{title}"></iframe>
</div>
<script src="https://player.vimeo.com/api/player.js"></script>'''


    def create_facebook_embed(self, fb_url, use_sdk=False):
        """Convert Facebook URL to embed code (267x591 - 9:16 ratio for portrait video)
        
        Args:
            fb_url: Facebook video URL
            use_sdk: If True, use Facebook SDK method (bypass security). If False, use iframe method.
        """
        import re
        from urllib.parse import quote
        
        # Clean URL
        clean_url = fb_url.strip()
        clean_url = clean_url.replace("m.facebook.com", "www.facebook.com")
        clean_url = clean_url.replace("web.facebook.com", "www.facebook.com")
        
        # Decide method: Use SDK if requested, otherwise Iframe
        if use_sdk:
            # Method 2: Facebook SDK (Javascript based)
            embed_code = (
                f'<div id="fb-root"></div>\n'
                f'<script async defer crossorigin="anonymous" src="https://connect.facebook.net/en_US/sdk.js#xfbml=1&version=v18.0" nonce="Aut0Wpr"></script>\n'
                f'<div class="fb-video" data-href="{clean_url}" data-width="267" data-show-text="false"></div>'
            )
        else:
            # Method 1: Iframe (HTML only, no JS required)
            # URL encode for Facebook embed
            encoded_url = quote(clean_url, safe='')
            
            # Dimensions for vertical video (9:16 approx)
            w = "360"
            h = "640"
            
            # Use a robust iframe URL compatible with Reels
            embed_code = (
                f'<iframe src="https://www.facebook.com/plugins/video.php?height={h}&href={encoded_url}&show_text=false&width={w}&t=0" '
                f'width="{w}" height="{h}" '
                f'style="border:none;overflow:hidden" '
                f'scrolling="no" frameborder="0" allowfullscreen="true" '
                f'allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>'
            )
        
        return embed_code

    def add_to_queue(self):
        # Grab raw text from Textbox (Bulk support)
        raw_video_text = self.entry_video.get("1.0", "end").strip()
        data = self.get_post_data() # Gets other fields (Title, Image, etc)
        
        # Check if empty
        if not data.title and not raw_video_text:
            messagebox.showwarning("Thiếu thông tin", "Nhập ít nhất tiêu đề hoặc video URL!")
            return

        # SPLIT LINES for Bulk Processing
        video_lines = [line.strip() for line in raw_video_text.split('\n') if line.strip()]
        
        if len(video_lines) > 1:
            # BULK MODE
            added_count = 0
            base_title = data.title
            
            self.log(f"📦 Phát hiện {len(video_lines)} dòng video. Đang thêm xử lý hàng loạt...")
            
            for idx, vid_line in enumerate(video_lines):
                try:
                    # Clone data for each post
                    import copy
                    current_post = copy.deepcopy(data)
                    current_post.video_url = vid_line
                    
                    # Handle Title
                    if not base_title: 
                         # If no title provided, use generic or let later steps handle it
                         current_post.title = "" 
                    else:
                         # Append index to title to differentiate if user provided one
                         current_post.title = f"{base_title} (Part {idx+1})"

                    # --- Facebook Logic (Mini version for bulk) ---
                    if 'facebook.com' in vid_line or 'fb.watch' in vid_line:
                        if not vid_line.startswith('<'): # URL not Embed
                             # Fetch title if missing
                             if not current_post.title:
                                 try:
                                     # Fast fetch attempt (Blocking UI slightly but accepting for batch)
                                     self.update_idletasks()
                                     ft = self.get_facebook_title(vid_line)
                                     if ft and ft != "Facebook Video":
                                         current_post.title = ft
                                 except: pass
                                 
                             # Generate Embed
                             # use_sdk defaults to False, uses Iframe (robust)
                             current_post.video_url = self.create_facebook_embed(vid_line)
                    
                    # --- YouTube Logic ---
                    elif 'youtube.com' in vid_line or 'youtu.be' in vid_line:
                        if not vid_line.startswith('<'):
                             # Extract video ID
                             import re
                             video_id = None
                             if 'youtu.be' in vid_line:
                                 match = re.search(r'youtu\.be/([\w-]+)', vid_line)
                                 if match: video_id = match.group(1)
                             else:
                                 match = re.search(r'v=([\w-]+)', vid_line)
                                 if match: video_id = match.group(1)
                             
                             if video_id:
                                 # Standard standard embed width
                                 width = 560
                                 height = 315
                                 current_post.video_url = f'<iframe width="{width}" height="{height}" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen="true"></iframe>'
                                 
                                 # Optional: Fetch title via oEmbed (fast)
                                 if not current_post.title:
                                     try:
                                         import requests
                                         oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
                                         res = requests.get(oembed_url, timeout=2)
                                         if res.status_code == 200:
                                             yt_data = res.json()
                                             current_post.title = yt_data.get('title', '')
                                     except: pass

                    # --- Vimeo Logic ---
                    elif 'vimeo.com' in vid_line:
                        if not vid_line.strip().startswith('<') and 'player.vimeo.com' not in vid_line:
                             import re
                             match = re.search(r'vimeo\.com/(\d+)', vid_line)
                             if match:
                                 vid_id = match.group(1)
                                 # Use new helper function for proper aspect ratio
                                 current_post.video_url = self.create_vimeo_embed(vid_id, current_post.title or "Vimeo Video")
                                 
                                 if not current_post.title:
                                     try:
                                          import requests
                                          oembed_url = f"https://vimeo.com/api/oembed.json?url=https://vimeo.com/{vid_id}"
                                          res = requests.get(oembed_url, timeout=2)
                                          if res.status_code == 200:
                                              data = res.json()
                                              current_post.title = data.get('title', '')
                                     except: pass
                    
                    # Add to queue
                    cleaned_data = {
                        'title': current_post.title,
                        'video_url': current_post.video_url,
                        'image_url': current_post.image_url,
                        'content': current_post.content,
                        'needs_body_content': getattr(current_post, 'needs_body_content', True),
                        'theme': self.get_selected_theme_id()
                    }
                    self.post_queue.append(cleaned_data)
                    added_count += 1
                    
                except Exception as e:
                    print(f"Error adding line {idx}: {e}")
            
            self.log(f"✅ Đã thêm {added_count} bài viết vào hàng chờ!")
            self.update_queue_display()
            # Clear ALL inputs after bulk add
            self.entry_video.delete("1.0", "end")
            self.entry_title.delete(0, "end")
            self.entry_image.delete(0, "end")
            if hasattr(self, 'entry_content_image'): self.entry_content_image.delete(0, "end")
            if hasattr(self, 'entry_content_image2'): self.entry_content_image2.delete(0, "end")
            if hasattr(self, 'entry_content_image3'): self.entry_content_image3.delete(0, "end")
            self.textbox_content.delete("1.0", "end")
            return

        # SINGLE MODE (Original Logic)
        # Ensure data.video_url is set correctly from the textbox
        data.video_url = raw_video_text
        
        if not data.title and not data.video_url:
             messagebox.showwarning("Thiếu thông tin", "Nhập ít nhất tiêu đề hoặc video URL!")
             return
             
        # ... Continue with original single logic below ...
        
        # --- Facebook Processing for Single Post ---
        if data.video_url and ('facebook.com' in data.video_url or 'fb.watch' in data.video_url):
            # Only process if it looks like a URL, not already an embed code
            if not data.video_url.strip().startswith('<'):
                # Check if should use oEmbed (let WordPress handle it)
                use_oembed = self.initial_config.get('facebook_use_oembed', False)
                
                if use_oembed:
                    self.log("🔍 Đang xử lý link Facebook (lấy tiêu đề, giữ URL cho WordPress oEmbed)...")
                    
                    # Only fetch title, keep URL as-is for WordPress oEmbed
                    if not data.title:
                        try:
                            self.update_idletasks() 
                            fetched_title = self.get_facebook_title(data.video_url)
                            if fetched_title and fetched_title != "Facebook Video":
                                data.title = fetched_title
                                self.entry_title.delete(0, "end")
                                self.entry_title.insert(0, fetched_title)
                        except Exception as e:
                            print(f"Lỗi lấy tiêu đề FB: {e}")
                    
                    # Keep URL as-is - WordPress will handle oEmbed
                    self.log("✅ Giữ URL Facebook cho WordPress tự xử lý (oEmbed)")
                else:
                    self.log("🔍 Đang xử lý link Facebook (lấy tiêu đề & mã nhúng)...")
                    
                    # 1. Fetch Title if missing
                    if not data.title:
                        try:
                            # Force UI update
                            self.update_idletasks() 
                            fetched_title = self.get_facebook_title(data.video_url)
                            if fetched_title and fetched_title != "Facebook Video":
                                data.title = fetched_title
                                self.entry_title.delete(0, "end")
                                self.entry_title.insert(0, fetched_title)
                        except Exception as e:
                            print(f"Lỗi lấy tiêu đề FB: {e}")

                    # 2. Generate Embed Code
                    try:
                        use_sdk = self.initial_config.get('facebook_use_sdk', False)
                        embed_code = self.create_facebook_embed(data.video_url, use_sdk=use_sdk)
                        if embed_code:
                            data.video_url = embed_code
                            # Optional: Update UI to show it's now an embed code? 
                            # self.entry_video.delete(0, "end")
                            # self.entry_video.insert(0, "[Converted to Embed Code]")
                    except Exception as e:
                        self.log(f"⚠️ Lỗi tạo embed FB: {e}")

        # --- Vimeo Processing for Single Post (If not handled by _extract_video_url) ---
        if data.video_url and 'vimeo.com' in data.video_url:
             # Check if it is a raw link that needs conversion to full embed code
             if not data.video_url.strip().startswith('<') and 'player.vimeo.com' not in data.video_url:
                  import re
                  match = re.search(r'vimeo\.com/(\d+)', data.video_url)
                  if match:
                      vid_id = match.group(1)
                      # Use new helper function for proper aspect ratio
                      data.video_url = self.create_vimeo_embed(vid_id, data.title or "Vimeo Video")
                      self.log(f"✅ Đã chuyển link Vimeo sang Embed Code (tự động phát hiện tỷ lệ)")
                      
                      # Fetch title if missing
                      if not data.title:
                          try:
                              import requests
                              oembed_url = f"https://vimeo.com/api/oembed.json?url=https://vimeo.com/{vid_id}"
                              res = requests.get(oembed_url, timeout=2)
                              if res.status_code == 200:
                                  data.title = res.json().get('title', '')
                                  self.entry_title.delete(0, "end")
                                  self.entry_title.insert(0, data.title)
                          except: pass


        # Auto-generate title if missing but has video
        if not data.title and data.video_url:
            if "youtube" in data.video_url.lower():
                data.title = f"Video YouTube - {time.strftime('%H:%M:%S')}"
            elif "vimeo" in data.video_url.lower():
                data.title = f"Video Vimeo - {time.strftime('%H:%M:%S')}"
            elif "facebook" in data.video_url.lower() or "fb.watch" in data.video_url.lower():
                data.title = f"Video Facebook - {time.strftime('%H:%M:%S')}"
            else:
                data.title = f"Video Embed - {time.strftime('%H:%M:%S')}"
        
        # Prepare queue item
        queue_item = data.__dict__
        
        # Check if content is empty -> AUTO ENABLE CONTENT MATCHING FROM POOL
        if not data.content.strip():
            queue_item['needs_body_content'] = True
            if hasattr(self, 'content_pool') and self.content_pool:
                self.log(f"   ℹ️ Bài viết trống nội dung -> Sẽ tự động ghép từ pool ({len(self.content_pool)} bài sẵn có)")
        
        self.post_queue.append(queue_item)
        self.update_queue_display()
        self.log(f"✅ Đã thêm vào hàng chờ: {data.title}")
        
        # Clear inputs
        self.entry_title.delete(0, "end")
        self.entry_video.delete("1.0", "end")
        self.entry_image.delete(0, "end")
        if hasattr(self, 'entry_content_image'): self.entry_content_image.delete(0, "end")  # Clear content image 1
        if hasattr(self, 'entry_content_image2'): self.entry_content_image2.delete(0, "end")  # Clear content image 2
        if hasattr(self, 'entry_content_image3'): self.entry_content_image3.delete(0, "end")  # Clear content image 3
        self.textbox_content.delete("1.0", "end")

    def update_queue_display(self):
        """Update Queue display using Cards with Thumbnails"""
        # Update label count
        if hasattr(self, 'lbl_queue_count'):
            self.lbl_queue_count.configure(text=f"({len(self.post_queue)} bài)")
            
        # Enable/Disable Run button
        if hasattr(self, 'btn_batch_post'):
            if self.post_queue:
                self.btn_batch_post.configure(state="normal", text="🚀 CHAY AUTO")
            else:
                self.btn_batch_post.configure(state="disabled", text="▶️ CHẠY AUTO POST (HÀNG CHỜ)")
            
        # Clear existing cards
        if hasattr(self, 'queue_scroll'):
            for widget in self.queue_scroll.winfo_children():
                widget.destroy()
        else:
            return
            
        # Populate new cards

        if not self.post_queue:
            ctk.CTkLabel(self.queue_scroll, text="Hàng chờ trống. Thêm bài viết để bắt đầu.", text_color="gray").pack(pady=20)
            return

        for idx, post in enumerate(self.post_queue):
            try:
                # Post Data
                title = post.get('title', 'No Title')
                video_url = post.get('video_url', '')
                image_url = post.get('image_url', '')
                
                # Card Frame
                card = ctk.CTkFrame(self.queue_scroll, fg_color="#2b2b2b", corner_radius=8, border_width=1, border_color="#404040")
                card.pack(fill="x", pady=5, padx=5)
                
                # 1. Thumbnail (Left)
                thumb_frame = ctk.CTkFrame(card, width=80, height=60, fg_color="#1a1a1a")
                thumb_frame.pack(side="left", padx=5, pady=5)
                thumb_frame.pack_propagate(False)
                
                # Load Image if available
                has_img = False
                if image_url and os.path.exists(image_url):
                    try:
                        from PIL import Image, ImageTk
                        pil_img = Image.open(image_url)
                        # Resize preserving aspect ratio roughly or crop? simple thumbnail is fine
                        pil_img.thumbnail((80, 80))
                        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                        ctk.CTkLabel(thumb_frame, text="", image=ctk_img).pack(expand=True)
                        has_img = True
                    except Exception as e:
                        print(f"Error loading thumbnail for {image_url}: {e}")
                
                if not has_img:
                    ctk.CTkLabel(thumb_frame, text="No Img", font=("Arial", 9)).pack(expand=True)
                
                # 2. Info (Center)
                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=10)
                
                # Post Type Icon/Text
                post_type = "📄" # Default
                if 'facebook' in video_url: post_type = "Facebook 🟦"
                elif 'youtube' in video_url: post_type = "YouTube 🟥"
                elif 'vimeo' in video_url: post_type = "Vimeo 🟦"
                
                ctk.CTkLabel(info_frame, text=f"{idx+1}. {post_type}", font=("Segoe UI", 10), text_color="gray", anchor="w").pack(fill="x")
                ctk.CTkLabel(info_frame, text=title[:60] + "..." if len(title)>60 else title, font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x")
                ctk.CTkLabel(info_frame, text=video_url[:80]+"..." if len(video_url)>80 else video_url, font=("Consolas", 9), text_color="gray", anchor="w").pack(fill="x")
                
                # 3. Actions (Right)
                action_frame = ctk.CTkFrame(card, fg_color="transparent")
                action_frame.pack(side="right", padx=10)
                
                # Delete Button
                ctk.CTkButton(action_frame, text="🗑️", width=40, fg_color="#ef4444", hover_color="#dc2626",
                              command=lambda i=idx: self.remove_from_queue(i)).pack()
                
            except Exception as e:
                print(f"Error displaying queue item {idx}: {e}")

    def remove_from_queue(self, index):
        """Remove item from queue by index and refresh display"""
        if 0 <= index < len(self.post_queue):
            removed = self.post_queue.pop(index)
            self.log(f"🗑️ Đã xoá khỏi hàng chờ: {removed.get('title')}")
            self.update_queue_display()

    def clear_queue(self):
        self.post_queue = []
        self.update_queue_display()
        self.log("🗑️ Đã xóa toàn bộ hàng chờ.")

    def get_post_data(self):
        data = AppData()
        data.title = self.entry_title.get()
        
        # Extract video URL from iframe if user pasted full iframe code
        video_input = self.entry_video.get("1.0", "end").strip()
        data.video_url = self._extract_video_url(video_input)
        
        data.image_url = self.entry_image.get()
        data.content_image = self.entry_content_image.get()  # Content image 1
        data.content_image2 = self.entry_content_image2.get()  # Content image 2
        data.content_image3 = self.entry_content_image3.get()  # Content image 3
        data.auto_fetch_images = self.chk_auto_fetch_images.get()  # Auto-fetch flag
        data.content = self.textbox_content.get("1.0", "end")
        data.theme = self.get_selected_theme_id()  # Get selected theme
        return data
    
    def _extract_video_url(self, input_text):
        """
        Extract video URL or full embed code from various input formats:
        - Full Vimeo embed with div wrapper: Use entire code
        - Facebook video URL: Convert to fixed-size iframe (267x591)
        - Iframe code: Extract src URL
        - Direct URL: Use as-is
        - Vimeo share link: Convert to player URL
        """
        if not input_text:
            return ""
        
        import re
        from urllib.parse import quote
        
        # Case 1: Full Vimeo embed code with <div> wrapper and <script>
        # This is the BEST format - use it entirely
        if '<div style="padding:' in input_text and '<script src="https://player.vimeo.com/api/player.js">' in input_text:
            print(f"[GUI] Detected full Vimeo embed code with wrapper")
            # Return the entire embed code - WordPress will handle it
            return input_text
        
        # Case 2: Facebook video URL - Convert to responsive iframe
        if 'facebook.com' in input_text or 'fb.watch' in input_text or 'fb.com' in input_text:
            print(f"[GUI] Detected Facebook video URL")
            
            # Extract the actual Facebook URL if it's in iframe already
            if '<iframe' in input_text:
                match = re.search(r'href=([^&\s]+)', input_text)
                if match:
                    fb_url = match.group(1)
                    # URL decode if needed
                    fb_url = fb_url.replace('%3A', ':').replace('%2F', '/')
                else:
                    # Try to extract from src
                    match = re.search(r'src=["\']([^"\']+)["\']', input_text)
                    if match:
                        fb_url = match.group(1)
                    else:
                        fb_url = input_text
            else:
                fb_url = input_text.strip()
            
            # Ensure it's a full URL
            if not fb_url.startswith('http'):
                fb_url = 'https://' + fb_url
            
            # URL encode for Facebook embed
            encoded_url = quote(fb_url, safe='')
            
            # Create Facebook iframe (267x591 - 9:16 ratio for portrait video)
            # Check if should use SDK method
            use_sdk = self.initial_config.get('facebook_use_sdk', False)
            
            if use_sdk:
                # Method 2: Facebook SDK (bypass security)
                # Format: <div class="fb-video" data-href="URL" data-width="267"></div>
                fb_iframe = (
                    f'<!-- Facebook SDK Script -->'
                    f'<script>window.fbAsyncInit = function() {{'
                    f'FB.init({{appId: "YOUR_APP_ID",xfbml: true,version: "v12.0"}});'
                    f'}};'
                    f'(function(d, s, id){{'
                    f'var js, fjs = d.getElementsByTagName(s)[0];'
                    f'if (d.getElementById(id)) {{return;}}'
                    f'js = d.createElement(s); js.id = id;'
                    f'js.src = "https://connect.facebook.net/en_US/sdk.js";'
                    f'fjs.parentNode.insertBefore(js, fjs);'
                    f'}}(document, "script", "facebook-jssdk"));</script>'
                    f'<!-- Facebook Video Embed -->'
                    f'<div class="fb-video" data-href="{fb_url}" data-width="267"></div>'
                )
            else:
                # Method 1: Direct iframe (default) - CRITICAL: NO SPACES between attributes!
                fb_iframe = (
                    f'<iframe src="https://www.facebook.com/plugins/video.php?height=591&href={encoded_url}&show_text=false&width=267&t=0" '
                    f'width="267" '
                    f'height="591" '
                    f'style="border:none;overflow:hidden" '
                    f'scrolling="no" '
                    f'frameborder="0" '
                    f'allowfullscreen="true" '
                    f'allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share" '
                    f'allowFullScreen="true">'
                    f'</iframe>'
                )
            
            print(f"[GUI] Created Facebook iframe: {fb_iframe[:100]}...")
            return fb_iframe
        
        # Case 3: Already a clean player URL
        if 'player.vimeo.com/video/' in input_text and '<' not in input_text:
            return input_text
        
        # Case 4: Iframe code - extract src attribute
        if '<iframe' in input_text.lower():
            # Match src="..." or src='...'
            match = re.search(r'src=["\']([^"\']+)["\']', input_text)
            if match:
                url = match.group(1)
                print(f"[GUI] Extracted URL from iframe: {url}")
                return url
        
        # Case 5: Regular vimeo.com link - convert to player URL
        if 'vimeo.com/' in input_text and 'player.vimeo.com' not in input_text:
            # Extract video ID
            match = re.search(r'vimeo\.com/(\d+)', input_text)
            if match:
                video_id = match.group(1)
                player_url = f"https://player.vimeo.com/video/{video_id}"
                print(f"[GUI] Converted vimeo.com link to player URL: {player_url}")
                return player_url
        
        # Case 6: Just return as-is (might be other video platform)
        return input_text

    def on_post_click(self):
        data = self.get_post_data()
        self.log("Đang đăng bài lẻ...")
        self.controller.handle_post_request(data)

    def on_queue_post_click(self):
        if not self.post_queue: 
            self.log("❌ Hàng chờ trống!")
            return
        
        self.log(f"🚀 Bắt đầu chạy AUTO - {len(self.post_queue)} bài trong hàng chờ")
        self.btn_batch_post.configure(state="disabled", text="⏳ Đang chạy AUTO...")
        
        # Start processing queue
        self.process_next_queue_post()

    def process_next_queue_post(self):
        if not self.post_queue:
            self.log("✅ Hoàn thành AUTO! Tất cả bài đã được xử lý.")
            self.btn_batch_post.configure(state="normal", text="🚀 CHAY AUTO")
            return
        
        item = self.post_queue[0]
        self.log(f"📝 Đang xử lý bài {len(self.post_queue)} còn lại: {item.get('title', 'Không có tiêu đề')}")
        
        # Check if this post needs body content from pool
        if item.get('needs_body_content', False) and hasattr(self, 'content_pool') and self.content_pool:
            # Get content from pool NOW (when posting)
            content_item = self.content_pool.pop(0)
            body_content = content_item['content']
            content_filename = content_item['filename']
            content_filepath = content_item.get('filepath', '')  # Get filepath for deletion
            
            # DON'T combine here - let wp_model.py handle video placement
            # Just update the raw_content with body text only
            item['content'] = body_content  # Only body content, no embed code
            item['needs_body_content'] = False
            item['content_source'] = content_filename
            item['txt_filepath'] = content_filepath  # Store filepath for deletion after post
            
            self.log(f"   📄 Ghép nội dung từ: {content_filename}")
            self.log(f"   🗑️ Đã xóa khỏi pool để tránh trùng lặp")
            self.log(f"   ✅ Nội dung body: {len(body_content)} ký tự")
            
            # Show remaining
            remaining = len(self.content_pool)
            if remaining > 0:
                self.log(f"   💾 Còn {remaining} nội dung trong pool")
            else:
                self.log(f"   ℹ️ Pool đã hết nội dung")
        
        # Convert dict to AppData
        data = AppData()
        data.title = item.get('title', '')
        data.video_url = item.get('video_url', '')  # This will be used to generate embed in wp_model.py
        data.image_url = item.get('image_url', '')

        # --- FALLBACK: Use Profile Pic from 'thumbnails' if no video thumb ---
        if not data.image_url:
            try:
                import random
                thumb_dir = "thumbnails"
                if os.path.exists(thumb_dir):
                    profiles = [
                        f for f in os.listdir(thumb_dir) 
                        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) 
                        and not f.startswith("car_api_") # Filter out downloaded car images
                    ]
                    if profiles:
                        # Pick random profile pic
                        selected_profile = random.choice(profiles)
                        data.image_url = os.path.abspath(os.path.join(thumb_dir, selected_profile))
                        self.log(f"   🖼️ Không có ảnh video -> Lấy ảnh đại diện: {selected_profile}")
            except Exception as e:
                print(f"Error picking profile pic: {e}")
        data.content_image = item.get('content_image', '')  # Content image 1
        data.content_image2 = item.get('content_image2', '')  # Content image 2
        data.content_image3 = item.get('content_image3', '')  # Content image 3
        data.auto_fetch_images = True  # Always auto-fetch for batch posting
        data.content = item.get('content', '')
        
        # Get theme from item or fallback to selected theme in GUI
        # This ensures that even old queue items respect the current GUI selection if they don't have a theme
        data.theme = item.get('theme', self.get_selected_theme_id())
        print(f"[DEBUG] Batch item theme: {data.theme}")
        
        # LƯU TITLE VÀO BIẾN TẠM để dùng trong on_post_finished
        self.current_posting_title = data.title
        print(f"[DEBUG] Saved current_posting_title: '{self.current_posting_title}'")  # Terminal only
        
        # Call controller to handle the post
        if self.controller:
            self.controller.handle_post_request(data, is_batch=True)
        else:
            # Mock success for testing
            self.after(2000, lambda: self.on_post_finished(True, f"https://test.com/{data.title.replace(' ','-')}", True))

    def on_post_finished(self, success, message, is_batch=False, post_title=None, image_path=None):
        if success:
            self.log(f"✅ THÀNH CÔNG: {message}")
            
            # Use the passed post_title if available logic
            final_title = "Unknown"
            
            if post_title:
                final_title = post_title
                print(f"[DEBUG] Got clean title passed from controller: '{final_title}'")  # Terminal only
            elif is_batch:
                # Fallback (should rarely happen now)
                if self.post_queue:
                    final_title = self.post_queue[0].get('title', 'Unknown')
            else:
                # Đăng bài lẻ - lấy từ input fields
                if hasattr(self, 'entry_title'):
                    try:
                        final_title = self.entry_title.get().strip()
                    except:
                        pass
            
            if not final_title or final_title == "Unknown":
                 final_title = f"Post {len(self.published_links) + 1}"

            # --- Resolve Image Path for History if not provided ---
            if not image_path:
                if is_batch and self.post_queue:
                    # Get from current queue item
                    image_path = self.post_queue[0].get('image_url', '')
                elif not is_batch:
                    # Get from UI
                    if hasattr(self, 'entry_image'):
                        image_path = self.entry_image.get()

            # Add to history with title AND image
            try:
                print(f"[DEBUG] Adding to history: '{final_title}' -> {message}")
                # Store in list with image path
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                history_item = {
                    'title': final_title,
                    'link': message,
                    'timestamp': timestamp,
                    'status': 'checking', # checking, success, error
                    'image_path': image_path
                }
                self.published_links.append(history_item)
                
                # Render immediately
                self.update_history_status(len(self.published_links)-1, 'checking')
                
                # AUTO-CHECK LINK sau 5 giây (tăng từ 2s để WordPress kịp xử lý)
                self.after(5000, lambda: self.check_published_link(message, final_title))
                
            except Exception as e:
                self.log(f"❌ Lỗi khi thêm vào lịch sử: {e}")
                import traceback
                traceback.print_exc()
            
            # Auto-delete files after successful post
            if is_batch and self.post_queue:
                completed_item = self.post_queue[0]
                
                # Delete thumbnail file if it exists
                thumbnail_path = completed_item.get('image_url', '')
                if thumbnail_path and os.path.exists(thumbnail_path):
                    try:
                        os.remove(thumbnail_path)
                        self.log(f"🗑️ Đã xóa thumbnail: {os.path.basename(thumbnail_path)}")
                    except Exception as e:
                        self.log(f"⚠️ Không thể xóa thumbnail: {e}")
                
                # Delete txt content file if it exists
                txt_filepath = completed_item.get('txt_filepath', '')
                if txt_filepath and os.path.exists(txt_filepath):
                    try:
                        os.remove(txt_filepath)
                        self.log(f"🗑️ Đã xóa file nội dung: {os.path.basename(txt_filepath)}")
                    except Exception as e:
                        self.log(f"⚠️ Không thể xóa file txt: {e}")
                
                # Remove completed item from queue
                self.post_queue.pop(0)
                self.log(f"✅ Hoàn thành: {completed_item.get('title', 'Không có tiêu đề')}")
                self.update_queue_display()
                # Continue with next item after 2 seconds
                self.after(2000, self.process_next_queue_post)
        else:
            self.log(f"❌ THẤT BẠI: {message}")
            if is_batch:
                # On failure, still remove item and continue (or you can choose to stop)
                failed_item = self.post_queue.pop(0) if self.post_queue else None
                if failed_item:
                    self.log(f"❌ Bỏ qua bài lỗi: {failed_item.get('title', 'Không có tiêu đề')}")
                    
                    # Also delete files on failure to avoid accumulation
                    thumbnail_path = failed_item.get('image_url', '')
                    if thumbnail_path and os.path.exists(thumbnail_path):
                        try:
                            os.remove(thumbnail_path)
                            self.log(f"🗑️ Đã xóa thumbnail của bài lỗi: {os.path.basename(thumbnail_path)}")
                        except:
                            pass
                    
                    # Delete txt file on failure too
                    txt_filepath = failed_item.get('txt_filepath', '')
                    if txt_filepath and os.path.exists(txt_filepath):
                        try:
                            os.remove(txt_filepath)
                            self.log(f"🗑️ Đã xóa file txt của bài lỗi: {os.path.basename(txt_filepath)}")
                        except:
                            pass
                
                self.update_queue_display()
                # Continue with next item after 3 seconds
                self.after(3000, self.process_next_queue_post)

    def _on_link_click(self, event):
        """Handle click on link in history"""
        try:
            # Get the index of the click
            index = self.history_textbox.index(f"@{event.x},{event.y}")
            
            # Get the range of the clicked tag
            tag_ranges = self.history_textbox.tag_ranges("link")
            
            # Find which link was clicked
            for i in range(0, len(tag_ranges), 2):
                start = tag_ranges[i]
                end = tag_ranges[i + 1]
                
                if self.history_textbox.compare(start, "<=", index) and self.history_textbox.compare(index, "<", end):
                    # Get the URL text
                    url = self.history_textbox.get(start, end)
                    
                    # Open in browser
                    import webbrowser
                    webbrowser.open(url)
                    self.log(f"🌐 Đã mở link: {url}")
                    break
        except Exception as e:
            print(f"[ERROR] Failed to open link: {e}")
    
    def add_to_history(self, link, title="", status="pending", image_path=None):
        """Add published post to history with title, link, status AND thumbnail"""
        # This function is now deprecated/replaced by the logic in on_post_finished
        # and update_history_status for initial rendering.
        # Keeping it for now to avoid breaking other parts if any still call it directly.
        print("[WARNING] add_to_history called directly. Consider using on_post_finished logic.")
        try:
            # Store in list with image path
            self.published_links.append({
                'title': title,
                'link': link,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': status,
                'image_path': image_path
            })
            
            # Display in history textbox
            def update_ui():
                if hasattr(self, 'history_textbox'):
                    self.history_textbox.configure(state="normal")
                    
                    index = len(self.published_links)
                    
                    # --- Insert Image (Thumbnail) ---
                    has_image = False
                    if image_path and os.path.exists(image_path):
                        try:
                            # Resize image for history list (e.g. 80x80)
                            pil_img = Image.open(image_path)
                            pil_img.thumbnail((80, 80)) 
                            photo = ImageTk.PhotoImage(pil_img)
                            
                            # Keep reference to avoid garbage collection
                            if not hasattr(self, 'history_images'):
                                self.history_images = []
                            self.history_images.append(photo)
                            
                            # Insert image
                            self.history_textbox.image_create("end", image=photo)
                            self.history_textbox.insert("end", "  ") # Spacing
                            has_image = True
                        except Exception as e:
                            print(f"[GUI] Error loading history thumb: {e}")
                    
                    # --- Status Icon ---
                    status_icon = "⏳"
                    if status == "success": status_icon = "✅"
                    elif status == "error": status_icon = "❌"
                    
                    # --- Title ---
                    self.history_textbox.insert("end", f"[{index}] {status_icon} {title}\n")
                    
                    # --- Link ---
                    indent = "          " if has_image else ""
                    self.history_textbox.insert("end", f"{indent}🔗 ")
                    
                    link_start = self.history_textbox.index("end-1c")
                    self.history_textbox.insert("end", link)
                    link_end = self.history_textbox.index("end-1c")
                    self.history_textbox.tag_add("link", link_start, link_end)
                    
                    # --- Timestamp ---
                    self.history_textbox.insert("end", f"\n{indent}📅 {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    self.history_textbox.insert("end", "─" * 60 + "\n\n")
                    
                    self.history_textbox.see("end")
                    self.history_textbox.configure(state="disabled")
                else:
                    print(f"[WARNING] history_textbox not found, but saved to list: {title}")
            
            # Schedule UI update on main thread
            self.after(0, update_ui)
            
        except Exception as e:
            print(f"[ERROR] Failed to add to history: {e}")
            import traceback
            traceback.print_exc()
    
    def update_history_status(self, index, status):
        """Update status icon in history with Image Support"""
        if index >= len(self.published_links): return
        
        self.published_links[index]['status'] = status
        
        # Re-render entire history
        def rebuild_ui():
            try:
                self.history_textbox.configure(state="normal")
                self.history_textbox.delete("1.0", "end")
                
                # Keep references to prevent GC
                self.history_images_refs = [] 
                
                for i, item in enumerate(self.published_links, 1):
                    status_icon = "⏳"
                    if item['status'] == 'success': status_icon = "✅"
                    elif item['status'] == 'error': status_icon = "❌"
                    
                    title = item['title']
                    has_image = False
                    
                    # 1. Number
                    self.history_textbox.insert("end", f"[{i}] ", "bold")
                    
                    # 2. Image (If exists)
                    img_path = item.get('image_path')
                    if img_path and os.path.exists(img_path):
                        try:
                            from PIL import Image, ImageTk
                            pil_img = Image.open(img_path)
                            pil_img.thumbnail((30, 30)) # Small icon size
                            tk_img = ImageTk.PhotoImage(pil_img)
                            self.history_images_refs.append(tk_img) # Keep ref
                            
                            self.history_textbox.image_create("end", image=tk_img)
                            self.history_textbox.insert("end", " ") # Spacer
                            has_image = True
                        except Exception as e:
                            print(f"Error loading history image: {e}")
                    
                    # 3. Status & Title
                    self.history_textbox.insert("end", f"{status_icon} {title}\n")
                    
                    # 4. Link & Time
                    indent = "       " + ("     " if has_image else "") # Adjust indent
                    
                    self.history_textbox.insert("end", f"{indent}🔗 ")
                    link_start = self.history_textbox.index("end-1c")
                    self.history_textbox.insert("end", item['link'])
                    link_end = self.history_textbox.index("end-1c")
                    self.history_textbox.tag_add("link", link_start, link_end)
                    
                    self.history_textbox.insert("end", f"\n{indent}📅 {item.get('timestamp','')}\n")
                    self.history_textbox.insert("end", "─" * 60 + "\n\n")

                self.history_textbox.see("end")
                self.history_textbox.configure(state="disabled")
                
            except Exception as e:
                print(f"UI Rebuild Error: {e}")
                
        self.after(0, rebuild_ui)
        
        # Re-render entire history
        def rebuild_ui():
            try:
                self.history_textbox.configure(state="normal")
                self.history_textbox.delete("1.0", "end")
                
                # Keep references to prevent GC
                self.history_images_refs = [] 
                
                for i, item in enumerate(self.published_links, 1):
                    status_icon = "⏳"
                    if item['status'] == 'success': status_icon = "✅"
                    elif item['status'] == 'error': status_icon = "❌"
                    
                    title = item['title']
                    has_image = False
                    
                    # 1. Number
                    self.history_textbox.insert("end", f"[{i}] ", "bold")
                    
                    # 2. Image (If exists)
                    img_path = item.get('image_path')
                    if img_path and os.path.exists(img_path):
                        try:
                            from PIL import Image, ImageTk
                            pil_img = Image.open(img_path)
                            pil_img.thumbnail((30, 30)) # Small icon size
                            tk_img = ImageTk.PhotoImage(pil_img)
                            self.history_images_refs.append(tk_img) # Keep ref
                            
                            self.history_textbox.image_create("end", image=tk_img)
                            self.history_textbox.insert("end", " ") # Spacer
                            has_image = True
                        except Exception as e:
                            print(f"Error loading history image: {e}")
                    
                    # 3. Status & Title
                    self.history_textbox.insert("end", f"{status_icon} {title}\n")
                    
                    # 4. Link & Time
                    indent = "       " + ("     " if has_image else "") # Adjust indent
                    
                    self.history_textbox.insert("end", f"{indent}🔗 ")
                    link_start = self.history_textbox.index("end-1c")
                    self.history_textbox.insert("end", item['link'])
                    link_end = self.history_textbox.index("end-1c")
                    self.history_textbox.tag_add("link", link_start, link_end)
                    
                    self.history_textbox.insert("end", f"\n{indent}📅 {item.get('timestamp','')}\n")
                    self.history_textbox.insert("end", "─" * 60 + "\n\n")

                self.history_textbox.see("end")
                self.history_textbox.configure(state="disabled")
                
            except Exception as e:
                print(f"UI Rebuild Error: {e}")
                
        self.after(0, rebuild_ui)
    
    def check_published_link(self, url, title):
        """
        Tự động check xem link đã đăng có accessible không
        Retry 3 lần với delay để WordPress kịp xử lý
        """
        def _check():
            try:
                import requests
                import time
                import re
                self.log(f"🔍 Đang kiểm tra link: {title}")
                
                # Find index of this link in history
                link_index = len(self.published_links)
                
                # Extract post ID from URL for alternative check
                post_id_match = re.search(r'[?&]p=(\d+)', url)
                post_id = post_id_match.group(1) if post_id_match else None
                
                # Retry up to 3 times with increasing delay
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = requests.get(url, timeout=10, allow_redirects=True)
                        status_code = response.status_code
                        
                        if status_code == 200:
                            self.log(f"   ✅ Link OK - Status 200")
                            self.update_history_status(link_index, "success")
                            return
                        elif status_code == 404:
                            if attempt < max_retries - 1:
                                # Retry after delay (WordPress might still be processing)
                                wait_time = (attempt + 1) * 3  # 3s, 6s, 9s
                                print(f"[LINK_CHECK] 404 on attempt {attempt+1}, retrying in {wait_time}s...")
                                time.sleep(wait_time)
                                continue
                            else:
                                # Final attempt failed - provide helpful message
                                if post_id:
                                    self.log(f"   ❌ Link lỗi 404 - Post ID {post_id} tồn tại nhưng URL không accessible")
                                    self.log(f"   💡 Có thể cần flush permalinks: WP Admin → Settings → Permalinks → Save")
                                else:
                                    self.log(f"   ❌ Link lỗi 404 (Not Found)")
                                self.update_history_status(link_index, "error")
                                return
                        elif status_code == 403:
                            self.log(f"   ❌ Link lỗi 403 (Forbidden) - Có thể bị security plugin block")
                            self.update_history_status(link_index, "error")
                            return
                        elif status_code == 500:
                            self.log(f"   ❌ Link lỗi 500 (Server Error)")
                            self.update_history_status(link_index, "error")
                            return
                        else:
                            self.log(f"   ⚠️ Link trả về status {status_code}")
                            self.update_history_status(link_index, "error")
                            return
                    except requests.exceptions.Timeout:
                        if attempt < max_retries - 1:
                            time.sleep(3)
                            continue
                        else:
                            self.log(f"   ⏱️ Timeout khi check link")
                            self.update_history_status(link_index, "error")
                            return
                    except requests.exceptions.ConnectionError:
                        if attempt < max_retries - 1:
                            time.sleep(3)
                            continue
                        else:
                            self.log(f"   🔌 Lỗi kết nối khi check link")
                            self.update_history_status(link_index, "error")
                            return
                    
            except Exception as e:
                self.log(f"   ❌ Lỗi check link: {e}")
                link_index = len(self.published_links)
                self.update_history_status(link_index, "error")
        
        # Run check in background thread
        import threading
        threading.Thread(target=_check, daemon=True).start()

    def copy_history_links(self):
        """Copy all links to clipboard"""
        self.clipboard_clear()
        
        # Create formatted text with titles and links
        text_lines = []
        for item in self.published_links:
            if isinstance(item, dict):
                text_lines.append(f"{item['title']}: {item['link']}")
            else:
                # Old format (just string)
                text_lines.append(str(item))
        
        self.clipboard_append("\n".join(text_lines))
        self.log("📋 Đã copy tất cả link vào clipboard.")

    def clear_history(self):
        """Clear all history"""
        self.published_links = []
        if hasattr(self, 'history_textbox'):
            self.history_textbox.configure(state="normal")
            self.history_textbox.delete("1.0", "end")
            self.history_textbox.configure(state="disabled")
        self.log("🗑️ Đã xóa toàn bộ lịch sử.")

    def browse_video_upload(self):
        filenames = filedialog.askopenfilenames(
            title="Chọn Video Upload",
            filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov *.wmv"), ("All Files", "*.*")]
        )
        if filenames:
            paths_str = "; ".join(filenames)
            self.entry_upload_path.delete(0, "end")
            self.entry_upload_path.insert(0, paths_str)
            self.log(f"Đã chọn {len(filenames)} file video.")

    def browse_thumbnail(self):
        """Open file dialog to select a thumbnail image"""
        filename = filedialog.askopenfilename(
            title="Chọn Ảnh Thumbnail",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp"), ("All Files", "*.*")]
        )
        if filename:
            self.entry_image.delete(0, "end")
            self.entry_image.insert(0, filename)
            self.log(f"🖼️ Đã chọn ảnh thumbnail: {os.path.basename(filename)}")

    def browse_content_image(self):
        """Open file dialog to select a content image"""
        filename = filedialog.askopenfilename(
            title="Chọn Ảnh Content 1",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp"), ("All Files", "*.*")]
        )
        if filename:
            self.entry_content_image.delete(0, "end")
            self.entry_content_image.insert(0, filename)
            self.log(f"🖼️ Đã chọn ảnh content 1: {os.path.basename(filename)}")
    
    def browse_content_image2(self):
        """Open file dialog to select content image 2"""
        filename = filedialog.askopenfilename(
            title="Chọn Ảnh Content 2",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp"), ("All Files", "*.*")]
        )
        if filename:
            self.entry_content_image2.delete(0, "end")
            self.entry_content_image2.insert(0, filename)
            self.log(f"🖼️ Đã chọn ảnh content 2: {os.path.basename(filename)}")
    
    def browse_content_image3(self):
        """Open file dialog to select content image 3"""
        filename = filedialog.askopenfilename(
            title="Chọn Ảnh Content 3",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.webp"), ("All Files", "*.*")]
        )
        if filename:
            self.entry_content_image3.delete(0, "end")
            self.entry_content_image3.insert(0, filename)
            self.log(f"🖼️ Đã chọn ảnh content 3: {os.path.basename(filename)}")

    def paste_image_from_clipboard(self, event=None):
        """Paste image from clipboard and save to thumbnails folder (for thumbnail field)"""
        return self.paste_image_from_clipboard_to_field(event, self.entry_image, "thumb")
    
    def paste_image_from_clipboard_to_field(self, event, target_field, field_name):
        """Paste image from clipboard and save to thumbnails folder (generic method)"""
        try:
            # Try to get image from clipboard
            img = ImageGrab.grabclipboard()
            
            if img is None:
                self.log("⚠️ Clipboard không chứa ảnh. Hãy chụp màn hình (PrtScn) hoặc copy ảnh trước.")
                return "break"
            
            # Create thumbnails folder if not exists
            if not os.path.exists("thumbnails"):
                os.makedirs("thumbnails")
            
            # Generate filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"thumbnails/pasted_{field_name}_{timestamp}.png"
            
            # Save image
            img.save(filename, "PNG")
            
            # Update the target field
            target_field.delete(0, "end")
            target_field.insert(0, filename)
            
            self.log(f"✅ Đã paste ảnh từ clipboard: {filename}")
            
            # Prevent default paste behavior
            return "break"
            
        except Exception as e:
            self.log(f"❌ Lỗi khi paste ảnh: {e}")
            return "break"


    def add_uploaded_video_link(self, title, embed_code, thumb=None):
        if hasattr(self, 'txt_upload_list'):
            self.txt_upload_list.configure(state="normal")
            display_text = f"✅ [UPLOADED] {title}\n"
            display_text += f"🔗 Embed Code:\n{embed_code}\n"
            if thumb:
                display_text += f"🖼 Thumbnail: {thumb}\n"
            display_text += "-"*50 + "\n"
            
            self.txt_upload_list.insert("end", display_text)
            self.txt_upload_list.see("end")
            self.txt_upload_list.configure(state="disabled")

    def on_upload_click(self):
        files_str = self.entry_upload_path.get().strip()
        if not files_str:
            self.log("❌ Chưa chọn file video!")
            return

        files = files_str.split("; ")
        self.log(f"Bắt đầu upload {len(files)} video...")
        self.btn_upload.configure(state="disabled", text="⏳ Đang tải lên...")
        
        import threading
        from model.vimeo_helper import VimeoHelper
        import queue
        
        # Create a queue for results
        result_queue = queue.Queue()
        completed_count = [0]  # Use list to allow modification in nested function
        total_files = len(files)

        def _upload_single_video(file_path, file_index, account_index):
            """Upload a single video with its own browser instance"""
            helper = VimeoHelper()
            try:
                # Load all available accounts first (important for rotation)
                helper.load_all_available_accounts()
                
                # Check headless option
                use_headless = bool(self.chk_headless_upload.get())
                mode_text = "Headless - Ẩn" if use_headless else "Visible - Hiện"
                self.after(0, lambda idx=file_index: self.log(f"[Luồng {account_index+1}] --- Upload File {idx+1}/{total_files}: {os.path.basename(file_path)} ---"))
                
                helper.init_driver(headless=use_headless)
                
                # Log callback for helper
                def _log(m): 
                    self.after(0, lambda msg=m, idx=file_index: self.log(f"[File {idx+1}] {msg}"))

                # Upload
                success, msg, data, quota = helper.upload_video(file_path, log_callback=_log)
                
                result_queue.put({
                    'index': file_index,
                    'success': success,
                    'msg': msg,
                    'data': data,
                    'quota': quota,
                    'file_path': file_path
                })
                
            except Exception as e:
                self.after(0, lambda err=e, idx=file_index: self.log(f"[File {idx+1}] Lỗi Thread: {err}"))
                result_queue.put({
                    'index': file_index,
                    'success': False,
                    'msg': str(e),
                    'data': None,
                    'quota': False,
                    'file_path': file_path
                })
            finally:
                helper.close()

        def _process_results():
            """Process upload results from queue"""
            try:
                result = result_queue.get_nowait()
                
                file_path = result['file_path']
                success = result['success']
                msg = result['msg']
                data = result['data']
                quota = result['quota']
                idx = result['index']
                
                if success:
                    # Check if we have data
                    if data:
                        title = data.get("title", "Video")
                        embed = data.get("embed_code", "No Embed Code")
                        thumb = data.get("thumbnail", None)
                        video_link = data.get("video_link", "")
                    else:
                        # No data but success - create basic info from filename
                        title = os.path.basename(file_path)
                        embed = f"<!-- Video đang xử lý: {title} -->"
                        thumb = None
                        video_link = ""
                        self.log("⚠️ Video đang xử lý, chưa có embed code đầy đủ")
                    
                    self.log(f"✅ {msg}")
                    self.add_uploaded_video_link(title, embed, thumb)
                    
                    # Auto add to queue if option is checked
                    if self.chk_auto_add_queue.get():
                        self.add_video_to_queue(title, embed, video_link, thumb)
                else:
                    self.log(f"❌ Lỗi: {msg}")
                    if quota:
                        self.log("⚠️ Quota Full!")
                
                completed_count[0] += 1
                
                # Check if all done
                if completed_count[0] >= total_files:
                    self.log(f"=== Hoàn thành upload {completed_count[0]}/{total_files} video ===")
                    self.btn_upload.configure(state="normal", text="⬆️ Bắt đầu Upload")
                else:
                    # Continue checking for more results
                    self.after(500, _process_results)
                    
            except queue.Empty:
                # No result yet, check again later
                if completed_count[0] < total_files:
                    self.after(500, _process_results)
                else:
                    self.btn_upload.configure(state="normal", text="⬆️ Bắt đầu Upload")

        # Determine number of available accounts
        total_accounts = 1
        try:
            if os.path.exists("vimeo_accounts.txt"):
                with open("vimeo_accounts.txt", "r", encoding="utf-8") as f:
                    acc_lines = [l for l in f.readlines() if l.strip()]
                    if acc_lines:
                        total_accounts = len(acc_lines)
            elif os.path.exists("vimeo_cookies.txt"):
                with open("vimeo_cookies.txt", "r", encoding="utf-8") as f:
                    c_lines = [l for l in f.readlines() if l.strip()]
                    if c_lines:
                        total_accounts = len(c_lines)
        except:
            pass
            
        self.log(f"🔎 Tìm thấy {total_accounts} tài khoản Vimeo để xoay vòng.")

        # Start parallel uploads with limited workers (2-3 threads max)
        max_parallel = 3  # Giới hạn 3 luồng song song
        self.log(f"🚀 Chạy song song tối đa {max_parallel} luồng upload...")
        
        # Use ThreadPoolExecutor to limit concurrent uploads
        from concurrent.futures import ThreadPoolExecutor
        
        def submit_upload(idx, file_path):
            """Submit a single upload task"""
            file_path = file_path.strip()
            if not file_path:
                completed_count[0] += 1
                return
            
            # Assign account index (rotate through ALL accounts)
            account_index = idx % total_accounts
            
            # Execute upload
            _upload_single_video(file_path, idx, account_index)
        
        # Create thread pool and submit all tasks
        executor = ThreadPoolExecutor(max_workers=max_parallel)
        
        for idx, file_path in enumerate(files):
            executor.submit(submit_upload, idx, file_path)
        
        # Don't wait for completion here - let them run in background
        executor.shutdown(wait=False)
        
        # Start result processor
        self.after(1000, _process_results)

    def add_video_to_queue(self, title, embed_code, video_link, thumbnail_path=None):
        """Add uploaded video to post queue automatically with thumbnail (content will be added when posting)"""
        try:
            # Clean title (remove file extension if present)
            clean_title = title.replace('.mp4', '').replace('.avi', '').replace('.mov', '').replace('.mkv', '')
            clean_title = clean_title.replace('_', ' ').strip()
            
            # DON'T store embed code in content - store in video_url so wp_model.py can place it correctly
            # The video_url will be used by generate_seo_content to create video block
            
            # Create post data with thumbnail (NO content yet)
            post_data = {
                'title': clean_title,  # Use video name as title
                'video_url': embed_code if embed_code else video_link,  # Store embed code as video_url
                'image_url': thumbnail_path if thumbnail_path else '',  # Thumbnail as featured image
                'content': '',  # Empty for now - will be filled with body content when posting
                'needs_body_content': True  # Flag to indicate we need to add body content when posting
            }
            
            self.post_queue.append(post_data)
            self.update_queue_display()
            self.log(f"📝 Đã thêm vào hàng chờ: {clean_title}")
            self.log(f"   🔗 Video: {video_link if video_link else 'Processing...'}")
            if thumbnail_path:
                self.log(f"   🖼️ Thumbnail: {os.path.basename(thumbnail_path)}")
            
            # Show content pool status
            if hasattr(self, 'content_pool'):
                remaining = len(self.content_pool)
                if remaining > 0:
                    self.log(f"   💾 Có {remaining} nội dung sẵn sàng để ghép khi đăng bài")
                else:
                    self.log(f"   ℹ️ Chưa có nội dung body (chỉ có video embed)")
            
        except Exception as e:
            self.log(f"❌ Lỗi thêm vào hàng chờ: {e}")

    def log_vimeo(self, message):
        """Log specifically to Vimeo tab"""
        # Update Main Log
        self.log(f"[VIMEO] {message}")
        
        # Update Vimeo Tab Log
        if hasattr(self, 'txt_vimeo_log'):
            self.txt_vimeo_log.configure(state="normal")
            self.txt_vimeo_log.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
            self.txt_vimeo_log.see("end")
            self.txt_vimeo_log.configure(state="disabled")

    def test_vimeo_cookie_login(self):
        """Test Vimeo cookie login functionality"""
        self.log_vimeo("🍪 Bắt đầu test cookie login...")
        self.btn_test_cookie.configure(state="disabled", text="⏳ Đang test...")
        
        import threading
        from model.vimeo_helper import VimeoHelper
        
        def _test_login():
            helper = VimeoHelper()
            try:
                # Check headless option
                use_headless = bool(self.chk_headless_test.get())
                helper.init_driver(headless=use_headless)
                
                # Log callback
                def _log(msg): 
                    self.after(0, lambda m=msg: self.log_vimeo(m))
                
                # Test cookie login
                success = helper.auto_login(log_callback=_log)
                
                if success:
                    self.after(0, lambda: self.log_vimeo("✅ Cookie login thành công!"))
                    
                    # Test upload page access
                    self.after(0, lambda: self.log_vimeo("🔍 Kiểm tra quyền truy cập upload..."))
                    helper.driver.get("https://vimeo.com/upload")
                    time.sleep(3)
                    
                    if "upload" in helper.driver.current_url.lower():
                        self.after(0, lambda: self.log_vimeo("✅ Có thể truy cập trang upload!"))
                    else:
                        self.after(0, lambda: self.log_vimeo("❌ Không thể truy cập trang upload."))
                        
                else:
                    self.after(0, lambda: self.log_vimeo("❌ Cookie login thất bại!"))
                    
            except Exception as e:
                self.after(0, lambda err=e: self.log_vimeo(f"❌ Lỗi test: {err}"))
            finally:
                helper.close()
                self.after(0, lambda: self.btn_test_cookie.configure(state="normal", text="🍪 Test Cookie Login"))
        
        threading.Thread(target=_test_login, daemon=True).start()

    def on_vimeo_reg_click(self):
        try:
            count = int(self.entry_vm_count.get())
        except:
            self.log("❌ Số lượng không hợp lệ (nhập số nguyên).")
            return

        self.log_vimeo(f"Bắt đầu quy trình tạo {count} tài khoản Vimeo...")
        self.btn_vm_reg.configure(state="disabled", text="⏳ Đang chạy...")
        
        import threading
        import random
        import string
        from model.vimeo_helper import VimeoHelper

        def _generate_identity():
            name = f"User{random.randint(10000, 99999)}"
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            email = f"nguyenduyduc{random_str}@gmail.com" # Updated pattern
            p_upper = random.choice(string.ascii_uppercase)
            p_lower = random.choice(string.ascii_lowercase)
            p_digits = ''.join(random.choices(string.digits, k=3))
            pwd = f"{p_upper}{p_lower}@{p_digits}xyz"
            return name, email, pwd

        def _run_batch():
            created = 0
            consecutive_failures = 0
            ip_blocked = False
            
            for i in range(count):
                self.after(0, lambda idx=i: self.log_vimeo(f"--- TÀI KHOẢN {idx+1}/{count} ---"))
                
                # 1. Gen Info
                name, email, pwd = _generate_identity()
                self.after(0, lambda n=name, e=email, p=pwd: self.log_vimeo(f"DATA: {e} | {p}"))
                
                # 2. Run Helper
                helper = VimeoHelper()
                try:
                    # Check headless option
                    use_headless = bool(self.chk_headless_vimeo.get())
                    helper.init_driver(headless=use_headless) # Use selected mode
                    
                    # Log callback wrapper
                    def _cb(msg): 
                        self.after(0, lambda m=msg: self.log_vimeo(m))

                    success, msg = helper.fill_registration_form(name, email, pwd, log_callback=_cb)
                    
                    if success:
                        self.after(0, lambda: self.log_vimeo("✅ Tạo thành công!"))
                        created += 1
                        consecutive_failures = 0  # Reset counter on success
                    else:
                        self.after(0, lambda m=msg: self.log_vimeo(f"❌ Thất bại: {m}"))
                        
                        # Check if it's an IP block error
                        if msg in ["IP_BLOCKED", "RATE_LIMITED", "ACCOUNT_LIMIT", "NETWORK_ERROR"]:
                            consecutive_failures += 1
                            self.after(0, lambda: self.log_vimeo(f"⚠️ Phát hiện vấn đề IP/Network (Lần {consecutive_failures})"))
                            
                            # If 2 consecutive IP blocks, stop and warn user
                            if consecutive_failures >= 2:
                                ip_blocked = True
                                self.after(0, lambda: self.log_vimeo("🛑 DỪNG: IP bị chặn liên tiếp!"))
                                
                                # Show popup warning
                                self.after(0, lambda: self.show_ip_block_warning())
                                break
                        else:
                            consecutive_failures = 0  # Reset if it's a different error
                        
                except Exception as e:
                    self.after(0, lambda err=e: self.log_vimeo(f"Lỗi: {err}"))
                finally:
                    helper.close()
            
            # Final summary
            if ip_blocked:
                self.after(0, lambda: self.log_vimeo(f"⚠️ KẾT THÚC SỚM: Tạo được {created}/{count} TK (IP bị chặn)"))
            else:
                self.after(0, lambda: self.log_vimeo(f"=== KẾT THÚC: Tạo được {created}/{count} TK ==="))
            
            self.after(0, lambda: self.btn_vm_reg.configure(state="normal", text="🚀 Bắt đầu Tạo"))

        threading.Thread(target=_run_batch, daemon=True).start()

    def show_ip_block_warning(self):
        """Show popup warning when IP is blocked"""
        try:
            messagebox.showwarning(
                "⚠️ IP Bị Chặn",
                "🚫 Vimeo đã chặn IP của bạn!\n\n"
                "📌 Nguyên nhân:\n"
                "• Tạo quá nhiều tài khoản từ cùng 1 IP\n"
                "• IP bị đánh dấu spam/bot\n"
                "• Rate limit (quá nhiều request)\n\n"
                "✅ Giải pháp:\n"
                "1. Đổi IP/VPN khác\n"
                "2. Đợi 30-60 phút rồi thử lại\n"
                "3. Sử dụng proxy xoay (rotating proxy)\n\n"
                "💡 Khuyến nghị: Đổi VPN/Proxy ngay!"
            )
        except Exception as e:
            print(f"[GUI] Error showing popup: {e}")
    
    def show_about_dialog(self):
        """Show About dialog with version info and changelog"""
        try:
            # Import version info
            try:
                from version import get_version_info, __app_name__, __author__, __build_date__
                version_info = get_version_info()
            except:
                version_info = {
                    "version": "2.0.2",
                    "app_name": "WprTool - WordPress Auto Posting",
                    "author": "NguyenDuyDuc",
                    "build_date": "2026-02-05",
                    "features": []
                }
            
            # Create popup window
            popup = ctk.CTkToplevel(self)
            popup.title("Thông Tin Phiên Bản")
            popup.geometry("500x400")
            popup.resizable(False, False)
            
            # Center window
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (500 // 2)
            y = (popup.winfo_screenheight() // 2) - (400 // 2)
            popup.geometry(f"500x400+{x}+{y}")
            
            # Main container
            main_frame = ctk.CTkFrame(popup, fg_color=self.colors['bg_light'])
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Header with icon and title
            header = ctk.CTkFrame(main_frame, fg_color=self.colors['primary'], corner_radius=12)
            header.pack(fill="x", pady=(0, 20))
            
            ctk.CTkLabel(
                header,
                text="🚀",
                font=("Segoe UI", 48)
            ).pack(pady=(20, 5))
            
            ctk.CTkLabel(
                header,
                text=version_info['app_name'],
                font=("Segoe UI", 20, "bold"),
                text_color="white"
            ).pack(pady=(0, 5))
            
            ctk.CTkLabel(
                header,
                text=f"Version {version_info['version']}",
                font=("Segoe UI", 14),
                text_color="white"
            ).pack(pady=(0, 20))
            
            # Info section
            info_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['bg_card'], corner_radius=12)
            info_frame.pack(fill="x", pady=(0, 15))
            
            info_items = [
                ("👤 Tác giả", version_info['author']),
                ("📅 Ngày phát hành", version_info['build_date']),
                ("🔧 Build", version_info['version']),
            ]
            
            for label, value in info_items:
                row = ctk.CTkFrame(info_frame, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=8)
                
                ctk.CTkLabel(
                    row,
                    text=label,
                    font=("Segoe UI", 11, "bold"),
                    text_color=self.colors['text_secondary']
                ).pack(side="left")
                
                ctk.CTkLabel(
                    row,
                    text=value,
                    font=("Segoe UI", 11),
                    text_color=self.colors['text_primary']
                ).pack(side="right")
            
            # Footer with close button
            footer = ctk.CTkFrame(main_frame, fg_color="transparent")
            footer.pack(fill="x", pady=(20, 0))
            
            ctk.CTkButton(
                footer,
                text="Đóng",
                width=150,
                height=36,
                font=("Segoe UI", 12, "bold"),
                fg_color=self.colors['primary'],
                hover_color=self.colors['primary_hover'],
                corner_radius=10,
                command=popup.destroy
            ).pack(pady=5)
            
            # Make popup modal
            popup.transient(self)
            popup.grab_set()
            
        except Exception as e:
            print(f"[GUI] Error showing about dialog: {e}")
            import traceback
            traceback.print_exc()
    
    def copy_all_links_with_titles(self):
        """Copy all published posts with titles in format: Title - Link"""
        try:
            import pyperclip
            
            if not self.published_posts:
                messagebox.showinfo("Thông Báo", "Chưa có bài viết nào được đăng!")
                return
            
            # Format: Title - Link (one per line)
            formatted_text = ""
            for post in self.published_posts:
                title = post.get('title', 'Untitled')
                link = post.get('link', '')
                formatted_text += f"{title} - {link}\n"
            
            # Copy to clipboard
            pyperclip.copy(formatted_text.strip())
            
            # Show success message
            count = len(self.published_posts)
            messagebox.showinfo(
                "Thành Công", 
                f"✅ Đã copy {count} bài viết!\n\nĐịnh dạng:\nTiêu đề - Link"
            )
            
            print(f"[COPY] Copied {count} posts to clipboard")
            
        except Exception as e:
            print(f"[COPY] Error: {e}")
            messagebox.showerror("Lỗi", f"Không thể copy: {e}")
    
    def kill_chrome_processes(self):
        """Kill all Chrome and ChromeDriver processes to free up resources"""
        try:
            import subprocess
            import os
            
            # Update status
            self.status_label.configure(text="🔪 Đang kill Chrome...", text_color=self.colors['warning'])
            self.update()
            
            # Method 1: Use batch file if exists
            bat_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kill_chrome.bat")
            if os.path.exists(bat_file):
                try:
                    subprocess.run([bat_file], shell=True, capture_output=True, timeout=5)
                except:
                    pass
            
            # Method 2: Direct taskkill commands
            processes = ['chrome.exe', 'chromedriver.exe', 'msedge.exe', 'msedgedriver.exe']
            killed_count = 0
            
            for process in processes:
                try:
                    result = subprocess.run(
                        ['taskkill', '/F', '/IM', process, '/T'],
                        capture_output=True,
                        text=True,
                        timeout=3
                    )
                    if result.returncode == 0:
                        killed_count += 1
                        print(f"[KILL] Killed: {process}")
                except Exception as e:
                    print(f"[KILL] Error killing {process}: {e}")
            
            # Show result
            if killed_count > 0:
                self.status_label.configure(
                    text=f"✅ Đã kill {killed_count} process Chrome!", 
                    text_color=self.colors['success']
                )
                messagebox.showinfo(
                    "Thành Công",
                    f"✅ Đã kill {killed_count} Chrome processes!\n\nMáy sẽ mượt hơn rồi đó! 🚀"
                )
            else:
                self.status_label.configure(
                    text="ℹ️ Không có Chrome process nào đang chạy",
                    text_color=self.colors['text_secondary']
                )
                messagebox.showinfo(
                    "Thông Báo",
                    "Không tìm thấy Chrome process nào đang chạy."
                )
            
            # Reset status after 3s
            self.after(3000, lambda: self.status_label.configure(
                text="✅ Sẵn sàng", 
                text_color=self.colors['success']
            ))
            
            print(f"[KILL] Chrome cleanup completed. Killed {killed_count} processes.")
            
        except Exception as e:
            print(f"[KILL] Error: {e}")
            self.status_label.configure(text="❌ Lỗi kill Chrome", text_color=self.colors['danger'])
            messagebox.showerror("Lỗi", f"Không thể kill Chrome:\n{e}")
    
    def add_published_post(self, title, link):
        """Add a published post to the list for copying"""
        try:
            self.published_posts.append({
                'title': title,
                'link': link
            })
            print(f"[PUBLISHED] Added: {title} - {link}")
        except Exception as e:
            print(f"[PUBLISHED] Error adding post: {e}")

    def logout(self):
        self.destroy()
        # Logic restart app...

# Mock Controller để test giao diện
class MockController:
    username = "AdminUser"
    def handle_login(self, s, u, p, headless):
        print(f"Login: {s}, {u}, Headless={headless}")
        # Giả lập login thành công sau 1s
        app.after(1000, app.login_success)
        
    def handle_post_request(self, data, is_batch=False):
        print(f"Posting: {data.title}")
        # Giả lập post thành công
        app.after(1500, lambda: app.on_post_finished(True, f"https://site.com/{data.title.replace(' ','-')}", is_batch))

if __name__ == "__main__":
    controller = MockController()
    app = GUIView(controller)
    app.mainloop()