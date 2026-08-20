from django.contrib import admin
from django.urls import include, path
from ninja import NinjaAPI

from activities.api import router as activities_router

api = NinjaAPI(
    title="TUDA Activities API",
    version="v1",
    description="API para consultar actividades, participantes e inscripciones.",
)

api.add_router("v1", activities_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("", include("activities.urls")),
]
