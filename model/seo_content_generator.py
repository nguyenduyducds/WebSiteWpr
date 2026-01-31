"""
SEO Content Generator - Generate WordPress-compatible HTML
"""
import os
import re

class SEOContentGenerator:
    """Generate SEO-optimized HTML content for WordPress"""
    
    def __init__(self):
        self.template_path = "templates/seo_template.html"
        self.load_template()
    
    def load_template(self):
        """Load HTML template"""
        try:
            if os.path.exists(self.template_path):
                with open(self.template_path, 'r', encoding='utf-8') as f:
                    self.template = f.read()
            else:
                # Use inline template if file not found
                self.template = self.get_inline_template()
        except Exception as e:
            print(f"[SEO] Error loading template: {e}")
            self.template = self.get_inline_template()
    
    def get_inline_template(self):
        """Fallback inline template"""
        return """
<article class="post-content seo-optimized">
    {{VIDEO_EMBED}}
    <div class="content-wrapper">
        <p class="intro-paragraph">{{INTRO_TEXT}}</p>
        <div class="content-images">
            {{CONTENT_IMAGE_1}}
            {{CONTENT_IMAGE_2}}
            {{CONTENT_IMAGE_3}}
        </div>
        <div class="main-content">{{MAIN_CONTENT}}</div>
    </div>
</article>

<style>
.post-content { max-width: 100%; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; color: #333; }
.video-wrapper { position: relative; width: 100%; padding-bottom: 56.25%; margin: 30px 0; overflow: hidden; border-radius: 8px; background: #000; }
.video-wrapper iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
.content-wrapper { padding: 20px 0; }
.intro-paragraph { font-size: 18px; line-height: 1.8; margin: 0 0 30px 0; color: #444; }
.content-images { margin: 30px 0; }
.content-image { width: 100%; max-width: 800px; height: auto; margin: 20px auto; display: block; border-radius: 8px; }
.main-content { font-size: 16px; line-height: 1.8; color: #333; }
.main-content p { margin: 0 0 20px 0; }
.main-content h2 { font-size: 24px; font-weight: 700; margin: 40px 0 20px 0; }
.main-content h3 { font-size: 20px; font-weight: 600; margin: 30px 0 15px 0; }
@media (max-width: 768px) { .intro-paragraph { font-size: 16px; } .main-content { font-size: 15px; } }
</style>
"""
    
    def generate_video_embed(self, video_url):
        """Generate responsive video embed HTML"""
        if not video_url:
            return ""
        
        # Clean URL - remove extra whitespace
        video_url = video_url.strip()
        
        # If already iframe code, wrap it
        if '<iframe' in video_url.lower():
            # Extract iframe
            iframe_match = re.search(r'<iframe[^>]*>.*?</iframe>', video_url, re.IGNORECASE | re.DOTALL)
            if iframe_match:
                iframe_code = iframe_match.group(0)
                # Ensure iframe has proper attributes
                if 'width=' not in iframe_code.lower():
                    iframe_code = iframe_code.replace('<iframe', '<iframe width="100%" height="100%"')
                return f'<div class="video-wrapper">{iframe_code}</div>'
        
        # Convert URL to embed
        embed_url = self.convert_to_embed_url(video_url)
        if embed_url:
            return f'''<div class="video-wrapper">
    <iframe src="{embed_url}" width="100%" height="100%" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>
</div>'''
        
        return ""
    
    def convert_to_embed_url(self, url):
        """Convert video URL to embed URL"""
        # YouTube
        if 'youtube.com' in url or 'youtu.be' in url:
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
                return url  # Already embed URL
            else:
                video_id = url.split('vimeo.com/')[-1].split('?')[0]
                return f"https://player.vimeo.com/video/{video_id}"
        
        # Facebook
        elif 'facebook.com' in url:
            return f"https://www.facebook.com/plugins/video.php?href={url}&show_text=0&width=560"
        
        return url
    
    def generate_content_image(self, image_url, alt_text="", index=1):
        """Generate content image HTML"""
        if not image_url:
            return ""
        
        if not alt_text:
            alt_text = f"Content Image {index}"
        
        return f'<img src="{image_url}" alt="{alt_text}" class="content-image" loading="lazy">'
    
    def generate_intro_text(self, title, video_url=""):
        """Generate SEO-friendly introduction text"""
        intro_templates = [
            f"Khám phá {title} - một chủ đề thú vị và đầy hấp dẫn. Trong bài viết này, chúng tôi sẽ chia sẻ những thông tin chi tiết và hữu ích nhất.",
            f"Tìm hiểu về {title} qua bài viết chi tiết này. Chúng tôi đã tổng hợp những thông tin quan trọng nhất để bạn có cái nhìn toàn diện.",
            f"{title} là một chủ đề được nhiều người quan tâm. Hãy cùng khám phá những điều thú vị trong bài viết dưới đây.",
        ]
        
        import random
        return random.choice(intro_templates)
    
    def generate_main_content(self, title, content_images=[]):
        """Generate main content with SEO structure"""
        content_parts = []
        
        # Section 1: Overview
        content_parts.append(f"<h2>Tổng Quan Về {title}</h2>")
        content_parts.append(f"<p>{title} là một chủ đề quan trọng và đáng được tìm hiểu kỹ lưỡng. Trong phần này, chúng ta sẽ đi sâu vào các khía cạnh chính.</p>")
        
        # Section 2: Details
        content_parts.append(f"<h2>Chi Tiết Về {title}</h2>")
        content_parts.append("<p>Dưới đây là những thông tin chi tiết và hữu ích:</p>")
        content_parts.append("<ul>")
        content_parts.append(f"<li>Thông tin quan trọng về {title}</li>")
        content_parts.append("<li>Các đặc điểm nổi bật</li>")
        content_parts.append("<li>Lợi ích và ứng dụng thực tế</li>")
        content_parts.append("</ul>")
        
        # Section 3: Benefits
        content_parts.append(f"<h2>Lợi Ích Của {title}</h2>")
        content_parts.append(f"<p>{title} mang lại nhiều lợi ích thiết thực. Hãy cùng tìm hiểu những điểm nổi bật:</p>")
        content_parts.append("<ol>")
        content_parts.append("<li>Tiết kiệm thời gian và công sức</li>")
        content_parts.append("<li>Hiệu quả cao và đáng tin cậy</li>")
        content_parts.append("<li>Dễ dàng sử dụng và áp dụng</li>")
        content_parts.append("</ol>")
        
        # Section 4: Conclusion
        content_parts.append(f"<h2>Kết Luận</h2>")
        content_parts.append(f"<p>Qua bài viết này, hy vọng bạn đã có cái nhìn tổng quan về {title}. Đây là một chủ đề thú vị và đáng để khám phá thêm.</p>")
        
        return "\n".join(content_parts)
    
    def generate_html(self, title, video_url="", featured_image="", content_images=[], custom_content=""):
        """Generate complete SEO-optimized HTML"""
        try:
            # Generate video embed
            video_html = self.generate_video_embed(video_url)
            
            # Generate intro text
            intro_text = self.generate_intro_text(title, video_url)
            
            # Generate content images
            image_htmls = []
            for i, img_url in enumerate(content_images[:3], 1):
                if img_url:
                    image_htmls.append(self.generate_content_image(img_url, title, i))
            
            # Pad with empty strings if less than 3 images
            while len(image_htmls) < 3:
                image_htmls.append("")
            
            # Generate main content
            if custom_content:
                main_content = custom_content
            else:
                main_content = self.generate_main_content(title, content_images)
            
            # Replace placeholders
            html = self.template
            html = html.replace('{{POST_TITLE}}', title)
            html = html.replace('{{FEATURED_IMAGE_URL}}', featured_image or '')
            html = html.replace('{{VIDEO_EMBED}}', video_html)
            html = html.replace('{{INTRO_TEXT}}', intro_text)
            html = html.replace('{{CONTENT_IMAGE_1}}', image_htmls[0])
            html = html.replace('{{CONTENT_IMAGE_2}}', image_htmls[1])
            html = html.replace('{{CONTENT_IMAGE_3}}', image_htmls[2])
            html = html.replace('{{MAIN_CONTENT}}', main_content)
            html = html.replace('{{CTA_TEXT}}', f'Cảm ơn bạn đã đọc bài viết về {title}!')
            
            # Clean up empty sections
            html = re.sub(r'<div class="content-images">\s*</div>', '', html)
            html = re.sub(r'<div class="featured-image-wrapper">\s*<img src="" [^>]*>\s*</div>', '', html)
            
            return html
            
        except Exception as e:
            print(f"[SEO] Error generating HTML: {e}")
            import traceback
            traceback.print_exc()
            return f"<p>{custom_content or 'Error generating content'}</p>"
    
    def clean_html_for_wordpress(self, html):
        """Clean HTML to be WordPress-compatible"""
        # Remove comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
        # Ensure proper spacing
        html = html.strip()
        
        return html


# Test function
if __name__ == "__main__":
    generator = SEOContentGenerator()
    
    # Test generation
    html = generator.generate_html(
        title="Ferrari F8 Tributo 2024",
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        featured_image="https://example.com/ferrari.jpg",
        content_images=[
            "https://example.com/ferrari1.jpg",
            "https://example.com/ferrari2.jpg",
            "https://example.com/ferrari3.jpg"
        ]
    )
    
    print("Generated HTML:")
    print(html[:500] + "...")
    print("\n✅ SEO Content Generator working!")
