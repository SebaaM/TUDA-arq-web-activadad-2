from rest_framework import serializers

from django.utils import timezone

from .models import Activity, Enrollment


class LocalDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if value is None:
            return None
        return timezone.localtime(value).isoformat()


class ActivitySerializer(serializers.ModelSerializer):
    starts_at = LocalDateTimeField()
    available_slots = serializers.SerializerMethodField(
        help_text="Cupos disponibles según las inscripciones persistidas."
    )

    class Meta:
        model = Activity
        fields = ("id", "title", "starts_at", "capacity", "available_slots")

    def get_available_slots(self, activity) -> int:
        enrolled_count = getattr(activity, "enrolled_count", None)
        if enrolled_count is None:
            enrolled_count = Enrollment.objects.filter(activity=activity).count()
        return activity.capacity - enrolled_count


class EnrollmentSerializer(serializers.ModelSerializer):
    activity_id = serializers.UUIDField(source="activity.id", read_only=True)
    enrolled_at = LocalDateTimeField()

    class Meta:
        model = Enrollment
        fields = ("activity_id", "enrolled_at")


class ErrorSerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.CharField()
