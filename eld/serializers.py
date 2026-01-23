from rest_framework import serializers

from .models import ELDLog, Trip


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [
            "id",
            "status",
            "current_location",
            "pickup_location",
            "dropoff_location",
            "current_cycle_used",
            "route_geometry",
            "route_waypoints",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "route_geometry",
            "route_waypoints",
            "created_at",
            "updated_at",
        ]


class ELDLogSerializer(serializers.ModelSerializer):
    duration = serializers.DurationField(read_only=True)

    class Meta:
        model = ELDLog
        fields = [
            "id",
            "trip",
            "status",
            "start_time",
            "end_time",
            "duration",
            "comment",
        ]
        read_only_fields = ["trip"]
