# ui/cards.py
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QDialog, QFormLayout, QLineEdit, QTextEdit, QDateEdit,
    QComboBox, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt, QMimeData, QPoint, QDate
from PyQt5.QtGui import QDrag, QPixmap
from models.task import Task

class CardTarea(QFrame):
    def __init__(self, nombre, descripcion, fecha_inicio, fecha_fin, prioridad, db=None, task_id=None):
        super().__init__()
        self.db = db
        self.id = task_id
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.prioridad = prioridad

        # --- UI general ---
        self.setStyleSheet("""
            background: #f2f2f2;
            border-radius: 14px;
        """)
        self.setFixedWidth(230)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)

        self.label_nombre = QLabel(f"<b>{self.nombre}</b>")
        self.label_nombre.setStyleSheet("font-family: Arial; font-size: 13px;")
        self.layout.addWidget(self.label_nombre)

        self.label_descripcion = QLabel(self._truncar_texto(self.descripcion))
        self.label_descripcion.setStyleSheet("font-family: Arial; font-size: 11px;")
        self.label_descripcion.setWordWrap(True)
        self.layout.addWidget(self.label_descripcion)

        self.label_fechas = QLabel(f"{self.fecha_inicio} → {self.fecha_fin}")
        self.label_fechas.setStyleSheet("font-family: Arial; font-size: 10px; color: gray;")
        self.layout.addWidget(self.label_fechas)

        self.indicador = QLabel("●")
        self.indicador.setStyleSheet(f"color: {self.prioridad}; font-size: 16px;")
        self.indicador.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.layout.addWidget(self.indicador)

        btns_layout = QHBoxLayout()
        self.btn_edit = QPushButton("Editar")
        self.btn_delete = QPushButton("Borrar")

        for btn in (self.btn_edit, self.btn_delete):
            btn.setFixedSize(55, 22)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #645394;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    color: #32294d;
                }
            """)

        self.btn_edit.clicked.connect(self.editar_tarea)
        self.btn_delete.clicked.connect(self.borrar_tarea)

        btns_layout.addStretch()
        btns_layout.addWidget(self.btn_edit)
        btns_layout.addWidget(self.btn_delete)
        self.layout.addLayout(btns_layout)

        self._drag_start_pos = None

    def _truncar_texto(self, texto, max_lineas=4, max_caracteres=180):
        if len(texto) > max_caracteres:
            return texto[:max_caracteres] + "..."
        lineas = texto.split("\n")
        if len(lineas) > max_lineas:
            return "\n".join(lineas[:max_lineas]) + "..."
        return texto

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            child = self.childAt(event.pos())
            if child in (self.btn_edit, self.btn_delete):
                self._drag_start_pos = None
            else:
                self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self._drag_start_pos is not None:
            if (event.pos() - self._drag_start_pos).manhattanLength() > 10:
                self.startDrag()
                self._drag_start_pos = None
        super().mouseMoveEvent(event)

    def startDrag(self):
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData("application/x-card-tarea", b"card")
        drag.setMimeData(mime)
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
        drag.exec_(Qt.MoveAction)

    def editar_tarea(self):
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Editar tarea")
        dialogo.setFixedSize(400, 350)

        layout = QFormLayout(dialogo)

        nombre_input = QLineEdit(self.nombre)
        layout.addRow("Nombre:", nombre_input)

        desc_input = QTextEdit(self.descripcion)
        desc_input.setFixedHeight(60)
        layout.addRow("Descripción:", desc_input)

        fecha_inicio_input = QDateEdit(QDate.fromString(self.fecha_inicio, "dd/MM/yyyy"))
        fecha_inicio_input.setCalendarPopup(True)
        fecha_fin_input = QDateEdit(QDate.fromString(self.fecha_fin, "dd/MM/yyyy"))
        fecha_fin_input.setCalendarPopup(True)

        fechas_layout = QHBoxLayout()
        fechas_layout.addWidget(QLabel("Inicio:"))
        fechas_layout.addWidget(fecha_inicio_input)
        fechas_layout.addWidget(QLabel("Fin:"))
        fechas_layout.addWidget(fecha_fin_input)
        layout.addRow(fechas_layout)

        prioridad_input = QComboBox()
        prioridad_input.addItem("Baja", "blue")
        prioridad_input.addItem("Media", "orange")
        prioridad_input.addItem("Alta", "red")
        idx = prioridad_input.findData(self.prioridad)
        if idx >= 0:
            prioridad_input.setCurrentIndex(idx)
        layout.addRow("Prioridad:", prioridad_input)

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(botones)
        botones.accepted.connect(dialogo.accept)
        botones.rejected.connect(dialogo.reject)

        if dialogo.exec_() == QDialog.Accepted:
            # Actualizar datos en objeto
            self.nombre = nombre_input.text().strip()
            self.descripcion = desc_input.toPlainText().strip()
            self.fecha_inicio = fecha_inicio_input.date().toString("dd/MM/yyyy")
            self.fecha_fin = fecha_fin_input.date().toString("dd/MM/yyyy")
            self.prioridad = prioridad_input.currentData()

            # Persistir en DB si tenemos referencia
            if self.db and self.id is not None:
                updated = Task(self.nombre, self.descripcion, self.fecha_inicio, self.fecha_fin, self.prioridad, task_id=self.id)
                self.db.update_task(self.id, updated)

            # Actualizar UI
            self.label_nombre.setText(f"<b>{self.nombre}</b>")
            self.label_descripcion.setText(self._truncar_texto(self.descripcion))
            self.label_fechas.setText(f"{self.fecha_inicio} → {self.fecha_fin}")
            self.indicador.setStyleSheet(f"color: {self.prioridad}; font-size: 16px;")

    def borrar_tarea(self):
        confirmacion = QMessageBox.question(
            self, "Confirmar borrado",
            "¿Seguro que quieres borrar esta tarea?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmacion == QMessageBox.Yes:
            # Borrar en DB si tenemos referencia
            if self.db and self.id is not None:
                try:
                    self.db.delete_task(self.id)
                except Exception:
                    pass
            self.setParent(None)
            self.deleteLater()



