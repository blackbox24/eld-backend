import logging
from datetime import timedelta

import openrouteservice  # type ignore
from decouple import config

from .models import ELDLog, Trip

logger = logging.getLogger(__name__)


class RouteService:
    def __init__(self):
        self.api_key = config("OPENROUTESERVICE_API_KEY", default=None)
        if not self.api_key:
            logger.error("OPENROUTESERVICE_API_KEY not found in environment variables.")
            raise ValueError("Openrouteservice API key is not configured.")
        self.client = openrouteservice.Client(key=self.api_key)

    def calculate_route(self, coordinates: list[list[float]]):
        """
        Calculates a route between given coordinates using Openrouteservice.

        Args:
            coordinates: A list of [longitude, latitude] pairs for the route.
                         Example: [[lon1, lat1], [lon2, lat2], ...]

        Returns:
            A dictionary containing route details (distance, duration, geometry)
            or None if the route calculation fails.
        """
        try:
            # Request route for a truck profile
            # 'truck' profile considers factors like truck restrictions, speed limits etc.
            routes = self.client.directions(
                coordinates=coordinates,
                profile="driving-hgv",  # HGV stands for Heavy Goods Vehicle (truck)
                format="json",
                validate=True,
            )

            if routes and routes["routes"]:
                route_summary = routes["routes"][0]["summary"]
                route_geometry = routes["routes"][0]["geometry"]
                route_duration = route_summary["duration"]  # in seconds
                route_distance = route_summary["distance"]  # in meters

                return {
                    "distance_meters": route_distance,
                    "duration_seconds": route_duration,
                    "geometry": route_geometry,  # GeoJSON LineString
                    # "waypoints": routes['routes'][0].get('segments', [{}])[0].get('steps', []), # Removed waypoints
                }
            return None

        except openrouteservice.exceptions.ApiError as e:
            logger.error(f"Openrouteservice API error: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during route calculation: {e}")
            return None


class ELDService:
    """
    Service to generate ELD logs based on trip details and route information.
    """

    def generate_eld_logs(self, trip: Trip, route_info: dict):
        """
        Generates ELD log entries for a given trip based on route information.
        This is a simplified version. HOS rules will be applied incrementally.
        """
        logs = []
        start_time = trip.created_at  # Assuming trip starts when it's created

        # 1. On-Duty (Not Driving) for Pickup
        pickup_duration = timedelta(hours=1)
        logs.append(
            ELDLog(
                trip=trip,
                status="on_duty",
                start_time=start_time,
                end_time=start_time + pickup_duration,
                comment="Pickup at origin",
            )
        )
        current_time = start_time + pickup_duration

        # 2. Driving
        driving_duration = timedelta(seconds=route_info["duration_seconds"])
        logs.append(
            ELDLog(
                trip=trip,
                status="driving",
                start_time=current_time,
                end_time=current_time + driving_duration,
                comment="Driving to destination",
            )
        )
        current_time += driving_duration

        # 3. On-Duty (Not Driving) for Dropoff
        dropoff_duration = timedelta(hours=1)
        logs.append(
            ELDLog(
                trip=trip,
                status="on_duty",
                start_time=current_time,
                end_time=current_time + dropoff_duration,
                comment="Dropoff at destination",
            )
        )
        current_time += dropoff_duration

        # 4. Off-Duty (end of trip for simplicity)
        # This can be expanded to proper 10-hour off-duty, sleeper berth etc.
        logs.append(
            ELDLog(
                trip=trip,
                status="off_duty",
                start_time=current_time,
                end_time=current_time + timedelta(hours=8),  # Placeholder for resting
                comment="End of trip, off duty",
            )
        )
        return ELDLog.objects.bulk_create(logs)
