# database/db_manager.py
import sqlite3
from models.task import Task
from typing import Optional

class DBManager:
    def __init__(self, db_name="dayplan.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        # Tabla de usuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            telefono TEXT,
            password TEXT NOT NULL
        )
        """)

        # Tabla de tareas vinculada a usuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            prioridad TEXT,
            completada INTEGER DEFAULT 0,
            usuario_id INTEGER,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
        """)
        self.conn.commit()
        
         # Tabla de agenda diaria
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agenda_diaria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            hora_inicio TEXT,
            hora_fin TEXT,
            usuario_id INTEGER,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
        )
        """)
        self.conn.commit()

    # Crear tarea
    def add_task(self, task: Task) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tareas (nombre, descripcion, fecha_inicio, fecha_fin, prioridad, completada, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            task.nombre, task.descripcion, task.fecha_inicio, task.fecha_fin, 
            task.prioridad, int(task.completada), task.usuario_id
        ))
        self.conn.commit()
        return cursor.lastrowid

    # Leer todas las tareas de un usuario
    def get_all_tasks(self, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, nombre, descripcion, fecha_inicio, fecha_fin, prioridad, completada, usuario_id
            FROM tareas WHERE usuario_id=?
        """, (usuario_id,))
        rows = cursor.fetchall()
        return [
            Task(row[1], row[2], row[3], row[4], row[5], 
                 task_id=row[0], completada=bool(row[6]), usuario_id=row[7])
            for row in rows
        ]

    # Obtener tarea por id
    def get_task(self, task_id: int) -> Optional[Task]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, nombre, descripcion, fecha_inicio, fecha_fin, prioridad, completada, usuario_id
            FROM tareas WHERE id=?
        """, (task_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Task(row[1], row[2], row[3], row[4], row[5],
                    task_id=row[0], completada=bool(row[6]), usuario_id=row[7])

    # Actualizar tarea
    def update_task(self, task_id, task: Task):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tareas
            SET nombre=?, descripcion=?, fecha_inicio=?, fecha_fin=?, prioridad=?, completada=?
            WHERE id=? AND usuario_id=?
        """, (task.nombre, task.descripcion, task.fecha_inicio, task.fecha_fin, 
              task.prioridad, int(task.completada), task_id, task.usuario_id))
        self.conn.commit()

    # Borrar tarea
    def delete_task(self, task_id, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tareas WHERE id=? AND usuario_id=?", (task_id, usuario_id))
        self.conn.commit()

    # Crear usuario
    def create_user(self, email, password, telefono=None) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (email, telefono, password) VALUES (?, ?, ?)
        """, (email, telefono or "", password))
        self.conn.commit()
        return cursor.lastrowid

    # Validar usuario
    def validate_user(self, email, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, password FROM usuarios WHERE email=?", (email,))
        row = cursor.fetchone()
        if row and row[1] == password:
            return row[0]  # devolvemos usuario_id
        return None

    # Obtener usuario
    def get_user(self, email):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, email, telefono FROM usuarios WHERE email=?", (email,))
        return cursor.fetchone()
    
    def get_user_by_id(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, email, telefono FROM usuarios WHERE id=?", (user_id,))
        return cursor.fetchone()


    def close(self):
        self.conn.close()
        
#______________________________________________________


        # Métodos para agenda diaria
    def add_agenda_item(self, nombre, hora_inicio, hora_fin, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO agenda_diaria (nombre, hora_inicio, hora_fin, usuario_id)
            VALUES (?, ?, ?, ?)
        """, (nombre, hora_inicio, hora_fin, usuario_id))
        self.conn.commit()

    def get_agenda_items(self, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT nombre, hora_inicio, hora_fin FROM agenda_diaria WHERE usuario_id=?
        """, (usuario_id,))
        return cursor.fetchall()

    def clear_agenda(self, usuario_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM agenda_diaria WHERE usuario_id=?", (usuario_id,))
        self.conn.commit()
