from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton
from PyQt5.QtCore import QDateTime, QDate, QTime, QTimer, Qt


class TiempoRestanteWindow(QWidget):
    def __init__(self, tareas, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tiempo restante de tareas")
        self.setFixedSize(420, 420)

        self.tareas = tareas

        layout = QVBoxLayout(self)

        # --- Lista con tiempos restantes ---
        self.label = QLabel("Tiempo restante por tarea:")
        layout.addWidget(self.label)

        self.lista_tiempos = QListWidget()
        layout.addWidget(self.lista_tiempos)

        # --- Botón cerrar ---
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.close)
        layout.addWidget(self.btn_cerrar)

        # Mostrar tiempos iniciales
        self.mostrar_tiempos()

        # --- Timer para refrescar cada minuto ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.mostrar_tiempos)
        self.timer.start(60000)  # 60,000 ms = 1 min

        # --- Estilos con borde gris oscuro ---
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                border-radius: 25px;
            }
            QLabel {
                font-family: Arial;
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
            QListWidget {
                border: none;
                background-color: #f2f2f2;
                border-radius: 12px;
                padding: 6px;
                font-family: Arial;
                font-size: 12px;
            }
            QPushButton {
                background-color: #645394;
                color: white;
                border-radius: 10px;
                padding: 5px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4b3c70; }
        """)

    def mostrar_tiempos(self):
        """Calcula y muestra el tiempo restante para cada tarea"""
        self.lista_tiempos.clear()
        ahora = QDateTime.currentDateTime()

        if not self.tareas:  # si no hay tareas, lista vacía
            return

        for tarea in self.tareas:
            try:
                nombre = getattr(tarea, "nombre", None)
                fecha_fin_str = getattr(tarea, "fecha_fin", None)

                if not nombre or not fecha_fin_str:
                    continue  # ignorar tareas inválidas

                fecha_qdate = QDate.fromString(fecha_fin_str, "dd/MM/yyyy")
                if not fecha_qdate.isValid():
                    self.lista_tiempos.addItem(f"{nombre} → Fecha inválida")
                    continue

                dt_fin = QDateTime(fecha_qdate, QTime(23, 59, 59))

                if ahora > dt_fin:
                    self.lista_tiempos.addItem(f"{nombre} → Expirada")
                else:
                    secs_restantes = ahora.secsTo(dt_fin)
                    dias = secs_restantes // 86400
                    horas = (secs_restantes % 86400) // 3600
                    minutos = (secs_restantes % 3600) // 60
                    self.lista_tiempos.addItem(
                        f"{nombre} → {dias}d {horas}h {minutos}m"
                    )

            except Exception as e:
                self.lista_tiempos.addItem(f"Error con tarea: {e}")

    # --- Drag de la ventana ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


