from abc import ABC, abstractmethod

class WallpaperProvider(ABC):
    """Base class for all wallpaper providers"""
    
    @property
    @abstractmethod
    def name(self):
        """Return the name of the provider"""
        pass
    
    @property
    def requires_api_key(self):
        """Return True if this provider requires an API key"""
        return False
    
    @property
    def supported_categories(self):
        """Return list of categories supported by this provider"""
        return []
    
    @abstractmethod
    def fetch_wallpapers(self, count=1, category='all', resolution='1920x1080', offset=0):
        """
        Fetch wallpapers from the provider
        
        Returns:
            list of dicts containing:
                - url: Direct URL to the wallpaper image
                - title: Title or description
                - provider: Provider name
                - resolution: Image resolution
                - category: Category or tags
        """
        pass