from uuid import UUID

from ninja import Router, Header
from ninja.errors import HttpError

from .models import Activity, Participant, Enrollment
from .schemas import ActivityDetailOut, ActivityOut, EnrollmentOut, ParticipantOut

router = Router()

DEMO_PARTICIPANT_HEADER = "X-Participant-ID"


def get_participant(participant_id: str) -> Participant:
    try:
        return Participant.objects.get(id=participant_id)
    except (Participant.DoesNotExist, ValueError):
        raise HttpError(400, "Invalid participant identity")


@router.get("/activities/", response=list[ActivityDetailOut])
def list_activities(request):
    return Activity.objects.order_by("starts_at")


@router.get("/activities/{activity_id}/", response=ActivityDetailOut)
def get_activity(request, activity_id: UUID):
    try:
        return Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        raise HttpError(404, "Activity not found")


@router.get("/participants/", response=list[ParticipantOut])
def list_participants(request):
    return Participant.objects.all()


@router.get("/participants/{participant_id}/", response=ParticipantOut)
def get_participant_detail(request, participant_id: UUID):
    try:
        return Participant.objects.get(id=participant_id)
    except Participant.DoesNotExist:
        raise HttpError(404, "Participant not found")


@router.get("/me/enrollments/", response=list[EnrollmentOut])
def list_enrollments(request, X_Participant_ID: str = Header(...)):
    participant = get_participant(X_Participant_ID)
    return Enrollment.objects.filter(participant=participant)


@router.put(
    "/me/enrollments/{activity_id}/",
    response={201: EnrollmentOut, 200: EnrollmentOut},
)
def enroll(request, activity_id: UUID, X_Participant_ID: str = Header(...)):
    participant = get_participant(X_Participant_ID)

    try:
        activity = Activity.objects.get(id=activity_id)
    except Activity.DoesNotExist:
        raise HttpError(404, "Activity not found")

    existing = Enrollment.objects.filter(
        activity=activity, participant=participant
    ).first()

    if existing is not None:
        other_enrollments = Enrollment.objects.filter(activity=activity).exclude(
            participant=participant
        ).count()
        if other_enrollments >= activity.capacity:
            raise HttpError(409, "Activity capacity exceeded")
        return 200, existing

    enrolled_count = Enrollment.objects.filter(activity=activity).count()
    if enrolled_count >= activity.capacity:
        raise HttpError(409, "Activity capacity exceeded")

    enrollment = Enrollment.objects.create(activity=activity, participant=participant)
    return 201, enrollment


@router.delete("/me/enrollments/{activity_id}/cancel/", response={204: None})
def cancel_enrollment(request, activity_id: UUID, X_Participant_ID: str = Header(...)):
    participant = get_participant(X_Participant_ID)

    if not Activity.objects.filter(id=activity_id).exists():
        raise HttpError(404, "Activity not found")

    try:
        enrollment = Enrollment.objects.get(activity_id=activity_id, participant=participant)
        enrollment.delete()
        return 204, None
    except Enrollment.DoesNotExist:
        raise HttpError(404, "Enrollment not found")
