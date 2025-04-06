import requests
import random

BING_API_URL = "https://www.bing.com/HPImageArchive.aspx"

# Keywords associated with each category for filtering
CATEGORY_KEYWORDS = {
    "all": [],  # No filtering
    "nature": ["nature", "forest", "tree", "flower", "garden", "park", "lake"],
    "mountains": ["mountain", "peak", "hill", "valley", "highlands"],
    "ocean": ["ocean", "sea", "beach", "coast", "shore", "waves", "coral", "reef"],
    "rivers": ["river", "stream", "waterfall", "creek", "brook", "water"],
    "landscape": ["landscape", "vista", "panorama", "horizon", "scenic"],
    "architecture": ["architecture", "building", "tower", "castle", "monument", "temple", "church"],
    "cityscape": ["city", "skyline", "urban", "downtown", "metropolis"],
    "abstract": ["abstract", "pattern", "texture", "geometric"],
    "travel": ["travel", "destination", "tourism", "vacation", "landmark"]
}

# Keywords to exclude for certain categories
EXCLUDE_KEYWORDS = {
    "nature": ["city", "building", "animal", "bird", "insect", "wildlife"],
    "mountains": ["animal", "building", "city"],
    "ocean": ["animal", "whale", "shark", "fish", "bird"],
    "landscape": ["animal", "person", "people", "building"]
}

def matches_category(image_data, category):
    """
    Check if an image matches a given category based on its metadata
    
    Args:
        image_data: Image data from Bing API
        category: Category to check against
    
    Returns:
        Boolean indicating if image matches category
    """
    # If category is "all", always match
    if category == "all":
        return True
        
    # Get title, copyright, and description (all lowercase)
    title = image_data.get('title', '').lower()
    copyright_text = image_data.get('copyright', '').lower()
    description = image_data.get('desc', '').lower()
    
    # Combine all text fields for searching
    combined_text = f"{title} {copyright_text} {description}"
    
    # Check if any keywords for this category are in the text
    keywords = CATEGORY_KEYWORDS.get(category, [])
    excludes = EXCLUDE_KEYWORDS.get(category, [])
    
    # Check if any exclude keywords are in the text
    for word in excludes:
        if word in combined_text:
            return False
    
    # Must match at least one keyword
    if keywords:
        for word in keywords:
            if word in combined_text:
                return True
        return False  # No keywords matched
    
    return True  # No keywords to filter by

def fetch_wallpaper_data(num=1, resolution='1920x1080', wallpaper_type='all', offset=0):
    """
    Fetch wallpaper data from Bing API and filter by type
    
    Args:
        num: Number of images to retrieve
        resolution: Image resolution
        wallpaper_type: Type of wallpaper (nature, architecture, etc.)
        offset: Offset for image pagination (0 = most recent)
    
    Returns:
        JSON data containing filtered wallpaper information
    """
    # Request more images to allow for filtering
    request_count = max(num * 3, 8)  # Get at least 3x what we need
    
    # Use the provided offset but ensure within API limits
    idx = min(offset, 16)
    
    params = {
        'format': 'js',
        'idx': idx,
        'n': request_count,  # Request more to allow for filtering
        'mkt': 'en-US',
    }
    
    print(f"Fetching from Bing API with idx={idx}, n={request_count}")
    
    response = requests.get(BING_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        
        # If we're not filtering by type, return raw data
        if wallpaper_type == "all":
            # Still cap at requested number
            if 'images' in data:
                data['images'] = data['images'][:num]
            return data
            
        # Filter images by type
        if 'images' in data:
            filtered_images = []
            
            for image in data['images']:
                if matches_category(image, wallpaper_type):
                    filtered_images.append(image)
                    # Stop once we have enough
                    if len(filtered_images) >= num:
                        break
            
            # Replace with filtered images
            data['images'] = filtered_images
            print(f"Found {len(filtered_images)} images matching type '{wallpaper_type}'")
            return data
        
        return data
    else:
        response.raise_for_status()

def get_wallpaper_url(wallpaper_data):
    """Extract the wallpaper URL from the API response"""
    if 'images' in wallpaper_data and len(wallpaper_data['images']) > 0:
        image = wallpaper_data['images'][0]
        # Add proper resolution formatting to URL
        base_url = f"https://www.bing.com{image['url']}"
        # Resolution is typically already embedded in the URL
        return base_url
    return None

def get_wallpaper_title(wallpaper_data):
    """Extract the wallpaper title from the API response"""
    if 'images' in wallpaper_data and len(wallpaper_data['images']) > 0:
        return wallpaper_data['images'][0]['title']
    return None

def get_wallpaper_description(wallpaper_data):
    """Extract the wallpaper description from the API response"""
    if 'images' in wallpaper_data and len(wallpaper_data['images']) > 0:
        # Return copyright as description as it contains more details
        return wallpaper_data['images'][0].get('copyright', '')
    return None