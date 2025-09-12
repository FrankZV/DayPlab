from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QCalendarWidget, QListWidget,
    QLabel, QPushButton
)
from PyQt5.QtCore import QDate, Qt  


class CalendarioWindow(QWidget):
    def __init__(self, tareas_por_fecha, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calendario de Tareas")
        self.setFixedSize(420, 420)

        # Guardar referencia al diccionario de tareas
        self.tareas_por_fecha = tareas_por_fecha
        self.drag_position = None  #inicializa variable para arrastre

        layout = QVBoxLayout(self)

        # --- Calendario ---
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.mostrar_tareas_dia)

        # --- Lista de tareas del día ---
        self.label_tareas = QLabel("Tareas del día:")
        self.label_tareas.setContentsMargins(15, 5, 5, 5)

        self.lista_tareas = QListWidget()

        # --- Botón cerrar ---
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.close)

        # --- Añadir al layout ---
        layout.addWidget(self.calendar)
        layout.addWidget(self.label_tareas)
        layout.addWidget(self.lista_tareas)
        layout.addWidget(self.btn_cerrar)

        # --- Estilos minimalistas ---
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                border-radius: 15px;
            }
            QCalendarWidget {
                border: none;
                background-color: white;
                border-radius: 12px;
                font-family: Arial;
                font-size: 13px;
            }
            QCalendarWidget QWidget { alternate-background-color: #ffffff; }
            QCalendarWidget QToolButton {
                color: #645394;
                font-size: 15px;
                font-weight: bold;
                icon-size: 20px;
                background: transparent;
                border: none;
                padding: 0px 6px;
            }
            QCalendarWidget QToolButton::menu-indicator {
                subcontrol-position: right center; 
                subcontrol-origin: padding;
                left: 4px;
            }
            QCalendarWidget QMenu {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 6px;
            }
            QCalendarWidget QAbstractItemView {
                font-size: 12px;
                selection-background-color: #645394;
                selection-color: white;
            }
            QListWidget {
                border: none;
                background-color: #ffffff;
                border-radius: 12px;
                padding: 6px;
                font-family: Arial;
                font-size: 12px;
            }
            QLabel {
                font-family: Arial;
                font-size: 13px;
                font-weight: bold;
                color: #333333;
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

    def mostrar_tareas_dia(self, fecha: QDate):
        """Mostrar las tareas guardadas en el diccionario para la fecha seleccionada"""
        self.lista_tareas.clear()
        fecha_str = fecha.toString("dd/MM/yyyy")

        if fecha_str in self.tareas_por_fecha:
            for tarea in self.tareas_por_fecha[fecha_str]:
                self.lista_tareas.addItem(f"- {tarea}")
        else:
            self.lista_tareas.addItem("Sin tareas")

    # --- Drag de la ventana ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton: 
            self.move(event.globalPos() - self.drag_position)
            event.accept()
