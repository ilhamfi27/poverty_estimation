from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfileInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=70, blank=True)
    birth_date = models.DateTimeField()

    def __str__(self):
        return self.user.username
