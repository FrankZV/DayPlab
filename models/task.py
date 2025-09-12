   
# models/task.py
class Task:
    def __init__(self, nombre, descripcion, fecha_inicio, fecha_fin, prioridad, 
                 task_id=None, completada=False, usuario_id=None):
        self.id = task_id
        self.usuario_id = usuario_id
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.prioridad = prioridad
        self.completada = completada
        
