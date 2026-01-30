"""
WordPress Model - BlogPost class for content generation
"""

class BlogPost:
    """
    Represents a blog post with title, video, image, and content.
    Handles SEO content generation with video embeds.
    """
    
    def __init__(self, title, video_url="", image_url="", raw_content="", content_images=None):
        self.title = title
        self.video_url = video_url
        self.image_url = image_url
        self.raw_content = raw_content
        self.content_images = content_images or []
        self.content = ""
    
    def generate_seo_content(self):
        """
        Generate SEO-optimized content.
        If raw_content is provided, use it directly.
        Otherwise, auto-generate content with video embed.
        """
        print(f"[WP_MODEL] generate_seo_content called")
        print(f"[WP_MODEL] video_url: {self.video_url}")
        print(f"[WP_MODEL] raw_content length: {len(self.raw_content) if self.raw_content else 0}")
        
        # If user provided custom content, use it
        if self.raw_content and self.raw_content.strip():
            print(f"[WP_MODEL] Using raw_content path")
            # Nếu có content, chèn video sau 2 đoạn văn đầu tiên
            if self.video_url:
                print(f"[WP_MODEL] Generating video block...")
                video_block = self._generate_video_block(self.video_url)
                if video_block:
                    print(f"[WP_MODEL] Video block generated: {len(video_block)} chars")
                    # Tách nội dung thành các đoạn
                    content = self.raw_content
                    
                    # Tìm 2 đoạn văn đầu tiên (tìm 2 lần xuất hiện của </p>)
                    first_p_end = content.find('</p>')
                    print(f"[WP_MODEL] First </p> at position: {first_p_end}")
                    
                    if first_p_end != -1:
                        # Try to find the 5th paragraph to push video down (User request: "xuống tầm 3 dòng" from pos 2 -> pos 5)
                        # Find 2nd
                        p2 = content.find('</p>', first_p_end + 4)
                        if p2 != -1:
                            # Find 3rd
                            p3 = content.find('</p>', p2 + 4)
                            if p3 != -1:
                                # Find 4th
                                p4 = content.find('</p>', p3 + 4)
                                if p4 != -1:
                                    # Find 5th
                                    p5 = content.find('</p>', p4 + 4)
                                    if p5 != -1:
                                        insert_pos = p5 + 4
                                        self.content = content[:insert_pos] + "\n\n" + video_block + "\n\n" + content[insert_pos:]
                                        print(f"[WP_MODEL] Inserted video after 5th paragraph")
                                    else:
                                        # Fallback to 4th
                                        insert_pos = p4 + 4
                                        self.content = content[:insert_pos] + "\n\n" + video_block + "\n\n" + content[insert_pos:]
                                        print(f"[WP_MODEL] Inserted video after 4th paragraph")
                                else:
                                    insert_pos = p3 + 4
                                    self.content = content[:insert_pos] + "\n\n" + video_block + "\n\n" + content[insert_pos:]
                                    print(f"[WP_MODEL] Inserted video after 3rd paragraph")
                            else:
                                insert_pos = p2 + 4
                                self.content = content[:insert_pos] + "\n\n" + video_block + "\n\n" + content[insert_pos:]
                                print(f"[WP_MODEL] Inserted video after 2nd paragraph")
                        else:
                            insert_pos = first_p_end + 4
                            self.content = content[:insert_pos] + "\n\n" + video_block + "\n\n" + content[insert_pos:]
                            print(f"[WP_MODEL] Inserted video after 1st paragraph")
                    else:
                        # Fallback: Không tìm thấy thẻ </p> (có thể là plain text hoặc div)
                        # Thử tìm dấu xuống dòng \n
                        print(f"[WP_MODEL] No </p> found, trying newlines...")
                        newlines = [i for i, char in enumerate(content) if char == '\n']
                        
                        if len(newlines) >= 5:
                            # Chèn sau dòng thứ 5 (xuống 3 dòng so với cũ)
                            insert_pos = newlines[4] + 1
                            self.content = content[:insert_pos] + "\n\n" + video_block + "\n\n" + content[insert_pos:]
                            print(f"[WP_MODEL] Inserted video after 5th newline")
                        elif len(newlines) >= 2:
                            # Fallback nếu ít dòng hơn
                            insert_pos = newlines[-1] + 1 # Last newline available
                            self.content = content[:insert_pos] + "\n\n" + video_block + "\n\n" + content[insert_pos:]
                            print(f"[WP_MODEL] Inserted video after last available newline")
                        else:
                            # Không có xuống dòng, text liền mạch -> Chèn ở sâu hơn (khoảng ký tự 800)
                            target_pos = min(800, len(content) // 2)
                            # Tìm khoảng trắng gần nhất để không cắt đôi từ
                            space_pos = content.find(' ', target_pos)
                            if space_pos == -1: space_pos = target_pos
                            
                            self.content = content[:space_pos] + "\n\n" + video_block + "\n\n" + content[space_pos:]
                            print(f"[WP_MODEL] Inserted video after approx {space_pos} chars")
                else:
                    print(f"[WP_MODEL] Video block generation failed")
                    self.content = self.raw_content
            else:
                print(f"[WP_MODEL] No video_url provided")
                self.content = self.raw_content
            
            # Insert content images if provided (after video insertion)
            if self.content_images and len(self.content_images) > 0:
                print(f"[WP_MODEL] Inserting {len(self.content_images)} content image(s)...")
                
                # Calculate positions to distribute images evenly
                content_len = len(self.content)
                positions = []
                
                if len(self.content_images) == 1:
                    positions = [0.75]  # 75% position
                elif len(self.content_images) == 2:
                    positions = [0.50, 0.85]  # 50% and 85%
                elif len(self.content_images) >= 3:
                    positions = [0.35, 0.60, 0.85]  # 35%, 60%, 85%
                
                # Insert images from back to front to maintain positions
                for idx in range(len(self.content_images) - 1, -1, -1):
                    img_url = self.content_images[idx]
                    if not img_url or not img_url.strip():
                        continue
                    
                    # Use simple WordPress image block instead of complex HTML
                    img_block = f'''
<!-- wp:image {{"sizeSlug":"large","linkDestination":"none"}} -->
<figure class="wp-block-image size-large"><img src="{img_url}" alt=""/></figure>
<!-- /wp:image -->

<!-- wp:spacer {{"height":"20px"}} -->
<div style="height:20px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->
'''
                    
                    # Find position to insert
                    target_position = int(content_len * positions[idx])
                    
                    # Try to find a paragraph end near this position
                    search_start = max(0, target_position - 300)
                    search_end = min(content_len, target_position + 300)
                    search_area = self.content[search_start:search_end]
                    
                    # Look for </p> tag
                    p_end_pos = search_area.rfind('</p>')
                    if p_end_pos != -1:
                        insert_pos = search_start + p_end_pos + 4
                        self.content = self.content[:insert_pos] + "\n\n" + img_block + "\n\n" + self.content[insert_pos:]
                        print(f"[WP_MODEL] Inserted content image {idx+1} at position {insert_pos}")
                    else:
                        # Fallback: insert at target position
                        self.content = self.content[:target_position] + "\n\n" + img_block + "\n\n" + self.content[target_position:]
                        print(f"[WP_MODEL] Inserted content image {idx+1} at target position {target_position}")
            
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
        return f"""<!-- wp:html -->
<div class="video-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 30px auto;">
    <iframe src="{video_url}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>
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
            # METHOD 1: Try REST API first (BEST)
            print("[WP_AUTO] ========================================")
            print("[WP_AUTO] Attempting REST API method...")
            print("[WP_AUTO] ========================================")
            
            rest_client = WordPressRESTClient(self.site_url, self.username, self.password)
            
            # Test if REST API is available
            is_available, status_code, message = rest_client.test_api_availability()
            
            if is_available:
                print("[WP_AUTO] ✅ REST API available, using REST API method")
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
