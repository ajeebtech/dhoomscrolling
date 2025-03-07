from django.contrib.auth.models import User
from django.db import models

class UserInterest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interests = models.JSONField()
    voice = models.CharField(max_length=100, null=True, blank=True)  # Store voice choice