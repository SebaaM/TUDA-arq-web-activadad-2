from django.urls import path

from . import views
from .api import api


app_name = "activities"

urlpatterns = [
    path("", views.activity_list, name="list"),
    # Se incorporan los patrones de Ninja directamente para conservar el
    # namespace ``activities`` y los nombres de URL ya utilizados en pruebas.
    *api.urls[0],
]
