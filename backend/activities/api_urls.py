from django.urls import path

from .views import (
    ActivityDetailView,
    ActivityDetailViewV2,
    ActivityEnrollmentView,
    ActivityEnrollmentViewV2,
    ActivityListView,
    ActivityListViewV2,
    EnrollmentListView,
    EnrollmentListViewV2,
    ParticipantDetailView,
    ParticipantListView,
)


urlpatterns_v1 = [
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

urlpatterns_v2 = [
    path("api/v2/activities/", ActivityListViewV2.as_view(), name="api-activity-list-v2"),
    path(
        "api/v2/activities/<uuid:activity_id>/",
        ActivityDetailViewV2.as_view(),
        name="api-activity-detail-v2",
    ),
    path(
        "api/v2/me/enrollments/",
        EnrollmentListViewV2.as_view(),
        name="api-enrollment-list-v2",
    ),
    path(
        "api/v2/me/enrollments/<uuid:activity_id>/",
        ActivityEnrollmentViewV2.as_view(),
        name="api-enrollment-confirm-v2",
    ),
]

urlpatterns = urlpatterns_v1 + urlpatterns_v2