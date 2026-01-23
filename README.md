# ELD Logbook Automation

This is a full-stack application designed to automate the generation of Electronic Logging Device (ELD) logs for truck drivers. The backend is built with Django and the frontend with React.

## Objective

The application takes trip details as input and generates route instructions and ELD log sheets as output.

### Features

-   **Input:**
    -   Current Location
    -   Pickup Location
    -   Dropoff Location
    -   Current Cycle Used (in hours)
-   **Output:**
    -   An interactive map displaying the route, stops, and required rest periods.
    -   Completed daily log sheets, including support for multi-day trips.

### Business Logic Assumptions

-   **Driver Type:** Property-carrying driver.
-   **Hours of Service (HOS) Rule:** 70 hours in an 8-day period.
-   **Conditions:** Assumes no adverse driving conditions.
-   **Refueling:** At least one stop for fueling every 1,000 miles.
-   **Loading/Unloading:** 1 hour allocated for both pickup and drop-off.

## Tech Stack

-   **Backend:** Django, Django REST Framework
-   **Frontend:** React
-   **Database:** PostgreSQL (or SQLite for development)

## Getting Started

### Prerequisites

-   Python 3.10+
-   Node.js and npm/yarn
-   A free map API key (e.g., from Mapbox, Google Maps)

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd eld-backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file by copying the example:
    ```bash
    cp .env.example .env
    ```
    Update the `.env` file with your database settings, a Django `SECRET_KEY`, and your map API key.

5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The backend will be available at `http://127.0.0.1:8000`.

### Frontend Setup

(Instructions to be added for the React frontend.)

## API Documentation

The backend provides a RESTful API for managing trips and viewing ELD logs.

### Create a Trip

-   **Endpoint**: `POST /api/trips/`
-   **Description**: Creates a new trip. This will trigger a call to an external service to calculate the route and will generate a basic set of ELD logs.
-   **Request Body**:
    ```json
    {
        "current_location": {"latitude": 40.7128, "longitude": -74.0060},
        "pickup_location": {"latitude": 34.0522, "longitude": -118.2437},
        "dropoff_location": {"latitude": 41.8781, "longitude": -87.6298},
        "current_cycle_used": "25.50"
    }
    ```
-   **Successful Response** (`201 Created`):
    ```json
    {
        "id": 1,
        "current_location": {"latitude": 40.7128, "longitude": -74.0060},
        "pickup_location": {"latitude": 34.0522, "longitude": -118.2437},
        "dropoff_location": {"latitude": 41.8781, "longitude": -87.6298},
        "current_cycle_used": "25.50",
        "route_geometry": { ... }, // GeoJSON LineString
        "route_waypoints": [ ... ], // Array of waypoints
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:00:00Z"
    }
    ```

### List Trips

-   **Endpoint**: `GET /api/trips/`
-   **Description**: Retrieves a list of all created trips.
-   **Successful Response** (`200 OK`):
    ```json
    [
        {
            "id": 1,
            "current_location": {"latitude": 40.7128, "longitude": -74.0060},
            "pickup_location": {"latitude": 34.0522, "longitude": -118.2437},
            // ... other trip fields
        },
        // ... more trips
    ]
    ```

### Retrieve a Trip

-   **Endpoint**: `GET /api/trips/<id>/`
-   **Description**: Retrieves the details of a single trip by its ID.
-   **Successful Response** (`200 OK`):
    ```json
    {
        "id": 1,
        "current_location": {"latitude": 40.7128, "longitude": -74.0060},
        // ... other trip fields
    }
    ```

### List ELD Logs for a Trip

-   **Endpoint**: `GET /api/trips/<trip_id>/logs/`
-   **Description**: Retrieves a list of all ELD log entries for a specific trip.
-   **Successful Response** (`200 OK`):
    ```json
    [
        {
            "id": 1,
            "trip": 1,
            "status": "on_duty",
            "start_time": "2023-10-27T10:00:00Z",
            "end_time": "2023-10-27T11:00:00Z",
            "duration": "01:00:00",
            "comment": "Pickup at origin"
        },
        // ... more log entries
    ]
    ```