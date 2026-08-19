from datetime import datetime
from uuid import UUID

from django.core.management.base import BaseCommand
from django.utils import timezone

from activities.models import Activity, Participant, Enrollment


PARTICIPANTS = [
    {
        "id": UUID("a1234567-89ab-cdef-0123-456789abcdef"),
        "name": "Juan García",
    },
    {
        "id": UUID("b2345678-90ab-cdef-0123-456789abcdef"),
        "name": "María López",
    },
    {
        "id": UUID("c3456789-01ab-cdef-0123-456789abcdef"),
        "name": "Carlos Martínez",
    },
    {
        "id": UUID("d4567890-12ab-cdef-0123-456789abcdef"),
        "name": "Ana Rodríguez",
    },
    {
        "id": UUID("e5678901-23ab-cdef-0123-456789abcdef"),
        "name": "Pedro Fernández",
    },
]

ENROLLMENTS = [
    {
        "activity_id": UUID("1b470ddf-3e84-4b77-9aae-091d21e52bd6"),  # Introducción a APIs web
        "participant_id": UUID("a1234567-89ab-cdef-0123-456789abcdef"),  # Juan García
        "enrolled_at": timezone.make_aware(datetime(2026, 3, 20, 10, 30)),
    },
    {
        "activity_id": UUID("1b470ddf-3e84-4b77-9aae-091d21e52bd6"),  # Introducción a APIs web
        "participant_id": UUID("b2345678-90ab-cdef-0123-456789abcdef"),  # María López
        "enrolled_at": timezone.make_aware(datetime(2026, 3, 21, 14, 15)),
    },
    {
        "activity_id": UUID("1b470ddf-3e84-4b77-9aae-091d21e52bd6"),  # Introducción a APIs web
        "participant_id": UUID("c3456789-01ab-cdef-0123-456789abcdef"),  # Carlos Martínez
        "enrolled_at": timezone.make_aware(datetime(2026, 3, 22, 9, 0)),
    },
    {
        "activity_id": UUID("6ccaf64f-d37e-4e6c-ae03-f3d6547bb297"),  # Contratos HTTP observables
        "participant_id": UUID("b2345678-90ab-cdef-0123-456789abcdef"),  # María López
        "enrolled_at": timezone.make_aware(datetime(2026, 3, 23, 11, 45)),
    },
    {
        "activity_id": UUID("6ccaf64f-d37e-4e6c-ae03-f3d6547bb297"),  # Contratos HTTP observables
        "participant_id": UUID("d4567890-12ab-cdef-0123-456789abcdef"),  # Ana Rodríguez
        "enrolled_at": timezone.make_aware(datetime(2026, 3, 23, 16, 20)),
    },
    {
        "activity_id": UUID("80c08526-3da1-4f0a-845c-740fa33f1f50"),  # Taller de integración
        "participant_id": UUID("c3456789-01ab-cdef-0123-456789abcdef"),  # Carlos Martínez
        "enrolled_at": timezone.make_aware(datetime(2026, 3, 24, 13, 30)),
    },
    {
        "activity_id": UUID("80c08526-3da1-4f0a-845c-740fa33f1f50"),  # Taller de integración
        "participant_id": UUID("e5678901-23ab-cdef-0123-456789abcdef"),  # Pedro Fernández
        "enrolled_at": timezone.make_aware(datetime(2026, 3, 25, 10, 0)),
    },
]


class Command(BaseCommand):
    help = "Restaura los participantes e inscripciones de muestra sin crear duplicados."

    def handle(self, *args, **options):
        # Restaurar participantes
        expected_participant_ids = [participant["id"] for participant in PARTICIPANTS]
        Participant.objects.exclude(id__in=expected_participant_ids).delete()

        for participant in PARTICIPANTS:
            participant_id = participant["id"]
            defaults = {key: value for key, value in participant.items() if key != "id"}
            Participant.objects.update_or_create(id=participant_id, defaults=defaults)

        # Restaurar inscripciones
        Enrollment.objects.all().delete()

        for enrollment in ENROLLMENTS:
            try:
                activity = Activity.objects.get(id=enrollment["activity_id"])
                participant = Participant.objects.get(id=enrollment["participant_id"])
                Enrollment.objects.get_or_create(
                    activity=activity,
                    participant=participant,
                    defaults={"enrolled_at": enrollment["enrolled_at"]},
                )
            except (Activity.DoesNotExist, Participant.DoesNotExist) as e:
                self.stdout.write(
                    self.style.WARNING(f"Advertencia: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Datos restaurados: {len(PARTICIPANTS)} participantes y {len(ENROLLMENTS)} inscripciones."
            )
        )
