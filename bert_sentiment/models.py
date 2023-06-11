from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.CharField(max_length=500, blank=True)


class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.text}'


class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_data = models.TextField()
    sentiment = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {" ".join(self.text_data.split(" ")[:5])}'
