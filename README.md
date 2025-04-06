# Bing Wallpaper Downloader

This project is a background application that automatically downloads Bing wallpapers based on user-defined settings. Users can customize various parameters such as download frequency, wallpaper type, daily download limit, and resolution selection. The application also provides a manual download option.

## Features

- **Automatic Downloads**: Set a frequency for automatic wallpaper downloads.
- **Customizable Settings**: Choose wallpaper types and resolutions according to your preferences.
- **Daily Download Limit**: Manage how many wallpapers are downloaded each day.
- **Manual Download Option**: Download wallpapers on demand.
- **User-Friendly Interface**: Simple interface for managing settings and downloads.

## Project Structure

```
bing-wallpaper-downloader
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── downloader
│   │   ├── __init__.py
│   │   ├── bing_api.py
│   │   └── wallpaper_downloader.py
│   ├── config
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── config_manager.py
│   └── utils
│       ├── __init__.py
│       ├── image_utils.py
│       └── scheduler.py
├── tests
│   ├── __init__.py
│   ├── test_downloader.py
│   └── test_config.py
├── data
│   └── wallpapers
├── requirements.txt
├── setup.py
├── .gitignore
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/bing-wallpaper-downloader.git
   ```
2. Navigate to the project directory:
   ```
   cd bing-wallpaper-downloader
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python src/main.py
   ```
2. Configure your settings through the user interface.
3. Enjoy your new Bing wallpapers!

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.