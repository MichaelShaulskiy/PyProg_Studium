from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QPushButton, QLineEdit, QComboBox,
QHBoxLayout, QVBoxLayout, QWidget, QLabel
)


class AiSettings(QWidget):
    settings_confirmed = Signal(str, str, str) #ai_provider, api_key
    #TODO: Werte übergeben
    def __init__(self):
        super().__init__()
        self.setup_settings_window()
        
    def setup_settings_window(self):
        self.setWindowTitle("AI Settings")
        self.setup_ai_provider()
        self.setup_model_id()
        self.setup_api_key()
        self.setup_cancel_button()
        self.setup_ok_button()
        self.setup_layout()


    def setup_ai_provider(self):
        self.ai_provider_label = QLabel("Please enter your Endpoint-URL:")
        self.provider_url = QLineEdit()
        self.provider_url.setPlaceholderText("https://openrouter.ai/api/v1")

    def setup_api_key(self):
        self.key_label = QLabel("Please enter API Key:")
        self.api_key_edit = QLineEdit()
    
    def setup_model_id(self):
        self.model_id_label = QLabel("Enter model identifier:")
        self.model_id = QLineEdit()

    def setup_cancel_button(self):
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)

    def setup_ok_button(self):
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.save_settings)
        
    def save_settings(self):
        api_key = self.api_key_edit.text()
        ai_provider = self.provider_url.text()
        model_id = self.model_id.text()
        self.settings_confirmed.emit(ai_provider, api_key, model_id)
        self.close()

    def setup_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.ai_provider_label)
        layout.addWidget(self.provider_url)
        layout.addWidget(self.key_label)
        layout.addWidget(self.api_key_edit)
        layout.addWidget(self.model_id_label)
        layout.addWidget(self.model_id)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.cancel_button)
        btn_layout.addWidget(self.ok_button)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
