"""Dialogs for Lumina AI application."""

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QLineEdit, QTextEdit, QSlider,
    QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton,
    QListWidget, QListWidgetItem, QDialogButtonBox,
    QWidget, QFormLayout, QComboBox, QInputDialog, QMessageBox
)


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, settings_manager, parent=None):
        """Initialize settings dialog.

        Args:
            settings_manager: SettingsManager instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._settings = settings_manager
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(450)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # System Prompt Group
        system_group = QGroupBox("Persona & System Prompt")
        system_layout = QVBoxLayout()

        persona_layout = QHBoxLayout()
        persona_layout.addWidget(QLabel("Persona:"))
        self.persona_combo = QComboBox()
        self.persona_combo.currentIndexChanged.connect(self._on_persona_changed)
        persona_layout.addWidget(self.persona_combo)

        self.add_persona_btn = QPushButton("New")
        self.add_persona_btn.clicked.connect(self._add_persona)
        persona_layout.addWidget(self.add_persona_btn)

        self.del_persona_btn = QPushButton("Delete")
        self.del_persona_btn.clicked.connect(self._del_persona)
        persona_layout.addWidget(self.del_persona_btn)

        system_layout.addLayout(persona_layout)

        self.system_prompt_edit = QTextEdit()
        self.system_prompt_edit.setPlaceholderText("Enter system prompt...")
        self.system_prompt_edit.setMaximumHeight(80)
        self.system_prompt_edit.textChanged.connect(self._on_prompt_edited)
        system_layout.addWidget(self.system_prompt_edit)

        system_group.setLayout(system_layout)
        layout.addWidget(system_group)

        # Generation Parameters Group
        params_group = QGroupBox("Generation Parameters")
        params_layout = QFormLayout()

        # Temperature
        temp_layout = QHBoxLayout()
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 20)  # 0.0 to 2.0
        self.temperature_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.temperature_slider.setTickInterval(5)
        self.temperature_value = QDoubleSpinBox()
        self.temperature_value.setRange(0.0, 2.0)
        self.temperature_value.setSingleStep(0.1)
        self.temperature_value.setDecimals(1)
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_value)
        temp_layout.addWidget(QLabel(""))

        # Connect slider and spinbox
        self.temperature_slider.valueChanged.connect(
            lambda v: self.temperature_value.setValue(v / 10.0)
        )
        self.temperature_value.valueChanged.connect(
            lambda v: self.temperature_slider.setValue(int(v * 10))
        )

        params_layout.addRow("Temperature:", temp_layout)

        # Max Tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 8192)
        self.max_tokens_spin.setSingleStep(128)
        params_layout.addRow("Max Tokens:", self.max_tokens_spin)

        # Top-p
        top_p_layout = QHBoxLayout()
        self.top_p_slider = QSlider(Qt.Orientation.Horizontal)
        self.top_p_slider.setRange(0, 100)  # 0.0 to 1.0
        self.top_p_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.top_p_slider.setTickInterval(25)
        self.top_p_value = QDoubleSpinBox()
        self.top_p_value.setRange(0.0, 1.0)
        self.top_p_value.setSingleStep(0.1)
        self.top_p_value.setDecimals(1)
        top_p_layout.addWidget(self.top_p_slider)
        top_p_layout.addWidget(self.top_p_value)
        top_p_layout.addWidget(QLabel(""))

        self.top_p_slider.valueChanged.connect(
            lambda v: self.top_p_value.setValue(v / 100.0)
        )
        self.top_p_value.valueChanged.connect(
            lambda v: self.top_p_slider.setValue(int(v * 100))
        )

        params_layout.addRow("Top-p:", top_p_layout)

        # Stream checkbox
        self.stream_checkbox = QCheckBox("Stream response")
        self.stream_checkbox.setChecked(True)
        params_layout.addRow("", self.stream_checkbox)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_settings(self):
        """Load current settings into the dialog."""
        self._loading_personas = True
        self.persona_combo.clear()
        self._personas = [p.copy() for p in self._settings.personas]
        self._active_persona_id = self._settings.active_persona_id
        
        active_index = 0
        for i, p in enumerate(self._personas):
            self.persona_combo.addItem(p["name"], p["id"])
            if p["id"] == self._active_persona_id:
                active_index = i
                
        self.persona_combo.setCurrentIndex(active_index)
        self._loading_personas = False
        self._on_persona_changed(active_index)

        self.temperature_slider.setValue(int(self._settings.temperature * 10))
        self.temperature_value.setValue(self._settings.temperature)
        self.max_tokens_spin.setValue(self._settings.max_tokens)
        self.top_p_slider.setValue(int(self._settings.top_p * 100))
        self.top_p_value.setValue(self._settings.top_p)
        self.stream_checkbox.setChecked(self._settings.stream)

    def _on_persona_changed(self, index):
        if self._loading_personas or index < 0:
            return
        
        persona_id = self.persona_combo.currentData()
        self._active_persona_id = persona_id
        
        for p in self._personas:
            if p["id"] == persona_id:
                self.system_prompt_edit.blockSignals(True)
                self.system_prompt_edit.setText(p.get("prompt", ""))
                self.system_prompt_edit.blockSignals(False)
                break

    def _on_prompt_edited(self):
        prompt = self.system_prompt_edit.toPlainText()
        for p in self._personas:
            if p["id"] == self._active_persona_id:
                p["prompt"] = prompt
                break
                
    def _add_persona(self):
        name, ok = QInputDialog.getText(self, "New Persona", "Persona Name:")
        if ok and name:
            new_id = name.lower().replace(" ", "_")
            self._personas.append({"id": new_id, "name": name, "prompt": "You are a helpful AI assistant."})
            
            self._loading_personas = True
            self.persona_combo.addItem(name, new_id)
            self.persona_combo.setCurrentIndex(self.persona_combo.count() - 1)
            self._loading_personas = False
            self._on_persona_changed(self.persona_combo.count() - 1)
            
    def _del_persona(self):
        if len(self._personas) <= 1:
            QMessageBox.warning(self, "Cannot Delete", "You must have at least one persona.")
            return
            
        index = self.persona_combo.currentIndex()
        if index >= 0:
            self._personas.pop(index)
            self._loading_personas = True
            self.persona_combo.removeItem(index)
            self._loading_personas = False
            self._on_persona_changed(self.persona_combo.currentIndex())

    def _save_and_accept(self):
        """Save settings and close the dialog."""
        self._settings.personas = self._personas
        self._settings.active_persona_id = self._active_persona_id
        self._settings.temperature = self.temperature_value.value()
        self._settings.max_tokens = self.max_tokens_spin.value()
        self._settings.top_p = self.top_p_value.value()
        self._settings.stream = self.stream_checkbox.isChecked()
        self.accept()

    def get_settings(self):
        """Get the settings from the dialog.

        Returns:
            Dictionary of settings.
        """
        return {
            "temperature": self.temperature_value.value(),
            "max_tokens": self.max_tokens_spin.value(),
            "top_p": self.top_p_value.value(),
            "stream": self.stream_checkbox.isChecked(),
        }


class PromptCollectionDialog(QDialog):
    """Dialog for managing saved prompts."""

    def __init__(self, settings_manager, parent=None):
        """Initialize prompt collection dialog.

        Args:
            settings_manager: SettingsManager instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._settings = settings_manager
        self._setup_ui()
        self._load_prompts()

    def _setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("Prompt Collection")
        self.setMinimumSize(500, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Instructions
        label = QLabel("Select a prompt to use, or add new ones:")
        layout.addWidget(label)

        # Prompt list
        self.prompt_list = QListWidget()
        self.prompt_list.itemDoubleClicked.connect(self._use_prompt)
        layout.addWidget(self.prompt_list)

        # Add/Remove buttons
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Prompt")
        self.add_button.clicked.connect(self._add_prompt)
        button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self._remove_prompt)
        button_layout.addWidget(self.remove_button)

        button_layout.addStretch()

        self.use_button = QPushButton("Use Selected")
        self.use_button.clicked.connect(self._use_prompt)
        button_layout.addWidget(self.use_button)

        layout.addLayout(button_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_prompts(self):
        """Load prompts from settings."""
        self.prompt_list.clear()
        for prompt in self._settings.prompts:
            item = QListWidgetItem(prompt.get("name", "Unnamed"))
            item.setData(Qt.ItemDataRole.UserRole, prompt)
            self.prompt_list.addItem(item)

    def _add_prompt(self):
        """Show dialog to add a new prompt."""
        dialog = AddPromptDialog(self)
        if dialog.exec():
            prompt_data = dialog.get_prompt()
            self._settings.add_prompt(prompt_data["text"], prompt_data["name"])
            self._load_prompts()

    def _remove_prompt(self):
        """Remove selected prompt."""
        current_row = self.prompt_list.currentRow()
        if current_row >= 0:
            self._settings.remove_prompt(current_row)
            self._load_prompts()

    def _use_prompt(self):
        """Use the selected prompt."""
        current_item = self.prompt_list.currentItem()
        if current_item:
            self._selected_prompt = current_item.data(Qt.ItemDataRole.UserRole)
            self.accept()

    def get_selected_prompt(self) -> str:
        """Get the selected prompt text.

        Returns:
            The prompt text.
        """
        return getattr(self, "_selected_prompt", {}).get("text", "")


class AddPromptDialog(QDialog):
    """Dialog for adding a new prompt."""

    def __init__(self, parent=None):
        """Initialize add prompt dialog.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("Add Prompt")
        self.setMinimumWidth(400)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Prompt name...")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Text input
        layout.addWidget(QLabel("Prompt:"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter prompt text...")
        layout.addWidget(self.text_edit)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_prompt(self) -> dict:
        """Get the prompt data.

        Returns:
            Dictionary with 'name' and 'text' keys.
        """
        return {
            "name": self.name_edit.text(),
            "text": self.text_edit.toPlainText(),
        }

class PullWorker(QThread):
    progress = pyqtSignal(dict)
    finished = pyqtSignal(bool, str)

    def __init__(self, client, model_name):
        super().__init__()
        self.client = client
        self.model_name = model_name

    def run(self):
        try:
            self.client.pull_model(
                self.model_name,
                stream=True,
                callback=self.progress.emit
            )
            self.finished.emit(True, "Success")
        except Exception as e:
            self.finished.emit(False, str(e))

class ModelManagerDialog(QDialog):
    def __init__(self, client, parent=None):
        super().__init__(parent)
        self.client = client
        self._setup_ui()
        self._load_models()

    def _setup_ui(self):
        self.setWindowTitle("Model Manager")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        pull_layout = QHBoxLayout()
        self.pull_input = QLineEdit()
        self.pull_input.setPlaceholderText("Enter model to pull (e.g. llama2)")
        self.pull_btn = QPushButton("Pull Model")
        self.pull_btn.clicked.connect(self._pull_model)
        pull_layout.addWidget(self.pull_input)
        pull_layout.addWidget(self.pull_btn)
        layout.addLayout(pull_layout)
        
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        layout.addWidget(QLabel("Local Models:"))
        self.model_list = QListWidget()
        layout.addWidget(self.model_list)
        
        del_layout = QHBoxLayout()
        self.del_btn = QPushButton("Delete Selected")
        self.del_btn.clicked.connect(self._delete_model)
        del_layout.addWidget(self.del_btn)
        del_layout.addStretch()
        layout.addLayout(del_layout)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
    def _load_models(self):
        self.model_list.clear()
        try:
            models = self.client.get_models()
            for m in models:
                self.model_list.addItem(m.get("name", "Unknown"))
        except Exception as e:
            self.status_label.setText(f"Error loading models: {e}")
            
    def _pull_model(self):
        model_name = self.pull_input.text().strip()
        if not model_name:
            return
            
        self.pull_btn.setEnabled(False)
        self.status_label.setText(f"Pulling {model_name}...")
        
        self.worker = PullWorker(self.client, model_name)
        self.worker.progress.connect(self._on_pull_progress)
        self.worker.finished.connect(self._on_pull_finished)
        self.worker.start()
        
    def _on_pull_progress(self, data):
        status = data.get("status", "")
        if "completed" in data and "total" in data:
            completed = data["completed"] / (1024*1024)
            total = data["total"] / (1024*1024)
            self.status_label.setText(f"{status}: {completed:.1f}MB / {total:.1f}MB")
        else:
            self.status_label.setText(status)
            
    def _on_pull_finished(self, success, msg):
        self.pull_btn.setEnabled(True)
        if success:
            self.status_label.setText("Pull completed.")
            self.pull_input.clear()
            self._load_models()
        else:
            self.status_label.setText(f"Error: {msg}")
            
    def _delete_model(self):
        item = self.model_list.currentItem()
        if not item:
            return
            
        name = item.text()
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete {name}?")
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.client.delete_model(name)
                self.status_label.setText(f"Deleted {name}.")
                self._load_models()
            except Exception as e:
                self.status_label.setText(f"Error: {e}")
