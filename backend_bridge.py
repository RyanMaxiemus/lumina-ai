from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal

class BackendBridge(QObject):
    """Bridge between PyQt Python backend and JavaScript frontend."""

    # Signals going to JS (but usually we call JS functions directly via page().runJavaScript)
    # We define signals here if we want to use QWebChannel signal/slot mechanism, 
    # but runJavaScript is simpler for pushing data.
    
    # Signals to Python (to alert MainWindow)
    message_received = pyqtSignal(str)
    theme_toggled = pyqtSignal()
    settings_opened = pyqtSignal()
    models_opened = pyqtSignal()
    chat_loaded = pyqtSignal(str)
    attach_file_requested = pyqtSignal()
    chat_cleared = pyqtSignal()
    ui_ready = pyqtSignal()
    rename_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot(str)
    def send_message(self, text: str):
        """Called by JS when the user sends a message."""
        self.message_received.emit(text)

    @pyqtSlot()
    def toggle_theme(self):
        """Called by JS when the theme button is clicked."""
        self.theme_toggled.emit()

    @pyqtSlot()
    def open_settings(self):
        """Called by JS when settings button is clicked."""
        self.settings_opened.emit()

    @pyqtSlot()
    def open_models(self):
        """Called by JS when models button is clicked."""
        self.models_opened.emit()

    @pyqtSlot(str)
    def load_chat(self, chat_id: str):
        """Called by JS when a chat from history is clicked."""
        self.chat_loaded.emit(chat_id)

    @pyqtSlot()
    def attach_file(self):
        """Called by JS when attach file is clicked."""
        self.attach_file_requested.emit()

    @pyqtSlot()
    def clear_chat(self):
        """Called by JS when new chat/clear button is clicked."""
        self.chat_cleared.emit()

    @pyqtSlot()
    def page_loaded(self):
        """Called by JS when the channel is established and DOM is ready."""
        self.ui_ready.emit()

    @pyqtSlot(str, str)
    def rename_chat(self, chat_id: str, new_title: str):
        """Called by JS when user renames a chat."""
        self.rename_requested.emit(chat_id, new_title)
