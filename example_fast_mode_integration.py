"""
Example: How to integrate Fast API into your existing controller

This shows how to add a "Fast Mode" option to your GUI
"""

from model.wp_model import BlogPost, WPAutoClient, WPFastClient
import time


class AppControllerWithFastMode:
    """
    Enhanced controller with Fast Mode option
    """
    
    def __init__(self):
        # ... existing init code ...
        self.fast_mode_enabled = False  # NEW: Fast mode toggle
        self.fast_client = None  # NEW: Reusable fast client
    
    def toggle_fast_mode(self, enabled):
        """
        Enable/disable fast mode
        Called from GUI checkbox or button
        """
        self.fast_mode_enabled = enabled
        
        if enabled:
            print("[CONTROLLER] ⚡ FAST MODE ENABLED")
            self.view.log("⚡ Chế độ nhanh đã BẬT (1-2 giây/bài)")
        else:
            print("[CONTROLLER] 🐢 Normal mode")
            self.view.log("🐢 Chế độ thường (5-10 giây/bài)")
            
            # Close fast client if exists
            if self.fast_client:
                self.fast_client.close()
                self.fast_client = None
    
    def _process_post_fast(self, data, is_batch=False):
        """
        FAST MODE version of _process_post
        Uses WPFastClient instead of WPAutoClient
        """
        try:
            from model.wp_model import BlogPost
            
            # Create blog post (same as before)
            post = BlogPost(
                title=data.title,
                video_url=data.video_url,
                image_url=data.image_url,
                raw_content=data.content
            )
            post.generate_seo_content()
            
            # Use FAST CLIENT
            if self.fast_mode_enabled:
                print("[CONTROLLER] 🚀 Using FAST MODE")
                self.view.after(0, lambda: self.view.log("🚀 Đang đăng bài (CHẾ ĐỘ NHANH)..."))
                
                # Create or reuse fast client
                if not self.fast_client:
                    self.fast_client = WPFastClient(
                        self.site_url, 
                        self.username, 
                        self.password
                    )
                
                # Measure time
                start_time = time.time()
                
                # Post with fast client
                success, message = self.fast_client.post_article(
                    post,
                    reuse_client=self.fast_client.get_client()  # Reuse for speed
                )
                
                elapsed = time.time() - start_time
                
                # Update UI with timing
                self.view.after(0, lambda s=success, m=message, t=elapsed: 
                    self.view.log(f"{'✅' if s else '❌'} {m} (⏱️ {t:.2f}s)")
                )
            
            else:
                # Use normal mode (WPAutoClient)
                print("[CONTROLLER] 🐢 Using NORMAL MODE")
                self.view.after(0, lambda: self.view.log("🐢 Đang đăng bài (chế độ thường)..."))
                
                auto_client = WPAutoClient(
                    self.site_url, 
                    self.username, 
                    self.password
                )
                
                success, message = auto_client.post_article(post)
                
                self.view.after(0, lambda s=success, m=message: 
                    self.view.log(f"{'✅' if s else '❌'} {m}")
                )
            
            # Update UI
            self.view.after(0, lambda s=success, m=message, b=is_batch, t=post.title: 
                self.view.on_post_finished(s, m, b, t)
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            err_title = data.title if hasattr(data, 'title') else "Error Post"
            self.view.after(0, lambda msg=str(e), b=is_batch, t=err_title: 
                self.view.on_post_finished(False, msg, b, t)
            )


# ============================================================================
# GUI INTEGRATION EXAMPLE
# ============================================================================

"""
Add this to your GUI (view/gui_view.py):

1. Add checkbox in settings:

    self.fast_mode_var = tk.BooleanVar(value=False)
    fast_mode_check = tk.Checkbutton(
        settings_frame,
        text="⚡ Chế độ nhanh (Fast Mode - 1-2s/bài)",
        variable=self.fast_mode_var,
        command=self.on_fast_mode_toggle
    )
    fast_mode_check.pack()

2. Add callback:

    def on_fast_mode_toggle(self):
        enabled = self.fast_mode_var.get()
        self.controller.toggle_fast_mode(enabled)

3. Update handle_post_request in controller:

    def handle_post_request(self, data, is_batch=False):
        # Inject session credentials
        data.site_url = self.site_url
        data.username = self.username
        data.password = self.password

        # Choose method based on fast mode
        if self.fast_mode_enabled:
            thread = threading.Thread(target=self._process_post_fast, args=(data, is_batch))
        else:
            thread = threading.Thread(target=self._process_post, args=(data, is_batch))
        
        thread.start()
"""


# ============================================================================
# BATCH PROCESSING EXAMPLE
# ============================================================================

def batch_post_with_fast_mode(controller, posts_data):
    """
    Example: Batch post with fast mode
    
    Args:
        controller: AppController instance
        posts_data: List of post data objects
    """
    if controller.fast_mode_enabled:
        print("[BATCH] 🚀 Using PARALLEL FAST MODE")
        
        from model.wp_rest_api_fast import WordPressBatchProcessor
        
        # Create blog posts
        blog_posts = []
        for data in posts_data:
            post = BlogPost(
                title=data.title,
                video_url=data.video_url,
                raw_content=data.content
            )
            post.generate_seo_content()
            blog_posts.append(post)
        
        # Process in parallel
        processor = WordPressBatchProcessor(
            controller.site_url,
            controller.username,
            controller.password,
            max_workers=3  # 3 posts at once
        )
        
        start_time = time.time()
        results = processor.post_articles_parallel(blog_posts)
        elapsed = time.time() - start_time
        
        print(f"[BATCH] ✅ Completed {len(results)} posts in {elapsed:.2f}s")
        print(f"[BATCH] ⏱️ Average: {elapsed/len(results):.2f}s per post")
        
        return results
    
    else:
        print("[BATCH] 🐢 Using SEQUENTIAL NORMAL MODE")
        
        # Process one by one (slower)
        results = []
        for data in posts_data:
            # ... normal processing ...
            pass
        
        return results
