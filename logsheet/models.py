from django.db import models

from trip.models import Trip


# Create your models here.
class LogSheet(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="logs")
    day_number = models.PositiveIntegerField()
    driving_hours = models.DecimalField(max_digits=4, decimal_places=2)
    rest_hours = models.DecimalField(max_digits=4, decimal_places=2)
    fuel_stops = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log Day {self.day_number} for Trip {self.trip.id}"
