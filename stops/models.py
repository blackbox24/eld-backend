from django.db import models

from trip.models import Trip


class Stop(models.Model):
    STOP_TYPES = (
        ("pickup", "Pickup"),
        ("dropoff", "Dropoff"),
        ("fuel", "Fuel"),
        ("rest", "Rest"),
    )
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="stops")
    location = models.JSONField()  # { "lat": ..., "lng": ... }
    stop_type = models.CharField(max_length=20, choices=STOP_TYPES)
    timestamp = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["trip"]),
            models.Index(fields=["stop_type"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self):
        return f"{self.stop_type} stop at {self.location}"
