from django.urls import path

from .views import (
    ELDLogListAPIView,
    TripListCreateAPIView,
    TripRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    path("trips/", TripListCreateAPIView.as_view(), name="trip-list-create"),
    path(
        "trips/<int:pk>/",
        TripRetrieveUpdateDestroyAPIView.as_view(),
        name="trip-retrieve-update-destroy",
    ),
    path("trips/<int:trip_pk>/logs/", ELDLogListAPIView.as_view(), name="eld-log-list"),
]
