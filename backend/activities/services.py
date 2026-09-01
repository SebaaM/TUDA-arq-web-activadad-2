from typing import Optional, Tuple

from django.core.exceptions import ValidationError
from django.db.models import Count

from .models import Activity, Enrollment, Participant


class ActivityNotFoundError(Exception):
    pass


class CapacityExhaustedError(Exception):
    pass


def get_demo_participant(participant_id: Optional[str]) -> Optional[Participant]:
    if not participant_id:
        return None

    try:
        return Participant.objects.get(id=participant_id)
    except (Participant.DoesNotExist, ValidationError, ValueError):
        return None


def get_activities_with_availability():
    return Activity.objects.annotate(
        enrolled_count=Count("enrollment")
    ).order_by("starts_at")


def get_activity_or_404(activity_id) -> Activity:
    try:
        return Activity.objects.annotate(
            enrolled_count=Count("enrollment")
        ).get(id=activity_id)
    except (Activity.DoesNotExist, ValidationError, ValueError):
        raise ActivityNotFoundError() from None


def activity_exists(activity_id) -> bool:
    return Activity.objects.filter(id=activity_id).exists()


def create_or_get_enrollment(
    activity, participant
) -> Tuple[Enrollment, bool]:
    enrollment = Enrollment.objects.filter(
        activity=activity, participant=participant
    ).first()

    if enrollment is not None:
        return enrollment, False

    if Enrollment.objects.filter(activity=activity).count() >= activity.capacity:
        raise CapacityExhaustedError()

    return Enrollment.objects.create(activity=activity, participant=participant), True


def delete_enrollment_if_exists(activity, participant) -> None:
    Enrollment.objects.filter(
        activity=activity, participant=participant
    ).delete()