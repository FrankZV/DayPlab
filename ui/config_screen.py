# ui/config_screen.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox, QDialogButtonBox, QStyle
)

class ConfigWindow(QDialog):
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Configuración")
        self.setFixedSize(400, 270)

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

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.guardar_cambios)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

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



