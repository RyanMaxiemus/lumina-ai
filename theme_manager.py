"""Theme manager for Lumina AI application."""

import os
import subprocess
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication


class ThemeManager(QObject):
    """Manages application themes with system theme detection."""

    # Signals
    theme_changed = pyqtSignal(str)  # Emitted when theme changes

    def __init__(self, settings_manager):
        """Initialize theme manager.

        Args:
            settings_manager: SettingsManager instance for persisting theme.
        """
        super().__init__()
        self._settings = settings_manager
        self._current_theme = settings_manager.theme or "dark"
        self._app: Optional[QApplication] = None

    def set_app(self, app: QApplication) -> None:
        """Set the QApplication instance.

        Args:
            app: The QApplication instance.
        """
        self._app = app

    def detect_system_theme(self) -> str:
        """Detect system theme using gsettings on GNOME.

        Returns:
            'dark' or 'light' based on system preference.
        """
        try:
            # Try to get color-scheme preference (GNOME 42+)
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                value = result.stdout.strip().lower()
                if "dark" in value:
                    return "dark"
                elif "light" in value:
                    return "light"

            # Fallback to gtk-theme detection
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                theme_name = result.stdout.strip().lower()
                # Common dark theme names
                dark_keywords = ["dark", "arc-dark", "adwaita-dark", "Yaru-dark", "numix"]
                light_keywords = ["light", "adwaita", "Yaru", "ubuntu"]

                for keyword in dark_keywords:
                    if keyword in theme_name:
                        return "dark"
                for keyword in light_keywords:
                    if keyword in theme_name:
                        return "light"

        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Try Qt's platform theme detection as fallback
        if self._app:
            palette = self._app.palette()
            # Check if dark mode based on window text color brightness
            window_text = palette.windowText().color()
            if window_text.red() + window_text.green() + window_text.blue() < 384:
                return "dark"

        # Default to dark if detection fails
        return "dark"

    def get_theme_path(self, theme_name: str) -> str:
        """Get the full path to a theme QSS file.

        Args:
            theme_name: Theme name ('dark' or 'light').

        Returns:
            Full path to the theme QSS file.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if theme_name == "light":
            return os.path.join(base_dir, "assets", "themes", "light_theme.qss")
        else:
            return os.path.join(base_dir, "assets", "themes", "dark_theme.qss")

    def load_theme(self, theme_name: Optional[str] = None) -> bool:
        """Load and apply a theme.

        Args:
            theme_name: Theme name ('dark' or 'light'). If None, uses current.

        Returns:
            True if theme was loaded successfully.
        """
        if theme_name is None:
            theme_name = self._current_theme

        if theme_name not in ("dark", "light"):
            theme_name = "dark"

        theme_path = self.get_theme_path(theme_name)

        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                stylesheet = f.read()

            if self._app:
                self._app.setStyleSheet(stylesheet)

            self._current_theme = theme_name
            self._settings.theme = theme_name
            self.theme_changed.emit(theme_name)
            return True

        except (IOError, FileNotFoundError) as e:
            print(f"Error loading theme: {e}")
            return False

    def toggle_theme(self) -> str:
        """Toggle between dark and light themes.

        Returns:
            The new theme name.
        """
        new_theme = "light" if self._current_theme == "dark" else "dark"
        self.load_theme(new_theme)
        return new_theme

    @property
    def current_theme(self) -> str:
        """Get current theme name."""
        return self._current_theme

    @property
    def is_dark(self) -> bool:
        """Check if current theme is dark."""
        return self._current_theme == "dark"

    @property
    def next_theme_icon(self) -> str:
        """Get icon name for the next theme (for toggle button).

        Returns:
            'sun' for switching to light, 'moon' for switching to dark.
        """
        return "sun" if self._current_theme == "dark" else "moon"

    def get_icon_path(self, icon_name: str) -> str:
        """Get full path to an icon asset.

        Args:
            icon_name: Name of the icon file (without extension).

        Returns:
            Full path to the icon file.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "assets", "icons", f"{icon_name}.png")
