# notifications/utils.py
import requests
from twilio.rest import Client
from decouple import config

# -------- Mailgun --------
MAILGUN_DOMAIN = config("MAILGUN_DOMAIN", default=None)
MAILGUN_API_KEY = config("MAILGUN_API_KEY", default=None)
MAILGUN_FROM = config(
    "MAILGUN_FROM",
    default=f"No Reply <no-reply@{MAILGUN_DOMAIN}>" if MAILGUN_DOMAIN else None,
)

def _trunc(s: str, n: int) -> str:
    return (s or "") if len(s or "") <= n else (s[: n - 1] + "…")

def send_email(to: str, subject: str, text: str, reply_to: str | None = None):
    if not to:
        return False, "Missing recipient"
    if not (MAILGUN_DOMAIN and MAILGUN_API_KEY and MAILGUN_FROM):
        return False, "Mailgun not configured"

    payload = {
        "from": MAILGUN_FROM,
        "to": [to],
        "subject": _trunc(subject, 200),
        "text": text or "",
    }
    if reply_to:
        payload["h:Reply-To"] = reply_to

    try:
        r = requests.post(
            f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
            auth=("api", MAILGUN_API_KEY),
            data=payload,
            timeout=10,
        )
        return r.status_code in (200, 202), r.text
    except Exception as e:
        return False, f"Mailgun exception: {e!r}"

# -------- Twilio --------
TWILIO_SID = config("TWILIO_ACCOUNT_SID", default=None)
TWILIO_TOKEN = config("TWILIO_AUTH_TOKEN", default=None)
TWILIO_FROM = config("TWILIO_FROM_NUMBER", default=None)

def send_sms(to: str, body: str):
    """
    `to` must be E.164 format (e.g., +15555550123).
    """
    if not to:
        return False, "Missing recipient"
    if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM):
        return False, "Twilio not configured"

    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        msg = client.messages.create(
            to=to,
            from_=TWILIO_FROM,
            body=_trunc(body, 1600),  # Twilio hard cap ~1600 chars
        )
        return True, msg.sid
    except Exception as e:
        return False, f"Twilio exception: {e!r}"
