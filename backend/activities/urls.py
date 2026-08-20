from django.urls import path

from . import views


app_name = "activities"

urlpatterns = [
    path("", views.activity_list, name="list"),
    path("api/v1/activities/", views.activities_collection, name="api-activity-list"),
    path("api/v1/activities/<uuid:activity_id>/", views.activity_api_detail, name="api-activity-detail"),
    path("api/v1/participants/", views.participant_api_list, name="api-participant-list"),
    path("api/v1/participants/<uuid:participant_id>/", views.participant_api_detail, name="api-participant-detail"),
    path("api/v1/me/enrollments/", views.enrollment_api_list, name="api-enrollment-list"),
    path("api/v1/me/enrollments/<int:id>/", views.enrollment_api_detail, name="api-enrollment-detail"),
    path("api/v1/me/enrollments/<uuid:activity_id>/", views.activity_enrollment_api_put, name="api-enrollment-confirm"),
    path("api/v1/me/enrollments/<uuid:activity_id>/cancel/", views.activity_enrollment_api_delete, name="api-enrollment-cancel"),
    
]

#    path("api/v1/activities/<uuid:activity_id>/", views.activity_api_detail, name="api-detail"),
