from rest_framework import serializers

from django.utils import timezone

from .models import Activity, Enrollment, Participant


class LocalDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if value is None:
            return None
        return timezone.localtime(value).isoformat()


class ActivitySerializer(serializers.ModelSerializer):
    starts_at = LocalDateTimeField()

    class Meta:
        model = Activity
        fields = ("id", "title", "starts_at", "capacity")


class ActivityDetailSerializer(ActivitySerializer):
    available_slots = serializers.SerializerMethodField(
        help_text="Cupos disponibles según las inscripciones persistidas."
    )

    class Meta(ActivitySerializer.Meta):
        fields = ActivitySerializer.Meta.fields + ("available_slots",)

    def get_available_slots(self, activity) -> int:
        enrolled_count = getattr(activity, "enrolled_count", None)
        if enrolled_count is None:
            enrolled_count = Enrollment.objects.filter(activity=activity).count()
        return activity.capacity - enrolled_count


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ("id", "name")


class EnrollmentSerializer(serializers.Serializer):
    participant = ParticipantSerializer()
    activity = ActivitySerializer()
    enrolled_at = LocalDateTimeField()


class ActivitiesResponseSerializer(serializers.Serializer):
    data = ActivityDetailSerializer(many=True)
    error = serializers.CharField(allow_null=True)


class ActivityResponseSerializer(serializers.Serializer):
    data = ActivityDetailSerializer()


class ParticipantsResponseSerializer(serializers.Serializer):
    data = ParticipantSerializer(many=True)
    error = serializers.CharField(allow_null=True)


class ParticipantResponseSerializer(serializers.Serializer):
    data = ParticipantSerializer()
    error = serializers.CharField(allow_null=True)


class EnrollmentsResponseSerializer(serializers.Serializer):
    data = EnrollmentSerializer(many=True)
    error = serializers.CharField(allow_null=True)


class EnrollmentResponseSerializer(serializers.Serializer):
    data = EnrollmentSerializer()
    error = serializers.CharField(allow_null=True)


class ErrorResponseSerializer(serializers.Serializer):
    data = serializers.JSONField(allow_null=True)
    error = serializers.JSONField()


class MessageResponseSerializer(serializers.Serializer):
    error = serializers.CharField()
