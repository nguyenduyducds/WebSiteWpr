"""
Theme Manager - Handle multiple content themes
"""
import os
import re

class ThemeManager:
    """Manage and apply different content themes"""
    
    def __init__(self):
        self.themes = {
            'supercar': {
                'name': '🏎️ Supercar News',
                'description': 'Premium automotive content with luxury design',
                'file': 'templates/theme_supercar.html',
                'category': 'Automotive'
            },
            'news': {
                'name': '📰 Breaking News',
                'description': 'Modern news layout with breaking badge',
                'file': 'templates/theme_news.html',
                'category': 'News'
            },
            'default': {
                'name': '📝 Classic Blog',
                'description': 'Clean and simple blog layout',
                'file': 'templates/seo_template.html',
                'category': 'General'
            },
            'minimal': {
                'name': '✨ Minimal Clean',
                'description': 'Ultra simple and elegant design',
                'file': 'templates/theme_minimal.html',
                'category': 'General'
            },
            'tech': {
                'name': '💻 Tech Modern',
                'description': 'Developer-friendly tech style',
                'file': 'templates/theme_tech.html',
                'category': 'Technology'
            },
            'magazine': {
                'name': '📖 Magazine',
                'description': 'Editorial magazine style',
                'file': 'templates/theme_magazine.html',
                'category': 'Editorial'
            },
            'business': {
                'name': '💼 Business Pro',
                'description': 'Professional business layout',
                'file': 'templates/theme_business.html',
                'category': 'Business'
            },
            'lifestyle': {
                'name': '🌸 Lifestyle',
                'description': 'Warm and friendly blog style',
                'file': 'templates/theme_lifestyle.html',
                'category': 'Lifestyle'
            },
            'dark': {
                'name': '🌙 Dark Mode',
                'description': 'Modern dark theme',
                'file': 'templates/theme_dark.html',
                'category': 'Modern'
            }
        }
        
        self.current_theme = 'supercar'  # Default theme
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Load all theme templates"""
        for theme_id, theme_info in self.themes.items():
            try:
                template_path = theme_info['file']
                if os.path.exists(template_path):
                    with open(template_path, 'r', encoding='utf-8') as f:
                        self.templates[theme_id] = f.read()
                    print(f"[THEME] Loaded: {theme_info['name']}")
                else:
                    print(f"[THEME] Not found: {template_path}")
                    self.templates[theme_id] = self.get_fallback_template()
            except Exception as e:
                print(f"[THEME] Error loading {theme_id}: {e}")
                self.templates[theme_id] = self.get_fallback_template()
    
    def get_fallback_template(self):
        """Fallback template if file not found"""
        return """
<article class="post-content">
    {{VIDEO_EMBED}}
    <div class="content-wrapper">
        <h1>{{POST_TITLE}}</h1>
        <p>{{EXCERPT}}</p>
        {{MAIN_CONTENT}}
        {{CONTENT_IMAGES}}
    </div>
</article>
<style>
.post-content { max-width: 800px; margin: 0 auto; padding: 20px; font-family: sans-serif; line-height: 1.6; }
.post-content h1 { font-size: 32px; margin-bottom: 20px; }
.post-content p { margin: 15px 0; }
.video-wrapper { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 20px 0; }
.video-wrapper iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
</style>
"""
    
    def set_theme(self, theme_id):
        """Set current theme"""
        if theme_id in self.themes:
            self.current_theme = theme_id
            print(f"[THEME] Switched to: {self.themes[theme_id]['name']}")
            return True
        return False
    
    def get_theme_list(self):
        """Get list of available themes"""
        return [
            {
                'id': theme_id,
                'name': info['name'],
                'description': info['description'],
                'category': info['category']
            }
            for theme_id, info in self.themes.items()
        ]
    
    def generate_content(self, title, video_url="", featured_image="", content_images=[], custom_content="", theme_id=None):
        """Generate content using selected theme"""
        # Use specified theme or current theme
        theme = theme_id if theme_id and theme_id in self.templates else self.current_theme
        template = self.templates.get(theme, self.get_fallback_template())
        
        print(f"[THEME] Generating content with theme: {self.themes[theme]['name']}")
        
        # Generate components
        video_html = self.generate_video_embed(video_url)
        featured_image_html = self.generate_featured_image(featured_image, title)
        excerpt = self.generate_excerpt(title, custom_content)
        content_images_html = self.generate_content_images(content_images, title)
        main_content = custom_content if custom_content else self.generate_auto_content(title, theme)
        
        # Get current date
        from datetime import datetime
        publish_date = datetime.now().strftime("%B %d, %Y")
        
        # Calculate read time (rough estimate)
        word_count = len(main_content.split())
        read_time = max(1, word_count // 200)  # 200 words per minute
        
        # Replace placeholders
        html = template
        html = html.replace('{{POST_TITLE}}', title)
        html = html.replace('{{VIDEO_EMBED}}', video_html)
        html = html.replace('{{FEATURED_IMAGE}}', featured_image_html)
        html = html.replace('{{EXCERPT}}', excerpt)
        html = html.replace('{{MAIN_CONTENT}}', main_content)
        html = html.replace('{{CONTENT_IMAGES}}', content_images_html)
        html = html.replace('{{PUBLISH_DATE}}', publish_date)
        html = html.replace('{{READ_TIME}}', str(read_time))
        html = html.replace('{{VIEW_COUNT}}', '1,234')  # Placeholder
        html = html.replace('{{TAGS}}', self.generate_tags(title))
        html = html.replace('{{SPECIFICATIONS}}', self.generate_specs(title))
        html = html.replace('{{RELATED_POSTS}}', '')  # Empty for now
        
        # Add Open Graph meta tags for Facebook sharing
        og_meta = self.generate_og_meta_tags(title, excerpt, featured_image)
        html = og_meta + '\n\n' + html
        
        # Clean up empty sections
        html = re.sub(r'<div class="[^"]*">\s*</div>', '', html)
        
        return html
    
    def generate_video_embed(self, video_url):
        """Generate video embed HTML"""
        if not video_url:
            return ""
        
        # Helper: Clean and unescape
        import html
        video_url = html.unescape(video_url).strip()
        
        # STRATEGY CHANGE: Use WordPress [embed] shortcode for YouTube/Vimeo
        # This avoids JNews/Theme interfering with raw iframes (causing 404s)
        
        # 1. Extract URL if it's an iframe
        target_url = video_url
        if '<iframe' in video_url.lower():
            import re
            src_match = re.search(r'src=["\'](http[^"\']+)["\']', video_url)
            if src_match:
                target_url = src_match.group(1)
        
        # 2. Check if compatible with Shortcode
        if 'youtube.com' in target_url or 'youtu.be' in target_url or 'vimeo.com' in target_url:
            # Return WP shortcode (Cleanest method)
            # Remove any query params that might break embed if complex, but usually keep them
            return f'[embed]{target_url}[/embed]'

        # 3. Fallback for others (Facebook, etc) - Return RAW HTML
        vid_lower = video_url.lower()
        if '<iframe' in vid_lower or '<div' in vid_lower or '<script' in vid_lower or '<blockquote' in vid_lower:
             return video_url
        
        # 4. Convert URL to embed (Fallback)
        embed_url = self.convert_to_embed_url(video_url)
        if embed_url:
            return f'''<div class="video-wrapper">
    <iframe src="{embed_url}" width="100%" height="100%" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
</div>'''
        
        return ""
    
    def convert_to_embed_url(self, url):
        """Convert video URL to embed URL"""
        if not url: return None
        
        # Safety: If URL looks like HTML, return None to prevent injection
        if '<' in url and '>' in url:
            return None
        
        # YouTube
        if 'youtube.com' in url or 'youtu.be' in url:
            # If already embed URL, return it
            if '/embed/' in url:
                return url
                
            video_id = None
            if 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[-1].split('?')[0]
            elif 'watch?v=' in url:
                video_id = url.split('watch?v=')[-1].split('&')[0]
                
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"
        
        # Vimeo
        elif 'vimeo.com' in url:
            if 'player.vimeo.com' in url:
                return url
            else:
                try:
                    video_id = url.split('vimeo.com/')[-1].split('?')[0]
                    if video_id.isdigit():
                        return f"https://player.vimeo.com/video/{video_id}"
                except: pass
        
        # Facebook plugin URL
        elif 'facebook.com' in url and not url.startswith('<'):
            return f"https://www.facebook.com/plugins/video.php?href={url}&show_text=0&width=560"
        
        return url
    
    def generate_featured_image(self, image_url, alt_text):
        """Generate featured image HTML"""
        # Return EMPTY because WordPress theme handles Featured Image display
        # We don't want to duplicate it in the content body
        return ""
    
    def generate_og_meta_tags(self, title, description, image_url):
        """
        Generate Open Graph meta tags for Facebook/social sharing
        Note: We don't include og:image here because WordPress will auto-generate it
        from the featured image. This avoids issues with local file paths.
        """
        # Clean description (remove HTML tags)
        clean_desc = re.sub(r'<[^>]+>', '', description)
        clean_desc = clean_desc.strip()[:200]  # Limit to 200 chars
        
        # Escape quotes in attributes
        title_escaped = title.replace('"', '&quot;')
        desc_escaped = clean_desc.replace('"', '&quot;')
        
        og_tags = f'''<!-- Open Graph Meta Tags for Facebook Sharing -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title_escaped}",
  "description": "{desc_escaped}",
  "author": {{
    "@type": "Person",
    "name": "Admin"
  }}
}}
</script>

<!-- WordPress will auto-generate og:image from featured image -->
<!-- Force Facebook to prioritize featured image -->
<meta property="og:title" content="{title_escaped}" />
<meta property="og:description" content="{desc_escaped}" />
<meta property="og:type" content="article" />

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{title_escaped}" />
<meta name="twitter:description" content="{desc_escaped}" />'''
        
        return og_tags
    
    def generate_excerpt(self, title, content):
        """Generate excerpt from title and content"""
        excerpts = [
            f"Discover everything you need to know about {title}. This comprehensive guide covers all the essential details.",
            f"An in-depth look at {title}, featuring exclusive insights and expert analysis.",
            f"Get the latest updates on {title}. Read our detailed coverage and stay informed.",
        ]
        
        import random
        return random.choice(excerpts)
    
    def generate_content_images(self, image_urls, alt_base):
        """Generate content images HTML"""
        if not image_urls:
            return ""
        
        html_parts = []
        for i, url in enumerate(image_urls, 1):
            if url:
                html_parts.append(f'<img src="{url}" alt="{alt_base} - Image {i}" class="content-image" loading="lazy">')
        
        return '\n'.join(html_parts)
    
    def generate_auto_content(self, title, theme):
        """Generate auto content based on theme"""
        if theme == 'supercar':
            return self.generate_supercar_content(title)
        elif theme == 'news':
            return self.generate_news_content(title)
        else:
            return self.generate_default_content(title)
    
    def generate_supercar_content(self, title):
        """Generate supercar-themed content"""
        return f"""
<h2>Performance Overview</h2>
<p>The {title} represents the pinnacle of automotive engineering, combining raw power with sophisticated design. This masterpiece showcases what happens when cutting-edge technology meets uncompromising performance standards.</p>

<p>From its aggressive stance to its aerodynamic profile, every element has been meticulously crafted to deliver an unforgettable driving experience. The attention to detail is evident in every curve and contour.</p>

<h2>Design Philosophy</h2>
<p>The exterior design language speaks volumes about the vehicle's capabilities. Sharp lines and sculpted surfaces aren't just for aesthetics—they serve a functional purpose, channeling air flow and generating downforce at high speeds.</p>

<p>Inside the cabin, luxury meets functionality. Premium materials, advanced technology, and ergonomic design create an environment that's both comfortable and purposeful.</p>

<h2>Engineering Excellence</h2>
<p>Under the hood lies a powerplant that's been engineered to perfection. Every component has been optimized for maximum performance, from the intake system to the exhaust note that announces its presence.</p>

<p>The chassis and suspension setup provide the perfect balance between comfort and track-ready performance. Advanced electronics work seamlessly to deliver power to the road while maintaining control.</p>

<h2>The Driving Experience</h2>
<p>Behind the wheel, the {title} transforms every journey into an event. The immediate throttle response, precise steering, and powerful braking system work in harmony to create a connection between driver and machine.</p>

<p>Whether cruising on the highway or attacking a winding mountain road, this vehicle delivers confidence-inspiring performance that few can match.</p>
"""
    
    def generate_news_content(self, title):
        """Generate news-themed content"""
        return f"""
<h2>Breaking Story</h2>
<p>In a developing story, {title} has captured widespread attention across social media platforms and news outlets. Our team has been following this closely to bring you the most accurate and up-to-date information.</p>

<p>The situation continues to evolve, with new details emerging as we speak. Stay tuned for the latest updates as this story unfolds.</p>

<h2>Key Details</h2>
<p>According to sources close to the matter, several important factors have contributed to this situation. We've compiled the essential information you need to understand the full context.</p>

<p>Experts in the field have weighed in with their analysis, providing valuable insights into what this means for the broader community.</p>

<h2>Impact and Implications</h2>
<p>The ramifications of {title} extend beyond the immediate circumstances. Industry observers note that this could have lasting effects on related sectors and stakeholders.</p>

<p>We'll continue to monitor the situation and provide updates as more information becomes available.</p>
"""
    
    def generate_default_content(self, title):
        """Generate default content"""
        return f"""
<h2>Introduction</h2>
<p>Welcome to our comprehensive coverage of {title}. In this article, we'll explore all the important aspects and provide you with valuable insights.</p>

<h2>Main Points</h2>
<p>There are several key factors to consider when discussing {title}. Each element plays a crucial role in understanding the complete picture.</p>

<h2>Conclusion</h2>
<p>We hope this article has provided you with useful information about {title}. Stay tuned for more updates and detailed analysis.</p>
"""
    
    def generate_tags(self, title):
        """Generate tags HTML"""
        # Extract potential tags from title
        words = title.split()
        tags = []
        
        # Add some generic tags
        tags.append('<a href="#">Featured</a>')
        
        # Add words from title as tags (max 5)
        for word in words[:5]:
            if len(word) > 3:  # Only words longer than 3 chars
                tags.append(f'<a href="#">{word}</a>')
        
        return '\n'.join(tags)
    
    def generate_specs(self, title):
        """Generate specifications HTML (for supercar theme)"""
        return """
<div class="spec-item">
    <div class="spec-label">Engine</div>
    <div class="spec-value">V8 Twin-Turbo</div>
</div>
<div class="spec-item">
    <div class="spec-label">Power</div>
    <div class="spec-value">700+ HP</div>
</div>
<div class="spec-item">
    <div class="spec-label">0-60 MPH</div>
    <div class="spec-value">2.9 seconds</div>
</div>
<div class="spec-item">
    <div class="spec-label">Top Speed</div>
    <div class="spec-value">211 MPH</div>
</div>
"""


# Test
if __name__ == "__main__":
    manager = ThemeManager()
    
    print("\n=== Available Themes ===")
    for theme in manager.get_theme_list():
        print(f"{theme['name']} - {theme['description']}")
    
    print("\n=== Generating Content ===")
    html = manager.generate_content(
        title="Ferrari SF90 Stradale 2024",
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        theme_id="supercar"
    )
    
    print(f"Generated {len(html)} characters")
    print("✅ Theme Manager working!")
