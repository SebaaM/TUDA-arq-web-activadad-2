from django.contrib import admin
from django.urls import include, path
from .documentation import api_documentation, redoc, swagger_json, swagger_ui


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-docs/", api_documentation, name="api-documentation"),
    path(
        "swagger/",
        swagger_ui,
        name="schema-swagger-ui",
    ),
    path(
        "swagger.json",
        swagger_json,
        name="schema-json",
    ),
    path(
        "redoc/",
        redoc,
        name="schema-redoc",
    ),
    path("", include("activities.urls")),
]
