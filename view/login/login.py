
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import sys

# Add project root to path if needed (though usually handled by main.py)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from model.utils import resource_path

from model.security import get_machine_id, get_public_ip
import os
from model.key_storage import KEYS_DB_FILE

class LoginKeyView(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Config ---
        self.title("LVC MEDIA ")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Center the window
        self.center_window(400, 300)

        # --- Theme Config (Matching Main App) ---
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.colors = {
            'primary': '#F59E0B',       # Amber 500 (Gold)
            'primary_hover': '#B45309', # Amber 700 
            'bg': '#FFFBEB',            # Amber 50
            'card': '#FFFFFF',          # White
            'text': '#111827',          # Gray 900
            'text_secondary': '#4B5563' # Gray 600
        }

        self.configure(fg_color=self.colors['bg'])
        
        # Set Icon
        try:
            icon_path = resource_path("logo.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except: pass

        # --- UI Elements ---
        self.create_widgets()
        
        # State
        self.is_verified = False
        
        # Auto-Load Key
        self.saved_key_file = "license.key"
        self.load_saved_key()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Helper to copy text to clipboard
        def copy_hwid():
            self.clipboard_clear()
            self.clipboard_append(self.hwid_label.cget("text"))
            self.update()
            messagebox.showinfo("Copied", "Machine ID copied to clipboard!")

        self.copy_hwid_cmd = copy_hwid
    def create_widgets(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        

        
        # --- HWID (Fully Hidden / Removed from UI) ---
        # User requested to remove the "Show Machine ID" button to keep it clean.
        # Just input for key is enough.

        # Logo/Title removed as requested


        self.subtitle_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Segoe UI", 12),
            text_color=self.colors['text_secondary']
        )
        self.subtitle_label.pack(pady=(0, 30))

        # Key Input
        self.key_entry = ctk.CTkEntry(
            self.main_frame,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            height=50,
            font=("Consolas", 14),
            border_color="#E5E7EB",
            fg_color="white",
            text_color="black",
            justify="center"
        )
        self.key_entry.pack(fill="x", pady=(0, 20))
        
        # Bind Enter key
        self.key_entry.bind("<Return>", self.on_verify)

        # Verify Button
        self.verify_btn = ctk.CTkButton(
            self.main_frame,
            text="xác thực",
            height=50,
            font=("Segoe UI", 14, "bold"),
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_hover'],
            text_color="white",
            command=self.on_verify
        )
        self.verify_btn.pack(fill="x", pady=(0, 20))

        # # Footer
        # self.footer_label = ctk.CTkLabel(
        #     self.main_frame,
        #     text="Need help? Contact Support",
        #     font=("Segoe UI", 11),
        #     text_color=self.colors['text_secondary'],
        #     cursor="hand2"
        # )
        # self.footer_label.pack(side="bottom")
        # self.footer_label.bind("<Button-1>", lambda e: self.open_help())

    def on_verify(self, event=None):
        key = self.key_entry.get().strip()
        
        if not key:
            messagebox.showwarning("Warning", "Please enter a valid key!")
            return

        # TODO: Implement actual key validation logic here
        # For now, we accept any key that is not empty
        if self.validate_key(key):
            # Save key locally for next time
            try:
                with open(self.saved_key_file, "w") as f:
                    f.write(key)
            except: pass
            
            self.is_verified = True
            self.destroy() # Close window to proceed
        else:
            messagebox.showerror("Error", "Invalid License Key!")

    def load_saved_key(self):
        if os.path.exists(self.saved_key_file):
            try:
                with open(self.saved_key_file, "r") as f:
                    saved_key = f.read().strip()
                if saved_key:
                    self.key_entry.insert(0, saved_key)
                    # Optional: Auto-login if valid?
                    # self.on_verify() 
            except: pass



    def validate_key(self, key):
        # 1. Download latest database from GitHub
        try:
            import urllib.request
            import json
            import time
            from model.key_storage import KEYS_DB_FILE
            
            api_download_success = False
            
            # Attempt to download via API to bypass GitHub raw caching
            try:
                from model.github_uploader import GitHubUploader
                import github_config
                if getattr(github_config, 'GITHUB_TOKEN', '') and 'YOUR_TOKEN' not in github_config.GITHUB_TOKEN:
                    uploader = GitHubUploader(
                        github_config.GITHUB_TOKEN,
                        github_config.GITHUB_REPO_OWNER,
                        github_config.GITHUB_REPO_NAME
                    )
                    # This will download the remote file and save it to the local KEYS_DB_FILE path
                    success, msg = uploader.download_file(KEYS_DB_FILE)
                    if success:
                        print("[LICENSE] Downloaded latest key database via GitHub API (Cache bypassed)")
                        api_download_success = True
            except Exception as api_err:
                print(f"[LICENSE] API download attempt failed: {api_err}")
            
            # Fallback to Raw URL if API download fails or token is not configured
            if not api_download_success:
                GITHUB_DB_URL = "https://raw.githubusercontent.com/nguyenduyducds/WebSiteWpr/master/license_keys_db.json"
                url_with_cache_buster = f"{GITHUB_DB_URL}?t={int(time.time())}"
                
                try:
                    with urllib.request.urlopen(url_with_cache_buster, timeout=5) as response:
                        online_db = json.loads(response.read().decode('utf8'))
                        
                    with open(KEYS_DB_FILE, 'w') as f:
                        json.dump(online_db, f, indent=4)
                        
                    print("[LICENSE] Downloaded latest key database from GitHub Raw URL")
                except Exception as download_err:
                    print(f"[LICENSE] Could not download from GitHub Raw: {download_err}")
                    # Continue with local file if exists
        except Exception as e:
            print(f"[LICENSE] GitHub download error: {e}")
        
        # 2. Try DB Activation (with downloaded/local database)
        try:
            from model.key_storage import KeyStorage, KEYS_DB_FILE
            
            # Check if DB file exists locally
            if os.path.exists(KEYS_DB_FILE):
                storage = KeyStorage()
                hwid = get_machine_id()
                try:
                    ip = get_public_ip()
                except:
                    ip = "Unknown"
                    
                success, msg = storage.try_activate_key(key, hwid, ip)
                if success:
                    # Upload the updated JSON back to GitHub!
                    try:
                        from model.github_uploader import GitHubUploader
                        import github_config
                        if getattr(github_config, 'GITHUB_TOKEN', '') and 'YOUR_TOKEN' not in github_config.GITHUB_TOKEN:
                            uploader = GitHubUploader(
                                github_config.GITHUB_TOKEN,
                                github_config.GITHUB_REPO_OWNER,
                                github_config.GITHUB_REPO_NAME
                            )
                            upl_success, upl_msg = uploader.upload_file(KEYS_DB_FILE, f"User Activate Key: {key[:8]}...")
                            if upl_success:
                                print(f"[LICENSE] Uploaded activated key to GitHub: {upl_msg}")
                            else:
                                print(f"[LICENSE] Failed to upload to GitHub: {upl_msg}")
                    except Exception as e:
                        print(f"[LICENSE] Could not auto-upload to GitHub: {e}")
                    
                    return True
                else:
                    messagebox.showerror("Activation Failed", msg)
                    return False
        except Exception as e:
            # Fallback if DB file issues
            pass

        # 2. Fallback to Math validation (Offline / No DB)
        try:
            from model.security import validate_key
            return validate_key(key)
        except Exception as e:
            print(f"Key validation error: {e}")
            return False

    def open_help(self):
        try:
            import webbrowser
            webbrowser.open("https://www.facebook.com/nguyenduyducds") 
        except: pass
