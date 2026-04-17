"""
Animated GIF Loader for CustomTkinter
Load và animate GIF files trong CustomTkinter
"""

from PIL import Image
import customtkinter as ctk


class AnimatedGIF:
    """
    Load và animate GIF files trong CustomTkinter Label
    """
    
    def __init__(self, label: ctk.CTkLabel, gif_path: str, size: tuple = None):
        """
        Args:
            label: CTkLabel để hiển thị GIF
            gif_path: Đường dẫn đến file GIF
            size: (width, height) để resize, None = giữ nguyên size
        """
        self.label = label
        self.gif_path = gif_path
        self.size = size or (120, 120)  # Default size
        self.frames = []
        self.current_frame = 0
        self.is_playing = False
        self.delay = 100  # Default 100ms between frames
        
        self._load_gif()
    
    def _load_gif(self):
        """Load all frames from GIF"""
        try:
            gif = Image.open(self.gif_path)
            
            # Get original size for better scaling
            original_size = gif.size
            
            # Get frame count
            frame_count = 0
            try:
                while True:
                    gif.seek(frame_count)
                    frame = gif.copy().convert('RGBA')  # Convert to RGBA
                    
                    # High-quality resize with anti-aliasing
                    # Use LANCZOS for best quality (slower but better)
                    frame = frame.resize(self.size, Image.Resampling.LANCZOS)
                    
                    # Store PIL Image (not PhotoImage!)
                    self.frames.append(frame)
                    
                    frame_count += 1
            except EOFError:
                pass  # End of frames
            
            # Get delay from GIF (in milliseconds)
            try:
                self.delay = gif.info.get('duration', 100)
            except:
                self.delay = 100
            
            # OPTIMIZATION: Enforce minimum delay to prevent UI lag
            # 20ms is too fast (50fps) for Tkinter, causing lag.
            # 0ms causes infinite loop flooding.
            # Cap at ~20-30fps max (33ms-50ms)
            if self.delay < 50: 
                print(f"[GIF] ⚠️ Delay too low ({self.delay}ms), adjusting to 60ms for smooth UI")
                self.delay = 60
            
            print(f"[GIF] ✅ Loaded {len(self.frames)} frames from {self.gif_path}")
            print(f"[GIF] ⏱️ Delay: {self.delay}ms")
            
        except Exception as e:
            print(f"[GIF] ❌ Error loading {self.gif_path}: {e}")
            self.frames = []
    
    def play(self):
        """Start playing the GIF animation"""
        if not self.frames:
            print("[GIF] ⚠️ No frames to play!")
            return
        
        self.is_playing = True
        self._animate()
    
    def stop(self):
        """Stop playing the GIF animation"""
        self.is_playing = False
    
    def _animate(self):
        """Animate the GIF (internal)"""
        if not self.is_playing or not self.frames:
            return
        
        try:
            # Create CTkImage from current frame
            current_pil_image = self.frames[self.current_frame]
            ctk_image = ctk.CTkImage(
                light_image=current_pil_image,
                dark_image=current_pil_image,
                size=self.size
            )
            
            # Update label
            self.label.configure(image=ctk_image, text="")
            
            # Keep reference to prevent garbage collection
            self.label._current_gif_image = ctk_image
            
        except Exception as e:
            print(f"[GIF] ⚠️ Animation error: {e}")
        
        # Move to next frame
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        
        # Schedule next frame
        self.label.after(self.delay, self._animate)


# ===== USAGE EXAMPLE =====
if __name__ == "__main__":
    import customtkinter as ctk
    
    # Create window
    root = ctk.CTk()
    root.title("Animated GIF Demo")
    root.geometry("400x400")
    
    # Create label for GIF
    gif_label = ctk.CTkLabel(root, text="")
    gif_label.pack(pady=20)
    
    # Load and play GIF
    gif_path = "animaition/Hello Kitty Pink GIF.gif"
    animated_gif = AnimatedGIF(gif_label, gif_path, size=(200, 200))
    animated_gif.play()
    
    # Status label
    status = ctk.CTkLabel(root, text="Playing Hello Kitty GIF! 🐱💕")
    status.pack(pady=10)
    
    root.mainloop()
