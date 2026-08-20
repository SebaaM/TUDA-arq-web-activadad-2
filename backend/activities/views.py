from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods
from django.http import HttpResponse, JsonResponse
from .representations import serialize_activity, serialize_activities, serialize_enrollments, serialize_enrollment, serialize_participant, serialize_participants
from .models import Activity, Participant, Enrollment


# constante para el nombre del header HTTP que identifica al participante de prueba.
DEMO_PARTICIPANT_HEADER = "X-Participant-ID"


# se usa para obtener el participante de prueba a partir del header HTTP.
def get_demo_participant(request):
    participant_id = request.headers.get(DEMO_PARTICIPANT_HEADER)
    if not participant_id:
        return None

    try:
        return Participant.objects.get(id=participant_id)
    except (Participant.DoesNotExist, ValueError):
        return None


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

@require_GET
def activity_api_list(request):
    # 405: sólo se permite consultar esta colección mediante GET.
    activities = Activity.objects.all()
    payload = serialize_activities(activities)
    # payload = [serialize_activity(activity) for activity in activities]
    # 200: devuelve las actividades dentro de la clave data.
    return JsonResponse({"data": payload})

# @require_http_methods(["GET"])
@require_GET
def activities_collection(request):
    # 405: @require_GET rechaza cualquier método distinto de GET.
    activities = Activity.objects.order_by("starts_at")
    payload = []

    for activity in activities:
        activity_data = serialize_activity(activity)
        activity_data["available_slots"] = activity.capacity - Enrollment.objects.filter(
            activity=activity,
        ).count()
        payload.append(activity_data)

    # 200: mantiene el contrato JSON común {data, error} para las colecciones.
    return JsonResponse({
        "data": payload,
        "error": None,
    }, status=200)

@require_GET
def activity_api_detail(request, activity_id):
    # 405: este endpoint sólo acepta GET.
    try:
        activity = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        # 404: el UUID no corresponde a una actividad persistida.
        return JsonResponse({"error": "Activity not found"}, status=404)

    payload = serialize_activity(activity)
    payload["available_slots"] = activity.capacity - Enrollment.objects.filter(
        activity=activity,
    ).count()
    # 200: devuelve la actividad y sus cupos disponibles.
    return JsonResponse({"data": payload})

@require_GET
def participant_api_list(request):
    # 405: sólo se permite GET para listar participantes.
    try:
        participants = Participant.objects.all()
        payload = serialize_participants(participants=participants)
        # 200: listado de participantes obtenido correctamente.
        return JsonResponse({
            "data": payload,
            "error": None
        }, status=200)

    except ObjectDoesNotExist as e:
        # 404: no se encontró el recurso solicitado.
        return JsonResponse({
            "data": None,
            "error": str(e)
        }, status=404)

    except ValidationError as e:
        # 400: los datos no cumplen las validaciones del modelo.
        return JsonResponse({
            "data": None,
            "error": e.message_dict if hasattr(e, "message_dict") else str(e)
        }, status=400)

    except Exception as e:
        # Error inesperado
        # 500: error no previsto al consultar la colección.
        return JsonResponse({
            "data": None,
            "error": "Internal server error: " + str(e)
        }, status=500)

@require_GET
def participant_api_detail(request, participant_id):
    # 405: este endpoint sólo acepta GET.
    try:
        participant = Participant.objects.get(id=participant_id)
        payload = serialize_participant(participant) 
        # 200: participante encontrado y serializado.
        return JsonResponse({
            "data": payload,
            "error": None
        }, status=200)

    except Participant.DoesNotExist:
        # 404: el UUID no corresponde a un participante.
        return JsonResponse({
            "data": None,
            "error": "Participant not found"
        }, status=404)

    except Exception as e:
        # Error inesperado
        # 500: fallo no previsto al consultar el participante.
        return JsonResponse({
            "data": None,
            "error": "Internal server error: " + str(e)
        }, status=500)   

@require_GET
def enrollment_api_list(request):
    # 405: sólo se permite GET para consultar las inscripciones propias.
    participant = get_demo_participant(request)
    if participant is None:
        # 400: falta el header o no identifica a un participante válido.
        return JsonResponse({
            "data": None,
            "error": "Invalid participant identity"
        }, status=400)

    # /me sólo debe exponer las inscripciones del participante identificado.
    enrollments = Enrollment.objects.filter(participant=participant)
    payload = serialize_enrollments(enrollments=enrollments)
    # 200: devuelve las inscripciones del participante identificado.
    return JsonResponse({
        "data": payload,
        "error": None
    }, status=200)
        
@require_GET
def enrollment_api_detail(request, activity_id, participant_id):
    # 405: este endpoint sólo acepta GET.
    try:
        enrollment = Enrollment.objects.get(activity_id=activity_id, participant_id=participant_id)
        payload = serialize_enrollment(enrollment) 
        
        
        # 200: inscripción encontrada y serializada.
        return JsonResponse({
            "data": payload,
            "error": None
        }, status=200)

    except Enrollment.DoesNotExist:
        # 404: no existe la relación entre actividad y participante.
        return JsonResponse({
            "data": None,
            "error": "Enrollment not found"
        }, status=404)

    except Exception as e:
        # Error inesperado
        # 500: fallo no previsto al consultar la inscripción.
        return JsonResponse({
            "data": None,
            "error": "Internal server error: " + str(e)
        }, status=500)
        
@require_http_methods(["PUT"])
def activity_enrollment_api_put(request, activity_id):
    # 405: el decorador rechaza métodos distintos de PUT.
    # PUT es idempotente: repetir la petición no debe crear duplicados.
    participant = get_demo_participant(request)
    if participant is None:
        # 400: falta el header o no identifica a un participante válido.
        return JsonResponse({
            "data": None,
            "error": "Invalid participant identity"
        }, status=400)

    try:
        activity = Activity.objects.get(id=activity_id)
        enrollment = Enrollment.objects.filter(
            activity=activity,
            participant=participant,
        ).first()

        if enrollment is not None:
            # Una inscripción existente se devuelve sin crear otra fila.
            other_enrollments = Enrollment.objects.filter(activity=activity).exclude(
                participant=participant,
            ).count()
            if other_enrollments >= activity.capacity:
                # 409: la capacidad está agotada por otros participantes.
                return JsonResponse({
                    "data": None,
                    "error": "Activity capacity exceeded"
                }, status=409)

            # 200: la inscripción ya existía y se devuelve sin duplicarla.
            return JsonResponse({
                "data": serialize_enrollment(enrollment),
                "error": None
            }, status=200)

        # La disponibilidad se calcula contando las inscripciones persistidas.
        enrolled_count = Enrollment.objects.filter(activity=activity).count()
        if enrolled_count >= activity.capacity:
            # 409: no quedan cupos para crear la inscripción.
            return JsonResponse({
                "data": None,
                "error": "Activity capacity exceeded"
            }, status=409)

        # El modelo se modifica sólo después de validar el cupo disponible.
        enrollment = Enrollment.objects.create(
            activity=activity,
            participant=participant,
        )
        payload = serialize_enrollment(enrollment)
        # 201: se creó una nueva fila en Enrollment.
        return JsonResponse({
            "data": payload,
            "error": None
        }, status=201)

    except Activity.DoesNotExist:
        # 404: el UUID no corresponde a una actividad.
        return JsonResponse({
            "data": None,
            "error": "Activity not found"
        }, status=404)

    except Exception as e:
        # Error inesperado
        # 500: fallo no previsto durante la inscripción.
        return JsonResponse({
            "data": None,
            "error": "Internal server error: " + str(e)
        }, status=500)    


@require_http_methods(["DELETE"])
def activity_enrollment_api_delete(request, activity_id):
    # 405: el decorador rechaza métodos distintos de DELETE.
    # Primero se diferencia una actividad inexistente de una inscripción ausente.
    participant = get_demo_participant(request)
    if participant is None:
        # 400: falta el header o no identifica a un participante válido.
        return JsonResponse({
            "data": None,
            "error": "Invalid participant identity"
        }, status=400)

    if not Activity.objects.filter(id=activity_id).exists():
        # 404: el UUID no corresponde a una actividad.
        return JsonResponse({
            "data": None,
            "error": "Activity not found"
        }, status=404)

    try:
        enrollment = Enrollment.objects.get(
            activity_id=activity_id,
            participant=participant,
        )
        enrollment.delete()
        # DELETE exitoso no devuelve representación, sólo confirma la baja.
        # 204: la inscripción fue eliminada correctamente y no hay body.
        return HttpResponse(status=204)

    except Enrollment.DoesNotExist:
        # 404: no existe la inscripción que se quiere cancelar.
        return JsonResponse({
            "data": None,
            "error": "Enrollment not found"
        }, status=404)
        
        

    except Exception as e:
        # Error inesperado
        # 500: fallo no previsto durante la cancelación.
        return JsonResponse({
            "data": None,
            "error": "Internal server error: " + str(e)
        }, status=500)

