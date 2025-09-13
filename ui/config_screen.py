# ui/config_screen.py
from themes import light_theme, dark_theme
from theme_utils import save_theme_preference, load_theme_preference
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QDialogButtonBox, QStyle, QComboBox
)

class ConfigWindow(QDialog):
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Configuración")
        self.setFixedSize(400, 320)  # Aumenta el alto para el combo de tema

        self.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
                font-family: Arial;
                font-size: 14px;
            }
            QLabel {
                background-color: transparent;
                color: black;
                font-size: 16px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #c8c8c8;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 5px;
                color: black;
            }
            QLineEdit::placeholder {
                color: gray;
            }
        """)

        layout = QVBoxLayout(self)

        label = QLabel("Configuración de cuenta")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo actual")
        layout.addWidget(self.email_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Teléfono")
        layout.addWidget(self.phone_input)

        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.toggle_btn = QPushButton()
        self.toggle_btn.setFixedWidth(40)
        self.toggle_btn.setStyleSheet("border: none; background-color: #f9f9f9;")
        self.toggle_btn.setIcon(self.style().standardIcon(QStyle.SP_DesktopIcon))
        self.toggle_btn.clicked.connect(lambda: self.toggle_password(self.password_input, self.toggle_btn))

        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_btn)
        layout.addLayout(password_layout)

        # --- Selector de tema claro/oscuro ---
        tema_layout = QHBoxLayout()
        tema_label = QLabel("Tema:")
        tema_label.setStyleSheet("font-size: 15px; font-weight: normal;")
        self.tema_combo = QComboBox()
        self.tema_combo.addItem("Claro")
        self.tema_combo.addItem("Oscuro")
        tema_layout.addWidget(tema_label)
        tema_layout.addWidget(self.tema_combo)
        layout.addLayout(tema_layout)

        # Cargar preferencia guardada
        tema_actual = load_theme_preference()
        self.tema_combo.setCurrentText(tema_actual)

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.guardar_cambios)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)
        
#_____________________________________________________________________________

    def toggle_password(self, line_edit, button):
        if line_edit.echoMode() == QLineEdit.Password:
            line_edit.setEchoMode(QLineEdit.Normal)
            button.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        else:
            line_edit.setEchoMode(QLineEdit.Password)
            button.setIcon(self.style().standardIcon(QStyle.SP_DesktopIcon))

    def guardar_cambios(self):
        email = self.email_input.text().strip()
        telefono = self.phone_input.text().strip()
        password = self.password_input.text().strip()

        # --- Guardar preferencia de tema ---
        tema = self.tema_combo.currentText()
        if tema == "Claro":
            QApplication.instance().setStyleSheet(light_theme)
        else:
            QApplication.instance().setStyleSheet(dark_theme)
        save_theme_preference(tema)

        if not email:
            QMessageBox.warning(self, "Error", "Ingrese su correo para actualizar.")
            return

        if self.db:
            # Intentamos actualizar (si usuario no existe, lo creamos)
            if not self.db.get_user(email):
                self.db.create_user(email, password, telefono)
            else:
                self.db.update_user_contact(email, new_email=email, telefono=telefono or None, password=password or None)
            QMessageBox.information(self, "Éxito", "Datos actualizados correctamente.")
        else:
            QMessageBox.information(self, "Éxito", "Datos actualizados (modo demo).")
        self.accept()



