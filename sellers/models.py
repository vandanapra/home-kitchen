from django.db import models

# Create your models here.
class SellerProfile(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    kitchen_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    avg_rating = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
