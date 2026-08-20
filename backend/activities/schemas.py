from datetime import datetime
from typing import Optional
from uuid import UUID

from django.utils import timezone
from ninja import Schema


class ParticipantOut(Schema):
    id: UUID
    name: str


class ActivityOut(Schema):
    id: UUID
    title: str
    starts_at: datetime
    capacity: int

    @staticmethod
    def resolve_starts_at(obj):
        return timezone.localtime(obj.starts_at).isoformat()


class ActivityDetailOut(ActivityOut):
    available_slots: int

    @staticmethod
    def resolve_available_slots(obj):
        from .models import Enrollment

        return obj.capacity - Enrollment.objects.filter(activity=obj).count()


class EnrollmentOut(Schema):
    participant: ParticipantOut
    activity: ActivityDetailOut
    enrolled_at: datetime

    @staticmethod
    def resolve_enrolled_at(obj):
        return timezone.localtime(obj.enrolled_at).isoformat()


class ErrorResponse(Schema):
    data: Optional[dict] = None
    error: Optional[str] = None
