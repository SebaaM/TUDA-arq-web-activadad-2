# Backend Django y API OpenAPI

Aplicación Django con persistencia SQLite. La ruta `/` conserva la vista HTML clásica y `/api/v1` expone la API documentada con Django REST Framework y drf-spectacular.

## Requisitos

- Python 3.12 o posterior.

## Iniciar el proyecto

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_activities
python manage.py runserver
```

Abrir <http://127.0.0.1:8000/>.

## Documentación Swagger

Con el servidor iniciado, abrir:

- Swagger UI: <http://127.0.0.1:8000/api/docs>
- Documento OpenAPI JSON: <http://127.0.0.1:8000/api/openapi.json>
- Alias del esquema: <http://127.0.0.1:8000/api/v1/openapi.json>

`seed_activities` se puede ejecutar más de una vez: restaura el mismo conjunto de actividades sin duplicarlas.

## Contrato HTTP

| Método | Ruta | Éxito |
| --- | --- | --- |
| `GET` | `/api/v1/activities/` | `200`, colección con cupos disponibles |
| `GET` | `/api/v1/activities/{activity_id}/` | `200`, actividad |
| `GET` | `/api/v1/participants/` | `200`, participantes |
| `GET` | `/api/v1/participants/{participant_id}/` | `200`, participante |
| `GET` | `/api/v1/me/enrollments/` | `200`, inscripciones propias |
| `PUT` | `/api/v1/me/enrollments/{activity_id}/` | `201` al crear o `200` si ya existía (idempotente) |
| `DELETE` | `/api/v1/me/enrollments/{activity_id}/` | `204`, sin body (idempotente) |

Las operaciones bajo `/me` requieren `X-Participant-ID`. Una identidad ausente o desconocida produce `401`; una actividad o participante inexistente, `404`; y una actividad sin cupos, `409`. Los métodos no habilitados producen `405` con encabezado `Allow`.

### Formato de representación pública

Una actividad (tanto en la colección como en el detalle):

```json
{
  "id": "uuid",
  "title": "Taller de HTTP",
  "starts_at": "2026-04-10T18:00:00-03:00",
  "capacity": 20,
  "available_slots": 3
}
```

Una inscripción:

```json
{
  "activity_id": "uuid",
  "enrolled_at": "2026-04-03T15:20:00-03:00"
}
```

### Formato de error estable

Todos los errores usan una forma estable con `code` y `message`:

```json
{
  "code": "capacity_exhausted",
  "message": "No hay lugares disponibles."
}
```

Códigos disponibles: `capacity_exhausted`, `activity_not_found`, `authentication_required`.

### Idempotencia

- Un mismo `PUT` repetido devuelve `200` con la inscripción ya existente (se conserva `enrolled_at`, no se crea otra fila) en lugar de `409`.
- Un mismo `DELETE` repetido devuelve `204` igualmente; el efecto final es "sin inscripción".

## Trazabilidad: `X-Correlation-ID`

La API permite correlacionar una interacción concreta con sus respuestas y logs mediante el encabezado opcional `X-Correlation-ID`.

### Reglas del encabezado

- Si el request incluye `X-Correlation-ID`, la API **conserva exactamente** ese valor.
- Si no lo incluye, la API **genera un UUID** para la interacción.
- Todas las respuestas (éxito o error, v1 y v2) devuelven `X-Correlation-ID` con el valor efectivo.
- El valor se trata como identificador **opaco**: no se valida, no se normaliza ni se reemplaza.

```bash
curl -i -X PUT \
  -H "X-Participant-ID: a1234567-89ab-cdef-0123-456789abcdef" \
  -H "X-Correlation-ID: demo-42" \
  http://127.0.0.1:8000/api/v2/me/enrollments/1b470ddf-3e84-4b77-9aae-091d21e52bd6/

# HTTP/1.1 201 Created
# X-Correlation-ID: demo-42
```

### Eventos estructurados

Los logs de la API se emiten como una línea JSON por evento de negocios, con campos estables e identificados por el mismo `correlation_id`:

```json
{"timestamp": "2026-08-24T13:40:12-03:00", "level": "info", "event": "enrollment_created", "correlation_id": "demo-42", "method": "PUT", "path": "/api/v2/me/enrollments/1b470ddf-3e84-4b77-9aae-091d21e52bd6/", "result": "created", "activity_id": "1b470ddf-3e84-4b77-9aae-091d21e52bd6"}
```

Cada evento se emite a consola **y** se persiste de forma plana en
`backend/logs/trace.log` (un JSON por línea, UTF-8). El archivo rota al llegar a
1 MB y deja hasta 3 respaldos (`trace.log.1`, `trace.log.2`, `trace.log.3`).
`backend/logs/` está excluido de Git; borrarlo no afecta a la API porque el
directorio se recrea al iniciar. Para diagnosticar una interacción:

```bash
grep '"correlation_id": "demo-42"' backend/logs/trace.log
```

Eventos mínimos emitidos en cada interacción:

| Evento | Significado | Result posibles |
| --- | --- | --- |
| `request_received` | Entrada del request (emitido por el middleware) | — |
| `participant_auth_checked` | Verificación de la identidad de demostración | `ok`, `missing` |
| `activity_lookup` | Búsqueda de la actividad | `found`, `not_found` |
| `enrollment_created` | Inscripción creada | `created` |
| `enrollment_reused` | Inscripción ya existente (idempotente) | `reused` |
| `enrollment_rejected` | Inscripción rechazada por cupo | `capacity_exhausted` |
| `enrollment_cancelled` | Cancelación de inscripción | `cancelled`, `not_enrolled` |
| `request_completed` | Salida del request con status observable | `200`, `201`, `204`, `401`, `404`, `409`, `405`, `error` |

Con un mismo `correlation_id` es posible reconstruir la historia de una interacción:

```
request_received       correlation_id=demo-42
participant_auth_checked correlation_id=demo-42 result=ok
activity_lookup        correlation_id=demo-42 result=found
enrollment_created     correlation_id=demo-42 result=created
request_completed      correlation_id=demo-42 result=201
```

### Reglas de seguridad

Jamás se registran: valores de `Authorization`, cookies completas, tokens, ni payloads de request/response. La dirección de log siempre usa la ruta sin *query string* (`request.path`), de modo que un parámetro de consulta sensible no queda expuesto.

## Comandos útiles

```bash
# Ejecutar las pruebas
python manage.py test

# Abrir la consola de Django
python manage.py shell

# Vaciar la base y volver a cargar los datos de muestra
python manage.py flush --noinput
python manage.py seed_activities
```

## Estructura relevante

- `activities/models.py`: modelos `Activity`, `Participant` y `Enrollment`.
- `activities/views.py`: vista HTML clásica y vistas DRF de la API.
- `activities/api_urls.py`: enrutamiento de la API.
- `activities/serializers.py`: representaciones JSON públicas.
- `activities/templates/activities/activity_list.html`: documento HTML producido por Django.
- `activities/management/commands/seed_activities.py`: datos reproducibles.
- `correlation/middleware.py`: lectura/creación de `X-Correlation-ID` y eventos `request_received`/`request_completed`.
- `correlation/context.py`: contexto de trazabilidad (ContextVar) accesible sin pasar el ID en cada función.
- `correlation/log.py`: logger estructurado `tuda.trace` con schema estable y `log_event()`.

SQLite usa el archivo `db.sqlite3`, creado por `python manage.py migrate` y excluido de Git.
