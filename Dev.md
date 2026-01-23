# Developer Documentation: ELD Backend

This document provides a detailed technical overview of the ELD backend, intended for developers working on the project.

## 1. Backend Architecture

The backend is a [Django](https://www.djangoproject.com/) project, with the core business logic encapsulated within a dedicated app named `eld`. The architecture follows a standard Django REST Framework (DRF) pattern, separating concerns into models, views, serializers, and services.

-   **`config/`**: The main project configuration, including `settings.py` and `urls.py`.
-   **`eld/`**: The Django app containing all the logic for the Electronic Logging Device functionality.
    -   `models.py`: Defines the database schema with `Trip` and `ELDLog` models.
    -   `views.py`: Handles the API request/response logic using DRF's generic views.
    -   `serializers.py`: Defines how model data is converted to and from JSON.
    -   `services.py`: A dedicated layer for business logic and third-party API integrations, keeping the views clean.

## 2. Data Models

### `Trip` Model

Stores all information related to a single trip.

-   `current_location` (JSONField): The starting location of the driver.
-   `pickup_location` (JSONField): The pickup location for the trip.
-   `dropoff_location` (JSONField): The final dropoff location.
-   `current_cycle_used` (DecimalField): The number of hours already used in the driver's current 70-hour/8-day cycle.
-   `route_geometry` (JSONField, nullable): Stores the GeoJSON LineString of the calculated route from Openrouteservice.
-   `route_waypoints` (JSONField, nullable): Stores an array of waypoints/steps for the calculated route.

### `ELDLog` Model

Stores individual log events associated with a `Trip`.

-   `trip` (ForeignKey to `Trip`): Links the log entry to a specific trip.
-   `status` (CharField): The type of event (e.g., 'driving', 'on_duty', 'off_duty').
-   `start_time` (DateTimeField): The start time of the log event.
-   `end_time` (DateTimeField): The end time of the log event.
-   `comment` (TextField, nullable): An optional comment for the event.
-   `duration` (property): A calculated property that returns the duration of the event.

## 3. API Endpoints and Views

The API is built using Django REST Framework's generic views for simplicity and robustness.

-   **`TripListCreateAPIView`**:
    -   `GET /api/trips/`: Lists all trips.
    -   `POST /api/trips/`: Creates a new trip. Upon creation, it triggers the `RouteService` and `ELDService`.
-   **`TripRetrieveUpdateDestroyAPIView`**:
    -   `GET /api/trips/<id>/`: Retrieves a single trip by its ID.
    -   `PUT/PATCH /api/trips/<id>/`: Updates a trip.
    -   `DELETE /api/trips/<id>/`: Deletes a trip.
-   **`ELDLogListAPIView`**:
    -   `GET /api/trips/<trip_id>/logs/`: Lists all ELD log entries for a specific trip.

## 4. Services Layer (`eld/services.py`)

### `RouteService`

-   **Purpose**: To abstract the interaction with the Openrouteservice API.
-   **Integration**: It uses the `openrouteservice-py` client library. The API key is fetched from environment variables (`OPENROUTESERVICE_API_KEY`).
-   **Functionality**: The `calculate_route` method takes a list of coordinates and requests a route using the `driving-hgv` (Heavy Goods Vehicle) profile, which is suitable for trucks. It returns a dictionary containing the route's distance, duration, and geometry.

### `ELDService`

-   **Purpose**: To generate the sequence of ELD log events for a trip.
-   **Functionality**: The `generate_eld_logs` method currently implements a simplified trip simulation:
    1.  1 hour of 'on_duty' for pickup.
    2.  A 'driving' event for the duration calculated by `RouteService`.
    3.  1 hour of 'on_duty' for dropoff.
    4.  A final 'off_duty' event.
-   **Note**: This service is where the more complex HOS rules will be implemented.

## 5. Potential Bottlenecks and Scalability

1.  **External API Calls**: The `RouteService` makes a blocking call to the Openrouteservice API during the trip creation process.
    -   **Problem**: High latency from the external API will directly impact the response time of the `POST /api/trips/` endpoint.
    -   **Solution**: For frequently requested routes (same origin/destination), the route information could be cached (e.g., using Django's caching framework with Redis, which is already set up).

2.  **Synchronous ELD Log Generation**: The `ELDService` also runs synchronously within the same request.
    -   **Problem**: As the HOS rule logic becomes more complex (e.g., simulating multi-day trips with required breaks), the processing time will increase, slowing down the API response.
    -   **Solution**: For more complex calculations, this process should be moved to a background task using a distributed task queue like **Celery** with **Redis** or **RabbitMQ**. The API would then immediately return a trip ID, and the frontend could poll an endpoint to check the status of the log generation.

3.  **Database Performance**:
    -   **Problem**: As the `eld_log` table grows, queries could become slow.
    -   **Solution**: Database indexes have already been added to the foreign key (`trip`) and `start_time` on the `ELDLog` model, which will significantly improve filtering and ordering performance. This practice should be maintained for any new query-heavy models.

## 6. Edge Cases to Tackle

-   **Route Not Found**: If Openrouteservice returns no route, the current implementation logs a warning but doesn't inform the user. A `status` field could be added to the `Trip` model (e.g., 'pending', 'processed', 'error_no_route') to provide feedback.
-   **Complex HOS Rules**: The current `ELDService` is a placeholder. The full implementation needs to account for:
    -   The **70-hour/8-day rule**: The driver cannot drive if they have been on duty for 70 hours in the last 8 days.
    -   **11-hour driving limit**: A driver can only drive for 11 hours after 10 consecutive hours off duty.
    -   **14-hour duty limit**: A driver cannot drive beyond the 14th consecutive hour after coming on duty.
    -   **30-minute break**: A driver must take a 30-minute break after 8 hours of driving.
-   **Multi-day Trips**: The simulation needs to handle trips that span multiple days, including mandatory 10-hour off-duty breaks.
-   **Fueling Stops**: The assumption of a fueling stop every 1,000 miles needs to be implemented by inserting 'on_duty' events into the log sequence.

## 7. Security Implementations

-   **Secret Management**: The `python-decouple` library is used to load sensitive information like `SECRET_KEY`, `DATABASE_URL`, and API keys from environment variables (`.env` file), preventing them from being hardcoded in the source code.
-   **API Authentication**: The project is configured with `rest_framework_simplejwt` to support JSON Web Token (JWT) based authentication. While the current views are set to `AllowAny` for development, the framework is in place to easily secure endpoints by changing the permission classes.
-   **Django's Built-in Security**: The project benefits from Django's built-in security features, which are enabled by default:
    -   **Cross-Site Request Forgery (CSRF)** protection.
    -   **Cross-Site Scripting (XSS)** protection (via template auto-escaping).
    -   **SQL Injection** protection (by using Django's ORM).
-   **CORS**: `django-cors-headers` is configured to control which origins are allowed to make requests to the API, which is crucial for a full-stack application.
-   **Secure Headers**: Security-enhancing HTTP headers (`SECURE_HSTS_SECONDS`, `SECURE_CONTENT_TYPE_NOSNIFF`, etc.) are configured in `settings.py`.
