from django.db import models

class FoodItem(models.Model):
    seller = models.ForeignKey('sellers.SellerProfile', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_fast = models.BooleanField(default=False)
    is_veg = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    
class Menu(models.Model):
    seller = models.ForeignKey('sellers.SellerProfile', on_delete=models.CASCADE)
    date = models.DateField()

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)


