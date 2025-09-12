from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from PyQt5.QtCore import QDateTime, Qt

class NotificacionesWindow(QWidget):
    def __init__(self, tareas, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)  # se cierra solo al hacer clic afuera
        self.setFixedSize(250, 200)
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                border: 2px solid #645394;
                border-radius: 12px;
            }
            QLabel {
                font-family: Arial;
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                margin: 4px;
            }
            QListWidget {
                border: none;
                background-color: #ffffff;
                border-radius: 8px;
                padding: 4px;
                font-family: Arial;
                font-size: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        self.label = QLabel("Notificaciones")
        layout.addWidget(self.label)

        self.lista = QListWidget()
        layout.addWidget(self.lista)

        self.cargar_notificaciones(tareas)

    def cargar_notificaciones(self, tareas):
        """Muestra tareas que van a vencer en menos de 24h"""
        self.lista.clear()
        ahora = QDateTime.currentDateTime()

        for tarea in tareas:
            try:
                fecha_fin = QDateTime.fromString(tarea.fecha_fin, "dd/MM/yyyy")
                if not fecha_fin.isValid():
                    continue

                horas_restantes = ahora.secsTo(fecha_fin) / 3600
                if 0 < horas_restantes <= 24:
                    self.lista.addItem(f"{tarea.nombre} → vence pronto")
            except Exception:
                pass

        if self.lista.count() == 0:
            self.lista.addItem("Sin notificaciones")
