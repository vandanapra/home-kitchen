from django.db import models
from django.utils import timezone

# Create your models here.
class SellerProfile(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE,related_name="seller_profile")
    kitchen_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    avg_rating = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class MenuDay(models.Model):
    seller = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="menu_days"
    )
    date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("seller", "date")
        ordering = ["date"]

    def __str__(self):
        return f"{self.seller.mobile} - {self.date}"
    
class MenuItem(models.Model):
    menu_day = models.ForeignKey(
        MenuDay,
        on_delete=models.CASCADE,
        related_name="items"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
