from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    ROLES = (("admin", "ADMIN"), ("driver", "DRIVER"))

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=6, choices=ROLES, default="driver")
