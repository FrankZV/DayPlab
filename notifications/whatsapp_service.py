# notifications/whatsapp_service.py
import requests
from utils.config import load_config

def send_whatsapp(to_number: str, message: str) -> bool:
    """
    Enviar WhatsApp usando Meta Cloud API (token y phone_number_id en config).
    Config keys esperadas: WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID
    """
    cfg = load_config()
    token = cfg.get("WHATSAPP_TOKEN")
    phone_id = cfg.get("WHATSAPP_PHONE_NUMBER_ID")
    if not token or not phone_id:
        raise RuntimeError("WhatsApp Cloud API no configurada (WHATSAPP_TOKEN / WHATSAPP_PHONE_NUMBER_ID).")

    url = f"https://graph.facebook.com/v16.0/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"preview_url": False, "body": message}
    }
    resp = requests.post(url, headers=headers, json=payload)
    return resp.status_code in (200, 201)
