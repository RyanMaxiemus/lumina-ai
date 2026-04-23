# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Lumina AI is a PyQt6-based desktop chat application that connects to a local Ollama instance for LLM inference with streaming responses.

## Running the Application

```bash
python3 main.py
```

Requires Ollama running on `http://localhost:11434`.

## Architecture

- **main.py** - Entry point, initializes QApplication, SettingsManager, ThemeManager, and MainWindow
- **main_window.py** - MainWindow class containing all UI components and chat logic
- **ollama_client.py** - Ollama API client with streaming support (OllamaClient, AsyncOllamaClient)
- **theme_manager.py** - ThemeManager handles theme detection (via gsettings on GNOME) and switching
- **settings_manager.py** - SettingsManager for JSON-based configuration persistence
- **chat_widgets.py** - ChatMessageWidget and ChatHistoryWidget for message display
- **dialogs.py** - SettingsDialog and PromptCollectionDialog

## Key Design Patterns

- **GenerationWorker** (QThread in main_window.py) - Handles async Ollama API calls to prevent UI freezing
- **ThemeManager signals** - theme_changed signal emitted on theme toggle
- **Settings are persisted** to config.json in the app directory

## Color Scheme

- Dark mode accent: `#1181c8` (vibrant light blue)
- Dark background: `#1e1e2e`
- Light background: `#f5f5f7`

## Dependencies

- PyQt6>=6.6.0
- requests>=2.31.0
- Python>=3.10
