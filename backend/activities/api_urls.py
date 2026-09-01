from django.urls import path

from .views import (
    ActivityDetailView,
    ActivityEnrollmentView,
    ActivityListView,
    EnrollmentListView,
    ParticipantDetailView,
    ParticipantListView,
)


urlpatterns = [
    path("api/v1/activities/", ActivityListView.as_view(), name="api-activity-list"),
    path(
        "api/v1/activities/<uuid:activity_id>/",
        ActivityDetailView.as_view(),
        name="api-activity-detail",
    ),
    path(
        "api/v1/participants/",
        ParticipantListView.as_view(),
        name="api-participant-list",
    ),
    path(
        "api/v1/participants/<uuid:participant_id>/",
        ParticipantDetailView.as_view(),
        name="api-participant-detail",
    ),
    path(
        "api/v1/me/enrollments/",
        EnrollmentListView.as_view(),
        name="api-enrollment-list",
    ),
    path(
        "api/v1/me/enrollments/<uuid:activity_id>/",
        ActivityEnrollmentView.as_view(),
        name="api-enrollment-confirm",
    ),
]
