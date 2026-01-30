"""
Batch posting helper - CSV format support
CSV columns: title, video_url, image_path, content (optional)
"""
import csv
import os

class BatchPostData:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.posts = []
        self.load_posts()
    
    def load_posts(self):
        """Load posts from CSV file"""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"File không tồn tại: {self.csv_path}")
        
        with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                post = {
                    'title': row.get('title', '').strip(),
                    'video_url': row.get('video_url', '').strip(),
                    'image_url': row.get('image_path', '').strip(),
                    'content': row.get('content', '').strip()
                }
                if post['title']:  # Only add if has title
                    self.posts.append(post)
        
        return len(self.posts)
    
    def get_post(self, index):
        """Get post at index"""
        if 0 <= index < len(self.posts):
            return self.posts[index]
        return None
    
    def total_posts(self):
        return len(self.posts)
