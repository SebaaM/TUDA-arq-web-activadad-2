# API de actividades

Documentación práctica de la API REST del proyecto TUDA.

## Datos básicos

- **Base URL local:** `http://127.0.0.1:8000`
- **Versión:** `v1`
- **Formato:** JSON
- **Content-Type:** `application/json`
- **Documentación interactiva:** `http://127.0.0.1:8000/swagger/`
- **Esquema OpenAPI:** `http://127.0.0.1:8000/swagger.json`

Los identificadores de actividades y participantes son UUID. En los ejemplos se usan estas variables:

```bash
BASE_URL="http://127.0.0.1:8000"
ACTIVITY_ID="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
PARTICIPANT_ID="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
```

En Windows PowerShell:

```powershell
$BASE_URL = "http://127.0.0.1:8000"
$ACTIVITY_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
$PARTICIPANT_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
```

La API no recibe un cuerpo JSON para las operaciones de consulta, inscripción o cancelación. La identidad de prueba se envía mediante el header `X-Participant-ID`.

## Resumen de endpoints

| Método   | Endpoint                                       | Descripción                                           | Respuesta exitosa        |
| -------- | ---------------------------------------------- | ----------------------------------------------------- | ------------------------ |
| `GET`    | `/api/v1/activities/`                          | Lista todas las actividades                           | `200 OK`                 |
| `GET`    | `/api/v1/activities/{activity_id}/`            | Obtiene una actividad                                 | `200 OK`                 |
| `GET`    | `/api/v1/participants/`                        | Lista todos los participantes                         | `200 OK`                 |
| `GET`    | `/api/v1/participants/{participant_id}/`       | Obtiene un participante                               | `200 OK`                 |
| `GET`    | `/api/v1/me/enrollments/`                      | Lista las inscripciones del participante identificado | `200 OK`                 |
| `GET`    | `/api/v1/me/enrollments/{id}/`                 | Obtiene una inscripción por su id                     | `200 OK`\*               |
| `PUT`    | `/api/v1/me/enrollments/{activity_id}/`        | Inscribe al participante en una actividad             | `201 Created` o `200 OK` |
| `DELETE` | `/api/v1/me/enrollments/{activity_id}/cancel/` | Cancela la inscripción del participante               | `204 No Content`         |

\* El endpoint de detalle de inscripción está declarado con `{id}`, pero actualmente la vista recibe `activity_id` y `participant_id`. Ver [inconsistencia conocida](#inconsistencia-conocida-en-el-detalle-de-inscripcion).

## 1. Listar actividades

### Petición

```bash
curl "$BASE_URL/api/v1/activities/"
```

### Respuesta `200 OK`

```json
{
	"data": [
		{
			"id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
			"title": "Introducción a la arquitectura web",
			"starts_at": "2026-08-20T10:00:00+02:00",
			"capacity": 30,
			"available_slots": 28
		}
	],
	"error": null
}
```

## 2. Obtener una actividad

### Petición

```bash
curl "$BASE_URL/api/v1/activities/$ACTIVITY_ID/"
```

### Respuesta `200 OK`

```json
{
	"data": {
		"id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
		"title": "Introducción a la arquitectura web",
		"starts_at": "2026-08-20T10:00:00+02:00",
		"capacity": 30,
		"available_slots": 28
	}
}
```

### Respuesta `404 Not Found`

```json
{
	"error": "Activity not found"
}
```

## 3. Listar participantes

### Petición

```bash
curl "$BASE_URL/api/v1/participants/"
```

### Respuesta `200 OK`

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

### Petición

```bash
curl "$BASE_URL/api/v1/participants/$PARTICIPANT_ID/"
```

### Respuesta `200 OK`

```json
{
	"data": {
		"id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
		"name": "Ana García"
	},
	"error": null
}
```

### Respuesta `404 Not Found`

```json
{
	"data": null,
	"error": "Participant not found"
}
```

## 5. Listar mis inscripciones

Este endpoint filtra las inscripciones usando el participante indicado en `X-Participant-ID`.

### Petición

```bash
curl \
  -H "X-Participant-ID: $PARTICIPANT_ID" \
  "$BASE_URL/api/v1/me/enrollments/"
```

### Respuesta `200 OK`

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
				"starts_at": "2026-08-20T10:00:00+02:00",
				"capacity": 30
			},
			"enrolled_at": "2026-08-19T12:30:00+02:00"
		}
	],
	"error": null
}
```

### Respuesta `400 Bad Request`

Se devuelve cuando falta el header o su UUID no corresponde a un participante existente.

```json
{
	"data": null,
	"error": "Invalid participant identity"
}
```

## 6. Obtener una inscripción

### Petición documentada actualmente

```bash
curl \
  -H "X-Participant-ID: $PARTICIPANT_ID" \
  "$BASE_URL/api/v1/me/enrollments/1/"
```

### Respuesta esperada `200 OK`

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
			"starts_at": "2026-08-20T10:00:00+02:00",
			"capacity": 30
		},
		"enrolled_at": "2026-08-19T12:30:00+02:00"
	},
	"error": null
}
```

### Respuesta `404 Not Found`

```json
{
	"data": null,
	"error": "Enrollment not found"
}
```

## 7. Inscribirse en una actividad

La operación `PUT` es idempotente: si el participante ya está inscrito, no se crea un duplicado y se devuelve `200 OK`.

### Petición

```bash
curl -X PUT \
  -H "X-Participant-ID: $PARTICIPANT_ID" \
  "$BASE_URL/api/v1/me/enrollments/$ACTIVITY_ID/"
```

### Respuesta `201 Created`

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
			"starts_at": "2026-08-20T10:00:00+02:00",
			"capacity": 30
		},
		"enrolled_at": "2026-08-19T12:30:00+02:00"
	},
	"error": null
}
```

### Respuesta `200 OK` cuando ya existe

El cuerpo tiene la misma estructura que el ejemplo anterior.

### Respuesta `400 Bad Request`

```json
{
	"data": null,
	"error": "Invalid participant identity"
}
```

### Respuesta `404 Not Found`

```json
{
	"data": null,
	"error": "Activity not found"
}
```

### Respuesta `409 Conflict`

```json
{
	"data": null,
	"error": "Activity capacity exceeded"
}
```

### Respuesta `403 Forbidden`

Django puede rechazar la petición si no se envía un token CSRF válido. Para clientes basados en sesión, hay que obtener la cookie y enviar el header `X-CSRFToken`.

## 8. Cancelar una inscripción

### Petición

```bash
curl -X DELETE \
  -H "X-Participant-ID: $PARTICIPANT_ID" \
  "$BASE_URL/api/v1/me/enrollments/$ACTIVITY_ID/cancel/"
```

### Respuesta `204 No Content`

La respuesta es correcta y no contiene cuerpo.

### Respuesta `400 Bad Request`

```json
{
	"data": null,
	"error": "Invalid participant identity"
}
```

### Respuesta `404 Not Found`

Actividad inexistente:

```json
{
	"data": null,
	"error": "Activity not found"
}
```

Inscripción inexistente:

```json
{
	"data": null,
	"error": "Enrollment not found"
}
```

### Respuesta `403 Forbidden`

Django puede rechazar la petición si no se envía un token CSRF válido.

## Códigos HTTP comunes

| Código | Significado                                               |
| ------ | --------------------------------------------------------- |
| `200`  | Consulta correcta o inscripción ya existente              |
| `201`  | Inscripción creada                                        |
| `204`  | Inscripción cancelada, sin contenido de respuesta         |
| `400`  | Identidad del participante ausente o inválida             |
| `403`  | Token CSRF ausente o inválido en operaciones de escritura |
| `404`  | Recurso o inscripción inexistente                         |
| `405`  | Método HTTP no permitido                                  |
| `409`  | La actividad no tiene cupos disponibles                   |
| `500`  | Error interno no previsto                                 |

## Inconsistencia conocida en el detalle de inscripción

La ruta actual en `backend/activities/urls.py` es:

```text
/api/v1/me/enrollments/<int:id>/
```

pero la vista `enrollment_api_detail` está definida con los parámetros `activity_id` y `participant_id`. Por ese motivo, la petición de la sección 6 puede producir un error del servidor en lugar de resolver la inscripción. La documentación OpenAPI también expone esta ruta como `/api/v1/me/enrollments/{id}/`.

Para que este endpoint sea funcional hay que decidir uno de estos contratos:

- Buscar la inscripción por un único `id` y adaptar la vista y el modelo.
- Cambiar la ruta para recibir `activity_id` y `participant_id`, y mantener la búsqueda compuesta actual.

Este archivo documenta el contrato publicado actualmente y deja la incompatibilidad visible hasta que se elija la corrección.
