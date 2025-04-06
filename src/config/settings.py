# Configuration settings for the Bing Wallpaper Downloader

DEFAULT_DOWNLOAD_FREQUENCY = "daily"  # Options: daily, weekly, hourly
# Update WALLPAPER_TYPES with more specific categories
WALLPAPER_TYPES = [
    "all", 
    "nature", 
    "mountains", 
    "ocean", 
    "rivers", 
    "landscape", 
    "architecture", 
    "cityscape", 
    "abstract", 
    "travel"
]
DAILY_DOWNLOAD_LIMIT = 5  # Default limit for daily downloads
RESOLUTION_OPTIONS = ["1920x1080", "2560x1440", "3840x2160"]  # Available resolution options
MANUAL_DOWNLOAD_OPTION = True  # Allow manual download of wallpapers

# Available wallpaper providers
WALLPAPER_PROVIDERS = [
    "Bing",
    "Unsplash",
    "Pexels",
    "Pixabay"
]

# Default provider
DEFAULT_WALLPAPER_PROVIDER = "Bing"

# Default API keys (empty by default)
DEFAULT_API_KEYS = {
    "Unsplash": "",
    "Pexels": "", 
    "Pixabay": ""
}
