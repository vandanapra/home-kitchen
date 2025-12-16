from datetime import date
from subscription.models import Subscription
from food.models import Menu, MenuItem
from orders.models import Order, OrderItem
from notifications.services import send_whatsapp_message

def create_daily_subscription_orders():
    today = date.today()

    subscriptions = Subscription.objects.filter(
        status='ACTIVE',
        start_date__lte=today,
        end_date__gte=today
    )

    for sub in subscriptions:

        # ❌ Skip if order already created
        if Order.objects.filter(
            customer=sub.customer,
            seller=sub.seller,
            order_date=today,
            is_subscription_order=True
        ).exists():
            continue

        # ✅ Get today's menu
        menu = Menu.objects.filter(
            seller=sub.seller,
            date=today
        ).first()

        if not menu:
            continue

        menu_items = MenuItem.objects.filter(menu=menu)

        if not menu_items.exists():
            continue

        # ✅ Create order
        order = Order.objects.create(
            customer=sub.customer,
            seller=sub.seller,
            total_amount=0,
            status='PENDING',
            is_subscription_order=True
        )

        total = 0

        for item in menu_items:
            OrderItem.objects.create(
                order=order,
                food_item=item.food_item,
                quantity=1
            )
            total += item.food_item.price

        order.total_amount = total
        order.save()
        # ✅ WHATSAPP MESSAGE (YOUR EXACT MESSAGE)
        message = f"""
🍛 Daily Tiffin Order Created!
Seller: {sub.seller.kitchen_name}
Total: ₹{order.total_amount}
Date: {today}
"""

        send_whatsapp_message(
            sub.customer.mobile,
            message
        )

        # ✅ Optional: Notify Seller
        send_whatsapp_message(
            sub.seller.user.mobile,
            f"New daily tiffin order from {sub.customer.name} for today."
        )