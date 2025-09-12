from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(500, 300)
        self.setStyleSheet("background-color: #23282e; color: white;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Logo
        logo = QLabel()
        pixmap = QPixmap("Iconos/DP-01.png")  
        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Texto debajo del logo
        self.label = QLabel("Cargando DayPlan...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.label)

    def iniciar(self, callback, tiempo=3000):
        """Muestra el splash y luego abre la app principal"""
        self.show()
        QTimer.singleShot(tiempo, lambda: self._abrir(callback))

    def _abrir(self, callback):
        self.close()
        callback()


