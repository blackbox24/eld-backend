from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
# Create your models here.


class Trip(models.Model):
    current_loc = models.JSONField(null=False, blank=False)
    pickup_loc = models.JSONField(null=False, blank=False)
    dropoff_loc = models.JSONField(null=False, blank=False)
    cycles_hrs = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(
                fields=("created_by",),
            )
        ]
        ordering = ["-created_at"]
