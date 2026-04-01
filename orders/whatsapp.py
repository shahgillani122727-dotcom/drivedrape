import requests
from django.conf import settings


def send_whatsapp_notification(order):
    """
    Send WhatsApp notification to business owner when new order placed.
    Uses WhatsApp Business API (or fallback wa.me link).

    For production: integrate with:
    - Twilio WhatsApp API
    - Meta WhatsApp Cloud API
    - UltraMsg / CallMeBot (easy free options)
    """
    message = _build_order_message(order)

    # ── Option 1: CallMeBot (Free, easy setup) ──────────────────────
    # Sign up at callmebot.com, get API key, set in settings
    callmebot_key = getattr(settings, 'CALLMEBOT_API_KEY', None)
    if callmebot_key:
        try:
            number = settings.WHATSAPP_BUSINESS_NUMBER.replace('+', '')
            url = (
                f"https://api.callmebot.com/whatsapp.php"
                f"?phone={number}&text={requests.utils.quote(message)}&apikey={callmebot_key}"
            )
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                order.whatsapp_sent = True
                order.save(update_fields=['whatsapp_sent'])
                return True
        except Exception as e:
            print(f"WhatsApp error: {e}")

    # ── Option 2: Twilio ────────────────────────────────────────────
    twilio_sid   = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    twilio_from  = getattr(settings, 'TWILIO_WHATSAPP_FROM', None)

    if twilio_sid and twilio_token and twilio_from:
        try:
            from twilio.rest import Client
            client = Client(twilio_sid, twilio_token)
            client.messages.create(
                body=message,
                from_=f"whatsapp:{twilio_from}",
                to=f"whatsapp:{settings.WHATSAPP_BUSINESS_NUMBER}"
            )
            order.whatsapp_sent = True
            order.save(update_fields=['whatsapp_sent'])
            return True
        except Exception as e:
            print(f"Twilio WhatsApp error: {e}")

    return False


def _build_order_message(order):
    items_text = "\n".join(
        f"  • {item.product_name} × {item.quantity} = Rs.{item.line_total}"
        for item in order.items.all()
    )
    return (
        f"🛒 *NEW ORDER — Drive Drape*\n\n"
        f"📋 Order ID: #{order.order_id}\n"
        f"👤 Name: {order.full_name}\n"
        f"📱 Phone: {order.phone}\n"
        f"📍 City: {order.get_city_display()}\n"
        f"🏠 Address: {order.address}\n\n"
        f"🛍️ Items:\n{items_text}\n\n"
        f"💰 Subtotal: Rs.{order.subtotal}\n"
        f"🚚 Shipping: Rs.{order.shipping_cost}\n"
        f"💵 *Total: Rs.{order.total}*\n\n"
        f"💳 Payment: {order.get_payment_method_display()}\n"
        f"📝 Notes: {order.notes or 'None'}\n\n"
        f"⏰ Placed at: {order.created_at.strftime('%d %b %Y, %I:%M %p')}"
    )


def send_customer_whatsapp(order):
    """
    Generate a wa.me confirmation link for customer
    (shown on order confirmation page)
    """
    number = settings.WHATSAPP_BUSINESS_NUMBER.replace('+', '').replace(' ', '')
    message = (
        f"Hi! I just placed order #{order.order_id} on Drive Drape. "
        f"Total: Rs.{order.total}. Payment: {order.get_payment_method_display()}. "
        f"Please confirm."
    )
    return f"https://wa.me/{number}?text={requests.utils.quote(message)}"
