from django.db import models

class SubscriptionPlan(models.Model):
    seller = models.ForeignKey(
        'sellers.SellerProfile',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)  # Weekly / Monthly
    price = models.DecimalField(max_digits=8, decimal_places=2)
    includes_fast_food = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.seller.kitchen_name}"

class Subscription(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    )

    customer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE
    )
    seller = models.ForeignKey(
        'sellers.SellerProfile',
        on_delete=models.CASCADE
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    created_at = models.DateTimeField(auto_now_add=True)
