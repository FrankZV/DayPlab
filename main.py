# main.py
import os
from database.db_manager import DBManager
from models.task import Task
# Ruta base del proyecto (donde está este archivo main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def icon_path(filename):
    return os.path.join(BASE_DIR, "Iconos", filename)

#_---------------- Librerías para notificaciones ---------------- #
from notifications.email_service import send_email
from notifications.whatsapp_service import send_whatsapp
#__________________________________________________________________#


from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QDialog, QFormLayout, QLineEdit,
    QTextEdit, QDateEdit, QComboBox, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, QSize, QTimer
from PyQt5.QtGui import QIcon

from ui.calendario import CalendarioWindow
from ui.tiempo_restante import TiempoRestanteWindow
from ui.cards import CardTarea
from ui.notificaciones import NotificacionesWindow
from ui.agenda_diaria import AgendaDiaria
from ui.splash_screen import SplashScreen
from ui.config_screen import ConfigWindow

# ---------------- Diccionario de tareas por fecha ---------------- #
tareas_por_fecha = {}  # clave: fecha (str dd/MM/yyyy), valor: lista de nombres de tareas

# ---------------- Diálogo Crear Tarea ---------------- #
class DialogoCrearTarea(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nueva tarea")
        self.setFixedSize(400, 350)

        layout = QFormLayout(self)

        # Nombre
        self.nombre = QLineEdit()
        layout.addRow("Nombre:", self.nombre)

        # Descripción
        self.descripcion = QTextEdit()
        self.descripcion.setFixedHeight(60)
        self.descripcion.textChanged.connect(self.limitar_texto)
        layout.addRow("Descripción:", self.descripcion)

        # Fechas
        self.fecha_inicio = QDateEdit(QDate.currentDate())
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_fin = QDateEdit(QDate.currentDate())
        self.fecha_fin.setCalendarPopup(True)

        fechas_layout = QHBoxLayout()
        fechas_layout.addWidget(QLabel("Inicio:"))
        fechas_layout.addWidget(self.fecha_inicio)
        fechas_layout.addWidget(QLabel("Fin:"))
        fechas_layout.addWidget(self.fecha_fin)
        layout.addRow(fechas_layout)

        # Prioridad
        self.prioridad = QComboBox()
        self.prioridad.addItem("Baja", "blue")
        self.prioridad.addItem("Media", "orange")
        self.prioridad.addItem("Alta", "red")
        layout.addRow("Prioridad:", self.prioridad)

        # Botones
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self._on_accept)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)

    def limitar_texto(self):
        texto = self.descripcion.toPlainText()
        if len(texto) > 120:
            self.descripcion.setPlainText(texto[:120])
            cursor = self.descripcion.textCursor()
            cursor.setPosition(120)
            self.descripcion.setTextCursor(cursor)

    def _on_accept(self):
        # Validación: fecha fin no puede ser anterior a inicio
        if self.fecha_fin.date() < self.fecha_inicio.date():
            QMessageBox.warning(self, "Fechas inválidas", "La fecha de fin no puede ser anterior a la fecha de inicio.")
            return
        if not self.nombre.text().strip():
            QMessageBox.warning(self, "Nombre requerido", "Ingrese un nombre para la tarea.")
            return
        self.accept()

    def obtener_datos(self):
        return {
            "nombre": self.nombre.text().strip(),
            "descripcion": self.descripcion.toPlainText().strip(),
            "fecha_inicio": self.fecha_inicio.date().toString("dd/MM/yyyy"),
            "fecha_fin": self.fecha_fin.date().toString("dd/MM/yyyy"),
            "prioridad": self.prioridad.currentData()
        }

# ---------------- App Principal ---------------- #
app = QApplication([])

# ---------------- Base de Datos ---------------- #
db = DBManager()

# ---------------- Usuarios en sesion ---------------- #
current_user_id = None  # aquí guardamos el usuario en sesión
current_user_id = 1  # Para pruebas sin login
#db.set_current_user(current_user_id)



ventana = QWidget()
ventana.setWindowTitle("DayPlan - Gestión de Tareas y Agenda Diaria")
ventana.setWindowIcon(QIcon(icon_path("DP-01.png")))
ventana.setGeometry(100, 100, 1200, 700)
ventana.setStyleSheet("background-color: #F08080;")

layout_principal = QHBoxLayout(ventana)

# ---------------- Columnas kanban ---------------- #
class Columna(QFrame):
    def __init__(self, titulo):
        super().__init__()
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            background: #ffffff;
            border-radius: 18px;
            color: #23282e;
        """)

        self.vbox = QVBoxLayout(self)
        self.vbox.setContentsMargins(12, 12, 12, 12)
        self.vbox.setSpacing(10)

        label = QLabel(f"<b>{titulo}</b>")
        label.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.vbox.addWidget(label)
        self.vbox.addStretch()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-card-tarea"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-card-tarea"):
            event.acceptProposedAction()

    def dropEvent(self, event):
        widget = event.source()
        if widget:
            widget.setParent(None)
            self.vbox.insertWidget(self.vbox.count() - 1, widget)
            widget.show()
            event.acceptProposedAction()

def crear_columna(titulo):
    frame = Columna(titulo)
    return frame, frame.vbox

columna_iniciadas, layout_iniciadas = crear_columna("Iniciadas")
columna_proceso, layout_proceso = crear_columna("En proceso")
columna_finalizadas, layout_finalizadas = crear_columna("Finalizadas")

kanban_vertical_layout = QVBoxLayout()
kanban_horizontal_layout = QHBoxLayout()

kanban_horizontal_layout.addWidget(columna_iniciadas, stretch=1)
kanban_horizontal_layout.addWidget(columna_proceso, stretch=1)
kanban_horizontal_layout.addWidget(columna_finalizadas, stretch=1)

# ---------------- Barra inferior (Botones de acción) ---------------- #
botones_layout = QHBoxLayout()
botones_centro_layout = QHBoxLayout()

btn_task = QPushButton("+ Task")
btn_task.setFixedSize(100, 40)
btn_task.setStyleSheet("""
    background: #645394;
    color: #ffffff;
    border-radius: 14px;
    font-size: 15px;
    font-weight: bold;
""")

btn_calendar = QPushButton()
btn_calendar.setFixedSize(50, 40)
btn_calendar.setIcon(QIcon(icon_path("Calendar.png")))
btn_calendar.setIconSize(QSize(24, 24))
btn_calendar.setStyleSheet("""
    QPushButton {
        background: #645394;
        border-radius: 14px;
    }
    QPushButton:hover {
        background: #32294d;
    }
""")

btn_tiempo = QPushButton()
btn_tiempo.setFixedSize(50, 40)
btn_tiempo.setIcon(QIcon(icon_path("Clock.png")))
btn_tiempo.setIconSize(QSize(24, 24))
btn_tiempo.setStyleSheet("""
    QPushButton {
        background: #645394;
        border-radius: 14px;
    }
    QPushButton:hover {
        background: #32294d;
    }
""")

btn_notificaciones = QPushButton()
btn_notificaciones.setFixedSize(50, 40)
btn_notificaciones.setIcon(QIcon(icon_path("Notification.png")))
btn_notificaciones.setIconSize(QSize(24, 24))
btn_notificaciones.setStyleSheet("""
    QPushButton {
        background: #645394;
        border-radius: 14px;
    }
    QPushButton:hover {
        background: #32294d;
    }
""")

btn_config = QPushButton("•••")
btn_config.setFixedSize(50, 40)
btn_config.setStyleSheet("""
    QPushButton {
        background: #645394;
        border-radius: 14px;
        color: white;
        font-size: 18px;
    }
    QPushButton:hover {
        background: #32294d;
    }
""")
btn_config.clicked.connect(lambda: abrir_config())

botones_centro_layout.addStretch(1)
botones_centro_layout.addWidget(btn_task)
botones_centro_layout.addWidget(btn_calendar)
botones_centro_layout.addWidget(btn_tiempo)
botones_centro_layout.addSpacing(200)
botones_centro_layout.addWidget(btn_notificaciones)
botones_centro_layout.addStretch(1)
botones_centro_layout.addWidget(btn_config)

botones_layout.addLayout(botones_centro_layout)



# ---------------- Función para notificar usuario ---------------- #
def notificar_usuario(tarea, usuario):
    mensaje = f"Recordatorio: {tarea.nombre}\nVence el {tarea.fecha_fin}"

    # Enviar correo si el usuario tiene email
    if usuario[1]:
        try:
            send_email(usuario[1], "Recordatorio de tarea", mensaje)
        except Exception as e:
            print("Error enviando email:", e)

    # Enviar WhatsApp si el usuario tiene teléfono
    if usuario[2]:
        try:
            send_whatsapp(usuario[2], mensaje)
        except Exception as e:
            print("Error enviando WhatsApp:", e)


# ---------------- Funciones botones ---------------- #
def crear_tarea():
    dialogo = DialogoCrearTarea()
    if dialogo.exec_() == QDialog.Accepted:
        datos = dialogo.obtener_datos()
        if datos["nombre"]:
            nueva_tarea = Task(
                datos["nombre"],
                datos["descripcion"],
                datos["fecha_inicio"],
                datos["fecha_fin"],
                datos["prioridad"],
                usuario_id=current_user_id  # ahora asignamos el usuario
            )

            # Guardar en DB y obtener id
            tarea_id = db.add_task(nueva_tarea)
            
            # Notificar al usuario
            usuario = db.get_user_by_id(current_user_id)
            if usuario:
                notificar_usuario(nueva_tarea, usuario)               
                            
            nueva_tarea.id = tarea_id

            # Mostrar en UI (pasar db y id)
            card = CardTarea(
                nueva_tarea.nombre,
                nueva_tarea.descripcion,
                nueva_tarea.fecha_inicio,
                nueva_tarea.fecha_fin,
                nueva_tarea.prioridad,
                db=db,
                task_id=nueva_tarea.id
            )
            layout_iniciadas.insertWidget(layout_iniciadas.count() - 1, card)

            # Registrar en el calendario
            fecha = nueva_tarea.fecha_inicio
            if fecha not in tareas_por_fecha:
                tareas_por_fecha[fecha] = []
            tareas_por_fecha[fecha].append(nueva_tarea.nombre)

btn_task.clicked.connect(crear_tarea)

def abrir_calendario():
    ventana_calendario = CalendarioWindow(tareas_por_fecha, ventana)
    ventana_calendario.show()

btn_calendar.clicked.connect(abrir_calendario)

def abrir_tiempo_restante():
    tareas = []
    for layout in [layout_iniciadas, layout_proceso, layout_finalizadas]:
        for i in range(layout.count() - 1):
            widget = layout.itemAt(i).widget()
            if widget:
                tareas.append(widget)
    ventana_tiempo = TiempoRestanteWindow(tareas, ventana)
    ventana_tiempo.show()

btn_tiempo.clicked.connect(abrir_tiempo_restante)

ventana_notif = None
def abrir_notificaciones():
    global ventana_notif
    if ventana_notif and ventana_notif.isVisible():
        ventana_notif.close()
        ventana_notif = None
        return
    tareas = []
    for layout in [layout_iniciadas, layout_proceso, layout_finalizadas]:
        for i in range(layout.count() - 1):
            widget = layout.itemAt(i).widget()
            if widget:
                tareas.append(widget)
    ventana_notif = NotificacionesWindow(tareas, ventana)
    pos = btn_notificaciones.mapToGlobal(btn_notificaciones.rect().topLeft())
    ventana_notif.move(
        pos.x(),
        pos.y() - ventana_notif.height() - 5
    )
    ventana_notif.show()

btn_notificaciones.clicked.connect(abrir_notificaciones)

def abrir_config():
    ventana_config = ConfigWindow(parent=ventana, db=db)
    ventana_config.exec_()

# Integración layout
kanban_vertical_layout.addLayout(kanban_horizontal_layout)
kanban_vertical_layout.addLayout(botones_layout)

# -------- Agenda diaria -------- #
frame_agenda = QFrame()
frame_agenda.setStyleSheet("""
    background: #23282e;
    border-radius: 18px;
    color: white;
""")
#__________ Cerrar sesión __________#
def cerrar_sesion():
    global current_user_id, login_window
    current_user_id = None

    # Vaciar columnas Kanban
    for layout in [layout_iniciadas, layout_proceso, layout_finalizadas]:
        while layout.count() > 1:  # dejamos solo el stretch
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # Limpiar agenda
    if hasattr(agenda_widget, "clear"):
        agenda_widget.clear()

    # Volver a login
    abrir_login()
    ventana.hide()
#__________________________________#
btn_cerrar_sesion = QPushButton("Cerrar sesión")
btn_cerrar_sesion.setFixedSize(120, 30)
btn_cerrar_sesion.setStyleSheet("""
    QPushButton {
        background: #645394;
        color: #ffffff;
        border-radius: 14px;
        font-size: 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background: #32294d;
    }
""")
btn_cerrar_sesion.clicked.connect(cerrar_sesion)
layout_principal.addWidget(btn_cerrar_sesion, alignment=Qt.AlignTop | Qt.AlignRight)
#___________________________________


layout_agenda = QVBoxLayout(frame_agenda)
layout_agenda.setContentsMargins(12, 12, 12, 12)
layout_agenda.setSpacing(8)

label_today = QLabel(f"<b>Today<br>{QDate.currentDate().toString('dd/MM/yyyy')}</b>")
label_today.setAlignment(Qt.AlignCenter)
label_today.setStyleSheet("color: white; font-size: 14px;")
layout_agenda.addWidget(label_today)

label_agenda = QLabel("Agenda diaria")
label_agenda.setAlignment(Qt.AlignCenter)
label_agenda.setStyleSheet("color: white; font-size: 12px;")
layout_agenda.addWidget(label_agenda)

agenda_widget = AgendaDiaria()
layout_agenda.addWidget(agenda_widget, stretch=1)

layout_principal.addWidget(frame_agenda, stretch=1)
layout_principal.addLayout(kanban_vertical_layout, stretch=3)


# Cargar tareas SOLO del usuario logueado
for tarea in db.get_all_tasks(current_user_id):
    card = CardTarea(
        tarea.nombre,
        tarea.descripcion,
        tarea.fecha_inicio,
        tarea.fecha_fin,
        tarea.prioridad,
        db=db,
        task_id=tarea.id
    )
    layout_iniciadas.insertWidget(layout_iniciadas.count() - 1, card)

    if tarea.fecha_inicio not in tareas_por_fecha:
        tareas_por_fecha[tarea.fecha_inicio] = []
    tareas_por_fecha[tarea.fecha_inicio].append(tarea.nombre)

    
# ---------------- Función para abrir app tras login ---------------- # 
    
def abrir_app(usuario_id):
    global current_user_id, tareas_por_fecha, agenda_widget
    current_user_id = usuario_id
    tareas_por_fecha = {}
    
    

    # Vaciar columnas Kanban
    for layout in [layout_iniciadas, layout_proceso, layout_finalizadas]:
        while layout.count() > 1:  # dejamos solo el stretch
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # Limpiar agenda     
    if hasattr(agenda_widget, "clear"):
        agenda_widget.clear()
        
    # Reemplazar el widget de agenda por uno nuevo con el usuario correcto
    layout_agenda.removeWidget(agenda_widget)
    agenda_widget.deleteLater()
    agenda_widget = AgendaDiaria(db=db, usuario_id=current_user_id)
    layout_agenda.addWidget(agenda_widget, stretch=1)
        
    

    # Cargar tareas desde la DB para este usuario
    for tarea in db.get_all_tasks(current_user_id):
        card = CardTarea(
            tarea.nombre,
            tarea.descripcion,
            tarea.fecha_inicio,
            tarea.fecha_fin,
            tarea.prioridad,
            db=db,
            task_id=tarea.id
        )
        layout_iniciadas.insertWidget(layout_iniciadas.count() - 1, card)

        # Registrar en el diccionario de calendario
        fecha = tarea.fecha_inicio
        if fecha not in tareas_por_fecha:
            tareas_por_fecha[fecha] = []
        tareas_por_fecha[fecha].append(tarea.nombre)

    ventana.show()


# --- Login y Splash --- #

login_window = None
def abrir_login():
    global login_window
    from ui.login_screen import LoginWindow
    # Pasamos db al login para validar/crear usuario
    login_window = LoginWindow(callback_abrir_app=abrir_app, db=db)
    login_window.show()

# ---------------- SplashScreen ---------------- #
splash = SplashScreen()
print("Mostrando splash...")

splash.show()
app.processEvents()  # 👈 fuerza a Qt a renderizar la splash inmediatamente

splash.raise_()
splash.activateWindow()
QTimer.singleShot(5000, lambda: splash._abrir(abrir_login))

app.exec_()








