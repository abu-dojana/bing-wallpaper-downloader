import requests
from .provider_base import WallpaperProvider

class UnsplashProvider(WallpaperProvider):
    @property
    def name(self):
        return "Unsplash"
    
    @property
    def requires_api_key(self):
        return True
    
    @property
    def supported_categories(self):
        return [
            "all", "nature", "mountains", "ocean", 
            "rivers", "landscape", "architecture", 
            "cityscape", "abstract", "travel", "forest"
        ]
    
    def fetch_wallpapers(self, count=1, category='all', resolution='1920x1080', offset=0, api_key=None):
        if not api_key:
            raise ValueError("Unsplash API requires an API key")
            
        # Map our categories to Unsplash query terms
        query = self._map_category_to_query(category)
        
        params = {
            'client_id': api_key,
            'query': query,
            'per_page': count,
            'page': offset + 1,  # Unsplash uses 1-based indexing
            'orientation': 'landscape'  # Best for wallpapers
        }
        
        response = requests.get("https://api.unsplash.com/search/photos", params=params)
        if response.status_code == 200:
            data = response.json()
            results = []
            
            if 'results' in data:
                for photo in data['results']:
                    # Get the URL that matches our requested resolution best
                    url = self._get_best_resolution_url(photo['urls'], resolution)
                    
                    results.append({
                        'url': url,
                        'title': photo.get('description', 'Unsplash Wallpaper'),
                        'provider': self.name,
                        'resolution': resolution,
                        'category': category
                    })
                    
            return results
        else:
            response.raise_for_status()
            
    def _map_category_to_query(self, category):
        """Map our internal categories to Unsplash search queries"""
        if category == 'all':
            return 'wallpaper'
        return category
        
    def _get_best_resolution_url(self, urls, target_resolution):
        """Get the URL that best matches the requested resolution"""
        # Unsplash provides raw, full, regular, small, and thumb sizes
        # For wallpapers, raw or full are usually best
        if '3840x2160' in target_resolution:  # 4K
            return urls.get('raw', urls.get('full'))
        else:
            return urls.get('full', urls.get('regular'))