"""
Image API Helper - Fetch car images from Unsplash
"""
import requests
import os
import random

class ImageAPI:
    """Fetch high-quality car images from multiple APIs (Unsplash, Pexels, Pixabay)"""
    
    def __init__(self):
        # Unsplash API Access Key
        # Get free key at: https://unsplash.com/developers
        self.unsplash_key = "KOWQbbcCZUyx0kkh27r0VgMZhBBx5Aba1riXrYzosLc"
        self.unsplash_url = "https://api.unsplash.com"
        
        # Pexels API Key (Free: 200 requests/hour)
        # Get free key at: https://www.pexels.com/api/
        self.pexels_key = "K4ZuklaOzH9RlKWP0BZ24nPJYQD5ZPZRTS9KrzWMfy2g2EWIGOPCRvz7"  # Demo key
        self.pexels_url = "https://api.pexels.com/v1"
        
        # Pixabay API Key (Free: 100 requests/minute)
        # Get free key at: https://pixabay.com/api/docs/
        self.pixabay_key = "54519937-ad665dd8ae77ce4f1055115e9"
        self.pixabay_url = "https://pixabay.com/api/"
        
        # Cache to track used images and avoid duplicates
        self.used_images = set()
        self.image_pool = []  # Pool of available images
        self.current_api_index = 0  # Rotate between APIs
    
    def optimize_image_for_upload(self, image_path, max_width=1200, quality=85):
        """
        Optimize image before upload to reduce size and speed up upload
        
        Args:
            image_path: Path to original image
            max_width: Maximum width (default 1200px)
            quality: JPEG quality (default 85)
            
        Returns:
            str: Path to optimized image
        """
        try:
            from PIL import Image
            
            # Open image
            img = Image.open(image_path)
            
            # Get original size
            original_size = os.path.getsize(image_path)
            width, height = img.size
            
            # Check if optimization needed
            if width <= max_width and original_size < 200 * 1024:  # < 200KB
                print(f"[IMAGE_API] Image already optimized: {width}x{height}, {original_size // 1024}KB")
                return image_path
            
            # Resize if too large
            if width > max_width:
                ratio = max_width / width
                new_height = int(height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                print(f"[IMAGE_API] Resized: {width}x{height} → {max_width}x{new_height}")
            
            # Convert to RGB if needed (for JPEG)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Save optimized version
            optimized_path = image_path.replace('.jpg', '_optimized.jpg').replace('.png', '_optimized.jpg')
            img.save(optimized_path, 'JPEG', quality=quality, optimize=True)
            
            optimized_size = os.path.getsize(optimized_path)
            reduction = ((original_size - optimized_size) / original_size) * 100
            
            print(f"[IMAGE_API] ✅ Optimized: {original_size // 1024}KB → {optimized_size // 1024}KB (giảm {reduction:.1f}%)")
            
            return optimized_path
            
        except Exception as e:
            print(f"[IMAGE_API] ⚠️ Optimization failed: {e}, using original")
            return image_path
    
    def extract_car_brand(self, title):
        """Extract car brand from title"""
        # Common car brands
        brands = [
            'Ferrari', 'Lamborghini', 'Porsche', 'BMW', 'Mercedes', 'Audi', 
            'Bugatti', 'McLaren', 'Aston Martin', 'Bentley', 'Rolls Royce',
            'Maserati', 'Jaguar', 'Tesla', 'Corvette', 'Mustang', 'Camaro',
            'Dodge', 'Chevrolet', 'Ford', 'Toyota', 'Honda', 'Nissan',
            'Lexus', 'Acura', 'Infiniti', 'Cadillac', 'Lincoln', 'Jeep',
            'Range Rover', 'Land Rover', 'Volvo', 'Alfa Romeo', 'Lotus',
            'Koenigsegg', 'Pagani', 'Maybach', 'Genesis', 'Polestar'
        ]
        
        title_upper = title.upper()
        
        for brand in brands:
            if brand.upper() in title_upper:
                return brand
        
        # Check for generic car keywords
        car_keywords = ['SUPERCAR', 'SPORTS CAR', 'LUXURY CAR', 'EXOTIC CAR', 'HYPERCAR']
        for keyword in car_keywords:
            if keyword in title_upper:
                return 'luxury car'
        
        return None
    
    def search_car_images(self, query, count=3, page=1):
        """
        Search for car images on Unsplash
        Returns list of image URLs (using 'raw' quality with size params for better reliability)
        """
        try:
            # If no API key set, return empty list
            if self.unsplash_key == "YOUR_UNSPLASH_ACCESS_KEY":
                print("[IMAGE_API] ⚠️ Unsplash API key not configured. Skipping image fetch.")
                return []
            
            url = f"{self.unsplash_url}/search/photos"
            params = {
                'query': query,
                'per_page': 30,  # Get 30 results per page (max allowed)
                'page': page,
                'orientation': 'landscape',
                'client_id': self.unsplash_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                # Extract image URLs - use 'raw' with size params for better control
                image_urls = []
                for result in results:
                    if 'urls' in result and 'raw' in result['urls']:
                        # Add size parameters to raw URL for optimization
                        raw_url = result['urls']['raw']
                        # Resize to 1920px width, high quality
                        optimized_url = f"{raw_url}&w=1920&q=85&fm=jpg"
                        
                        # Skip if already used
                        if optimized_url not in self.used_images:
                            image_urls.append(optimized_url)
                
                print(f"[IMAGE_API] ✅ Unsplash: Found {len(image_urls)} new images for '{query}' (page {page})")
                return image_urls
            elif response.status_code == 403:
                print(f"[IMAGE_API] ❌ Unsplash API key invalid or rate limit exceeded")
                return []
            else:
                print(f"[IMAGE_API] ❌ Unsplash API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[IMAGE_API] ❌ Unsplash error: {e}")
            return []
    
    def search_pexels_images(self, query, count=3, page=1):
        """
        Search for car images on Pexels
        Returns list of image URLs
        """
        try:
            if not self.pexels_key or self.pexels_key == "YOUR_PEXELS_API_KEY":
                print("[IMAGE_API] ⚠️ Pexels API key not configured.")
                return []
            
            url = f"{self.pexels_url}/search"
            headers = {'Authorization': self.pexels_key}
            params = {
                'query': query,
                'per_page': 30,
                'page': page,
                'orientation': 'landscape'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get('photos', [])
                
                # Extract large image URLs
                image_urls = []
                for photo in photos:
                    if 'src' in photo and 'large2x' in photo['src']:
                        img_url = photo['src']['large2x']
                        if img_url not in self.used_images:
                            image_urls.append(img_url)
                
                print(f"[IMAGE_API] ✅ Pexels: Found {len(image_urls)} new images for '{query}' (page {page})")
                return image_urls
            else:
                print(f"[IMAGE_API] ❌ Pexels API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[IMAGE_API] ❌ Pexels error: {e}")
            return []
    
    def search_pixabay_images(self, query, count=3, page=1):
        """
        Search for car images on Pixabay
        Returns list of image URLs
        """
        try:
            if not self.pixabay_key or self.pixabay_key == "YOUR_PIXABAY_API_KEY":
                print("[IMAGE_API] ⚠️ Pixabay API key not configured.")
                return []
            
            url = self.pixabay_url
            params = {
                'key': self.pixabay_key,
                'q': query,
                'image_type': 'photo',
                'orientation': 'horizontal',
                'category': 'transportation',
                'per_page': 30,
                'page': page,
                'safesearch': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                hits = data.get('hits', [])
                
                # Extract large image URLs
                image_urls = []
                for hit in hits:
                    if 'largeImageURL' in hit:
                        img_url = hit['largeImageURL']
                        if img_url not in self.used_images:
                            image_urls.append(img_url)
                
                print(f"[IMAGE_API] ✅ Pixabay: Found {len(image_urls)} new images for '{query}' (page {page})")
                return image_urls
            else:
                print(f"[IMAGE_API] ❌ Pixabay API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[IMAGE_API] ❌ Pixabay error: {e}")
            return []
    
    def search_multi_source(self, query, count=3, page=1):
        """
        Search for images from multiple sources (Unsplash, Pexels, Pixabay) with rotation
        Returns list of image URLs from the current API source
        """
        apis = [
            ('Unsplash', self.search_car_images),
            ('Pexels', self.search_pexels_images),
            ('Pixabay', self.search_pixabay_images)
        ]
        
        # Try current API first
        api_name, api_func = apis[self.current_api_index]
        print(f"[IMAGE_API] 🔄 Using {api_name} API (rotation index: {self.current_api_index})")
        
        results = api_func(query, count, page)
        
        # If no results, try next API
        if not results:
            print(f"[IMAGE_API] ⚠️ {api_name} returned no results, trying next API...")
            self.current_api_index = (self.current_api_index + 1) % len(apis)
            api_name, api_func = apis[self.current_api_index]
            results = api_func(query, count, page)
        
        # Rotate to next API for next request
        self.current_api_index = (self.current_api_index + 1) % len(apis)
        
        return results

    
    def get_car_images_from_title(self, title, count=3):
        """
        Get car images based on title - with randomization to avoid duplicates
        Returns list of image URLs (ONLY luxury/sports/supercars)
        """
        # Extract car brand from title
        brand = self.extract_car_brand(title)
        
        # Build multiple search queries for variety - ONLY HIGH-END CARS
        queries = []
        
        if brand:
            print(f"[IMAGE_API] 🏎️ Detected car brand: {brand}")
            queries = [
                f"{brand} supercar luxury",
                f"{brand} sports car exotic",
                f"{brand} hypercar racing",
                f"{brand} luxury performance car",
                f"{brand} exotic supercar"
            ]
        else:
            print(f"[IMAGE_API] 🏎️ No specific brand detected, using high-end car search")
            queries = [
                "luxury supercar exotic",
                "hypercar sports car",
                "exotic luxury sports car",
                "high performance supercar",
                "luxury exotic automobile",
                "supercar racing track",
                "luxury sports car showroom"
            ]
        
        # Randomly select a query to add variety
        query = random.choice(queries)
        print(f"[IMAGE_API] 🔍 Search query: '{query}'")
        
        # If image pool is low, fetch more images
        if len(self.image_pool) < count * 2:
            # Fetch from multiple pages for more variety
            page = random.randint(1, 3)  # Random page 1-3
            new_images = self.search_multi_source(query, count, page=page)
            
            # Add to pool
            self.image_pool.extend(new_images)
            
            # If still not enough, try another query
            if len(self.image_pool) < count and len(queries) > 1:
                alt_query = random.choice([q for q in queries if q != query])
                print(f"[IMAGE_API] 🔍 Trying alternative query: '{alt_query}'")
                alt_images = self.search_multi_source(alt_query, count, page=1)
                self.image_pool.extend(alt_images)
        
        # Shuffle pool for randomness
        random.shuffle(self.image_pool)
        
        # Select images from pool
        selected_images = []
        while len(selected_images) < count and self.image_pool:
            img = self.image_pool.pop(0)
            if img not in self.used_images:
                selected_images.append(img)
                self.used_images.add(img)
        
        print(f"[IMAGE_API] ✅ Selected {len(selected_images)} unique images")
        print(f"[IMAGE_API] 📊 Pool size: {len(self.image_pool)}, Used: {len(self.used_images)}")
        
        return selected_images
    
    def download_image(self, url, save_path, retries=3):
        """Download image from URL to local path with retry logic"""
        import time
        
        for attempt in range(retries):
            try:
                # Add headers to avoid being blocked
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
                }
                
                response = requests.get(url, timeout=30, stream=True, headers=headers)
                
                if response.status_code == 200:
                    # Write to file
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Validate file size (must be > 1KB)
                    file_size = os.path.getsize(save_path)
                    if file_size < 1024:
                        print(f"[IMAGE_API] ⚠️ File too small ({file_size} bytes), retrying...")
                        os.remove(save_path)
                        time.sleep(2)
                        continue
                    
                    print(f"[IMAGE_API] ✅ Downloaded: {save_path} ({file_size} bytes)")
                    return True
                else:
                    print(f"[IMAGE_API] ⚠️ Download failed (attempt {attempt+1}/{retries}): HTTP {response.status_code}")
                    if attempt < retries - 1:
                        time.sleep(2)
                        continue
                    return False
                    
            except Exception as e:
                print(f"[IMAGE_API] ⚠️ Download error (attempt {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return False
        
        return False
    
    def save_image_to_library(self, source_path, custom_name=None):
        """
        Save image from thumbnails to saved_car_images library
        
        Args:
            source_path: Path to source image (e.g., thumbnails/car_api_xxx.jpg)
            custom_name: Optional custom name for saved image
            
        Returns:
            tuple: (success: bool, saved_path: str or None)
        """
        try:
            # Create saved_car_images folder if not exists
            save_folder = "saved_car_images"
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
                print(f"[IMAGE_API] 📁 Created folder: {save_folder}")
            
            # Check if source exists
            if not os.path.exists(source_path):
                print(f"[IMAGE_API] ❌ Source image not found: {source_path}")
                return False, None
            
            # Generate save filename
            if custom_name:
                filename = custom_name
                if not filename.endswith(('.jpg', '.jpeg', '.png')):
                    filename += '.jpg'
            else:
                # Use original filename
                filename = os.path.basename(source_path)
            
            save_path = os.path.join(save_folder, filename)
            
            # Check if file already exists
            if os.path.exists(save_path):
                # Add timestamp to avoid overwrite
                import time
                timestamp = int(time.time())
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                save_path = os.path.join(save_folder, filename)
            
            # Copy file
            import shutil
            shutil.copy2(source_path, save_path)
            
            file_size = os.path.getsize(save_path)
            print(f"[IMAGE_API] 💾 Saved image to library: {save_path} ({file_size} bytes)")
            
            return True, save_path
            
        except Exception as e:
            print(f"[IMAGE_API] ❌ Error saving image: {e}")
            import traceback
            traceback.print_exc()
            return False, None
    
    def delete_image(self, image_path):
        """
        Delete image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            if not os.path.exists(image_path):
                print(f"[IMAGE_API] ⚠️ Image not found: {image_path}")
                return False
            
            os.remove(image_path)
            print(f"[IMAGE_API] 🗑️ Deleted image: {image_path}")
            return True
            
        except Exception as e:
            print(f"[IMAGE_API] ❌ Error deleting image: {e}")
            return False
    
    def get_saved_images(self):
        """
        Get list of saved images from library
        
        Returns:
            list: List of image paths
        """
        try:
            save_folder = "saved_car_images"
            if not os.path.exists(save_folder):
                return []
            
            images = []
            for filename in os.listdir(save_folder):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    images.append(os.path.join(save_folder, filename))
            
            # Sort by modification time (newest first)
            images.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            return images
            
        except Exception as e:
            print(f"[IMAGE_API] ❌ Error getting saved images: {e}")
            return []
    
    def get_thumbnail_images(self):
        """
        Get list of images from thumbnails folder
        
        Returns:
            list: List of image paths
        """
        try:
            thumb_folder = "thumbnails"
            if not os.path.exists(thumb_folder):
                return []
            
            images = []
            for filename in os.listdir(thumb_folder):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    # Only include car_api images
                    if 'car_api' in filename.lower():
                        images.append(os.path.join(thumb_folder, filename))
            
            # Sort by modification time (newest first)
            images.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            return images
            
        except Exception as e:
            print(f"[IMAGE_API] ❌ Error getting thumbnail images: {e}")
            return []
    
    def save_uploaded_image_url(self, image_url, post_title="", post_url=""):
        """
        Save uploaded image URL to JSON file for later download
        
        Args:
            image_url: URL of uploaded image on WordPress
            post_title: Title of the post (optional)
            post_url: URL of the post (optional)
        """
        try:
            import json
            import time
            
            json_file = "uploaded_images.json"
            
            # Load existing data
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"images": []}
            
            # Add new entry
            entry = {
                "url": image_url,
                "post_title": post_title,
                "post_url": post_url,
                "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "downloaded": False
            }
            
            # Check if URL already exists
            existing = [img for img in data["images"] if img["url"] == image_url]
            if not existing:
                data["images"].append(entry)
                
                # Save to file
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"[IMAGE_API] 💾 Saved uploaded image URL: {image_url}")
            
        except Exception as e:
            print(f"[IMAGE_API] ❌ Error saving uploaded image URL: {e}")
    
    def get_uploaded_images(self):
        """
        Get list of uploaded images from JSON file
        
        Returns:
            list: List of image entries (dict with url, post_title, etc.)
        """
        try:
            import json
            
            json_file = "uploaded_images.json"
            
            if not os.path.exists(json_file):
                return []
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data.get("images", [])
            
        except Exception as e:
            print(f"[IMAGE_API] ❌ Error getting uploaded images: {e}")
            return []
    
    def download_uploaded_image(self, image_url):
        """
        Download image from WordPress URL to saved_car_images folder
        
        Args:
            image_url: URL of image on WordPress
            
        Returns:
            tuple: (success: bool, saved_path: str or None)
        """
        try:
            import json
            import time
            from urllib.parse import urlparse
            
            # Create saved_car_images folder if not exists
            save_folder = "saved_car_images"
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
            
            # Extract filename from URL
            parsed = urlparse(image_url)
            filename = os.path.basename(parsed.path)
            
            # If filename is empty or invalid, generate one
            if not filename or not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                timestamp = int(time.time())
                filename = f"wordpress_image_{timestamp}.jpg"
            
            save_path = os.path.join(save_folder, filename)
            
            # Check if file already exists
            if os.path.exists(save_path):
                # Add timestamp to avoid overwrite
                name, ext = os.path.splitext(filename)
                timestamp = int(time.time())
                filename = f"{name}_{timestamp}{ext}"
                save_path = os.path.join(save_folder, filename)
            
            # Download image
            success = self.download_image(image_url, save_path)
            
            if success:
                # Update JSON to mark as downloaded
                json_file = "uploaded_images.json"
                if os.path.exists(json_file):
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Find and update entry
                    for img in data["images"]:
                        if img["url"] == image_url:
                            img["downloaded"] = True
                            img["downloaded_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                            img["local_path"] = save_path
                            break
                    
                    # Save updated data
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"[IMAGE_API] 📥 Downloaded from WordPress: {save_path}")
                return True, save_path
            else:
                return False, None
                
        except Exception as e:
            print(f"[IMAGE_API] ❌ Error downloading uploaded image: {e}")
            import traceback
            traceback.print_exc()
            return False, None


# Alternative: Pexels API (backup option)
class PexelsImageAPI:
    """Fetch car images from Pexels API"""
    
    def __init__(self):
        # Pexels API Key (get free at: https://www.pexels.com/api/)
        self.api_key = "K4ZuklaOzH9RlKWP0BZ24nPJYQD5ZPZRTS9KrzWMfy2g2EWIGOPCRvz7"
        self.base_url = "https://api.pexels.com/v1"
    
    def search_car_images(self, query, count=3):
        """Search for car images on Pexels"""
        try:
            if not self.api_key or self.api_key == "YOUR_PEXELS_API_KEY":
                print("[PEXELS_API] ⚠️ Pexels API key not configured.")
                return []
            
            url = f"{self.base_url}/search"
            headers = {'Authorization': self.api_key}
            params = {
                'query': query,
                'per_page': count,
                'orientation': 'landscape'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get('photos', [])
                
                # Extract large image URLs
                image_urls = [
                    photo['src']['large']
                    for photo in photos
                    if 'src' in photo and 'large' in photo['src']
                ]
                
                print(f"[PEXELS_API] ✅ Found {len(image_urls)} images")
                return image_urls[:count]
            else:
                print(f"[PEXELS_API] ❌ API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[PEXELS_API] ❌ Error: {e}")
            return []
