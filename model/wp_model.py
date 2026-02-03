"""
WordPress Model - BlogPost class for content generation
"""

class BlogPost:
    """
    Represents a blog post with title, video, image, and content.
    Handles SEO content generation with video embeds.
    """
    
    def __init__(self, title, video_url="", image_url="", raw_content="", content_images=None, featured_media_id=None):
        self.title = title
        self.video_url = video_url
        self.image_url = image_url
        self.raw_content = raw_content
        self.content_images = content_images or []
        self.content = ""
        self.theme = "none"  # Default theme: no theme (use WordPress default)
        self.featured_media_id = featured_media_id  # NEW: Media ID for REST API
    
    def generate_seo_content(self):
        """
        Generate SEO-optimized content using SEO template.
        If raw_content is provided, use it directly.
        Otherwise, auto-generate content with SEO structure.
        """
        print(f"[WP_MODEL] generate_seo_content called")
        print(f"[WP_MODEL] video_url: {self.video_url}")
        print(f"[WP_MODEL] raw_content length: {len(self.raw_content) if self.raw_content else 0}")
        print(f"[WP_MODEL] content_images: {len(self.content_images)}")
        
        # Get theme
        theme_id = getattr(self, 'theme', 'none')  # Default to 'none' instead of 'supercar'
        print(f"[WP_MODEL] Using theme: {theme_id}")

        
        # If theme is "none", use old raw HTML method
        if theme_id == 'none':
            print(f"[WP_MODEL] Theme is 'none', using raw HTML (no CSS)")
            
            # --- AUTO FORMATTING FIX ---
            # Fix text merging issue: Convert single newlines to double newlines to force paragraphs
            if self.raw_content and '<p>' not in self.raw_content and len(self.raw_content) > 0:
                print(f"[WP_MODEL] Plain text detected. Auto-formatting paragraphs...")
                
                # 1. Normalize line endings
                formatted_text = self.raw_content.replace('\r\n', '\n')
                
                # 2. Check if text has ANY double newlines (paragraphs)
                if '\n\n' not in formatted_text:
                     # 3. If NO double newlines exist, assume single newlines are meant to be paragraphs
                     # Convert EVERY single newline to double newline
                     print(f"[WP_MODEL] No double newlines found. Converting single newlines to paragraphs.")
                     formatted_text = formatted_text.replace('\n', '\n\n')
                else:
                     # If mixed, ensure they represent paragraphs correctly
                     print(f"[WP_MODEL] Double newlines detected. Preserving structure.")
                     pass
                
                self.raw_content = formatted_text
            # ---------------------------
            
            self._generate_content_fallback()
            return
        
        # Try to use theme manager for styled content
        try:
            from model.theme_manager import ThemeManager
            manager = ThemeManager()
            
            # If user provided custom content, use it
            if self.raw_content and self.raw_content.strip():
                print(f"[WP_MODEL] Using custom content with theme wrapper")
                # Use theme manager to wrap custom content
                self.content = manager.generate_content(
                    title=self.title,
                    video_url=self.video_url,
                    featured_image=self.image_url,
                    content_images=self.content_images,
                    custom_content=self.raw_content,
                    theme_id=theme_id
                )
            else:
                print(f"[WP_MODEL] Auto-generating content with theme")
                # Auto-generate content using theme
                self.content = manager.generate_content(
                    title=self.title,
                    video_url=self.video_url,
                    featured_image=self.image_url,
                    content_images=self.content_images,
                    theme_id=theme_id
                )
            
            print(f"[WP_MODEL] ✅ Theme content generated: {len(self.content)} chars")
            return
            
        except Exception as e:
            print(f"[WP_MODEL] ⚠️ Theme manager failed: {e}, using fallback")
            import traceback
            traceback.print_exc()
        
        # Fallback to old method if theme manager fails
        self._generate_content_fallback()
    
    def _generate_content_fallback(self):
        """Fallback method using old content generation"""
        print(f"[WP_MODEL] Using fallback content generation")
        
        # If user provided custom content, use it
        if self.raw_content and self.raw_content.strip():
            print(f"[WP_MODEL] Using raw_content path")
            
            # Check if we have content images
            # First image = featured image (full width at top)
            # Remaining images = content gallery (small, at bottom)
            content = self.raw_content
            
            if self.content_images and len(self.content_images) > 0:
                # Extract first image as featured image metadata, but DO NOT insert into body
                # because WordPress themes usually display the Featured Image automatically at the top.
                featured_img_url = self.content_images[0]
                remaining_images = self.content_images[1:] if len(self.content_images) > 1 else []
                
                print(f"[WP_MODEL] Identified featured image: {featured_img_url}")
                print(f"[WP_MODEL] NOT inserting into body to avoid duplication (Theme handles it)")
                
                # FIX: Inject OG Meta Tag for scrapers that look at body content
                # This helps ensure the correct thumbnail is picked if they scan the body
                meta_tag = f'<!-- SEO Hint --><meta property="og:image" content="{featured_img_url}" /><div style="display:none;"><img src="{featured_img_url}" alt="featured_hidden"></div>'
                content = meta_tag + content 
                
                # Store remaining images for gallery insertion later
                self.content_images = remaining_images
                print(f"[WP_MODEL] Remaining images for gallery: {len(remaining_images)}")
                
                # IMPORTANT: Assign to self.content so it's preserved
                self.content = content
                
                # Store remaining images for gallery insertion later
                self.content_images = remaining_images
                print(f"[WP_MODEL] Remaining images for gallery: {len(remaining_images)}")
            else:
                # No images, just use raw content
                self.content = content
            
            # Nếu có content, chèn video sau 2 đoạn văn đầu tiên
            if self.video_url:
                print(f"[WP_MODEL] Generating video block...")
                video_block = self._generate_video_block(self.video_url)
                if video_block:
                    print(f"[WP_MODEL] Video block generated: {len(video_block)} chars")
                    content = self.content
                    
                    # Xác định điểm bắt đầu tìm kiếm (tránh Featured Image Block ở đầu)
                    search_start_pos = 0
                    
                    # Tìm khối HTML đầu tiên (chính là Featured Image)
                    first_html_end = content.find('<!-- /wp:html -->')
                    
                    target_pos = -1
                    insert_method = "after_intro"
                    
                    if first_html_end != -1:
                        # Bắt đầu tìm kiếm từ sau ảnh bìa
                        search_start = first_html_end + len('<!-- /wp:html -->')
                        
                        # Tìm điểm kết thúc đoạn văn đầu tiên (Intro)
                        min_text_length = 50
                        subset_content = content[search_start:]
                        
                        # Tìm các dấu hiệu ngắt đoạn
                        p_end = subset_content.find('</p>')
                        wp_p_end = subset_content.find('<!-- /wp:paragraph -->')
                        double_newline = subset_content.find('\n\n')
                        
                        # Lấy vị trí nhỏ nhất (gần nhất) nhưng phải > min_text_length
                        candidates = []
                        if p_end != -1 and p_end > min_text_length: candidates.append(p_end + 4) # +4 cho </p>
                        if wp_p_end != -1 and wp_p_end > min_text_length: candidates.append(wp_p_end + len('<!-- /wp:paragraph -->'))
                        if double_newline != -1 and double_newline > min_text_length: candidates.append(double_newline + 2)
                        
                        if candidates:
                            target_pos = search_start + min(candidates)
                            print(f"[WP_MODEL] ✅ Found insertion point after first paragraph at pos: {target_pos}")
                            insert_method = "after_paragraph"
                        else:
                            print("[WP_MODEL] ⚠️ No clear paragraph break found. Inserting after Featured Image.")
                            target_pos = search_start
                            insert_method = "after_image"
                    else:
                        # Fallback cũ
                        if '<!-- /wp:spacer -->' in content:
                           end_marker = '<!-- /wp:spacer -->'
                           target_pos = content.find(end_marker) + len(end_marker)
                        else:
                           target_pos = min(len(content), 500)
                           insert_method = "fallback_pos"

                    # Thực hiện chèn video_block
                    if target_pos != -1:
                        content_before = content[:target_pos]
                        content_after = content[target_pos:]
                        
                        # Đóng gói video vào block HTML nếu chưa có
                        if "<!-- wp:html -->" not in video_block:
                            final_video_html = f'\n\n<!-- wp:html -->\n{video_block}\n<!-- /wp:html -->\n\n'
                        else:
                             final_video_html = f'\n\n{video_block}\n\n'
                        
                        self.content = content_before + final_video_html + content_after
                        print(f"[WP_MODEL] ✅ Video inserted successfully ({insert_method})!")
                    else:
                        print(f"[WP_MODEL] ⚠️ Could not determine video insertion point. Appending to end.")
                        self.content = content + f'\n\n<!-- wp:html -->\n{video_block}\n<!-- /wp:html -->'

                else:
                    print(f"[WP_MODEL] Video block generation failed")
                    self.content = self.raw_content
            else:
                print(f"[WP_MODEL] No video_url provided")
                self.content = self.raw_content
            
            # Insert content images if provided (after video insertion)
            # Insert each image SEPARATELY at different positions (not as a gallery)
            if self.content_images and len(self.content_images) > 0:
                print(f"[WP_MODEL] Inserting {len(self.content_images)} content image(s) separately...")
                
                content = self.content
                
                # Find paragraph positions
                paragraphs = []
                pos = 0
                while True:
                    p_end = content.find('</p>', pos)
                    if p_end == -1:
                        break
                    paragraphs.append(p_end + 4)  # Position after </p>
                    pos = p_end + 4
                
                insertion_mode = 'char' # Default to char index insertion (for <p> tags or large text)
                
                if not paragraphs:
                    # No <p> tags, try newlines
                    print(f"[WP_MODEL] No </p> found, checking newlines...")
                    lines = content.split('\n')
                    
                    # Check if text is a huge block without newlines (e.g. < 5 lines but long text)
                    if len(lines) < 5 and len(content) > 500:
                        print(f"[WP_MODEL] Text is a large block. Finding sentence endings to insert images...")
                        # Strategy: Insert at 1/3, 2/3 positions at NEAREST PERIOD
                        chunk_size = len(content) // (len(self.content_images) + 1)
                        insert_positions = []
                        
                        current_pos = 0
                        for _ in range(len(self.content_images)):
                            target = current_pos + chunk_size
                            # Find period near target
                            period_pos = content.find('. ', target)
                            if period_pos == -1: period_pos = content.find('.', target)
                            
                            if period_pos != -1:
                                insert_positions.append(period_pos + 1) # Insert after period
                                current_pos = period_pos
                            else:
                                # Fallback: just use length
                                insert_positions.append(target)
                                current_pos = target
                        insertion_mode = 'char'
                    else:
                        # Normal newline splitting
                        print(f"[WP_MODEL] Using newlines for image insertion")
                        insert_positions = [
                            len(lines) // 3,
                            2 * len(lines) // 3,
                            len(lines) - 1
                        ]
                        insertion_mode = 'line' # Use line insertion
                else:
                    # Insert images after paragraphs 2, 4, 6 (or available positions)
                    insert_positions = []
                    target_paragraphs = [2, 4, 6, 8, 10]  # After 2nd, 4th, 6th paragraph
                    for target in target_paragraphs:
                        if target < len(paragraphs):
                            insert_positions.append(paragraphs[target])
                        if len(insert_positions) >= len(self.content_images):
                            break
                    insertion_mode = 'char' # Paragraph positions are char indices
                
                # Insert images from back to front (to preserve positions)
                for i in range(min(len(self.content_images), len(insert_positions)) - 1, -1, -1):
                    img_url = self.content_images[i]
                    if not img_url or not img_url.strip():
                        continue
                    
                    # Create single image HTML (centered, medium size)
                    img_html = f'''
<!-- wp:html -->
<div style="text-align: center; margin: 60px 0 40px 0;">
    <img src="{img_url}" alt="" style="width: 100%; height: auto; max-width: 600px; border-radius: 8px;" />
</div>
<!-- /wp:html -->

<!-- wp:spacer {{"height":"20px"}} -->
<div style="height:20px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->
'''
                    
                    if insertion_mode == 'char':
                        # Insert at character position
                        insert_pos = insert_positions[i]
                        # Add double newline if inserting into text block to force break
                        if not paragraphs:
                             content = content[:insert_pos] + "\n\n" + img_html + "\n\n" + content[insert_pos:]
                        else:
                             content = content[:insert_pos] + img_html + content[insert_pos:]
                        
                        print(f"[WP_MODEL] Inserted image {i+1} at char position {insert_pos}")
                    else:
                        # Insert at line position (list of strings)
                        lines = content.split('\n')
                        insert_line = insert_positions[i]
                        lines.insert(insert_line, img_html)
                        content = '\n'.join(lines)
                        print(f"[WP_MODEL] Inserted image {i+1} at line {insert_line}")
                
                self.content = content
            
            print(f"[WP_MODEL] Final content length: {len(self.content)}")
            return self.content
        
        # Auto-generate content with video embed - SEO OPTIMIZED STRUCTURE (ENGLISH RANDOMIZED)
        print(f"[WP_MODEL] Using auto-generate path (SEO Standard - English)")
        
        import random
        
        # --- DEFINING TEMPLATES ---
        
        # Template 1: Breaking News / Trending
        t_news = {
            "intro_h2": f"Breaking News: {self.title}",
            "intro_p1": f"Welcome to our latest coverage on <strong>{self.title}</strong>. This topic has been trending across social media platforms and sparking conversations worldwide.",
            "intro_p2": "In this report, we break down the key details, analyze the footage, and provide you with everything you need to know about this developing story.",
            "highlights_h2": "Key Highlights",
            "highlights_list": [
                f"<strong>Viral Content:</strong> Experience the moment everyone is talking about regarding {self.title}.",
                "<strong>In-Depth Analysis:</strong> A closer look at the details you might have missed.",
                "<strong>Global Impact:</strong> How this event is resonating with audiences everywhere.",
                "<strong>Expert Opinions:</strong> Insights and reactions from the community."
            ],
            "detail_h2": "Detailed Report",
            "detail_p1": "Beyond the headlines, this video offers a unique perspective that clarifies the context of the situation. The footage speaks for itself, capturing specific moments that define the narrative.",
            "detail_p2": "Observers have noted the significance of these events. Whether you are following this story closely or just tuning in, the video above provides the most accurate visual representation available.",
            "faq_h2": "Frequently Asked Questions",
            "faq_q1": "What is the main focus of this video?",
            "faq_a1": "The video focuses on the core events surrounding the title topic, offering real-time footage and context.",
            "faq_q2": "Where can I find more updates?",
            "faq_a2": "Stay tuned to our website for follow-up reports and detailed analysis as this story unfolds.",
            "conclusion_h2": "Conclusion",
            "conclusion_p1": f"We hope this report on <em>{self.title}</em> has kept you informed. Information is power, and staying updated with accurate visuals is more important than ever.",
            "conclusion_p2": "Thank you for reading. Don't forget to share this article and leave your thoughts in the comments below!"
        }

        # Template 2: Supercars / Speed / Luxury
        t_cars = {
            "intro_h2": f"Review & Impressions: {self.title}",
            "intro_p1": f"Get ready for high-octane action with <strong>{self.title}</strong>. Today, we are diving into the world of performance, speed, and engineering excellence.",
            "intro_p2": "Whether you are a petrolhead or just admire automotive beauty, this video showcases the incredible details that set this machine apart from the rest.",
            "highlights_h2": "Performance & Features",
            "highlights_list": [
                f"<strong>Stunning Visuals:</strong> Witness the sleek design and aesthetics of {self.title}.",
                "<strong>Raw Power:</strong> Experience the sound and fury of top-tier engineering.",
                "<strong>Driving Dynamics:</strong> A look at how it handles on the road (or track).",
                "<strong>Luxury Details:</strong> The craftsmanship that defines this class of vehicle."
            ],
            "detail_h2": "Behind the Wheel",
            "detail_p1": "This video isn't just about specs; it's about the feeling. The acceleration, the braking, and the sheer presence of the vehicle are captured perfectly in the footage above.",
            "detail_p2": "From the roar of the engine to the subtle design curves, every second is a treat for automotive enthusiasts. It highlights why this sector of the industry continues to captivate millions.",
            "faq_h2": "Enthusiast Q&A",
            "faq_q1": "Is this a new model release?",
            "faq_a1": "This video features specific highlights that may be a new release, a custom build, or a classic review.",
            "faq_q2": "What makes this video special?",
            "faq_a2": "It captures the visceral experience of the vehicle, going beyond simple static images.",
            "conclusion_h2": "Final Thoughts",
            "conclusion_p1": f"<em>{self.title}</em> is truly a marvel. Videos like this remind us why we love automotive culture so much.",
            "conclusion_p2": "Ride safe and stay tuned for more supercar reviews, speed tests, and luxury showcases!"
        }

        # Template 3: General Viral / Entertainment (Fallback)
        t_viral = {
            "intro_h2": f"Must Watch: {self.title}",
            "intro_p1": f"This is the video that has captured the internet's attention: <strong>{self.title}</strong>. If you haven't seen it yet, you are in for a treat.",
            "intro_p2": "We have curated this content specially for our viewers, ensuring you get the best quality and the most entertaining moments right here.",
            "highlights_h2": "Why You Should Watch",
            "highlights_list": [
                f"<strong>Entertainment Value:</strong> Top-tier content related to {self.title}.",
                "<strong>Unique Moments:</strong> Scenes that you won't find anywhere else.",
                "<strong>High Quality:</strong> Curated for the best viewing experience.",
                "<strong>Trending Topic:</strong> Join the thousands who are watching this right now."
            ],
            "detail_h2": "The Full Story",
            "detail_p1": "Content like this brings communities together. It allows us to share a laugh, a moment of awe, or a new discovery. The creators have done an amazing job capturing the essence of the subject.",
            "detail_p2": "As you watch, pay attention to the details. It's often the small things that make these videos go viral and stay memorable for a long time.",
            "faq_h2": "Common Questions",
            "faq_q1": "Why is this trending?",
            "faq_a1": "Due to its engaging nature and high relevance to current interests.",
            "faq_q2": "Can I share this?",
            "faq_a2": "Absolutely! We encourage you to share this page with friends and family so they can enjoy it too.",
            "conclusion_h2": "Wrap Up",
            "conclusion_p1": f"That's a wrap on <em>{self.title}</em>. We hope you enjoyed watching it as much as we enjoyed sharing it with you.",
            "conclusion_p2": "Bookmark our site for your daily dose of viral videos and entertainment. See you next time!"
        }

        # --- RANDOM SELECTION ---
        # 40% News, 40% Cars, 20% Viral
        weights = [0.4, 0.4, 0.2] 
        template = random.choices([t_news, t_cars, t_viral], weights=weights, k=1)[0]
        
        content_parts = []
        
        # 1. INTRODUCTION Section with styled heading
        content_parts.append(f"""<!-- wp:heading -->
<h2 class="wp-block-heading">{template['intro_h2']}</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>{template['intro_p1']}</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>{template['intro_p2']}</p>
<!-- /wp:paragraph -->
""")
        
        # 2. VIDEO EMBED (Placed prominently after intro)
        if self.video_url:
            video_block = self._generate_video_block(self.video_url)
            if video_block:
                content_parts.append(video_block)
                print(f"[WP_MODEL] Added video block to auto-generated content")

        # 3. KEY HIGHLIGHTS Section with simple list
        list_items = "\n".join([f"<li>{item}</li>" for item in template['highlights_list']])
        content_parts.append(f"""
<!-- wp:heading -->
<h2 class="wp-block-heading">✨ {template['highlights_h2']}</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul>
{list_items}
</ul>
<!-- /wp:list -->
""")

        # 4. DETAILED ANALYSIS Section
        content_parts.append(f"""
<!-- wp:heading -->
<h2 class="wp-block-heading">📊 {template['detail_h2']}</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>{template['detail_p1']}</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>{template['detail_p2']}</p>
<!-- /wp:paragraph -->
""")

        # 5. FAQ Section with simple format
        content_parts.append(f"""
<!-- wp:heading -->
<h2 class="wp-block-heading">❓ {template['faq_h2']}</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p><strong>1. {template['faq_q1']}</strong><br>
{template['faq_a1']}</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>2. {template['faq_q2']}</strong><br>
{template['faq_a2']}</p>
<!-- /wp:paragraph -->
""")

        # 6. CONCLUSION & CTA
        content_parts.append(f"""
<!-- wp:heading -->
<h2 class="wp-block-heading">🎯 {template['conclusion_h2']}</h2>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>{template['conclusion_p1']}</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>{template['conclusion_p2']}</p>
<!-- /wp:paragraph -->

<!-- wp:separator {{"className":"is-style-wide"}} -->
<hr class="wp-block-separator has-alpha-channel-opacity is-style-wide"/>
<!-- /wp:separator -->
""")
        
        self.content = "\n".join(content_parts)
        print(f"[WP_MODEL] Auto-generated SEO content length: {len(self.content)}")
        return self.content
    
    def _generate_video_block(self, video_url):
        """
        Generate WordPress Gutenberg video embed block
        Supports:
        1. Full Vimeo embed code (with <div> wrapper and <script>)
        2. Facebook URL (plain URL - let WordPress handle oEmbed)
        3. Facebook iframe (if provided)
        4. Facebook SDK embed (with script)
        5. Simple iframe URL
        """
        
        # Check if this is full Vimeo embed code (with div wrapper)
        if '<div style="padding:' in video_url and '<script' in video_url:
            print("[WP_MODEL] Using full Vimeo embed code (with wrapper)")
            # Wrap in WordPress HTML block
            return f"""<!-- wp:html -->
{video_url}
<!-- /wp:html -->

<!-- wp:spacer {{"height":"20px"}} -->
<div style="height:20px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->"""
        
        # Check if this is Facebook URL (plain URL - use WordPress oEmbed)
        if ('facebook.com' in video_url or 'fb.watch' in video_url) and '<' not in video_url:
            print("[WP_MODEL] Using Facebook URL with WordPress oEmbed")
            # Use WordPress embed block - let WordPress handle it
            return f"""<!-- wp:embed {{"url":"{video_url}","type":"video","providerNameSlug":"facebook","responsive":true}} -->
<figure class="wp-block-embed is-type-video is-provider-facebook wp-block-embed-facebook"><div class="wp-block-embed__wrapper">
{video_url}
</div></figure>
<!-- /wp:embed -->

<!-- wp:spacer {{"height":"20px"}} -->
<div style="height:20px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->"""
        
        # Check if this is Facebook iframe or SDK embed
        if 'facebook.com/plugins/video.php' in video_url or 'fb-video' in video_url or 'facebook-jssdk' in video_url:
            print("[WP_MODEL] Using Facebook embed code (iframe or SDK)")
            # Use as-is, NO wrapper, NO modification
            return f"""<!-- wp:html -->
{video_url}
<!-- /wp:html -->

<!-- wp:spacer {{"height":"20px"}} -->
<div style="height:20px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->"""
        
        # Otherwise, use simple iframe embed with responsive wrapper (for Vimeo, YouTube, etc.)
        print("[WP_MODEL] Using simple iframe embed with responsive wrapper")
        
        # For Vimeo, add background=1 to hide thumbnail (prevent theme from using it as featured image)
        final_video_url = video_url
        if 'vimeo.com' in video_url:
            # REMOVED background=1 because it mutes video and disables controls
            # User wants sound and ability to pause
            print(f"[WP_MODEL] Keeping original Vimeo URL (Controls enabled)")
            pass
        
        return f"""<!-- wp:html -->
<div class="video-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 30px auto 60px auto;">
    <iframe src="{final_video_url}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>
</div>
<!-- /wp:html -->

<!-- wp:spacer {{"height":"20px"}} -->
<div style="height:20px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->"""


class WordPressClient:
    """
    Placeholder for WordPress client (not used in current implementation).
    The actual posting is handled by SeleniumWPClient.
    """
    pass


# ============================================================================
# AUTO-SELECT BEST POSTING METHOD
# ============================================================================

from model.selenium_wp import SeleniumWPClient
from model.wp_rest_api import WordPressRESTClient
from model.wp_rest_api_fast import WordPressRESTClientFast

class WPAutoClient:
    """
    Automatically selects the best WordPress posting method:
    1. REST API (fastest, most reliable) - if available
    2. Selenium + Classic Editor (fallback) - if REST API blocked
    """
    
    def __init__(self, site_url, username, password):
        self.site_url = site_url
        self.username = username
        self.password = password
        self.client = None
        self.method = None  # 'rest_api' or 'selenium'
    
    def post_article(self, blog_post, reuse_selenium_client=None):
        """
        Post article to WordPress - automatically selects best method
        
        Priority:
        1. REST API (fastest, most reliable)
        2. Selenium + Classic Editor (fallback)
        
        Args:
            blog_post: BlogPost object with title, content, image_url
            reuse_selenium_client: Existing SeleniumWPClient to reuse (optional)
            
        Returns:
            tuple: (success: bool, result: str)
        """
        try:
            # METHOD 1: Try REST API first (BEST) - AGGRESSIVE MODE
            print("[WP_AUTO] ========================================")
            print("[WP_AUTO] Attempting REST API method (AGGRESSIVE)...")
            print("[WP_AUTO] ========================================")
            
            rest_client = WordPressRESTClient(self.site_url, self.username, self.password)
            
            # Test if REST API is available - AGGRESSIVE MODE (always try)
            is_available, status_code, message = rest_client.test_api_availability(aggressive=True)
            
            if is_available:
                print("[WP_AUTO] ✅ REST API mode enabled (aggressive)")
                self.method = 'rest_api'
                self.client = rest_client
                
                success, result = rest_client.post_article(blog_post)
                
                if success:
                    print(f"[WP_AUTO] ✅ REST API method successful!")
                    print(f"[WP_AUTO] Post URL: {result}")
                    return True, result
                else:
                    print(f"[WP_AUTO] ⚠️ REST API method failed: {result}")
                    print("[WP_AUTO] Falling back to Selenium method...")
            else:
                print(f"[WP_AUTO] ⚠️ REST API not available ({status_code}): {message}")
                print("[WP_AUTO] Falling back to Selenium method...")
            
            # METHOD 2: Fallback to Selenium (if REST API failed or unavailable)
            print("[WP_AUTO] ========================================")
            print("[WP_AUTO] Using Selenium method...")
            print("[WP_AUTO] ========================================")
            
            self.method = 'selenium'
            
            # Reuse existing selenium client if provided (avoid re-login)
            if reuse_selenium_client and reuse_selenium_client.driver:
                print("[WP_AUTO] Reusing existing Selenium client (already logged in)")
                self.client = reuse_selenium_client
            else:
                print("[WP_AUTO] Creating new Selenium client")
                self.client = SeleniumWPClient(self.site_url, self.username, self.password)
                self.client.init_driver(headless=False)
            
            # Use Classic Editor method (most reliable for Selenium)
            success, result = self.client.post_article(blog_post, force_fresh_login=False, use_classic_editor=True)
            
            if success:
                print(f"[WP_AUTO] ✅ Selenium method successful!")
                print(f"[WP_AUTO] Post URL: {result}")
            else:
                print(f"[WP_AUTO] ❌ Selenium method failed: {result}")
            
            return success, result
            
        except Exception as e:
            print(f"[WP_AUTO] ❌ Critical error: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)
    
    def close(self):
        """Close the active client"""
        if self.client:
            self.client.close()
            print(f"[WP_AUTO] Closed {self.method} client")


# ============================================================================
# ULTRA-FAST CLIENT - For maximum speed (1 second target)
# ============================================================================

class WPFastClient:
    """
    Ultra-fast WordPress posting client
    Uses optimized REST API with aggressive mode
    Target: 1 second per API call
    
    Recommended for:
    - Batch posting (multiple posts)
    - Speed-critical operations
    - Sites with REST API enabled
    """
    
    def __init__(self, site_url, username, password):
        self.site_url = site_url
        self.username = username
        self.password = password
        self.client = None
    
    def post_article(self, blog_post, reuse_client=None):
        """
        Post article using ultra-fast REST API method
        
        Args:
            blog_post: BlogPost object with title, content, image_url
            reuse_client: Existing WordPressRESTClientFast to reuse (optional)
            
        Returns:
            tuple: (success: bool, result: str)
        """
        try:
            print("[WP_FAST] ========================================")
            print("[WP_FAST] 🚀 ULTRA-FAST MODE ACTIVATED")
            print("[WP_FAST] ========================================")
            
            # Reuse existing client if provided (avoid re-login)
            if reuse_client:
                print("[WP_FAST] Reusing existing fast client (already logged in)")
                self.client = reuse_client
            else:
                print("[WP_FAST] Creating new fast client")
                self.client = WordPressRESTClientFast(self.site_url, self.username, self.password)
            
            # Use fast posting method
            success, result = self.client.post_article_fast(blog_post)
            
            if success:
                print(f"[WP_FAST] ✅ FAST method successful!")
                print(f"[WP_FAST] Post URL: {result}")
            else:
                print(f"[WP_FAST] ❌ FAST method failed: {result}")
            
            return success, result
            
        except Exception as e:
            print(f"[WP_FAST] ❌ Critical error: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)
    
    def get_client(self):
        """Get the underlying fast client for reuse"""
        return self.client
    
    def close(self):
        """Close the active client"""
        if self.client:
            self.client.close()
            print(f"[WP_FAST] Closed fast client")

