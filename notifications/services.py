from twilio.rest import Client
from django.conf import settings

def send_whatsapp_message(to, message):
    """
    to: whatsapp:+91XXXXXXXXXX
    """
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )

    msg = client.messages.create(
        from_=settings.TWILIO_WHATSAPP_FROM,
        to=f"whatsapp:{to}",
        body=message
    )

    return msg.sid
