para correr el proyecto con la libreria, es necesario instalar PyQt5, para eso copie el siguiente comando en la terminal despues de abrir el proyecto DayPlan: pip install PyQt5


ESTRUCTURA DEL PROYECTO 

gestor_tareas/
│── main.py                  # antes index.py → punto de entrada principal
│
│── ui/                      # Interfaces gráficas (PyQt5)
│   ├── agenda_diaria.py
│   ├── calendario.py
│   ├── cards.py
│   ├── config_screen.py
│   ├── login_screen.py
│   ├── notificaciones.py
│   ├── splash_screen.py
│   └── tiempo_restante.py
│
│── database/                # Gestión de SQLite
│   └── db_manager.py
│
│── models/                  # Clases de dominio
│   └── task.py              # Clase Task
│
│── notifications/           # Servicios externos
│   ├── email_service.py     # Mailgun
│   └── whatsapp_service.py  # Meta API
│
│── utils/                   # Utilidades y configuraciones
│   ├── config.py
│   └── helpers.py
│
└── requirements.txt

