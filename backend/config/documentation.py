from django.http import JsonResponse
from django.shortcuts import render


API_SCHEMA = {
    "openapi": "3.0.3",
    "info": {
        "title": "TUDA Activities API",
        "version": "v1",
        "description": "API para consultar actividades, participantes e inscripciones.",
    },
    "servers": [{"url": "http://127.0.0.1:8000"}],
    "paths": {
        "/api/v1/activities/": {
            "get": {"summary": "Listar actividades", "responses": {"200": {"description": "Actividades disponibles"}}}
        },
        "/api/v1/activities/{activity_id}/": {
            "get": {"summary": "Obtener una actividad", "parameters": [{"$ref": "#/components/parameters/ActivityId"}], "responses": {"200": {"description": "Actividad encontrada"}, "404": {"description": "Actividad inexistente"}}}
        },
        "/api/v1/participants/": {
            "get": {"summary": "Listar participantes", "responses": {"200": {"description": "Participantes encontrados"}}}
        },
        "/api/v1/participants/{participant_id}/": {
            "get": {"summary": "Obtener un participante", "parameters": [{"$ref": "#/components/parameters/ParticipantId"}], "responses": {"200": {"description": "Participante encontrado"}, "404": {"description": "Participante inexistente"}}}
        },
        "/api/v1/me/enrollments/": {
            "get": {"summary": "Listar mis inscripciones", "parameters": [{"$ref": "#/components/parameters/ParticipantHeader"}], "responses": {"200": {"description": "Inscripciones del participante"}, "400": {"description": "Identidad inválida"}}}
        },
        "/api/v1/me/enrollments/{id}/": {
            "get": {"summary": "Obtener una inscripción", "parameters": [{"$ref": "#/components/parameters/EnrollmentId"}], "responses": {"200": {"description": "Inscripción encontrada"}, "404": {"description": "Inscripción inexistente"}}}
        },
        "/api/v1/me/enrollments/{activity_id}/": {
            "put": {"summary": "Inscribirse en una actividad", "parameters": [{"$ref": "#/components/parameters/ActivityId"}, {"$ref": "#/components/parameters/ParticipantHeader"}], "responses": {"201": {"description": "Inscripción creada"}, "200": {"description": "Inscripción ya existente"}, "409": {"description": "Sin cupos"}}},
            "delete": {"summary": "Cancelar una inscripción", "parameters": [{"$ref": "#/components/parameters/ActivityId"}, {"$ref": "#/components/parameters/ParticipantHeader"}], "responses": {"204": {"description": "Inscripción cancelada"}, "404": {"description": "Inscripción inexistente"}}}
        },
        "/api/v1/me/enrollments/{activity_id}/cancel/": {
            "delete": {"summary": "Cancelar mi inscripción", "parameters": [{"$ref": "#/components/parameters/ActivityId"}, {"$ref": "#/components/parameters/ParticipantHeader"}], "responses": {"204": {"description": "Inscripción cancelada"}}}
        },
    },
    "components": {
        "parameters": {
            "ActivityId": {"name": "activity_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}},
            "ParticipantId": {"name": "participant_id", "in": "path", "required": True, "schema": {"type": "string", "format": "uuid"}},
            "EnrollmentId": {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
            "ParticipantHeader": {"name": "X-Participant-ID", "in": "header", "required": True, "description": "UUID del participante de prueba", "schema": {"type": "string", "format": "uuid"}},
        },
    },
}


def api_documentation(request):
    return render(request, "api_documentation/index.html", using="jinja2")


def swagger_ui(request):
    return render(request, "api_documentation/swagger.html", using="jinja2")


def redoc(request):
    return render(request, "api_documentation/redoc.html", using="jinja2")


def swagger_json(request):
    return JsonResponse(API_SCHEMA)