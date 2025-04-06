from .bing_provider import BingProvider
from .unsplash_provider import UnsplashProvider
# Import other providers as you implement them

class ProviderFactory:
    """Factory for creating wallpaper provider instances"""
    
    @staticmethod
    def get_provider(provider_name):
        """Get a provider instance by name"""
        if provider_name == "Bing":
            return BingProvider()
        elif provider_name == "Unsplash":
            return UnsplashProvider()
        # Add other providers as they're implemented
        else:
            raise ValueError(f"Unknown provider: {provider_name}")