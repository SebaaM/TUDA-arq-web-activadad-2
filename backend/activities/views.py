from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods
from django.http import JsonResponse
from .representations import serialize_activity, serialize_activities, serialize_enrollments, serialize_enrollment, serialize_participant, serialize_participants
from .models import Activity, Participant, Enrollment


@require_GET
def activity_list(request):
    activities = Activity.objects.all()
    return render(
        request,
        "activities/activity_list.html",
        {"activities": activities},
    )

@require_GET
def activity_api_list(request):
    activities = Activity.objects.all()
    payload = serialize_activities(activities)
    # payload = [serialize_activity(activity) for activity in activities]
    return JsonResponse({"data": payload})

# @require_http_methods(["GET"])
@require_GET
def activities_collection(request):
    activities = Activity.objects.order_by("starts_at")
    payload = [
        {
        "id": str(activity.id),
        "title": activity.title,
        "starts_at": activity.starts_at.isoformat(),
        "capacity": activity.capacity,
        "available_slots": activity.capacity - Enrollment.objects.filter(
        activity=activity
        ).count(),
        }
    for activity in activities
    ]
    return JsonResponse(payload, safe=False)

@require_GET
def activity_api_detail(request, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        return JsonResponse({"error": "Activity not found"}, status=404)

    payload = serialize_activity(activity)
    return JsonResponse({"data": payload})

@require_GET
def participant_api_list(request):
    try:
        participants = Participant.objects.all()
        payload = serialize_participants(participants=participants)
        return JsonResponse({
            "data": payload,
            "error": None
        }, status=200)

    except ObjectDoesNotExist as e:
        return JsonResponse({
            "data": None,
            "error": str(e)
        }, status=404)

    except ValidationError as e:
        return JsonResponse({
            "data": None,
            "error": e.message_dict if hasattr(e, "message_dict") else str(e)
        }, status=400)

    except Exception as e:
        # Error inesperado
        return JsonResponse({
            "data": None,
            "error": "Internal server error: " + str(e)
        }, status=500)

@require_GET
def participant_api_detail(request, participant_id):
    try:
        participant = Participant.objects.get(id=participant_id)
        payload = serialize_participant(participant) 
        return JsonResponse({
            "data": payload,
            "error": None
        }, status=200)

    except Participant.DoesNotExist:
        return JsonResponse({
            "data": None,
            "error": "Participant not found"
        }, status=404)

    except Exception as e:
        # Error inesperado
        return JsonResponse({
            "data": None,
            "error": "Internal server error: " + str(e)
        }, status=500)   

@require_GET
def enrollment_api_list(request):
    try:
        enrollments = Enrollment.objects.all()
        payload = serialize_enrollments(enrollments=enrollments)
        return JsonResponse({
            "data": payload,
            "error": None
        }, status=200)

    except ObjectDoesNotExist as e:
        return JsonResponse({
            "data": None,
            "error": str(e)
        }, status=404)

    except ValidationError as e:
        return JsonResponse({
            "data": None,
            "error": e.message_dict if hasattr(e, "message_dict") else str(e)
        }, status=400)

    except Exception as e:
        # Error inesperado
        return JsonResponse({
            "data": None,
            "error": "Internal server error: " + str(e)
        }, status=500)
        
@require_GET
def enrollment_api_detail(request, activity_id, participant_id):
    try:
        enrollment = Enrollment.objects.get(activity_id=activity_id, participant_id=participant_id)
        payload = serialize_enrollment(enrollment) 
        
        
        return JsonResponse({
            "data": payload,
            "error": None
        }, status=200)

    except Enrollment.DoesNotExist:
        return JsonResponse({
            "data": None,
            "error": "Enrollment not found"
        }, status=404)

    except Exception as e:
        # Error inesperado
        return JsonResponse({
            "data": None,
            "error": "Internal server error: " + str(e)
        }, status=500)
        
@require_http_methods(["PUT"])
def activity_enrollment_api_put(request, activity_id, participant_id):
    #inscribe a un participante en una actividad si hay cupo disponible.
    try:
        activity = Activity.objects.get(id=activity_id)
        enrollment = Enrollment.objects.get(activity_id=activity_id, participant_id=participant_id)

        enrolled_count = Enrollment.objects.filter(activity=activity).exclude(
            activity_id=activity_id,
            participant_id=participant_id,
        ).count()
        if enrolled_count >= activity.capacity:
            return JsonResponse({
                "data": None,
                "error": "Activity capacity exceeded"
            }, status=409)

        payload = serialize_enrollment(enrollment) 
        return JsonResponse({
            "data": payload,
            "error": None
        }, status=200)

    except Enrollment.DoesNotExist:
        return JsonResponse({
            "data": None,
            "error": "Enrollment not found"
        }, status=404)

    except Activity.DoesNotExist:
        return JsonResponse({
            "data": None,
            "error": "Activity not found"
        }, status=404)

    except Exception as e:
        # Error inesperado
        return JsonResponse({
            "data": None,
            "error": "Internal server error: " + str(e)
        }, status=500)    


@require_http_methods(["DELETE"])
def activity_enrollment_api_delete(request, activity_id, participant_id):
    #elimina la inscripción de un participante en una actividad.
    try:
        enrollment = Enrollment.objects.get(activity_id=activity_id, participant_id=participant_id)
        enrollment.delete()
        return JsonResponse({
            "data": None,
            "error": None
        }, status=204)

    except Enrollment.DoesNotExist:
        return JsonResponse({
            "data": None,
            "error": "Enrollment not found"
        }, status=404)
        
        

    except Exception as e:
        # Error inesperado
        return JsonResponse({
            "data": None,
            "error": "Internal server error: " + str(e)
        }, status=500)

