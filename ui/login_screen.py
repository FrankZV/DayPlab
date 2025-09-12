# ui/login_screen.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QMessageBox, QHBoxLayout, QStyle
)
from PyQt5.QtGui import QIcon

class LoginWindow(QWidget):
    def __init__(self, callback_abrir_app, db):
        super().__init__()
        self.callback_abrir_app = callback_abrir_app
        self.db = db
        self.setWindowTitle("Login")
        self.setGeometry(400, 200, 400, 350)

        layout = QVBoxLayout(self)

        label = QLabel("Iniciar sesión")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)

        # Campo correo
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo")
        layout.addWidget(self.email_input)

        # Campo teléfono (opcional, se usa al registrar usuario)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Teléfono (opcional)")
        layout.addWidget(self.phone_input)

        # Campo contraseña
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.btn_toggle_pass = QPushButton()
        self.btn_toggle_pass.setFixedWidth(40)
        self.btn_toggle_pass.setIcon(self.style().standardIcon(QStyle.SP_DesktopIcon))
        self.btn_toggle_pass.clicked.connect(
            lambda: self.toggle_password(self.password_input, self.btn_toggle_pass)
        )

        pass_layout = QHBoxLayout()
        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(self.btn_toggle_pass)
        layout.addLayout(pass_layout)

        # Confirmar contraseña (solo para registro)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirmar contraseña (si es nuevo usuario)")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.btn_toggle_confirm = QPushButton()
        self.btn_toggle_confirm.setFixedWidth(40)
        self.btn_toggle_confirm.setIcon(self.style().standardIcon(QStyle.SP_DesktopIcon))
        self.btn_toggle_confirm.clicked.connect(
            lambda: self.toggle_password(self.confirm_password_input, self.btn_toggle_confirm)
        )

        confirm_layout = QHBoxLayout()
        confirm_layout.addWidget(self.confirm_password_input)
        confirm_layout.addWidget(self.btn_toggle_confirm)
        layout.addLayout(confirm_layout)

        # Botón ingresar
        btn_ingresar = QPushButton("Ingresar")
        btn_ingresar.clicked.connect(self.validar_login)
        layout.addWidget(btn_ingresar)

        # Botón omitir (entra como invitado sin usuario_id)
        btn_omitir = QPushButton("Omitir")
        btn_omitir.clicked.connect(self.omitir)
        layout.addWidget(btn_omitir)

    def toggle_password(self, line_edit, button):
        """Mostrar / ocultar contraseña"""
        if line_edit.echoMode() == QLineEdit.Password:
            line_edit.setEchoMode(QLineEdit.Normal)
            button.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        else:
            line_edit.setEchoMode(QLineEdit.Password)
            button.setIcon(self.style().standardIcon(QStyle.SP_DesktopIcon))

    def validar_login(self):
        """Valida usuario o lo crea si no existe"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        confirm = self.confirm_password_input.text().strip()

        if not email:
            QMessageBox.warning(self, "Error", "Ingresa un correo.")
            return

        # --- Si existe usuario en DB, validar contraseña ---
        if self.db.validate_user(email, password):
            user = self.db.get_user(email)
            if user:
                usuario_id = user[0]  # ID del usuario
                self.close()
                self.callback_abrir_app(usuario_id)  # ✅ pasamos id
                return

        # --- Si no existe, crear nuevo usuario ---
        if not self.db.get_user(email):
            if not password:
                QMessageBox.warning(self, "Error", "Ingrese contraseña para crear usuario.")
                return
            if password != confirm:
                QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
                return

            usuario_id = self.db.create_user(email, password, self.phone_input.text().strip())
            QMessageBox.information(self, "Usuario creado", "Usuario creado correctamente. Iniciando sesión.")
            self.close()
            self.callback_abrir_app(usuario_id)  # ✅ pasamos id del nuevo usuario
            return

        QMessageBox.warning(self, "Error", "Credenciales inválidas.")

    def omitir(self):
        """Entrar como invitado (usuario_id=None)"""
        self.close()
        self.callback_abrir_app(None)

