"""Endpoints HTTP de la API de actividades implementados con Django Ninja."""

from typing import Any, Optional
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from ninja import Header, NinjaAPI, Schema

from .models import Activity, Enrollment, Participant
from .representations import (
    serialize_activity,
    serialize_enrollment,
    serialize_enrollments,
    serialize_participant,
    serialize_participants,
)


DEMO_PARTICIPANT_HEADER = "X-Participant-ID"


class ActivityData(Schema):
    id: UUID
    title: str
    starts_at: str
    capacity: int


class ActivityDetailData(ActivityData):
    available_slots: int


class ParticipantData(Schema):
    id: UUID
    name: str


class EnrollmentData(Schema):
    participant: ParticipantData
    activity: ActivityData
    enrolled_at: str


class ActivitiesResponse(Schema):
    data: list[ActivityDetailData]
    error: None = None


class ActivityResponse(Schema):
    data: ActivityDetailData


class ParticipantsResponse(Schema):
    data: list[ParticipantData]
    error: None = None


class ParticipantResponse(Schema):
    data: ParticipantData
    error: None = None


class EnrollmentsResponse(Schema):
    data: list[EnrollmentData]
    error: None = None


class EnrollmentResponse(Schema):
    data: EnrollmentData
    error: None = None


class ErrorResponse(Schema):
    data: None = None
    error: str | dict[str, Any]


class MessageResponse(Schema):
    error: str


api = NinjaAPI(
    title="TUDA Activities API",
    version="v1",
    description="API para consultar actividades, participantes e inscripciones.",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    urls_namespace="activities",
)


def get_demo_participant(participant_id: Optional[str]) -> Optional[Participant]:
    """Obtiene el participante de prueba sin alterar el contrato de errores."""
    if not participant_id:
        # La ausencia del header se trata igual que una identidad inválida para
        # evitar revelar datos o permitir operaciones sin participante.
        return None

    try:
        return Participant.objects.get(id=participant_id)
    except (Participant.DoesNotExist, ValidationError, ValueError):
        # El UUID puede estar mal formado o no corresponder a un participante;
        # ambos casos se convierten en la respuesta 400 del endpoint consumidor.
        return None


def serialize_activity_detail(activity: Activity) -> dict:
    # El cupo se calcula al consultar para que la respuesta refleje las
    # inscripciones actuales, incluida la actividad sin inscripciones.
    payload = serialize_activity(activity)
    payload["available_slots"] = activity.capacity - Enrollment.objects.filter(
        activity=activity
    ).count()
    return payload


@api.get(
    "/api/v1/activities/",
    response={200: ActivitiesResponse},
    tags=["Activities"],
    summary="Listar actividades",
    url_name="api-activity-list",
)
def activities_collection(request):
    # GET es safe (solo lectura) e idempotente: repetirlo no modifica datos.
    activities = Activity.objects.order_by("starts_at")
    return 200, {
        "data": [serialize_activity_detail(activity) for activity in activities],
        "error": None,
    }


@api.get(
    "/api/v1/activities/{uuid:activity_id}/",
    response={200: ActivityResponse, 404: MessageResponse},
    tags=["Activities"],
    summary="Obtener una actividad",
    url_name="api-activity-detail",
)
def activity_api_detail(request, activity_id: UUID):
    # GET es safe e idempotente. Un UUID válido sin coincidencia produce 404;
    # la conversión del parámetro inválido la resuelve Django Ninja.
    try:
        activity = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        return 404, {"error": "Activity not found"}

    return 200, {"data": serialize_activity_detail(activity)}


@api.get(
    "/api/v1/participants/",
    response={200: ParticipantsResponse, 400: ErrorResponse, 404: ErrorResponse, 500: ErrorResponse},
    tags=["Participants"],
    summary="Listar participantes",
    url_name="api-participant-list",
)
def participant_api_list(request):
    # GET es safe e idempotente. Se conservan respuestas diferenciadas para
    # errores de validación/consulta (400/404) y fallos no previstos (500).
    try:
        return 200, {"data": serialize_participants(Participant.objects.all()), "error": None}
    except ObjectDoesNotExist as exc:
        return 404, {"data": None, "error": str(exc)}
    except ValidationError as exc:
        error = exc.message_dict if hasattr(exc, "message_dict") else str(exc)
        return 400, {"data": None, "error": error}
    except Exception as exc:
        return 500, {"data": None, "error": "Internal server error: " + str(exc)}


@api.get(
    "/api/v1/participants/{uuid:participant_id}/",
    response={200: ParticipantResponse, 404: ErrorResponse, 500: ErrorResponse},
    tags=["Participants"],
    summary="Obtener un participante",
    url_name="api-participant-detail",
)
def participant_api_detail(request, participant_id: UUID):
    # GET es safe e idempotente. La ausencia del participante es 404 y una
    # excepción inesperada se informa como 500 sin cambiar el recurso.
    try:
        participant = Participant.objects.get(id=participant_id)
        return 200, {"data": serialize_participant(participant), "error": None}
    except Participant.DoesNotExist:
        return 404, {"data": None, "error": "Participant not found"}
    except Exception as exc:
        return 500, {"data": None, "error": "Internal server error: " + str(exc)}


@api.get(
    "/api/v1/me/enrollments/",
    response={200: EnrollmentsResponse, 400: ErrorResponse},
    tags=["Enrollments"],
    summary="Listar mis inscripciones",
    url_name="api-enrollment-list",
)
def enrollment_api_list(
    request, x_participant_id: Optional[str] = Header(None, alias=DEMO_PARTICIPANT_HEADER)
):
    # GET es safe e idempotente: solo consulta las inscripciones de la
    # identidad indicada. Sin header o con header inválido se responde 400.
    participant = get_demo_participant(x_participant_id)
    if participant is None:
        return 400, {"data": None, "error": "Invalid participant identity"}

    enrollments = Enrollment.objects.filter(participant=participant)
    return 200, {"data": serialize_enrollments(enrollments), "error": None}


@api.get(
    "/api/v1/me/enrollments/{int:id}/",
    response={200: EnrollmentResponse, 404: ErrorResponse, 500: ErrorResponse},
    tags=["Enrollments"],
    summary="Obtener una inscripción",
    url_name="api-enrollment-detail",
)
def enrollment_api_detail(request, id: int):
    # GET es safe e idempotente. El identificador inexistente se responde con
    # 404 y no se permite que una excepción de consulta llegue al cliente.
    try:
        enrollment = Enrollment.objects.get(id=id)
        return 200, {"data": serialize_enrollment(enrollment), "error": None}
    except Enrollment.DoesNotExist:
        return 404, {"data": None, "error": "Enrollment not found"}
    except Exception as exc:
        return 500, {"data": None, "error": "Internal server error: " + str(exc)}


@api.put(
    "/api/v1/me/enrollments/{uuid:activity_id}/",
    response={200: EnrollmentResponse, 201: EnrollmentResponse, 400: ErrorResponse, 404: ErrorResponse, 409: ErrorResponse, 500: ErrorResponse},
    tags=["Enrollments"],
    summary="Inscribirse en una actividad",
    url_name="api-enrollment-confirm",
)
def activity_enrollment_api_put(
    request,
    activity_id: UUID,
    x_participant_id: Optional[str] = Header(None, alias=DEMO_PARTICIPANT_HEADER),
):
    # PUT no es safe porque puede crear una inscripción, pero es idempotente en
    # repeticiones secuenciales: devuelve la inscripción existente en vez de
    # crear otra. La identidad inválida siempre es 400; la concurrencia no se
    # serializa aquí y requeriría una transacción para una garantía más fuerte.
    participant = get_demo_participant(x_participant_id)
    if participant is None:
        return 400, {"data": None, "error": "Invalid participant identity"}

    try:
        activity = Activity.objects.get(id=activity_id)
        enrollment = Enrollment.objects.filter(
            activity=activity, participant=participant
        ).first()

        if enrollment is not None:
            # La restricción única del modelo garantiza una inscripción por
            # pareja. Si el estado ya estaba sobrecapacidad, se informa 409.
            other_enrollments = Enrollment.objects.filter(activity=activity).exclude(
                participant=participant
            ).count()
            if other_enrollments >= activity.capacity:
                return 409, {"data": None, "error": "Activity capacity exceeded"}
            return 200, {"data": serialize_enrollment(enrollment), "error": None}

        # Se verifica el cupo antes de insertar; una actividad completa no
        # acepta nuevas inscripciones y conserva su estado sin cambios.
        if Enrollment.objects.filter(activity=activity).count() >= activity.capacity:
            return 409, {"data": None, "error": "Activity capacity exceeded"}

        enrollment = Enrollment.objects.create(activity=activity, participant=participant)
        # La primera solicitud crea el recurso y devuelve su representación.
        return 201, {"data": serialize_enrollment(enrollment), "error": None}
    except Activity.DoesNotExist:
        return 404, {"data": None, "error": "Activity not found"}
    except Exception as exc:
        return 500, {"data": None, "error": "Internal server error: " + str(exc)}


@api.delete(
    "/api/v1/me/enrollments/{uuid:activity_id}/cancel/",
    response={204: None, 400: ErrorResponse, 404: ErrorResponse, 500: ErrorResponse},
    tags=["Enrollments"],
    summary="Cancelar mi inscripción",
    url_name="api-enrollment-cancel",
)
def activity_enrollment_api_delete(
    request,
    activity_id: UUID,
    x_participant_id: Optional[str] = Header(None, alias=DEMO_PARTICIPANT_HEADER),
):
    # DELETE no es safe porque modifica el estado, pero es idempotente respecto
    # del estado final: la inscripción queda eliminada tras la primera llamada.
    # Una repetición sin inscripción se informa 404 para hacer visible el estado.
    participant = get_demo_participant(x_participant_id)
    if participant is None:
        return 400, {"data": None, "error": "Invalid participant identity"}

    if not Activity.objects.filter(id=activity_id).exists():
        return 404, {"data": None, "error": "Activity not found"}

    try:
        enrollment = Enrollment.objects.get(activity_id=activity_id, participant=participant)
        enrollment.delete()
        # 204 confirma que la eliminación se realizó sin cuerpo de respuesta.
        return 204, None
    except Enrollment.DoesNotExist:
        return 404, {"data": None, "error": "Enrollment not found"}
    except Exception as exc:
        return 500, {"data": None, "error": "Internal server error: " + str(exc)}
