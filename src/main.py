import sys
import os
import datetime  # Add this import
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSystemTrayIcon, QAction, QMenu, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox, QPushButton, QFileDialog
from downloader.wallpaper_downloader import WallpaperDownloader
from downloader.bing_api import fetch_wallpaper_data, get_wallpaper_url
from config.config_manager import ConfigManager
from config.settings import WALLPAPER_TYPES, RESOLUTION_OPTIONS
from utils.scheduler import Scheduler
import threading
import time

class SettingsDialog(QDialog):
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.config = self.config_manager.config
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Wallpaper Settings')
        self.setMinimumWidth(400)
        layout = QVBoxLayout()

        # Frequency
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel('Download Frequency:'))
        self.freq_combo = QComboBox()
        self.freq_combo.addItems([
            '1 second', '30 seconds', '1 minute', '15 minutes', '30 minutes',
            'hourly', 'daily', 'weekly'
        ])
        self.freq_combo.setCurrentText(self.config.get('download_frequency', 'daily'))
        freq_layout.addWidget(self.freq_combo)
        layout.addLayout(freq_layout)

        # Wallpaper Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel('Wallpaper Type:'))
        self.type_combo = QComboBox()
        self.type_combo.addItems(WALLPAPER_TYPES)
        self.type_combo.setCurrentText(self.config.get('wallpaper_type', 'nature'))
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Resolution
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel('Resolution:'))
        self.res_combo = QComboBox()
        self.res_combo.addItems(RESOLUTION_OPTIONS)
        self.res_combo.setCurrentText(self.config.get('resolution', '1920x1080'))
        res_layout.addWidget(self.res_combo)
        layout.addLayout(res_layout)

        # Daily limit
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel('Daily download limit:'))
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 24)
        self.limit_spin.setValue(self.config.get('daily_download_limit', 5))
        limit_layout.addWidget(self.limit_spin)
        layout.addLayout(limit_layout)

        # Fetch count for preview (NEW)
        fetch_layout = QHBoxLayout()
        fetch_layout.addWidget(QLabel('Preview fetch count:'))
        self.fetch_spin = QSpinBox()
        self.fetch_spin.setRange(4, 20)
        self.fetch_spin.setValue(self.config.get('preview_fetch_count', 8))
        fetch_layout.addWidget(self.fetch_spin)
        layout.addLayout(fetch_layout)

        # Save location
        save_layout = QHBoxLayout()
        save_layout.addWidget(QLabel('Save location:'))
        self.location_label = QLabel(self.config.get('save_location', os.path.abspath('data/wallpapers')))
        save_layout.addWidget(self.location_label)
        browse_btn = QPushButton('Browse')
        browse_btn.clicked.connect(self.select_save_location)
        save_layout.addWidget(browse_btn)
        layout.addLayout(save_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def select_save_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Location")
        if folder:
            self.location_label.setText(folder)

    def save_settings(self):
        try:
            self.config['download_frequency'] = self.freq_combo.currentText()
            self.config['wallpaper_type'] = self.type_combo.currentText()
            self.config['resolution'] = self.res_combo.currentText()
            self.config['daily_download_limit'] = self.limit_spin.value()
            self.config['preview_fetch_count'] = self.fetch_spin.value()  # NEW
            self.config['save_location'] = self.location_label.text()
            result = self.config_manager.save_config()
            if result:
                self.accept()
            else:
                raise Exception("Failed to save configuration")
        except Exception as e:
            print(f"Error in save_settings: {str(e)}")
            # Don't close the dialog if there's an error

# Now modify WallpaperPreviewDialog to implement dynamic loading

class WallpaperPreviewDialog(QDialog):
    def __init__(self, wallpaper_app, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wallpaper Preview")
        self.setMinimumSize(800, 450)  # 16:9 aspect ratio
        self.current_index = 0
        self.wallpaper_urls = []
        self.current_url = None
        self.wallpaper_app = wallpaper_app
        self.page = 0  # Track which page we're on for pagination
        
        # Get fetch count from settings
        self.fetch_count = self.wallpaper_app.config_manager.config.get('preview_fetch_count', 8)
        
        # Get current wallpaper type from settings
        self.current_type = self.wallpaper_app.config_manager.config.get('wallpaper_type', 'all')
        
        self.init_ui()
        
        # Fetch initial set of wallpapers after UI is initialized
        self.fetch_wallpapers(self.fetch_count)

    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        
        # Type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Wallpaper Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(WALLPAPER_TYPES)
        self.type_combo.setCurrentText(self.current_type)
        self.type_combo.currentTextChanged.connect(self.type_changed)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Image preview area
        self.image_label = QLabel("Loading wallpapers...")
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.image_label)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("← Previous")
        self.prev_btn.clicked.connect(self.show_previous)
        self.prev_btn.setEnabled(False)  # Initially disabled
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.show_next)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        download_btn = QPushButton("Download Current")
        download_btn.clicked.connect(self.download_current)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(download_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def type_changed(self, new_type):
        """Handle wallpaper type change"""
        print(f"Wallpaper type changed to: {new_type}")
        self.current_type = new_type
        self.page = 0  # Reset page to start fresh
        self.fetch_wallpapers(self.fetch_count)  # Fetch new wallpapers of selected type

    def fetch_wallpapers(self, count=8, append=False):
        """
        Fetch wallpapers for navigation
        
        Args:
            count: Number of wallpapers to fetch
            append: Whether to append to existing list or replace it
        """
        try:
            print(f"Fetching {count} wallpapers, append={append}, page={self.page}, type={self.current_type}...")
            settings = self.wallpaper_app.config_manager.config
            resolution = settings.get('resolution', '1920x1080')
            
            # Calculate offset based on page number
            offset = self.page * count
            
            # Use the current selected type instead of the one from settings
            wallpaper_type = self.current_type
            
            # Show loading state in the image label
            if hasattr(self, 'image_label'):
                self.image_label.setText("Loading wallpapers...")
                QtWidgets.QApplication.processEvents()  # Update UI immediately
            
            # Fetch wallpaper data with calculated offset and selected type
            wallpaper_data = fetch_wallpaper_data(count, resolution, wallpaper_type, offset)
            
            if 'images' in wallpaper_data and len(wallpaper_data['images']) > 0:
                # Create new list or prepare to append
                if not append:
                    self.wallpaper_urls = []
                
                # Extract URLs from all images
                new_urls = []
                for image in wallpaper_data['images']:
                    url = f"https://www.bing.com{image['url']}"
                    new_urls.append(url)
                    print(f"Found wallpaper URL: {url}")
                
                # Add the new URLs to our collection
                if append:
                    self.wallpaper_urls.extend(new_urls)
                    print(f"Appended {len(new_urls)} wallpapers, total now {len(self.wallpaper_urls)}")
                else:
                    self.wallpaper_urls = new_urls
                    print(f"Set {len(new_urls)} wallpapers")
                
                # Set the current URL to the first one if we're on a fresh list
                if not append and self.wallpaper_urls:
                    self.current_index = 0  # Reset to first image
                    self.current_url = self.wallpaper_urls[0]
                    print(f"Set current URL to: {self.current_url}")
                    self.show_wallpaper(0)  # Show the first wallpaper
                    
                # If already showing a wallpaper, update the UI
                elif hasattr(self, 'image_label') and self.image_label and append:
                    self.update_navigation_buttons()
                    
                return len(new_urls)
            else:
                if hasattr(self, 'image_label'):
                    self.image_label.setText(f"No images found for {wallpaper_type}")
                print(f"No images found for type: {wallpaper_type}")
                return 0
        except Exception as e:
            import traceback
            print(f"Error fetching wallpapers: {e}")
            print(traceback.format_exc())
            if hasattr(self, 'image_label'):
                self.image_label.setText(f"Error fetching wallpapers: {str(e)}")
            return 0
    
    # Update show_next method to fetch more wallpapers when needed
    def show_next(self):
        """Show the next wallpaper, fetching more if needed"""
        next_index = self.current_index + 1
        
        # If we're near the end of our list, try to fetch more
        if next_index >= len(self.wallpaper_urls) - 2:
            self.page += 1  # Move to the next page
            items_added = self.fetch_wallpapers(self.fetch_count, append=True)
            print(f"Fetched {items_added} additional wallpapers")
        
        # Show the next wallpaper if available
        if next_index < len(self.wallpaper_urls):
            self.show_wallpaper(next_index)
    
    # Update the navigation button states
    def update_navigation_buttons(self):
        """Update button states based on current position"""
        if hasattr(self, 'prev_btn') and self.prev_btn:
            self.prev_btn.setEnabled(self.current_index > 0)
        
        if hasattr(self, 'next_btn') and self.next_btn:
            # Always enable next button - it will fetch more if needed
            self.next_btn.setEnabled(True)
        
        # Update title to show position
        if hasattr(self, 'setWindowTitle'):
            self.setWindowTitle(f"Wallpaper Preview ({self.current_index + 1}/{len(self.wallpaper_urls)})")
    
    # Update show_wallpaper to use the new update_navigation_buttons method
    def show_wallpaper(self, index):
        """Display the wallpaper at the given index"""
        if 0 <= index < len(self.wallpaper_urls):
            try:
                from PyQt5.QtGui import QPixmap
                from PyQt5.QtCore import Qt
                import requests
                from io import BytesIO
                
                # Update current index and URL
                self.current_index = index
                self.current_url = self.wallpaper_urls[index]
                
                # Download image data
                response = requests.get(self.current_url)
                image_data = BytesIO(response.content)
                
                # Create pixmap from image data
                pixmap = QPixmap()
                pixmap.loadFromData(image_data.read())
                
                # Scale pixmap to fit the dialog while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(780, 430, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                
                # Update navigation button states
                self.update_navigation_buttons()
                
            except Exception as e:
                self.image_label.setText(f"Failed to load image: {str(e)}")
        else:
            self.image_label.setText("No image at this index")
    
    def show_previous(self):
        """Show the previous wallpaper"""
        if self.current_index > 0:
            self.show_wallpaper(self.current_index - 1)
    
    def download_current(self):
        """Download the currently displayed wallpaper"""
        if self.current_url:
            # Start download in a separate thread to avoid UI freezing
            threading.Thread(
                target=lambda: self.wallpaper_app.download_wallpaper(self.current_url)
            ).start()
            
            # Notify user - don't close the dialog
            QtWidgets.QMessageBox.information(
                self,
                "Download Started",
                "The wallpaper download has started.\nYou can continue browsing while it downloads."
            )

class WallpaperApp:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.config_manager = ConfigManager()
        self.config_manager.load_config()
        self.downloader = WallpaperDownloader(self.config_manager.get_setting('daily_download_limit'))
        self.scheduler = Scheduler()
        
        # Initialize datetime attributes BEFORE starting scheduler
        self.app_start_time = datetime.datetime.now()
        self.last_download_time = self.app_start_time
        
        # Create save directory if it doesn't exist
        save_location = self.config_manager.get_setting('save_location') or os.path.abspath('data/wallpapers')
        os.makedirs(save_location, exist_ok=True)
        
        self.setup_ui()
        self.setup_scheduler()  # Now the thread will start after app_start_time is defined
        
    def setup_ui(self):
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(self.app.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))  # Default icon
        self.tray_icon.setToolTip('Bing Wallpaper Downloader')
        self.tray_icon.setVisible(True)

        self.menu = QMenu()
        self.menu.addAction("Download Now", self.manual_download)
        self.menu.addAction("Settings", self.open_settings)
        self.menu.addSeparator()
        self.menu.addAction("Exit", self.exit_app)
        self.tray_icon.setContextMenu(self.menu)
        
        # Show a notification
        self.tray_icon.showMessage(
            "Bing Wallpaper Downloader",
            "Application started in system tray",
            QSystemTrayIcon.Information,
            2000
        )

    def setup_scheduler(self):
        # Start scheduler in a separate thread
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def run_scheduler(self):
        frequency = self.config_manager.get_setting('download_frequency')
        wallpaper_type = self.config_manager.get_setting('wallpaper_type')
        resolution = self.config_manager.get_setting('resolution')
        
        # Schedule based on frequency setting
        self.scheduler.schedule_download(frequency, wallpaper_type, resolution)
        
        # Simple scheduler implementation
        while True:
            # Check every minute if it's time to download
            for task in self.scheduler.get_scheduled_tasks():
                if self.is_time_to_download(task):
                    self.download_wallpaper()
            time.sleep(60)  # Check every minute
    
    def is_time_to_download(self, task):
        """Check if it's time to download based on frequency setting"""
        import datetime
        now = datetime.datetime.now()
        frequency = task['frequency']
        
        # Get last download time from config or use app start time
        last_download = getattr(self, 'last_download_time', self.app_start_time)
        time_diff = (now - last_download).total_seconds()
        
        if frequency == '1 second':
            return time_diff >= 1
        elif frequency == '30 seconds':
            return time_diff >= 30
        elif frequency == '1 minute':
            return time_diff >= 60
        elif frequency == '15 minutes':
            return time_diff >= 900
        elif frequency == '30 minutes':
            return time_diff >= 1800
        elif frequency == 'hourly':
            return time_diff >= 3600
        elif frequency == 'daily':
            return time_diff >= 86400  # 24 hours
        elif frequency == 'weekly':
            return time_diff >= 604800  # 7 days
        
        return False

    def manual_download(self):
        try:
            print("Manual download requested")
            # Create preview dialog with reference to this app
            preview_dialog = WallpaperPreviewDialog(self, None)  # app first, parent=None
            
            # Show the dialog - no need to check result since downloading is handled internally
            print("Opening preview dialog")
            preview_dialog.exec_()
            print("Preview dialog closed")
            
        except Exception as e:
            import traceback
            print(f"Error in manual download: {str(e)}")
            print(traceback.format_exc())
            self.tray_icon.showMessage(
                "Preview Error",
                f"Error showing preview: {str(e)}",
                QSystemTrayIcon.Critical,
                5000  # Show for longer
            )

    def download_wallpaper(self, wallpaper_url=None):
        try:
            settings = self.config_manager.config
            save_location = settings.get('save_location', os.path.abspath('data/wallpapers'))
            
            # If URL not provided, fetch it
            if not wallpaper_url:
                wallpaper_type = settings.get('wallpaper_type', 'all')
                resolution = settings.get('resolution', '1920x1080')
                wallpaper_data = fetch_wallpaper_data(1, resolution, wallpaper_type)
                wallpaper_url = get_wallpaper_url(wallpaper_data)
            
            if wallpaper_url:
                # Generate filename with timestamp
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"bing_{timestamp}.jpg"
                save_path = os.path.join(save_location, filename)
                
                download_success = self.downloader.download_wallpaper(wallpaper_url, save_path)
                
                if download_success:
                    # Update last download time
                    self.last_download_time = datetime.datetime.now()
                    
                    # Show notification
                    self.tray_icon.showMessage(
                        "Wallpaper Downloaded",
                        f"New wallpaper saved to {save_path}",
                        QSystemTrayIcon.Information,
                        2000
                    )
                else:
                    self.tray_icon.showMessage(
                        "Download Failed",
                        "Failed to save wallpaper",
                        QSystemTrayIcon.Warning,
                        2000
                    )
            else:
                self.tray_icon.showMessage(
                    "Download Failed",
                    "Could not get wallpaper URL",
                    QSystemTrayIcon.Warning,
                    2000
                )
        except Exception as e:
            self.tray_icon.showMessage(
                "Error",
                f"Failed to download wallpaper: {str(e)}",
                QSystemTrayIcon.Critical,
                2000
            )

    def open_settings(self):
        try:
            print("Opening settings dialog...")
            self.settings_dialog = SettingsDialog(self.config_manager)
            result = self.settings_dialog.exec_()
            print(f"Dialog closed with result: {result} (Accepted={QDialog.Accepted})")
            
            if result == QDialog.Accepted:
                print("Settings were accepted, updating application...")
                # Get the latest settings
                frequency = self.config_manager.config.get('download_frequency')
                wallpaper_type = self.config_manager.config.get('wallpaper_type')
                resolution = self.config_manager.config.get('resolution')
                
                # Update downloader with new limits
                daily_limit = self.config_manager.config.get('daily_download_limit', 5)
                print(f"Setting download limit to: {daily_limit}")
                self.downloader.set_download_limit(daily_limit)
                
                # Update scheduler tasks
                print("Updating scheduler tasks...")
                self.scheduler.scheduled_tasks = []
                self.scheduler.schedule_download(frequency, wallpaper_type, resolution)
                print("Scheduler tasks updated successfully")
                
                # Show success message
                print("Showing success message")
                self.tray_icon.showMessage(
                    "Settings Saved",
                    "Your wallpaper settings have been updated",
                    QSystemTrayIcon.Information,
                    2000
                )
                print("Message displayed, processing events...")
                QtWidgets.QApplication.processEvents()
                print("Events processed, method complete")
        except Exception as e:
            import traceback
            print(f"Error in settings dialog: {e}")
            print(traceback.format_exc())
            self.tray_icon.showMessage(
                "Settings Error",
                f"Error saving settings: {str(e)}",
                QSystemTrayIcon.Critical,
                2000
            )
            QtWidgets.QApplication.processEvents()

    def exit_app(self):
        self.tray_icon.setVisible(False)
        QtWidgets.QApplication.quit()

    def run(self):
        # Add this to keep the app reference alive
        self.app.setQuitOnLastWindowClosed(False)
        return self.app.exec_()

def main():
    app = WallpaperApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main()