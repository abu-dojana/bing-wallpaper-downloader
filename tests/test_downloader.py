import unittest
from src.downloader.wallpaper_downloader import WallpaperDownloader

class TestWallpaperDownloader(unittest.TestCase):

    def setUp(self):
        self.downloader = WallpaperDownloader()

    def test_download_wallpaper(self):
        # Assuming download_wallpaper returns True on success
        result = self.downloader.download_wallpaper()
        self.assertTrue(result)

    def test_set_download_limit(self):
        self.downloader.set_download_limit(5)
        self.assertEqual(self.downloader.daily_limit, 5)

    def test_download_limit_exceeded(self):
        self.downloader.set_download_limit(1)
        self.downloader.download_wallpaper()
        result = self.downloader.download_wallpaper()  # Attempt to download again
        self.assertFalse(result)  # Assuming it returns False if limit is exceeded

if __name__ == '__main__':
    unittest.main()