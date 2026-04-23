"""Main window for Lumina AI application."""

from datetime import datetime
import os
import json

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl, QDir
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebChannel import QWebChannel

from dialogs import SettingsDialog, PromptCollectionDialog, ModelManagerDialog
from ollama_client import OllamaClient, OllamaError, ConnectionError, ModelError, APIError
from backend_bridge import BackendBridge
from chat_manager import ChatManager
from rag_utils import parse_document
from PyQt6.QtWidgets import QFileDialog, QMessageBox
import json
import os

class TitleWorker(QThread):
    """Worker thread for async title generation."""
    completed = pyqtSignal(str)
    
    def __init__(self, client, model, text):
        super().__init__()
        self._client = client
        self._model = model
        self._text = text
        
    def run(self):
        try:
            prompt = [{"role": "user", "content": f"Summarize this text in 3 to 5 words, do not use quotes, keep it short: {self._text}"}]
            response = self._client.generate(
                model=self._model,
                prompt=prompt,
                stream=False
            )
            title = response.replace('"', '').replace("'", "").strip()
            self.completed.emit(title)
        except Exception:
            self.completed.emit("Untitled Chat")

class GenerationWorker(QThread):
    """Worker thread for async generation."""

    # Signals
    token_received = pyqtSignal(str)
    completed = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, client, model, prompt, system, temperature, max_tokens, top_p, stream):
        super().__init__()
        self._client = client
        self._model = model
        self._prompt = prompt
        self._system = system
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._top_p = top_p
        self._stream = stream
        self._running = True

    def run(self):
        try:
            if self._stream:
                import time
                full_response = []
                self._token_buffer = []
                self._last_emit_time = time.time()

                def token_callback(token):
                    if self._running:
                        full_response.append(token)
                        self._token_buffer.append(token)
                        current_time = time.time()
                        if current_time - self._last_emit_time > 0.05 or len(self._token_buffer) > 20:
                            self.token_received.emit("".join(self._token_buffer))
                            self._token_buffer.clear()
                            self._last_emit_time = current_time

                self._client.generate(
                    model=self._model,
                    prompt=self._prompt,
                    system=self._system,
                    temperature=self._temperature,
                    max_tokens=self._max_tokens,
                    top_p=self._top_p,
                    stream=True,
                    callback=token_callback,
                )
                if self._token_buffer:
                    self.token_received.emit("".join(self._token_buffer))
                self.completed.emit("".join(full_response))
            else:
                response = self._client.generate(
                    model=self._model,
                    prompt=self._prompt,
                    system=self._system,
                    temperature=self._temperature,
                    max_tokens=self._max_tokens,
                    top_p=self._top_p,
                    stream=False,
                )
                self.completed.emit(response)

        except ConnectionError as e:
            self.error.emit(f"Connection Error: {str(e)}")
        except ModelError as e:
            self.error.emit(f"Model Error: {str(e)}")
        except APIError as e:
            self.error.emit(f"API Error: {str(e)}")
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")

    def stop(self):
        self._running = False


class MainWindow(QMainWindow):
    """Main application window using WebEngine."""

    def __init__(self, settings_manager, theme_manager):
        super().__init__()
        self._settings = settings_manager
        self._theme = theme_manager

        self._ollama_client = OllamaClient(settings_manager.ollama_url)
        self._current_worker = None
        self._title_worker = None
        self._is_generating = False
        self._chat_manager = ChatManager()
        self._chat_manager.new_chat()
        self._rag_context = ""

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("Lumina AI")
        self.setMinimumSize(800, 600)

        # Central widget is the web view
        self.web_view = QWebEngineView()
        
        # Enables local file access for the web engine, required for some local assets
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.web_view.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        self.setCentralWidget(self.web_view)

        # Setup channel
        self.channel = QWebChannel()
        self.bridge = BackendBridge(self)
        self.channel.registerObject("backend", self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        # Connect bridge signals
        self.bridge.message_received.connect(self._on_bridge_message_received)
        self.bridge.theme_toggled.connect(self._on_theme_toggle)
        self.bridge.settings_opened.connect(self._on_settings_clicked)
        self.bridge.models_opened.connect(self._on_models_clicked)
        self.bridge.chat_loaded.connect(self._on_chat_loaded)
        self.bridge.attach_file_requested.connect(self._on_attach_file_clicked)
        self.bridge.chat_cleared.connect(self._on_clear_clicked)
        self.bridge.ui_ready.connect(self._on_ui_ready)
        self.bridge.rename_requested.connect(self._on_rename_requested)

        # Load initial theme HTML
        self._load_html_for_theme(self._theme.current_theme)

    def _load_html_for_theme(self, theme_name):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filename = "ui_dark.html" if theme_name == "dark" else "ui_light.html"
        file_path = os.path.join(base_dir, filename)
        url = QUrl.fromLocalFile(file_path)
        self.web_view.setUrl(url)

    def _connect_signals(self):
        """Connect signals and slots."""
        self._theme.theme_changed.connect(self._on_theme_changed)

    def _on_theme_toggle(self):
        """Triggered from web UI to toggle theme."""
        self._theme.toggle_theme()

    def _on_theme_changed(self, theme_name):
        """When theme manager updates, reload the HTML."""
        self._load_html_for_theme(theme_name)

    def _on_ui_ready(self):
        """Triggered from web UI once QWebChannel connects and page holds DOM."""
        self.web_view.page().runJavaScript("window.clearHistory();")
        
        avatar_url = "assets/icons/avatar.png"
        
        for msg in self._chat_manager.history:
            content = msg.get('content', '')
            escaped_content = json.dumps(content)[1:-1]
            js = f'window.addMessage("{msg.get("role", "")}", "{escaped_content}", "{avatar_url}");'
            self.web_view.page().runJavaScript(js)

        self._update_frontend_history()

        # Set UI state back
        state_js = f"window.setAiState({'true' if self._is_generating else 'false'});"
        self.web_view.page().runJavaScript(state_js)

    def _on_settings_clicked(self):
        """Handle settings button click."""
        dialog = SettingsDialog(self._settings, self)
        dialog.exec()
        # Refresh settings in case they changed
        self._ollama_client.base_url = self._settings.ollama_url

    def _on_models_clicked(self):
        """Handle manage models click."""
        dialog = ModelManagerDialog(self._ollama_client, self)
        dialog.exec()

    def _update_frontend_history(self):
        convs = self._chat_manager.get_conversations()
        convs_json = json.dumps(convs)
        self.web_view.page().runJavaScript(f"window.renderHistory({convs_json});")

    def _on_chat_loaded(self, chat_id: str):
        if self._chat_manager.load_chat(chat_id):
            self.web_view.page().runJavaScript("window.clearHistory();")
            self._rag_context = ""
            avatar_url = "assets/icons/avatar.png"
            for msg in self._chat_manager.history:
                content = msg.get('content', '')
                escaped_content = json.dumps(content)[1:-1]
                js = f'window.addMessage("{msg.get("role", "")}", "{escaped_content}", "{avatar_url}");'
                self.web_view.page().runJavaScript(js)

    def _on_clear_clicked(self):
        """Handle new chat button click."""
        self._chat_manager.new_chat()
        self._rag_context = ""
        self.web_view.page().runJavaScript("window.clearHistory();")
        self._update_frontend_history()

    def _on_rename_requested(self, chat_id: str, new_title: str):
        """Handle renaming a chat session."""
        self._chat_manager.rename_chat(chat_id, new_title)
        self._update_frontend_history()

    def _on_attach_file_clicked(self):
        """Handle attachment click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Attach Document", "", "Documents (*.txt *.md *.pdf *.csv);;All Files (*)"
        )
        if file_path:
            content = parse_document(file_path)
            if content:
                self._rag_context += f"\\n\\n--- Document: {os.path.basename(file_path)} ---\\n{content}\\n"
                js = f"alert('Attached {os.path.basename(file_path)} successfully.');"
                self.web_view.page().runJavaScript(js)
            else:
                self.web_view.page().runJavaScript("alert('Failed to read document or document is empty.');")

    def _on_bridge_message_received(self, text):
        """Called by Javascript when the send button is clicked."""
        if self._is_generating:
            return

        self._is_generating = True
        self.web_view.page().runJavaScript("window.setAiState(true);")

        # Select model
        model = self._settings.default_model
        if not model:
            # Fallback
            try:
                models = self._ollama_client.get_models()
                if models:
                    model = models[0].get("name", "llama2")
                else:
                    model = "llama2"
            except Exception:
                model = "llama2"

        # Record user message
        self._chat_manager.add_message("user", text)
        
        escaped_content = json.dumps(text)[1:-1]
        avatar_url = "assets/icons/avatar.png"
        self.web_view.page().runJavaScript(f'window.addMessage("user", "{escaped_content}", "{avatar_url}");')

        # Add assistant message placeholder
        self.web_view.page().runJavaScript('window.startAiMessage();')
        self._current_response = []

        system = self._settings.system_prompt
        temperature = self._settings.temperature
        max_tokens = self._settings.max_tokens
        top_p = self._settings.top_p
        stream = self._settings.stream

        # Build prompt history
        prompts = []
        if system or self._rag_context:
            sys_combined = system or ""
            if self._rag_context:
                sys_combined += f"\\n\\nAdditional Context:\\n{self._rag_context}"
            prompts.append({'role': 'system', 'content': sys_combined})
        
        MAX_HISTORY = 10
        context_history = self._chat_manager.history[-MAX_HISTORY:] if len(self._chat_manager.history) > MAX_HISTORY else self._chat_manager.history
        prompts.extend(context_history)

        # The chat_manager already added the latest user message, so we don't append again

        self._current_worker = GenerationWorker(
            self._ollama_client, model, prompts, system, temperature, max_tokens, top_p, stream
        )
        self._current_worker.token_received.connect(self._on_token_received)
        self._current_worker.completed.connect(self._on_generation_completed)
        self._current_worker.error.connect(self._on_generation_error)
        self._current_worker.start()

    def _on_token_received(self, token):
        """Handle received token from streaming."""
        self._current_response.append(token)
        escaped_token = json.dumps(token)[1:-1]
        self.web_view.page().runJavaScript(f'window.appendAiToken("{escaped_token}");')

    def _on_generation_completed(self, response):
        """Handle generation completed."""
        content = "".join(self._current_response) if self._current_response else response
        self._chat_manager.add_message("assistant", content)
        self._update_frontend_history()
        self._finish_generation()
        
        if self._chat_manager.current_chat_title in ["Untitled Chat", None] and self._chat_manager.current_chat_id:
            user_msg = ""
            for msg in reversed(self._chat_manager.history):
                if msg.get("role") == "user":
                    user_msg = msg.get("content", "")
            if user_msg:
                model = self._settings.default_model or "llama2"
                self._title_worker = TitleWorker(self._ollama_client, model, user_msg)
                self._title_worker.completed.connect(self._on_title_generated)
                self._title_worker.start()

    def _on_title_generated(self, title: str):
        """Handle async title generation."""
        if title and title != "Untitled Chat" and self._chat_manager.current_chat_id:
            self._chat_manager.rename_chat(self._chat_manager.current_chat_id, title)
            self._update_frontend_history()

    def _on_generation_error(self, error):
        """Handle generation error."""
        self._show_error("Generation Error", error)
        self._finish_generation()

    def _finish_generation(self):
        """Finish generation and re-enable input."""
        self._is_generating = False
        self.web_view.page().runJavaScript('window.finishAiMessage();')
        self.web_view.page().runJavaScript('window.setAiState(false);')
        
        if self._current_worker:
            self._current_worker.deleteLater()
            self._current_worker = None

    def _show_error(self, title, message):
        """Show an error message box."""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.exec()

    def closeEvent(self, event):
        """Handle window close event."""
        if self._current_worker and self._current_worker.isRunning():
            self._current_worker.stop()
            self._current_worker.wait()
        event.accept()
