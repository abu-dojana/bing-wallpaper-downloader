import unittest
from src.config.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.config_manager = ConfigManager()
        self.test_config = {
            'download_frequency': 'daily',
            'wallpaper_type': 'nature',
            'resolution': '1920x1080',
            'daily_download_limit': 5
        }
        self.config_manager.save_config(self.test_config)

    def test_load_config(self):
        config = self.config_manager.load_config()
        self.assertEqual(config['download_frequency'], 'daily')
        self.assertEqual(config['wallpaper_type'], 'nature')
        self.assertEqual(config['resolution'], '1920x1080')
        self.assertEqual(config['daily_download_limit'], 5)

    def test_save_config(self):
        new_config = {
            'download_frequency': 'weekly',
            'wallpaper_type': 'abstract',
            'resolution': '2560x1440',
            'daily_download_limit': 10
        }
        self.config_manager.save_config(new_config)
        config = self.config_manager.load_config()
        self.assertEqual(config['download_frequency'], 'weekly')
        self.assertEqual(config['wallpaper_type'], 'abstract')
        self.assertEqual(config['resolution'], '2560x1440')
        self.assertEqual(config['daily_download_limit'], 10)

    def tearDown(self):
        self.config_manager.save_config({})  # Clear the config after tests

if __name__ == '__main__':
    unittest.main()