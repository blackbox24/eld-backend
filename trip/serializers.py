from rest_framework import serializers

from .models import Trip


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ["current_loc", "pickup_loc", "dropoff_loc", "cycles_hrs", "created_by"]
