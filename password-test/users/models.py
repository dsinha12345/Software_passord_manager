from django.db import models
from django.contrib.auth.models import User

class Password(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_entries')  # Add related_name
    service_name = models.CharField(max_length=100)
    service_url = models.URLField(blank=True, null=True)  # Optional field
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.service_name} ({self.username})'
