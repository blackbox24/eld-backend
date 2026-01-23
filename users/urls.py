from django.urls import path

from . import views

urlpatterns = [
    path("", views.get_users, name="all_users"),
    path("<int:id>/", views.get_single_user, name="single_user"),
]
