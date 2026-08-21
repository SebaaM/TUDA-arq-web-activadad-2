# API de actividades

API REST del proyecto TUDA implementada con **Django Ninja**. La especificación OpenAPI y Swagger UI se generan a partir de los esquemas y respuestas declarados en los endpoints.

## Datos básicos

- **Base URL local:** `http://127.0.0.1:8000`
- **Versión:** `v1`
- **Formato:** JSON (`application/json`)
- **Swagger UI:** `http://127.0.0.1:8000/api/docs`
- **OpenAPI JSON:** `http://127.0.0.1:8000/api/openapi.json`

Los IDs de actividades y participantes son UUID. La identidad de prueba se indica con el encabezado `X-Participant-ID`.

```bash
BASE_URL="http://127.0.0.1:8000"
ACTIVITY_ID="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
PARTICIPANT_ID="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
ENROLLMENT_ID=1
```

## Contrato de respuesta

Las colecciones y la mayoría de los recursos responden con el envoltorio `data` y `error`. En los casos correctos, `error` es `null`; en los errores de estos endpoints, `data` es `null`.

La consulta individual de una actividad conserva su formato original: en éxito devuelve solamente `data` y, si no existe, solamente `error`. La cancelación exitosa devuelve `204 No Content`, sin cuerpo.

## Resumen de endpoints

| Método | Endpoint | Resultado correcto |
| --- | --- | --- |
| `GET` | `/api/v1/activities/` | Lista las actividades y sus cupos disponibles |
| `GET` | `/api/v1/activities/{activity_id}/` | Obtiene una actividad |
| `GET` | `/api/v1/participants/` | Lista participantes |
| `GET` | `/api/v1/participants/{participant_id}/` | Obtiene un participante |
| `GET` | `/api/v1/me/enrollments/` | Lista las inscripciones del participante del header |
| `GET` | `/api/v1/me/enrollments/{id}/` | Obtiene una inscripción por su ID numérico |
| `PUT` | `/api/v1/me/enrollments/{activity_id}/` | Crea o confirma una inscripción |
| `DELETE` | `/api/v1/me/enrollments/{activity_id}/cancel/` | Cancela una inscripción |

## 1. Listar actividades

```bash
curl "$BASE_URL/api/v1/activities/"
```

Respuesta `200 OK`:

```json
{
  "data": [
    {
      "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "title": "Introducción a la arquitectura web",
      "starts_at": "2026-08-20T10:00:00-03:00",
      "capacity": 30,
      "available_slots": 28
    }
  ],
  "error": null
}
```

## 2. Obtener una actividad

```bash
curl "$BASE_URL/api/v1/activities/$ACTIVITY_ID/"
```

Respuesta `200 OK`:

```json
{
  "data": {
    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "title": "Introducción a la arquitectura web",
    "starts_at": "2026-08-20T10:00:00-03:00",
    "capacity": 30,
    "available_slots": 28
  }
}
```

Respuesta `404 Not Found`:

```json
{
  "error": "Activity not found"
}
```

## 3. Listar participantes

```bash
curl "$BASE_URL/api/v1/participants/"
```

Respuesta `200 OK`:

```json
{
  "data": [
    {
      "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
      "name": "Ana García"
    }
  ],
  "error": null
}
```

## 4. Obtener un participante

```bash
curl "$BASE_URL/api/v1/participants/$PARTICIPANT_ID/"
```

Respuesta `200 OK`:

```json
{
  "data": {
    "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    "name": "Ana García"
  },
  "error": null
}
```

Respuesta `404 Not Found`:

```json
{
  "data": null,
  "error": "Participant not found"
}
```

## 5. Listar mis inscripciones

```bash
curl -H "X-Participant-ID: $PARTICIPANT_ID" \
  "$BASE_URL/api/v1/me/enrollments/"
```

Respuesta `200 OK`:

```json
{
  "data": [
    {
      "participant": {
        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "name": "Ana García"
      },
      "activity": {
        "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "title": "Introducción a la arquitectura web",
        "starts_at": "2026-08-20T10:00:00-03:00",
        "capacity": 30
      },
      "enrolled_at": "2026-08-19T12:30:00-03:00"
    }
  ],
  "error": null
}
```

Respuesta `400 Bad Request` si el encabezado falta, no es un UUID válido o no identifica a un participante:

```json
{
  "data": null,
  "error": "Invalid participant identity"
}
```

## 6. Obtener una inscripción

```bash
curl "$BASE_URL/api/v1/me/enrollments/$ENROLLMENT_ID/"
```

Respuesta `200 OK`:

```json
{
  "data": {
    "participant": {
      "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
      "name": "Ana García"
    },
    "activity": {
      "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "title": "Introducción a la arquitectura web",
      "starts_at": "2026-08-20T10:00:00-03:00",
      "capacity": 30
    },
    "enrolled_at": "2026-08-19T12:30:00-03:00"
  },
  "error": null
}
```

Respuesta `404 Not Found`:

```json
{
  "data": null,
  "error": "Enrollment not found"
}
```

## 7. Inscribirse en una actividad

La operación es idempotente: si la inscripción ya existe devuelve la misma representación con `200 OK`, sin crear una fila adicional.

```bash
curl -X PUT \
  -H "X-Participant-ID: $PARTICIPANT_ID" \
  "$BASE_URL/api/v1/me/enrollments/$ACTIVITY_ID/"
```

Respuesta `201 Created` (o `200 OK` si ya existía):

```json
{
  "data": {
    "participant": {
      "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
      "name": "Ana García"
    },
    "activity": {
      "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "title": "Introducción a la arquitectura web",
      "starts_at": "2026-08-20T10:00:00-03:00",
      "capacity": 30
    },
    "enrolled_at": "2026-08-19T12:30:00-03:00"
  },
  "error": null
}
```

Respuestas de error:

```json
{
  "data": null,
  "error": "Invalid participant identity"
}
```

`400 Bad Request`, cuando el encabezado es inválido o falta.

```json
{
  "data": null,
  "error": "Activity not found"
}
```

`404 Not Found`, cuando no existe la actividad.

```json
{
  "data": null,
  "error": "Activity capacity exceeded"
}
```

`409 Conflict`, cuando no hay cupos disponibles.

## 8. Cancelar una inscripción

```bash
curl -X DELETE \
  -H "X-Participant-ID: $PARTICIPANT_ID" \
  "$BASE_URL/api/v1/me/enrollments/$ACTIVITY_ID/cancel/"
```

Respuesta `204 No Content`: no contiene cuerpo.

Errores `400 Bad Request` y `404 Not Found`:

```json
{
  "data": null,
  "error": "Invalid participant identity"
}
```

```json
{
  "data": null,
  "error": "Activity not found"
}
```

```json
{
  "data": null,
  "error": "Enrollment not found"
}
```

## Códigos HTTP

| Código | Uso |
| --- | --- |
| `200` | Consulta correcta o inscripción existente |
| `201` | Inscripción creada |
| `204` | Inscripción cancelada sin cuerpo |
| `400` | Identidad del participante inválida o ausente |
| `404` | Actividad, participante o inscripción inexistente |
| `405` | Método HTTP no permitido |
| `409` | Capacidad de la actividad agotada |
