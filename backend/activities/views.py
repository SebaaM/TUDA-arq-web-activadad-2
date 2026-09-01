from typing import Optional

from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import render
from django.views.decorators.http import require_GET
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Activity, Enrollment, Participant
from .serializers import ActivitySerializer, EnrollmentSerializer, ErrorSerializer


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

METHOD_NOT_ALLOWED = OpenApiResponse(description="Método no permitido.")
NO_CONTENT = OpenApiResponse(description="Inscripción cancelada.")


def get_demo_participant(participant_id: Optional[str]) -> Optional[Participant]:
    if not participant_id:
        return None

    try:
        return Participant.objects.get(id=participant_id)
    except (Participant.DoesNotExist, ValidationError, ValueError):
        return None


def error(code: str, message: str, http_status: int) -> Response:
    return Response({"code": code, "message": message}, status=http_status)


def authentication_error() -> Response:
    return error(
        "authentication_required",
        "Se requiere una identidad de participante válida.",
        status.HTTP_401_UNAUTHORIZED,
    )


def activity_not_found_error() -> Response:
    return error(
        "activity_not_found",
        "La actividad no existe.",
        status.HTTP_404_NOT_FOUND,
    )


@require_GET
def activity_list(request):
    activities = Activity.objects.all()
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
            200: ActivitySerializer(many=True),
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request):
        activities = Activity.objects.annotate(
            enrolled_count=Count("enrollment")
        ).order_by("starts_at")
        return Response(ActivitySerializer(activities, many=True).data)


class ActivityDetailView(APIView):
    @extend_schema(
        operation_id="getActivity",
        summary="Obtener una actividad",
        description="Recupera una actividad concreta a partir de su UUID.",
        tags=["Activities"],
        parameters=[ACTIVITY_ID_PARAMETER],
        responses={
            200: ActivitySerializer(),
            404: ErrorSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request, activity_id):
        try:
            activity = Activity.objects.annotate(
                enrolled_count=Count("enrollment")
            ).get(id=activity_id)
        except Activity.DoesNotExist:
            return activity_not_found_error()

        return Response(ActivitySerializer(activity).data)


class ParticipantListView(APIView):
    @extend_schema(
        operation_id="listParticipants",
        summary="Listar participantes",
        tags=["Participants"],
        responses={
            200: ActivitySerializer(many=True),
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request):
        return Response(
            [{"id": str(p.id), "name": p.name} for p in Participant.objects.all()]
        )


class ParticipantDetailView(APIView):
    @extend_schema(
        operation_id="getParticipant",
        summary="Obtener un participante",
        tags=["Participants"],
        parameters=[PARTICIPANT_ID_PARAMETER],
        responses={
            200: ActivitySerializer(),
            404: ErrorSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request, participant_id):
        try:
            participant = Participant.objects.get(id=participant_id)
        except (Participant.DoesNotExist, ValidationError, ValueError):
            return error(
                "participant_not_found",
                "El participante no existe.",
                status.HTTP_404_NOT_FOUND,
            )
        return Response({"id": str(participant.id), "name": participant.name})


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
            200: EnrollmentSerializer(many=True),
            401: ErrorSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def get(self, request):
        participant = get_demo_participant(request.headers.get(DEMO_PARTICIPANT_HEADER))
        if participant is None:
            return authentication_error()

        enrollments = Enrollment.objects.filter(participant=participant)
        return Response(EnrollmentSerializer(enrollments, many=True).data)


class ActivityEnrollmentView(APIView):
    @extend_schema(
        operation_id="putMyEnrollment",
        summary="Inscribirse en una actividad",
        description="Crea la inscripción (201) o devuelve la existente (200) si se repite.",
        tags=["Enrollments"],
        parameters=[ACTIVITY_ID_PARAMETER, PARTICIPANT_HEADER],
        request=None,
        responses={
            200: EnrollmentSerializer,
            201: EnrollmentSerializer,
            401: ErrorSerializer,
            404: ErrorSerializer,
            409: ErrorSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def put(self, request, activity_id):
        participant = get_demo_participant(request.headers.get(DEMO_PARTICIPANT_HEADER))
        if participant is None:
            return authentication_error()

        try:
            activity = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return activity_not_found_error()

        enrollment = Enrollment.objects.filter(
            activity=activity, participant=participant
        ).first()

        if enrollment is not None:
            return Response(EnrollmentSerializer(enrollment).data)

        if Enrollment.objects.filter(activity=activity).count() >= activity.capacity:
            return error(
                "capacity_exhausted",
                "No hay lugares disponibles.",
                status.HTTP_409_CONFLICT,
            )

        enrollment = Enrollment.objects.create(activity=activity, participant=participant)
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        operation_id="deleteMyEnrollment",
        summary="Cancelar mi inscripción",
        description="Elimina la inscripción (204). Una repetición también responde 204.",
        tags=["Enrollments"],
        parameters=[ACTIVITY_ID_PARAMETER, PARTICIPANT_HEADER],
        request=None,
        responses={
            204: NO_CONTENT,
            401: ErrorSerializer,
            404: ErrorSerializer,
            405: METHOD_NOT_ALLOWED,
        },
    )
    def delete(self, request, activity_id):
        participant = get_demo_participant(request.headers.get(DEMO_PARTICIPANT_HEADER))
        if participant is None:
            return authentication_error()

        if not Activity.objects.filter(id=activity_id).exists():
            return activity_not_found_error()

        Enrollment.objects.filter(
            activity_id=activity_id, participant=participant
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
