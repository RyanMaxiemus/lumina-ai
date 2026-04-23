"""Settings manager for Lumina AI application."""

import json
import os
from typing import Any, Dict, Optional


class SettingsManager:
    """Manages application settings with persistence to JSON file."""

    DEFAULT_SETTINGS = {
        "theme": "dark",  # "dark" or "light"
        "default_model": "llama2",
        "system_prompt": "You are a helpful AI assistant.",
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 0.9,
        "stream": True,
        "ollama_url": "http://localhost:11434",
        "prompts": [],  # List of saved prompts
        "personas": [{"id": "default", "name": "Default AI", "prompt": "You are a helpful AI assistant."}],
        "active_persona_id": "default",
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize settings manager.

        Args:
            config_path: Optional path to config file. If None, uses default location.
        """
        if config_path is None:
            # Use config.json in the same directory as main.py
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, "config.json")

        self._config_path = config_path
        self._settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create default settings."""
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged = self.DEFAULT_SETTINGS.copy()
                    merged.update(settings)
                    return merged
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading settings: {e}")

        # Return defaults
        return self.DEFAULT_SETTINGS.copy()

    def _save_settings(self) -> None:
        """Save current settings to file."""
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value.

        Args:
            key: Setting key name.
            default: Default value if key doesn't exist.

        Returns:
            Setting value or default.
        """
        return self._settings.get(key, default)

    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set a setting value.

        Args:
            key: Setting key name.
            value: Value to set.
            save: Whether to persist to file immediately.
        """
        self._settings[key] = value
        if save:
            self._save_settings()

    def get_all(self) -> Dict[str, Any]:
        """Get all settings.

        Returns:
            Dictionary of all settings.
        """
        return self._settings.copy()

    def set_all(self, settings: Dict[str, Any], save: bool = True) -> None:
        """Set multiple settings at once.

        Args:
            settings: Dictionary of settings to update.
            save: Whether to persist to file immediately.
        """
        self._settings.update(settings)
        if save:
            self._save_settings()

    def reset(self) -> None:
        """Reset all settings to defaults."""
        self._settings = self.DEFAULT_SETTINGS.copy()
        self._save_settings()

    # Convenience methods for common settings

    @property
    def theme(self) -> str:
        """Get current theme."""
        return self.get("theme", "dark")

    @theme.setter
    def theme(self, value: str) -> None:
        """Set theme."""
        self.set("theme", value)

    @property
    def default_model(self) -> str:
        """Get default model."""
        return self.get("default_model", "llama2")

    @default_model.setter
    def default_model(self, value: str) -> None:
        """Set default model."""
        self.set("default_model", value)

    @property
    def system_prompt(self) -> str:
        """Get system prompt."""
        active_id = self.active_persona_id
        for p in self.personas:
            if p.get("id") == active_id:
                return p.get("prompt", "")
        return self.get("system_prompt", "")

    @system_prompt.setter
    def system_prompt(self, value: str) -> None:
        """Set system prompt for active persona."""
        active_id = self.active_persona_id
        personas_list = self.personas
        for p in personas_list:
            if p.get("id") == active_id:
                p["prompt"] = value
                self.personas = personas_list
                return
        
        # If not found, create new
        personas_list.append({"id": active_id, "name": active_id, "prompt": value})
        self.personas = personas_list

    @property
    def personas(self) -> list:
        return self.get("personas", [{"id": "default", "name": "Default AI", "prompt": self.get("system_prompt", "You are a helpful AI assistant.")}])

    @personas.setter
    def personas(self, value: list) -> None:
        self.set("personas", value)

    @property
    def active_persona_id(self) -> str:
        return self.get("active_persona_id", "default")

    @active_persona_id.setter
    def active_persona_id(self, value: str) -> None:
        self.set("active_persona_id", value)

    @property
    def temperature(self) -> float:
        """Get temperature setting."""
        return self.get("temperature", 0.7)

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set temperature."""
        self.set("temperature", value)

    @property
    def max_tokens(self) -> int:
        """Get max tokens setting."""
        return self.get("max_tokens", 2048)

    @max_tokens.setter
    def max_tokens(self, value: int) -> None:
        """Set max tokens."""
        self.set("max_tokens", value)

    @property
    def top_p(self) -> float:
        """Get top_p setting."""
        return self.get("top_p", 0.9)

    @top_p.setter
    def top_p(self, value: float) -> None:
        """Set top_p."""
        self.set("top_p", value)

    @property
    def stream(self) -> bool:
        """Get stream setting."""
        return self.get("stream", True)

    @stream.setter
    def stream(self, value: bool) -> None:
        """Set stream."""
        self.set("stream", value)

    @property
    def ollama_url(self) -> str:
        """Get Ollama URL."""
        return self.get("ollama_url", "http://localhost:11434")

    @ollama_url.setter
    def ollama_url(self, value: str) -> None:
        """Set Ollama URL."""
        self.set("ollama_url", value)

    @property
    def prompts(self) -> list:
        """Get saved prompts list."""
        return self.get("prompts", [])

    @prompts.setter
    def prompts(self, value: list) -> None:
        """Set prompts list."""
        self.set("prompts", value)

    def add_prompt(self, prompt: str, name: str = "") -> None:
        """Add a prompt to the saved prompts list.

        Args:
            prompt: The prompt text.
            name: Optional name/label for the prompt.
        """
        prompts = self.prompts
        prompts.append({"name": name or f"Prompt {len(prompts) + 1}", "text": prompt})
        self.prompts = prompts

    def remove_prompt(self, index: int) -> None:
        """Remove a prompt by index.

        Args:
            index: Index of the prompt to remove.
        """
        prompts = self.prompts
        if 0 <= index < len(prompts):
            prompts.pop(index)
            self.prompts = prompts

    def get_prompt(self, index: int) -> Optional[Dict[str, str]]:
        """Get a prompt by index.

        Args:
            index: Index of the prompt.

        Returns:
            Prompt dict with 'name' and 'text' keys, or None if not found.
        """
        prompts = self.prompts
        if 0 <= index < len(prompts):
            return prompts[index]
        return None
