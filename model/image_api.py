"""
Image API Helper - Fetch car images from Unsplash
"""
import requests
import os
import random

class ImageAPI:
    """Fetch high-quality car images from Unsplash API"""
    
    def __init__(self):
        # Unsplash API Access Key (Demo key - replace with your own for production)
        # Get free key at: https://unsplash.com/developers
        self.access_key = "KOWQbbcCZUyx0kkh27r0VgMZhBBx5Aba1riXrYzosLc"  # User needs to get their own key
        self.base_url = "https://api.unsplash.com"
        
        # Cache to track used images and avoid duplicates
        self.used_images = set()
        self.image_pool = []  # Pool of available images
    
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
            if self.access_key == "YOUR_UNSPLASH_ACCESS_KEY":
                print("[IMAGE_API] ⚠️ Unsplash API key not configured. Skipping image fetch.")
                return []
            
            url = f"{self.base_url}/search/photos"
            params = {
                'query': query,
                'per_page': 30,  # Get 30 results per page (max allowed)
                'page': page,
                'orientation': 'landscape',
                'client_id': self.access_key
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
                
                print(f"[IMAGE_API] ✅ Found {len(image_urls)} new images for '{query}' (page {page})")
                return image_urls
            elif response.status_code == 403:
                print(f"[IMAGE_API] ❌ API key invalid or rate limit exceeded")
                return []
            else:
                print(f"[IMAGE_API] ❌ API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[IMAGE_API] ❌ Error fetching images: {e}")
            return []
    
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
            new_images = self.search_car_images(query, count, page=page)
            
            # Add to pool
            self.image_pool.extend(new_images)
            
            # If still not enough, try another query
            if len(self.image_pool) < count and len(queries) > 1:
                alt_query = random.choice([q for q in queries if q != query])
                print(f"[IMAGE_API] 🔍 Trying alternative query: '{alt_query}'")
                alt_images = self.search_car_images(alt_query, count, page=1)
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


# Alternative: Pexels API (backup option)
class PexelsImageAPI:
    """Fetch car images from Pexels API"""
    
    def __init__(self):
        # Pexels API Key (get free at: https://www.pexels.com/api/)
        self.api_key = "YOUR_PEXELS_API_KEY"
        self.base_url = "https://api.pexels.com/v1"
    
    def search_car_images(self, query, count=3):
        """Search for car images on Pexels"""
        try:
            if self.api_key == "YOUR_PEXELS_API_KEY":
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
