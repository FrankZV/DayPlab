import os

CONFIG_FILE = "user_theme.cfg"

def save_theme_preference(theme_name):
    with open(CONFIG_FILE, "w") as f:
        f.write(theme_name)

def load_theme_preference():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return f.read().strip()
    return "Claro"  # Valor por defecto