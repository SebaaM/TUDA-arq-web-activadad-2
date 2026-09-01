from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("activities.urls")),
    path(
        "api/openapi.json",
        SpectacularJSONAPIView.as_view(),
        name="api-schema",
    ),
    path(
        "api/v1/openapi.json",
        SpectacularJSONAPIView.as_view(),
        name="api-schema-v1",
    ),
    path(
        "api/docs",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
]
