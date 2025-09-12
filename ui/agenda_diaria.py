from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QTimeEdit
)
from PyQt5.QtCore import Qt, QTime, QTimer


class DialogoAgregarActividad(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nueva actividad")
        self.setFixedSize(300, 200)

        layout = QFormLayout(self)

        self.nombre = QLineEdit()
        layout.addRow("Actividad:", self.nombre)

        self.hora_inicio = QTimeEdit()
        self.hora_inicio.setDisplayFormat("HH:mm")
        self.hora_inicio.setTime(QTime.currentTime())
        layout.addRow("Hora inicio:", self.hora_inicio)

        self.hora_fin = QTimeEdit()
        self.hora_fin.setDisplayFormat("HH:mm")
        self.hora_fin.setTime(QTime.currentTime().addSecs(3600))  # +1 hora por defecto
        layout.addRow("Hora fin:", self.hora_fin)

        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)

    def obtener_datos(self):
        return self.nombre.text().strip(), self.hora_inicio.time(), self.hora_fin.time()
#_____________________________________________________________________________________________________________________
class AgendaDiaria(QWidget):     
    def __init__(self, db=None, usuario_id=None):
        super().__init__()
        self.db = db
        self.usuario_id = usuario_id    
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Lista de actividades
        self.lista_agenda = QListWidget()
        self.lista_agenda.setStyleSheet("""
            QListWidget {
                background: #2e343c;
                border-radius: 10px;
                padding: 8px;
                font-size: 13px;
                color: white;
            }
        """)
        layout.addWidget(self.lista_agenda)

        # Botón agregar (SIEMPRE visible)
        self.btn_add_agenda = QPushButton("+")
        self.btn_add_agenda.setFixedSize(40, 40)
        self.btn_add_agenda.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #23282e;
                border-radius: 20px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.btn_add_agenda.clicked.connect(self.agregar_actividad)
        layout.addWidget(self.btn_add_agenda, alignment=Qt.AlignCenter)

        # Lista interna de actividades
        
        self.actividades_diarias = []
        if self.db and self.usuario_id:
            self.cargar_actividades_db()
            
        # Timer para revisar cada minuto
        self.timer = QTimer()
        self.timer.timeout.connect(self.revisar_actividades)
        self.timer.start(60000)

    # --------------------- Métodos existentes --------------------- #
                
    def agregar_actividad(self):
        dialogo = DialogoAgregarActividad()
        if dialogo.exec_() == QDialog.Accepted:
            nombre, hora_inicio, hora_fin = dialogo.obtener_datos()
            if nombre:
                if hora_inicio >= hora_fin:
                    hora_fin = QTime(hora_fin.hour() + 24, hora_fin.minute())
                self.actividades_diarias.append({
                    "nombre": nombre,
                    "hora_inicio": hora_inicio,
                    "hora_fin": hora_fin
                })
                if self.db and self.usuario_id:
                    self.db.add_agenda_item(
                        nombre,
                        hora_inicio.toString("HH:mm"),
                        hora_fin.toString("HH:mm"),
                        self.usuario_id
                    )
                self.actualizar_lista()
                
                
    def cargar_actividades_db(self):
            self.actividades_diarias.clear()
            items = self.db.get_agenda_items(self.usuario_id)
            for nombre, hora_inicio, hora_fin in items:
                self.actividades_diarias.append({
                    "nombre": nombre,
                    "hora_inicio": QTime.fromString(hora_inicio, "HH:mm"),
                    "hora_fin": QTime.fromString(hora_fin, "HH:mm")
                })
            self.actualizar_lista()

    def clear(self):
        self.actividades_diarias.clear()
        self.lista_agenda.clear()
        if self.db and self.usuario_id:
            self.db.clear_agenda(self.usuario_id)
                
                
                

    def actualizar_lista(self):
        self.lista_agenda.clear()
        for act in self.actividades_diarias:
            self.lista_agenda.addItem(
                f"{act['hora_inicio'].toString('HH:mm')} - {act['hora_fin'].toString('HH:mm')}  →  {act['nombre']}"
            )

    def revisar_actividades(self):
        ahora = QTime.currentTime()
        for i in range(len(self.actividades_diarias) - 1, -1, -1):
            act = self.actividades_diarias[i]
            if ahora >= act["hora_fin"]:
                self.actividades_diarias.pop(i)
                self.lista_agenda.takeItem(i)        

    # --------------------- NUEVO clear() --------------------- #
    def clear(self):
        """Limpia solo las actividades diarias, pero deja el botón visible"""
        self.actividades_diarias.clear()
        self.lista_agenda.clear()


                

#_____________________________________________________________________________________________________________________