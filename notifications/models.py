from django.db import models

class Notification(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    channel = models.CharField(max_length=20)  # SMS / WhatsApp
    message = models.TextField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

