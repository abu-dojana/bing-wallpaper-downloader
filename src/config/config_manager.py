class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = {}

    def load_config(self):
        import json
        try:
            with open(self.config_file, 'r') as file:
                self.config = json.load(file)
        except FileNotFoundError:
            self.config = self.default_config()
            self.save_config()

    def save_config(self):
        import json
        try:
            with open(self.config_file, 'w') as file:
                json.dump(self.config, file, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            return False

    def default_config(self):
        return {
            "download_frequency": "daily",
            "wallpaper_type": "all",
            "daily_download_limit": 5,
            "manual_download": False,
            "resolution": "1920x1080",
            "preview_fetch_count": 8  # NEW default fetch count
        }

    def get_setting(self, key):
        return self.config.get(key)

    def set_setting(self, key, value):
        self.config[key] = value
        self.save_config()