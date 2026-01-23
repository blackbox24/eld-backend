from django.db import models


class Trip(models.Model):
    """
    Represents a single trip with its details.
    """

    TRIP_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processed", "Processed"),
        ("error_no_route", "Error: No Route Found"),
        ("error_processing", "Error: Processing Failed"),
        ("error_invalid_location", "Error: Invalid Location Data"),
    ]

    status = models.CharField(max_length=30, choices=TRIP_STATUS_CHOICES, default="pending")
    current_location = models.JSONField()
    pickup_location = models.JSONField()
    dropoff_location = models.JSONField()
    current_cycle_used = models.DecimalField(max_digits=4, decimal_places=2, help_text="in hours")
    route_geometry = models.JSONField(
        blank=True, null=True, help_text="GeoJSON LineString of the calculated route"
    )
    route_waypoints = models.JSONField(
        blank=True, null=True, help_text="Array of waypoints in the calculated route"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["current_location"]),
            models.Index(fields=["pickup_location"]),
            models.Index(fields=["dropoff_location"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Trip from {self.pickup_location} to {self.dropoff_location}"


class ELDLog(models.Model):
    """
    Represents a single ELD log event.
    """

    LOG_STATUS_CHOICES = [
        ("off_duty", "Off Duty"),
        ("sleeper_berth", "Sleeper Berth"),
        ("driving", "Driving"),
        ("on_duty", "On Duty (Not Driving)"),
    ]

    trip = models.ForeignKey(Trip, related_name="logs", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=LOG_STATUS_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    comment = models.TextField(blank=True, null=True)

    @property
    def duration(self):
        return self.end_time - self.start_time

    class Meta:
        indexes = [
            models.Index(fields=["trip"]),
            models.Index(fields=["start_time"]),
        ]
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.trip}: {self.status} from {self.start_time} to {self.end_time}"
