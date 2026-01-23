from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from eld.models import ELDLog, Trip


class SeedDbCommandTest(TestCase):
    @patch("eld.services.RouteService.calculate_route")
    def test_seed_db_command_success(self, mock_calculate_route):
        """
        Test that the seed_db command successfully creates Trip and ELDLog objects.
        """
        # --- Mock Setup ---
        # Mock the return value of the route service to simulate a successful API call
        mock_route_info = {
            "distance_meters": 1270000,  # Approx. NY to Chicago
            "duration_seconds": 45000,
            "geometry": {
                "type": "LineString",
                "coordinates": [[-74.006, 40.7128], [-87.6298, 41.8781]],
            },
            "waypoints": [],
        }
        mock_calculate_route.return_value = mock_route_info

        # --- Call Command ---
        call_command("seed_db")

        # --- Assertions ---
        # Check that 2 trips were created (as defined in the seed_db command)
        self.assertEqual(Trip.objects.count(), 2)

        # Check that the trips were marked as processed
        processed_trips = Trip.objects.filter(status="processed").count()
        self.assertEqual(processed_trips, 2)

        # Check that ELD logs were created for these trips
        # The simple service creates 4 log entries per trip
        self.assertGreater(ELDLog.objects.count(), 0)
        self.assertEqual(ELDLog.objects.count(), 2 * 4)

        # Spot-check the first trip's logs
        first_trip = Trip.objects.first()
        self.assertIsNotNone(first_trip)  # Ensure first_trip is not None for mypy
        self.assertEqual(first_trip.logs.count(), 4)  # type: ignore

        # Check the log statuses created for the first trip
        log_statuses = list(first_trip.logs.values_list("status", flat=True).order_by("start_time"))  # type: ignore
        expected_statuses = ["on_duty", "driving", "on_duty", "off_duty"]
        self.assertEqual(log_statuses, expected_statuses)

    @patch("eld.services.RouteService.calculate_route")
    def test_seed_db_command_route_not_found(self, mock_calculate_route):
        """
        Test that the trip status is set to 'error_no_route' if the service returns None.
        """
        # --- Mock Setup ---
        # Simulate the route service failing to find a route
        mock_calculate_route.return_value = None

        # --- Call Command ---
        call_command("seed_db")

        # --- Assertions ---
        # Check that 2 trips were still created
        self.assertEqual(Trip.objects.count(), 2)

        # Check that their status is correctly set to 'error_no_route'
        error_trips = Trip.objects.filter(status="error_no_route").count()
        self.assertEqual(error_trips, 2)

        # Ensure no ELD logs were created in this case
        self.assertEqual(ELDLog.objects.count(), 0)
