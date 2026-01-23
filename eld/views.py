import logging

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import ELDLog, Trip
from .serializers import ELDLogSerializer, TripSerializer
from .services import ELDService, RouteService  # Import the services

logger = logging.getLogger(__name__)


class TripListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to retrieve a list of trips or create a new trip.
    """

    queryset = Trip.objects.all().order_by("-created_at")
    serializer_class = TripSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        trip = serializer.save()

        # Extract coordinates for routing
        # Assuming location JSONField stores {"latitude": X, "longitude": Y}
        try:
            pickup_coords = [trip.pickup_location["longitude"], trip.pickup_location["latitude"]]
            dropoff_coords = [trip.dropoff_location["longitude"], trip.dropoff_location["latitude"]]
        except KeyError:
            logger.error(
                f"Invalid location data for Trip {trip.id}. Missing 'latitude' or 'longitude'."
            )
            # Optionally, delete the trip or mark it as invalid
            return Response(
                {"detail": "Invalid location data provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate route
        try:
            route_service = RouteService()
            route_info = route_service.calculate_route(coordinates=[pickup_coords, dropoff_coords])

            if route_info:
                # Store route geometry and waypoints in the trip for later use (e.g., frontend map display)
                trip.route_geometry = route_info[
                    "geometry"
                ]  # Assuming you add this field to Trip model
                trip.route_waypoints = route_info[
                    "waypoints"
                ]  # Assuming you add this field to Trip model
                trip.save(
                    update_fields=["route_geometry", "route_waypoints"]
                )  # Save the updated fields

                # Generate ELD logs
                eld_service = ELDService()
                eld_service.generate_eld_logs(trip, route_info)
                logger.info(f"ELD logs generated for Trip {trip.id}")
            else:
                logger.warning(
                    f"Could not calculate route for Trip {trip.id}. No ELD logs generated."
                )
                # Handle this case, e.g., return an error response, or mark trip for manual review
        except ValueError as e:
            logger.error(f"Configuration error for Trip {trip.id}: {e}")
            # This is typically due to missing API key
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(
                f"Error during route calculation or ELD log generation for Trip {trip.id}: {e}"
            )
            return Response(
                {"detail": "Error processing trip route or logs."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TripRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a trip.
    """

    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [AllowAny]


class ELDLogListAPIView(generics.ListAPIView):
    """
    API view to retrieve a list of ELD logs for a specific trip.
    """

    serializer_class = ELDLogSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        This view should return a list of all the ELD logs
        for the trip as determined by the trip_pk portion of the URL.
        """
        trip_pk = self.kwargs["trip_pk"]
        return ELDLog.objects.filter(trip__pk=trip_pk)
