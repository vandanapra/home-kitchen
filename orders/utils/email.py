from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from django.utils import timezone
from django.core.mail import EmailMessage
from decimal import Decimal

def send_order_email_to_seller(seller_email, order):
    invoice_no = generate_invoice_number(order)
    subject = f"🛎️ New Order Received ({invoice_no})"

    items_text = "\n".join([
        f"- {item.menu_item.name} × {item.quantity}"
        for item in order.orderitem_set.all()
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


def generate_invoice_number(order):
    """
    Format: INV-2026-001
    """
    year = order.created_at.year

    # Order ID ko sequence banane ke liye pad karein
    sequence = str(order.id).zfill(3)

    return f"INV-{year}-{sequence}"

def generate_order_invoice_pdf(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50

    invoice_no = generate_invoice_number(order)

    # 🔹 Header
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, y, "Home Kitchen - Invoice")

    y -= 30
    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Invoice No: {invoice_no}")
    y -= 15
    p.drawString(50, y, f"Invoice Date: {timezone.now().strftime('%d %b %Y')}")
    y -= 15
    p.drawString(50, y, f"Order ID: {order.id}")

    y -= 30
    p.drawString(50, y, f"Customer: {order.customer.name}")
    y -= 15
    p.drawString(50, y, f"Kitchen: {order.seller.kitchen_name}")
    y -= 15
    p.drawString(50, y, f"Order Day: {order.day}")
    y -= 15
    p.drawString(50, y, f"Order Date: {order.order_date}")

    # 🔹 Table Header
    y -= 30
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Item")
    p.drawString(300, y, "Qty")
    p.drawString(350, y, "Price")

    y -= 15
    p.setFont("Helvetica", 10)

    total = Decimal("0.00")

    for item in order.orderitem_set.all():
        line_total = item.menu_item.price * item.quantity
        total += line_total

        p.drawString(50, y, item.menu_item.name)
        p.drawString(300, y, str(item.quantity))
        p.drawString(350, y, f"₹{line_total}")
        y -= 15

    # 🔹 Total
    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total Amount: ₹{total}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer



def send_invoice_email_to_customer(order):
    invoice_no = generate_invoice_number(order)
    pdf_buffer = generate_order_invoice_pdf(order)

    subject = f"🧾 Invoice {invoice_no} - Home Kitchen"

    body = f"""
Hello {order.customer.name},

Thank you for your order!

Invoice Number: {invoice_no}
Kitchen: {order.seller.kitchen_name}
Order Day: {order.day}
Order Date: {order.order_date}
Total Amount: ₹{order.total_amount}

Please find your invoice attached.

Regards,
Home Kitchen Team
"""

    email = EmailMessage(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [order.customer.email],
    )

    email.attach(
        f"{invoice_no}.pdf",
        pdf_buffer.read(),
        "application/pdf"
    )

    email.send(fail_silently=False)
