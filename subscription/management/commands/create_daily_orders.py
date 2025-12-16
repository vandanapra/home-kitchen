from django.core.management.base import BaseCommand
from subscription.services import create_daily_subscription_orders

class Command(BaseCommand):
    help = "Create daily orders for active subscriptions"

    def handle(self, *args, **kwargs):
        create_daily_subscription_orders()
        self.stdout.write(
            self.style.SUCCESS("Daily subscription orders created successfully")
        )


