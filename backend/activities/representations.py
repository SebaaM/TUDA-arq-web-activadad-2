from django.utils import timezone

def serialize_activity(activity):
   
    return {
        "id": activity.id,
        "title": activity.title,
        "starts_at":  timezone.localtime(activity.starts_at).isoformat(),
        "capacity": activity.capacity,
    }

def serialize_activities(activities):
    return [serialize_activity(activity) for activity in activities]

def serialize_participant(participant):
    return {
        "id": participant.id,
        "name": participant.name,
    }

def serialize_participants(participants):
    return [serialize_participant(participant) for participant in participants]

def serialize_enrollment(enrollment):
    return {
        "participant": serialize_participant(enrollment.participant),
        "activity": serialize_activity(enrollment.activity),
        "enrolled_at": timezone.localtime(enrollment.enrolled_at).isoformat(),
    }

def serialize_enrollments(enrollments):
    return [serialize_enrollment(enrollment) for enrollment in enrollments]
