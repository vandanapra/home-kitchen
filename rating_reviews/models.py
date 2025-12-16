from django.db import models

class Review(models.Model):
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE)
    seller = models.ForeignKey('sellers.SellerProfile', on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

