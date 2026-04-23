"""Chat widgets for Lumina AI application."""

from datetime import datetime
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QTextCursor, QTextDocument


class ChatMessageWidget(QFrame):
    """Widget for displaying a single chat message."""

    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"

    def __init__(self, role: str, content: str, timestamp: datetime = None, parent=None):
        """Initialize chat message widget.

        Args:
            role: Message role ('user' or 'assistant').
            content: Message content.
            timestamp: Optional message timestamp.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._role = role
        self._timestamp = timestamp or datetime.now()

        self._setup_ui()
        self.set_content(content)

    def _setup_ui(self):
        """Set up the UI components."""
        # Set frame properties
        self.setFrameShape(QFrame.Shape.NoFrame)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Header with role label
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        role_label = QLabel(self._role.capitalize())
        role_label.setObjectName("roleLabel")

        if self._role == self.ROLE_USER:
            self.setObjectName("userMessageFrame")
            role_label.setObjectName("userRoleLabel")
            role_label.setStyleSheet("color: #1181c8; font-weight: bold; font-size: 12px;")
        else:
            self.setObjectName("aiMessageFrame")
            role_label.setObjectName("aiRoleLabel")
            role_label.setStyleSheet("color: #4de58a; font-weight: bold; font-size: 12px;")

        header_layout.addWidget(role_label)
        header_layout.addStretch()

        # Timestamp
        timestamp_label = QLabel(self._timestamp.strftime("%H:%M"))
        timestamp_label.setObjectName("timestampLabel")
        timestamp_label.setStyleSheet("color: #606070; font-size: 11px;")
        header_layout.addWidget(timestamp_label)

        layout.addLayout(header_layout)

        # Message content
        content_label = QLabel()
        content_label.setObjectName("messageLabel")
        content_label.setWordWrap(True)
        content_label.setTextFormat(Qt.TextFormat.PlainText)
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        content_label.setOpenExternalLinks(True)

        # Set style based on role
        if self._role == self.ROLE_USER:
            content_label.setStyleSheet("color: #e4e4ef; font-size: 14px; line-height: 1.5;")
        else:
            content_label.setStyleSheet("color: #e4e4ef; font-size: 14px; line-height: 1.5;")

        layout.addWidget(content_label)
        self._content_label = content_label

    def set_content(self, content: str):
        """Set the message content.

        Args:
            content: The message text.
        """
        # Escape HTML characters for safe display
        escaped = self._escape_html(content)
        self._content_label.setText(escaped)

    def append_content(self, content: str):
        """Append content to the message (for streaming).

        Args:
            content: The text to append.
        """
        # Escape HTML characters
        escaped = self._escape_html(content)
        current = self._content_label.text()
        self._content_label.setText(current + escaped)

    def get_content(self) -> str:
        """Get the message content.

        Returns:
            The message text.
        """
        return self._content_label.text()

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters.

        Args:
            text: Text to escape.

        Returns:
            Escaped text.
        """
        return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )


class ChatHistoryWidget(QWidget):
    """Widget for displaying the chat history."""

    def __init__(self, parent=None):
        """Initialize chat history widget.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self._messages: list[ChatMessageWidget] = []
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        from PyQt6.QtWidgets import QVBoxLayout

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addStretch()

    def add_message(self, role: str, content: str = "", timestamp: datetime = None) -> ChatMessageWidget:
        """Add a new message to the chat history.

        Args:
            role: Message role ('user' or 'assistant').
            content: Optional initial content.
            timestamp: Optional timestamp.

        Returns:
            The created ChatMessageWidget.
        """
        # Remove the stretch
        layout = self.layout()
        if layout.count() > 0 and layout.itemAt(layout.count() - 1).spacerItem():
            layout.removeItem(layout.itemAt(layout.count() - 1))

        # Create and add message widget
        message = ChatMessageWidget(role, content, timestamp)
        self._messages.append(message)
        layout.addWidget(message)

        # Add stretch back
        layout.addStretch()

        return message

    def clear(self):
        """Clear all messages from the chat history."""
        layout = self.layout()

        # Remove all message widgets
        for message in self._messages:
            layout.removeWidget(message)
            message.deleteLater()

        self._messages.clear()

        # Add stretch back
        layout.addStretch()

    def get_message_count(self) -> int:
        """Get the number of messages.

        Returns:
            Number of messages.
        """
        return len(self._messages)

    def get_messages(self) -> list:
        """Get all message widgets.

        Returns:
            List of ChatMessageWidget instances.
        """
        return self._messages

    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat history."""
        # This will be called from the parent widget that has the scroll area
        pass
