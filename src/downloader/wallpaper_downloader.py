import requests
import os
from datetime import datetime

class WallpaperDownloader:
    def __init__(self, download_limit=5):
        self.download_limit = download_limit
        self.downloaded_today = 0
        self.reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
    def download_wallpaper(self, wallpaper_url, save_path):
        """Download a wallpaper from URL and save it to the given path"""
        current_time = datetime.now()
        
        # Reset counter if it's a new day
        if current_time.date() > self.reset_time.date():
            self.downloaded_today = 0
            self.reset_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if self.downloaded_today < self.download_limit:
            try:
                response = requests.get(wallpaper_url, stream=True)
                response.raise_for_status()
                
                # Ensure the directory exists
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                with open(save_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                        
                self.downloaded_today += 1
                print(f"Downloaded wallpaper: {wallpaper_url} to {save_path}")
                return True
            except Exception as e:
                print(f"Error downloading wallpaper: {str(e)}")
                return False
        else:
            print("Daily download limit reached.")
            return False

    def set_download_limit(self, limit):
        """Set the daily download limit"""
        try:
            self.download_limit = int(limit)
            print(f"Download limit set to: {self.download_limit}")
            return True
        except Exception as e:
            print(f"Error setting download limit: {str(e)}")
            return False