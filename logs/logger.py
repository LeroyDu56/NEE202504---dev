# sdks/python/nee_logger.py
import os, uuid, requests
from datetime import datetime, timezone

API_URL = os.getenv("LOG_API_URL", "http://192.168.200.152:8765")
API_KEY = os.getenv("LOG_API_KEY", "")


def _now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

def log_event( message,Source=None, CodeLog=None, UserId=None, RequestId=None, Ts=None):
    """Appelle cette fonction dans tes try/except."""
    if not RequestId: RequestId = str(uuid.uuid4())
    if Ts is None: Ts = _now_iso()

    ev = {
        "CodeLog": CodeLog,
        "Ts": Ts,
        "Source": Source,
        "UserId": UserId,
        "RequestId": RequestId,
        "Message": message,
        "schema_version": "1.0"
    }
    # Nettoie les champs None
    ev = {k: v for k, v in ev.items() if v is not None}

    try:
        requests.post(
            API_URL.rstrip("/") + "/logs/ingest",
            json={"events": [ev]},
            headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
            timeout=2.0
        )
    except Exception:
        # ultra-simple : on ignore l'erreur réseau (rien ne bloque ton appli)
        pass

    return RequestId  # utile pour corréler si besoin
