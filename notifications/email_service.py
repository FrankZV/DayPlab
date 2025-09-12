# notifications/email_service.py
import requests
from utils.config import load_config

def send_email(to_email: str, subject: str, text: str) -> bool:
    """
    Envía un email usando Mailgun (config en utils/config.py).
    Devuelve True si el envío fue OK (status 200/201).
    """
    cfg = load_config()
    api_key = cfg.get("MAILGUN_API_KEY")
    domain = cfg.get("MAILGUN_DOMAIN")
    if not api_key or not domain:
        raise RuntimeError("Mailgun no configurado (MAILGUN_API_KEY / MAILGUN_DOMAIN).")

    url = f"https://api.mailgun.net/v3/{domain}/messages"
    auth = ("api", api_key)
    data = {
        "from": f"DayPlan <mail@{domain}>",
        "to": to_email,
        "subject": subject,
        "text": text
    }
    resp = requests.post(url, auth=auth, data=data)
    return resp.status_code in (200, 201)
