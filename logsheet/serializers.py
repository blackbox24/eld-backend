from rest_framework import serializers

from .models import LogSheet


class LogSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogSheet
        fields = [
            "trip",
            "day_number",
            "driving_hours",
            "rest_hours",
            "fuel_stops",
        ]
