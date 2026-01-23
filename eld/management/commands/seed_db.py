import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from eld.models import Trip
from eld.services import ELDService, RouteService

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = "Seeds the database with initial trip data and generates corresponding ELD logs."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting database seeding..."))

        # Clear existing data
        self.stdout.write("Clearing existing Trip and ELDLog data...")
        Trip.objects.all().delete()

        # --- Sample Trip 1: New York to Chicago ---
        trip1_data = {
            "current_location": {"latitude": 40.7128, "longitude": -74.0060},  # New York, NY
            "pickup_location": {"latitude": 40.7128, "longitude": -74.0060},  # New York, NY
            "dropoff_location": {"latitude": 41.8781, "longitude": -87.6298},  # Chicago, IL
            "current_cycle_used": "10.00",
        }

        # --- Sample Trip 2: Los Angeles to Las Vegas ---
        trip2_data = {
            "current_location": {"latitude": 34.0522, "longitude": -118.2437},  # Los Angeles, CA
            "pickup_location": {"latitude": 34.0522, "longitude": -118.2437},  # Los Angeles, CA
            "dropoff_location": {"latitude": 36.1699, "longitude": -115.1398},  # Las Vegas, NV
            "current_cycle_used": "5.50",
        }

        trips_to_process = [trip1_data, trip2_data]

        for i, trip_data in enumerate(trips_to_process, 1):
            self.stdout.write(f"--- Processing Trip {i}/{len(trips_to_process)} ---")

            # Create the Trip object
            trip = Trip.objects.create(**trip_data)
            self.stdout.write(f"  Created Trip {trip.id} (status: {trip.status})")

            # This mimics the logic from the view's create method
            try:
                self.stdout.write(f"  Calculating route for Trip {trip.id}...")

                pickup_coords = [
                    trip.pickup_location["longitude"],
                    trip.pickup_location["latitude"],
                ]
                dropoff_coords = [
                    trip.dropoff_location["longitude"],
                    trip.dropoff_location["latitude"],
                ]

                route_service = RouteService()
                route_info = route_service.calculate_route(
                    coordinates=[pickup_coords, dropoff_coords]
                )

                if route_info:
                    trip.route_geometry = route_info["geometry"]
                    trip.route_waypoints = route_info["waypoints"]

                    self.stdout.write("  Route calculated. Generating ELD logs...")
                    eld_service = ELDService()
                    eld_service.generate_eld_logs(trip, route_info)

                    trip.status = "processed"
                    self.stdout.write(
                        self.style.SUCCESS(f"  Successfully processed Trip {trip.id}")
                    )
                else:
                    trip.status = "error_no_route"
                    self.stdout.write(
                        self.style.WARNING(f"  Could not find route for Trip {trip.id}")
                    )

                trip.save()

            except Exception as e:
                logger.error(f"An error occurred while processing Trip {trip.id}: {e}")
                trip.status = "error_processing"
                trip.save()
                self.stdout.write(self.style.ERROR(f"  Failed to process Trip {trip.id}"))

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
