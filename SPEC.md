# Lumina AI - Ollama Chat Application Specification

## 1. Project Overview

**Project Name**: Lumina AI
**Type**: Desktop Chat Application
**Core Functionality**: A PyQt6-based chat interface that connects to a local Ollama instance for LLM inference with streaming responses
**Target Users**: Users who want a clean, modern desktop interface for interacting with local LLM models via Ollama

---

## 2. UI/UX Specification

### 2.1 Window Structure

- **Main Window**: `QMainWindow` with minimum size 800x600, default 1000x700
- **Layout**: Vertical layout with:
  - Header area (model selection, theme toggle, settings)
  - Chat display area (scrollable, takes remaining space)
  - Input area (prompt text edit + send button)
  - Status bar (connection status, model info)

### 2.2 Visual Design

#### Color Palette

**Dark Mode (Default)**:
- Background Primary: `#1e1e2e` (deep navy)
- Background Secondary: `#2a2a3e` (slightly lighter)
- Text Primary: `#e4e4ef` (off-white)
- Text Secondary: `#a0a0b0` (muted gray)
- Accent: `#1181c8` (vibrant light blue)
- Accent Hover: `#1496e8` (brighter blue)
- User Message BG: `#2d3f5a` (blue-tinted dark)
- AI Message BG: `#2a2a3e` (secondary background)
- Error: `#e54d4d` (red)
- Success: `#4de58a` (green)

**Light Mode**:
- Background Primary: `#f5f5f7` (light gray)
- Background Secondary: `#ffffff` (white)
- Text Primary: `#1e1e2e` (dark navy)
- Text Secondary: `#606070` (muted gray)
- Accent: `#1181c8` (vibrant light blue)
- Accent Hover: `#0d6dad` (darker blue)
- User Message BG: `#e3eaf3` (light blue tint)
- AI Message BG: `#ffffff` (white)
- Error: `#d93a3a` (red)
- Success: `#2ab856` (green)

#### Typography

- **Font Family**: System default (Segoe UI on Windows, Ubuntu/ Cantarell on Linux)
- **Heading Size**: 16px (window title)
- **Body Size**: 14px (chat messages)
- **Input Size**: 14px
- **Small/Status**: 12px

#### Spacing System

- Window padding: 0px (frameless-style content)
- Section padding: 16px
- Component spacing: 12px
- Message bubble padding: 12px
- Message spacing: 8px

#### Visual Effects

- **Button Glow (Dark Mode)**: `box-shadow: 0 0 15px rgba(17, 129, 200, 0.5)` on hover
- **Button Border Radius**: 8px
- **Message Border Radius**: 12px
- **Input Border Radius**: 8px

### 2.3 Components

#### Header Bar
- Model dropdown (QComboBox) - left side
- Settings button (QPushButton) - right side
- Theme toggle button (QPushButton with icon) - right side

#### Chat Display Area
- QScrollArea containing QWidget with QVBoxLayout
- Each message is a QFrame with:
  - Role label (User/AI) in accent color
  - Message content in QLabel
  - Timestamp (subtle, bottom-right)
- Auto-scrolls to bottom on new message

#### Input Area
- QTextEdit for multi-line input (min height 60px, max height 150px)
- Send button (QPushButton) with icon
- Prompt collection button (QPushButton) to open saved prompts

#### Status Bar
- Connection status indicator (green dot = connected, red = disconnected)
- Model name display
- Character count

#### Settings Dialog (QDialog)
- System prompt text edit
- Generation parameters:
  - Temperature slider (0.0 - 2.0, default 0.7)
  - Max tokens input (default 2048)
  - Top-p slider (0.0 - 1.0, default 0.9)
- Stream toggle checkbox Dialog (

#### Prompt CollectionQDialog)
- List of saved prompts (QListWidget)
- Add new prompt button
- Delete prompt button
- Use prompt button (inserts into input)

---

## 3. Functional Specification

### 3.1 Core Features

1. **Chat Functionality**
   - Send user prompts to Ollama /api/generate endpoint
   - Stream responses token-by-token
   - Display both user and AI messages in scrollable history
   - Handle streaming and non-streaming modes

2. **Ollama Integration**
   - Connect to http://localhost:11434
   - Use /api/generate endpoint
   - Configurable default model
   - Fetch available models from /api/tags endpoint

3. **Theme Management**
   - Detect system theme via gsettings on GNOME
   - Dark/Light mode toggle
   - Persist theme preference
   - Animated/smooth theme switch

4. **Error Handling**
   - Ollama server not running → Show connection error with retry option
   - Invalid model → Show error, suggest available models
   - API errors → Display user-friendly message
   - Network timeout → Allow retry

### 3.2 User Interactions

- Type prompt in input area → Press Enter (with Ctrl) or click Send
- Click theme toggle → Switch between dark/light
- Click settings → Open settings dialog
- Click prompt collection → Open prompt library
- Click clear history → Confirm and clear chat

### 3.3 Data Flow

1. **App Launch**:
   - Detect system theme
   - Load saved settings from config file
   - Fetch available Ollama models
   - Display main window

2. **Send Message**:
   - Validate input (not empty)
   - Add user message to history
   - Start async request to Ollama
   - Stream response to chat
   - Handle errors gracefully

3. **Settings Change**:
   - Update parameters in memory
   - Save to config file
   - Apply immediately

### 3.4 Key Modules/Classes

- `main.py` - Application entry point
- `main_window.py` - MainWindow class
- `ollama_client.py` - Ollama API client
- `theme_manager.py` - Theme detection and switching
- `settings_manager.py` - Configuration persistence
- `chat_history.py` - Chat message model
- `dialogs.py` - Settings and Prompt Collection dialogs

### 3.5 Edge Cases

- Empty prompt submission → Ignore/disable send
- Very long responses → Handle gracefully, no UI freeze
- Ollama model not found → Show error, suggest valid models
- Rapid successive prompts → Queue or cancel previous
- Window resize → Responsive layout

---

## 4. Acceptance Criteria

### 4.1 Success Conditions

- [ ] Application launches without errors
- [ ] Dark/Light theme toggle works correctly
- [ ] System theme detection works on GNOME
- [ ] Can connect to local Ollama instance
- [ ] Chat messages display correctly (user and AI)
- [ ] Streaming responses appear in real-time
- [ ] Settings dialog opens and saves parameters
- [ ] Model selection dropdown populates from Ollama
- [ ] Prompt collection saves and loads prompts
- [ ] Clear history works
- [ ] Error messages display for connection issues
- [ ] UI does not freeze during API calls

### 4.2 Visual Checkpoints

- [ ] Dark mode has #1181c8 accent with glow effect on buttons
- [ ] Light mode has clean, modern appearance
- [ ] Theme toggle icon reflects next theme (sun for dark, moon for light)
- [ ] Messages have proper bubble styling
- [ ] Input area resizes appropriately
- [ ] Status bar shows correct connection state

---

## 5. File Structure

```
lumina-ai/
├── main.py                 # Entry point
├── main_window.py         # Main window UI
├── ollama_client.py       # Ollama API client
├── theme_manager.py       # Theme management
├── settings_manager.py    # Settings persistence
├── chat_widgets.py        # Chat message widgets
├── dialogs.py             # Settings & prompt collection dialogs
├── assets/
│   ├── icons/
│   │   ├── sun.png         # 24x24 theme toggle icon
│   │   ├── moon.png        # 24x24 theme toggle icon
│   │   ├── send.png        # 24x24 send button icon
│   │   ├── settings.png    # 24x24 settings icon
│   │   └── prompts.png     # 24x24 prompt collection icon
│   └── themes/
│       ├── dark_theme.qss
│       └── light_theme.qss
└── config.json            # User settings (generated)
```

---

## 6. Dependencies

- PyQt6>=6.6.0
- requests>=2.31.0
- python>=3.10
