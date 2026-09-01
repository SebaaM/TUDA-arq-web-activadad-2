from typing import Any, Optional

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count
from django.shortcuts import render
from django.views.decorators.http import require_GET
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Activity, Enrollment, Participant
from .serializers import (
    ActivitiesResponseSerializer,
    ActivityDetailSerializer,
    ActivityResponseSerializer,
    EnrollmentResponseSerializer,
    EnrollmentSerializer,
    EnrollmentsResponseSerializer,
    ErrorResponseSerializer,
    MessageResponseSerializer,
    ParticipantResponseSerializer,
    ParticipantSerializer,
    ParticipantsResponseSerializer,
)


DEMO_PARTICIPANT_HEADER = "X-Participant-ID"

PARTICIPANT_HEADER = OpenApiParameter(
    name=DEMO_PARTICIPANT_HEADER,
    type=str,
    location=OpenApiParameter.HEADER,
    required=True,
    description=(
        "UUID del participante de demostración. Se usa como identidad de "
        "laboratorio; no es autenticación real."
    ),
)
ACTIVITY_ID_PARAMETER = OpenApiParameter(
    name="activity_id",
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.PATH,
    required=True,
    description="Identificador único de la actividad.",
)
PARTICIPANT_ID_PARAMETER = OpenApiParameter(
    name="participant_id",
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.PATH,
    required=True,
    description="Identificador único del participante.",
)
ENROLLMENT_ID_PARAMETER = OpenApiParameter(
    name="id",
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    required=True,
    description="Identificador numérico de la inscripción.",
)

METHOD_NOT_ALLOWED = OpenApiResponse(description="Método no permitido.")
NO_CONTENT = OpenApiResponse(description="Inscripción cancelada.")


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


def ok(data: Any, *, http_status: int = status.HTTP_200_OK, include_error: bool = True) -> Response:
    payload = {"data": data}
    if include_error:
        payload["error"] = None
    return Response(payload, status=http_status)


def error(message: Any, http_status: int, *, include_data: bool = True) -> Response:
    payload: dict[str, Any] = {"error": message}
    if include_data:
        payload["data"] = None
    return Response(payload, status=http_status)


def activity_detail_payload(activity: Activity) -> dict:
    return ActivityDetailSerializer(activity).data


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


class ActivityListView(APIView):
    @extend_schema(
        operation_id="listActivities",
        summary="Listar actividades",
        description="Devuelve todas las actividades ordenadas por fecha de inicio, con cupos disponibles.",
        tags=["Activities"],
        responses={
            200: ActivitiesResponseSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request):
        # GET es safe (solo lectura) e idempotente: repetirlo no modifica datos.
        activities = Activity.objects.annotate(
            enrolled_count=Count("enrollment")
        ).order_by("starts_at")
        return ok(ActivityDetailSerializer(activities, many=True).data)


class ActivityDetailView(APIView):
    @extend_schema(
        operation_id="getActivity",
        summary="Obtener una actividad",
        description="Recupera una actividad concreta a partir de su UUID.",
        tags=["Activities"],
        parameters=[ACTIVITY_ID_PARAMETER],
        responses={
            200: ActivityResponseSerializer,
            404: MessageResponseSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request, activity_id):
        # GET es safe e idempotente. Un UUID válido sin coincidencia produce 404.
        try:
            activity = Activity.objects.annotate(
                enrolled_count=Count("enrollment")
            ).get(id=activity_id)
        except Activity.DoesNotExist:
            return error(
                "Activity not found",
                status.HTTP_404_NOT_FOUND,
                include_data=False,
            )

        return ok(activity_detail_payload(activity), include_error=False)


class ParticipantListView(APIView):
    @extend_schema(
        operation_id="listParticipants",
        summary="Listar participantes",
        tags=["Participants"],
        responses={
            200: ParticipantsResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request):
        # GET es safe e idempotente. Se conservan respuestas diferenciadas para
        # errores de validación/consulta (400/404) y fallos no previstos (500).
        try:
            return ok(ParticipantSerializer(Participant.objects.all(), many=True).data)
        except ObjectDoesNotExist as exc:
            return error(str(exc), status.HTTP_404_NOT_FOUND)
        except ValidationError as exc:
            message = exc.message_dict if hasattr(exc, "message_dict") else str(exc)
            return error(message, status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return error(
                "Internal server error: " + str(exc),
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ParticipantDetailView(APIView):
    @extend_schema(
        operation_id="getParticipant",
        summary="Obtener un participante",
        tags=["Participants"],
        parameters=[PARTICIPANT_ID_PARAMETER],
        responses={
            200: ParticipantResponseSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request, participant_id):
        # GET es safe e idempotente. La ausencia del participante es 404 y una
        # excepción inesperada se informa como 500 sin cambiar el recurso.
        try:
            participant = Participant.objects.get(id=participant_id)
            return ok(ParticipantSerializer(participant).data)
        except Participant.DoesNotExist:
            return error("Participant not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error(
                "Internal server error: " + str(exc),
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EnrollmentListView(APIView):
    @extend_schema(
        operation_id="listMyEnrollments",
        summary="Listar mis inscripciones",
        description=(
            "Lista las inscripciones del participante indicado por "
            "X-Participant-ID."
        ),
        tags=["Enrollments"],
        parameters=[PARTICIPANT_HEADER],
        responses={
            200: EnrollmentsResponseSerializer,
            400: ErrorResponseSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request):
        # GET es safe e idempotente: solo consulta las inscripciones de la
        # identidad indicada. Sin header o con header inválido se responde 400.
        participant = get_demo_participant(request.headers.get(DEMO_PARTICIPANT_HEADER))
        if participant is None:
            return error("Invalid participant identity", status.HTTP_400_BAD_REQUEST)

        enrollments = Enrollment.objects.filter(participant=participant)
        return ok(EnrollmentSerializer(enrollments, many=True).data)


class EnrollmentDetailView(APIView):
    @extend_schema(
        operation_id="getEnrollment",
        summary="Obtener una inscripción",
        tags=["Enrollments"],
        parameters=[ENROLLMENT_ID_PARAMETER],
        responses={
            200: EnrollmentResponseSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request, id):
        # GET es safe e idempotente. El identificador inexistente se responde con
        # 404 y no se permite que una excepción de consulta llegue al cliente.
        try:
            enrollment = Enrollment.objects.get(id=id)
            return ok(EnrollmentSerializer(enrollment).data)
        except Enrollment.DoesNotExist:
            return error("Enrollment not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error(
                "Internal server error: " + str(exc),
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EnrollmentConfirmView(APIView):
    @extend_schema(
        operation_id="putMyEnrollment",
        summary="Inscribirse en una actividad",
        description=(
            "Crea o confirma una inscripción sin body. Responde 201 si la crea "
            "y 200 con la inscripción existente si se repite el mismo PUT."
        ),
        tags=["Enrollments"],
        parameters=[ACTIVITY_ID_PARAMETER, PARTICIPANT_HEADER],
        request=None,
        responses={
            200: EnrollmentResponseSerializer,
            201: EnrollmentResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            409: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def put(self, request, activity_id):
        # PUT no es safe porque puede crear una inscripción, pero es idempotente en
        # repeticiones secuenciales: devuelve la inscripción existente en vez de
        # crear otra. La identidad inválida siempre es 400; la concurrencia no se
        # serializa aquí y requeriría una transacción para una garantía más fuerte.
        participant = get_demo_participant(request.headers.get(DEMO_PARTICIPANT_HEADER))
        if participant is None:
            return error("Invalid participant identity", status.HTTP_400_BAD_REQUEST)

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
                    return error(
                        "Activity capacity exceeded",
                        status.HTTP_409_CONFLICT,
                    )
                return ok(EnrollmentSerializer(enrollment).data)

            # Se verifica el cupo antes de insertar; una actividad completa no
            # acepta nuevas inscripciones y conserva su estado sin cambios.
            if Enrollment.objects.filter(activity=activity).count() >= activity.capacity:
                return error("Activity capacity exceeded", status.HTTP_409_CONFLICT)

            enrollment = Enrollment.objects.create(
                activity=activity, participant=participant
            )
            # La primera solicitud crea el recurso y devuelve su representación.
            return ok(
                EnrollmentSerializer(enrollment).data,
                http_status=status.HTTP_201_CREATED,
            )
        except Activity.DoesNotExist:
            return error("Activity not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error(
                "Internal server error: " + str(exc),
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EnrollmentCancelView(APIView):
    @extend_schema(
        operation_id="deleteMyEnrollment",
        summary="Cancelar mi inscripción",
        description=(
            "Elimina la inscripción del participante. La primera llamada "
            "responde 204; una repetición sin inscripción se informa 404."
        ),
        tags=["Enrollments"],
        parameters=[ACTIVITY_ID_PARAMETER, PARTICIPANT_HEADER],
        request=None,
        responses={
            204: NO_CONTENT,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def delete(self, request, activity_id):
        # DELETE no es safe porque modifica el estado, pero es idempotente respecto
        # del estado final: la inscripción queda eliminada tras la primera llamada.
        # Una repetición sin inscripción se informa 404 para hacer visible el estado.
        participant = get_demo_participant(request.headers.get(DEMO_PARTICIPANT_HEADER))
        if participant is None:
            return error("Invalid participant identity", status.HTTP_400_BAD_REQUEST)

        if not Activity.objects.filter(id=activity_id).exists():
            return error("Activity not found", status.HTTP_404_NOT_FOUND)

        try:
            enrollment = Enrollment.objects.get(
                activity_id=activity_id, participant=participant
            )
            enrollment.delete()
            # 204 confirma que la eliminación se realizó sin cuerpo de respuesta.
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Enrollment.DoesNotExist:
            return error("Enrollment not found", status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return error(
                "Internal server error: " + str(exc),
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
