from django.db import models

class Order(models.Model):
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE)
    seller = models.ForeignKey('sellers.SellerProfile', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[('PENDING','Pending'),('PAID','Paid'),('DELIVERED','Delivered')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
   ## Add Flag to Prevent Duplicate Orders
    order_date = models.DateField(auto_now_add=True)
    is_subscription_order = models.BooleanField(default=False)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food_item = models.ForeignKey('food.FoodItem', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100, blank=True)


