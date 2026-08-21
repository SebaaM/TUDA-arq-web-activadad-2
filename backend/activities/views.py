from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Activity


@require_GET
def activity_list(request):
    # 405: Django rechaza cualquier método distinto de GET por el decorador.
    activities = Activity.objects.all()
    # 200: devuelve la página HTML con las actividades.
    return render(
        request,
        "activities/activity_list.html",
        {"activities": activities},
    )

