from django.urls import include, path

from . import views


app_name = "activities"

urlpatterns = [
    path("", views.activity_list, name="list"),
    path("", include("activities.api_urls")),
]
