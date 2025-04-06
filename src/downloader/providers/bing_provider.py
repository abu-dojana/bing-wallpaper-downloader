import requests
from .provider_base import WallpaperProvider

BING_API_URL = "https://www.bing.com/HPImageArchive.aspx"

class BingProvider(WallpaperProvider):
    @property
    def name(self):
        return "Bing"
    
    @property
    def supported_categories(self):
        return [
            "all", "nature", "mountains", "ocean", 
            "rivers", "landscape", "architecture", 
            "cityscape", "abstract", "travel"
        ]
    
    def fetch_wallpapers(self, count=1, category='all', resolution='1920x1080', offset=0):
        # Request more images to allow for filtering
        request_count = max(count * 3, 8)
        
        # Use the provided offset but ensure within API limits
        idx = min(offset, 16)
        
        params = {
            'format': 'js',
            'idx': idx,
            'n': request_count,
            'mkt': 'en-US',
        }
        
        print(f"Fetching from Bing API with idx={idx}, n={request_count}")
        
        response = requests.get(BING_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            results = []
            
            if 'images' in data:
                images = data['images']
                # Filter by category if needed
                if category != 'all':
                    images = [img for img in images if self._matches_category(img, category)]
                
                # Convert to our standardized format
                for image in images[:count]:
                    url = f"https://www.bing.com{image['url']}"
                    results.append({
                        'url': url,
                        'title': image.get('title', ''),
                        'provider': self.name,
                        'resolution': resolution,
                        'category': category
                    })
            
            return results
        else:
            response.raise_for_status()
    
    def _matches_category(self, image, category):
        # Implementation of the existing category matching code
        # (Copy the existing matches_category function logic here)
        # ...