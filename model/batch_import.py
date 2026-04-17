"""
Batch Import & Auto Scan - Import file danh sách video rồi tự động scan
"""

import csv
import json
import os
from pathlib import Path


class BatchImporter:
    """Import video links từ file CSV/Excel và chuẩn bị scan"""
    
    def __init__(self):
        self.videos = []
        self.errors = []
    
    def import_csv(self, file_path):
        """Import từ file CSV"""
        print(f"[IMPORT] 📂 Đang đọc file CSV: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Detect columns
                if not reader.fieldnames:
                    return False, "File CSV trống"
                
                print(f"[IMPORT] Columns: {reader.fieldnames}")
                
                # Map common column names
                url_col = None
                title_col = None
                
                for col in reader.fieldnames:
                    col_lower = col.lower().strip()
                    if 'url' in col_lower or 'link' in col_lower or 'video' in col_lower:
                        url_col = col
                    if 'title' in col_lower or 'name' in col_lower or 'tên' in col_lower:
                        title_col = col
                
                if not url_col:
                    return False, "Không tìm thấy cột URL/Link"
                
                print(f"[IMPORT] URL Column: {url_col}, Title Column: {title_col}")
                
                # Read rows
                row_count = 0
                for row in reader:
                    url = row.get(url_col, '').strip()
                    title = row.get(title_col, '').strip() if title_col else ''
                    
                    if url:
                        self.videos.append({
                            'url': url,
                            'title': title or 'Auto-generated',
                            'status': 'pending',
                            'thumbnail': None,
                            'embed_code': None,
                            'video_id': None
                        })
                        row_count += 1
                
                print(f"[IMPORT] ✅ Đã import {row_count} video")
                return True, f"Đã import {row_count} video"
                
        except Exception as e:
            error_msg = f"Lỗi đọc CSV: {str(e)}"
            print(f"[IMPORT] ❌ {error_msg}")
            self.errors.append(error_msg)
            return False, error_msg
    
    def import_json(self, file_path):
        """Import từ file JSON"""
        print(f"[IMPORT] 📂 Đang đọc file JSON: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        url = item.get('url') or item.get('link') or item.get('video_url')
                        title = item.get('title') or item.get('name') or 'Auto-generated'
                        
                        if url:
                            self.videos.append({
                                'url': url,
                                'title': title,
                                'status': 'pending',
                                'thumbnail': None,
                                'embed_code': None,
                                'video_id': None
                            })
            
            print(f"[IMPORT] ✅ Đã import {len(self.videos)} video từ JSON")
            return True, f"Đã import {len(self.videos)} video"
            
        except Exception as e:
            error_msg = f"Lỗi đọc JSON: {str(e)}"
            print(f"[IMPORT] ❌ {error_msg}")
            self.errors.append(error_msg)
            return False, error_msg
    
    def import_txt(self, file_path):
        """Import từ file TXT (mỗi dòng 1 link)"""
        print(f"[IMPORT] 📂 Đang đọc file TXT: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            row_count = 0
            for line in lines:
                url = line.strip()
                if url and not url.startswith('#'):  # Skip empty lines and comments
                    self.videos.append({
                        'url': url,
                        'title': 'Auto-generated',
                        'status': 'pending',
                        'thumbnail': None,
                        'embed_code': None,
                        'video_id': None
                    })
                    row_count += 1
            
            print(f"[IMPORT] ✅ Đã import {row_count} video từ TXT")
            return True, f"Đã import {row_count} video"
            
        except Exception as e:
            error_msg = f"Lỗi đọc TXT: {str(e)}"
            print(f"[IMPORT] ❌ {error_msg}")
            self.errors.append(error_msg)
            return False, error_msg
    
    def import_file(self, file_path):
        """Auto-detect file type and import"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.csv':
            return self.import_csv(file_path)
        elif file_ext == '.json':
            return self.import_json(file_path)
        elif file_ext == '.txt':
            return self.import_txt(file_path)
        else:
            return False, f"Định dạng file không hỗ trợ: {file_ext}"
    
    def get_videos(self):
        """Get list of imported videos"""
        return self.videos
    
    def get_pending_videos(self):
        """Get videos that haven't been scanned yet"""
        return [v for v in self.videos if v['status'] == 'pending']
    
    def mark_scanned(self, url, thumbnail, embed_code, video_id):
        """Mark video as scanned"""
        for video in self.videos:
            if video['url'] == url:
                video['status'] = 'scanned'
                video['thumbnail'] = thumbnail
                video['embed_code'] = embed_code
                video['video_id'] = video_id
                break
    
    def export_results(self, output_path):
        """Export scan results to JSON"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.videos, f, indent=2, ensure_ascii=False)
            print(f"[IMPORT] ✅ Đã export kết quả: {output_path}")
            return True
        except Exception as e:
            print(f"[IMPORT] ❌ Lỗi export: {e}")
            return False


# Test
if __name__ == "__main__":
    importer = BatchImporter()
    
    # Test CSV
    print("\n=== TEST CSV ===")
    success, msg = importer.import_csv("sample_posts.csv")
    print(f"Result: {msg}")
    print(f"Videos: {len(importer.get_videos())}")
