#!/usr/bin/env python3
"""Main entry point for Lumina AI application."""

import sys
import os

# Add the application directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from settings_manager import SettingsManager
from theme_manager import ThemeManager
from main_window import MainWindow


def main():
    """Main application entry point."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Lumina AI")
    app.setOrganizationName("Lumina")

    # Initialize settings manager
    settings = SettingsManager()

    # Initialize theme manager
    theme_manager = ThemeManager(settings)
    theme_manager.set_app(app)

    # Detect system theme on first launch
    if settings.theme == "dark" and not os.path.exists(settings._config_path):
        # First launch - try to detect system theme
        detected = theme_manager.detect_system_theme()
        settings.theme = detected

    # Apply initial theme
    theme_manager.load_theme()

    # Create and show main window
    window = MainWindow(settings, theme_manager)
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
