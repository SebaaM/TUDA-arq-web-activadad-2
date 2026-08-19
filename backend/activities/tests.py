from datetime import datetime
from uuid import UUID

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Activity, Enrollment, Participant


class ActivityListTests(TestCase):
    def test_lists_every_activity_field(self):
        activity = Activity.objects.create(
            id=UUID("1b470ddf-3e84-4b77-9aae-091d21e52bd6"),
            title="Diseño de una API",
            starts_at=timezone.make_aware(datetime(2026, 3, 23, 18, 0)),
            capacity=30,
        )

        response = self.client.get(reverse("activities:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(activity.id))
        self.assertContains(response, activity.title)
        self.assertContains(response, "2026-03-23T18:00:00-03:00")
        self.assertContains(response, "30")

    def test_rejects_non_get_requests(self):
        response = self.client.post(reverse("activities:list"))

        self.assertEqual(response.status_code, 405)

    def test_activity_detail_includes_available_slots(self):
        activity = Activity.objects.create(
            title="Diseño de una API",
            starts_at=timezone.make_aware(datetime(2026, 3, 23, 18, 0)),
            capacity=2,
        )
        participant = Participant.objects.create(name="Juan García")
        Enrollment.objects.create(activity=activity, participant=participant)

        response = self.client.get(
            reverse("activities:api-activity-detail", args=[activity.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["available_slots"], 1)


class ActivityEnrollmentPutTests(TestCase):
    def setUp(self):
        self.activity = Activity.objects.create(
            title="Diseño de una API",
            starts_at=timezone.make_aware(datetime(2026, 3, 23, 18, 0)),
            capacity=1,
        )
        self.participant = Participant.objects.create(name="Juan García")

    def test_confirms_enrollment_when_activity_has_capacity(self):
        Enrollment.objects.create(
            activity=self.activity,
            participant=self.participant,
        )

        response = self.client.put(
            reverse(
                "activities:api-enrollment-confirm",
                args=[self.activity.id],
            ),
            HTTP_X_PARTICIPANT_ID=str(self.participant.id),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["activity"]["id"], str(self.activity.id))
        self.assertEqual(response.json()["data"]["participant"]["id"], str(self.participant.id))
        self.assertEqual(Enrollment.objects.filter(activity=self.activity).count(), 1)

    def test_rejects_enrollment_when_activity_capacity_is_exceeded(self):
        first_participant = Participant.objects.create(name="María López")
        Enrollment.objects.create(activity=self.activity, participant=first_participant)
        Enrollment.objects.create(activity=self.activity, participant=self.participant)

        response = self.client.put(
            reverse(
                "activities:api-enrollment-confirm",
                args=[self.activity.id],
            ),
            HTTP_X_PARTICIPANT_ID=str(self.participant.id),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["error"], "Activity capacity exceeded")
        self.assertEqual(Enrollment.objects.filter(activity=self.activity).count(), 2)

    def test_creates_enrollment_using_participant_header(self):
        response = self.client.put(
            reverse("activities:api-enrollment-confirm", args=[self.activity.id]),
            HTTP_X_PARTICIPANT_ID=str(self.participant.id),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Enrollment.objects.filter(
                activity=self.activity,
                participant=self.participant,
            ).exists()
        )

    def test_rejects_missing_participant_header(self):
        response = self.client.put(
            reverse("activities:api-enrollment-confirm", args=[self.activity.id]),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_rejects_unknown_activity(self):
        response = self.client.put(
            reverse(
                "activities:api-enrollment-confirm",
                args=["00000000-0000-0000-0000-000000000000"],
            ),
            HTTP_X_PARTICIPANT_ID=str(self.participant.id),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)

    def test_rejects_unsupported_method(self):
        response = self.client.post(
            reverse("activities:api-enrollment-confirm", args=[self.activity.id]),
            HTTP_X_PARTICIPANT_ID=str(self.participant.id),
        )

        self.assertEqual(response.status_code, 405)

    def test_lists_only_the_participant_enrollments(self):
        other_participant = Participant.objects.create(name="María López")
        Enrollment.objects.create(activity=self.activity, participant=other_participant)
        Enrollment.objects.create(activity=self.activity, participant=self.participant)

        response = self.client.get(
            reverse("activities:api-enrollment-list"),
            HTTP_X_PARTICIPANT_ID=str(self.participant.id),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)
        self.assertEqual(
            response.json()["data"][0]["participant"]["id"],
            str(self.participant.id),
        )

    def test_cancels_enrollment_using_participant_header(self):
        Enrollment.objects.create(activity=self.activity, participant=self.participant)

        response = self.client.delete(
            reverse("activities:api-enrollment-cancel", args=[self.activity.id]),
            HTTP_X_PARTICIPANT_ID=str(self.participant.id),
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            Enrollment.objects.filter(
                activity=self.activity,
                participant=self.participant,
            ).exists()
        )

    def test_rejects_canceling_unknown_enrollment(self):
        response = self.client.delete(
            reverse("activities:api-enrollment-cancel", args=[self.activity.id]),
            HTTP_X_PARTICIPANT_ID=str(self.participant.id),
        )

        self.assertEqual(response.status_code, 404)
