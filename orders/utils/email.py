from django.core.mail import send_mail
from django.conf import settings


def send_order_email_to_seller(seller_email, order):
    subject = "🛎️ New Order Received"

    items_text = "\n".join([
        f"- {item.menu_item.name} × {item.quantity}"
        for item in order.items.all()
    ])

    message = f"""
Hello,

You have received a new order.

Customer: {order.customer.name}
Order ID: {order.id}
Day: {order.day}
Date: {order.order_date}

Items:
{items_text}

Total Amount: ₹{order.total_amount}

Please login to Seller Dashboard to accept/reject the order.

Regards,
Home Kitchen Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [seller_email],
        fail_silently=False,
    )
