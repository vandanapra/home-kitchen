from django.db import models
from django.utils import timezone
class Order(models.Model):
    PAYMENT_CHOICES = (
        ("COD", "Cash on Delivery"),
        ("ONLINE", "Online Payment"),
        ("PARTIAL", "Partial Payment"),
    )
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE)
    seller = models.ForeignKey('sellers.SellerProfile', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        default="COD"
    )
    paid_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )
    status = models.CharField(max_length=20,choices=[
        ('PENDING','Pending'),
        ('PAID','Paid'),
        ('DELIVERED','Delivered'),
        ('ACCEPTED','Accepted'),
        ('REJECTED','Rejected'),
    ],default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    day = models.CharField(
        max_length=10,
        choices=[
            ("MONDAY","Monday"),
            ("TUESDAY","Tuesday"),
            ("WEDNESDAY","Wednesday"),
            ("THURSDAY","Thursday"),
            ("FRIDAY","Friday"),
            ("SATURDAY","Saturday"),
            ("SUNDAY","Sunday"),
        ],default=""
    )
   ## Add Flag to Prevent Duplicate Orders
    order_date = models.DateField(default=timezone.now)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.TextField(blank=True, null=True)
    delivery_address = models.TextField(default="")
    delivery_city = models.CharField(max_length=50,default="")
    delivery_pincode = models.CharField(max_length=10,default="")
    is_subscription_order = models.BooleanField(default=False)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    menu_item = models.ForeignKey('sellers.MenuItem', on_delete=models.CASCADE,null=True)
    quantity = models.PositiveIntegerField()

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100, blank=True)


