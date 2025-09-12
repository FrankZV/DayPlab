# utils/config.py
import os

def load_config():
    """
    Lee configuración desde variables de entorno.
    Devuelve un diccionario con keys:
     - MAILGUN_API_KEY
     - MAILGUN_DOMAIN
     - WHATSAPP_TOKEN
     - WHATSAPP_PHONE_NUMBER_ID
    """
    return {
        "MAILGUN_API_KEY": os.getenv("MAILGUN_API_KEY"),
        "MAILGUN_DOMAIN": os.getenv("MAILGUN_DOMAIN"),
        "WHATSAPP_TOKEN": os.getenv("WHATSAPP_TOKEN"),
        "WHATSAPP_PHONE_NUMBER_ID": os.getenv("WHATSAPP_PHONE_NUMBER_ID"),
    }
